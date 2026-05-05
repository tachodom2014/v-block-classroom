from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.utils import timezone

from .forms import AssignmentGradeForm, AssignmentSubmissionForm, SignUpForm
from .models import (
    AssignmentSubmission,
    Lesson,
    Question,
    QuestionResponse,
    UserProgress,
    VideoWatchTime,
)


def api_lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, is_active=True)
    
    model_url = None
    if lesson.model_file:
        try:
            model_url = lesson.model_file.url
        except ValueError:
            pass

    data = {
        "id": lesson.id,
        "title": lesson.title,
        "slug": lesson.slug,
        "modelUrl": model_url,
        "model_file": model_url,
    }
    return JsonResponse(data)


def _get_previous_lesson(lesson: Lesson):
    return (
        Lesson.objects.filter(is_active=True, order__lt=lesson.order)
        .order_by("-order")
        .first()
    )


def _grade_and_record(request, lesson: Lesson, user):
    question_ids = request.POST.getlist("question_ids")
    if not question_ids:
        return 0
    questions = Question.objects.filter(id__in=question_ids, lesson=lesson)
    question_map = {str(q.id): q for q in questions}
    score = 0
    responses = []
    for qid in question_ids:
        question = question_map.get(str(qid))
        if not question:
            continue
        answer = request.POST.get(f"answer_{qid}")
        if not answer:
            continue
        is_correct = answer == question.correct_answer
        if is_correct:
            score += 1
        responses.append(
            QuestionResponse(
                user=user,
                lesson=lesson,
                question=question,
                selected_choice=answer,
                is_correct=is_correct,
            )
        )
    if responses:
        QuestionResponse.objects.bulk_create(responses)
    return score


@login_required
def lesson_list(request):
    lessons = list(Lesson.objects.filter(is_active=True).order_by("order"))
    progress_map = {
        p.lesson_id: p
        for p in UserProgress.objects.filter(user=request.user, lesson__in=lessons)
    }
    unlocked_ids = set()
    for lesson in lessons:
        previous = _get_previous_lesson(lesson)
        if not previous:
            unlocked_ids.add(lesson.id)
            continue
        previous_progress = progress_map.get(previous.id)
        if previous_progress and previous_progress.is_completed:
            unlocked_ids.add(lesson.id)
    lesson_rows = [
        {
            "lesson": lesson,
            "unlocked": lesson.id in unlocked_ids,
            "progress": progress_map.get(lesson.id),
        }
        for lesson in lessons
    ]
    context = {"lesson_rows": lesson_rows}
    return render(request, "courses/lesson_list.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("courses:lesson_list")

    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("login")
        messages.error(request, "Please correct the errors below.")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, is_active=True)
    previous = _get_previous_lesson(lesson)
    if previous:
        previous_progress = UserProgress.objects.filter(
            user=request.user, lesson=previous
        ).first()
        if not previous_progress or not previous_progress.is_completed:
            messages.error(request, "Please complete the previous lesson first.")
            return redirect("courses:lesson_list")

    progress, _ = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)
    if progress.post_test_score is not None and not progress.is_completed:
        progress.is_completed = True
        progress.save(update_fields=["is_completed"])

    assignment_submission = AssignmentSubmission.objects.filter(
        user=request.user, lesson=lesson
    ).first()
    assignment_form = AssignmentSubmissionForm()
    if request.method == "POST" and request.POST.get("form_type") == "assignment":
        assignment_form = AssignmentSubmissionForm(request.POST, request.FILES)
        if assignment_form.is_valid():
            if assignment_submission:
                assignment_submission.file_upload = assignment_form.cleaned_data[
                    "file_upload"
                ]
                assignment_submission.save(update_fields=["file_upload", "updated_at"])
            else:
                assignment_submission = AssignmentSubmission.objects.create(
                    user=request.user,
                    lesson=lesson,
                    file_upload=assignment_form.cleaned_data["file_upload"],
                )
            messages.success(request, "Assignment uploaded successfully.")
            return redirect("courses:lesson_detail", slug=lesson.slug)
        messages.error(request, "Please upload a valid file.")

    pre_test_questions = None
    post_test_questions = None
    show_post_test = request.GET.get("post_test") == "1"

    if progress.pre_test_score is None:
        pre_test_questions = list(
            Question.objects.filter(lesson=lesson, test_type=Question.TestType.PRE_TEST)
            .order_by("?")[:15]
        )
        if request.method == "POST" and request.POST.get("test_type") == "pre":
            progress.pre_test_score = _grade_and_record(request, lesson, request.user)
            progress.save(update_fields=["pre_test_score"])
            messages.success(request, "Pre-test submitted.")
            return redirect("courses:lesson_detail", slug=lesson.slug)

    if progress.pre_test_score is not None:
        if request.method == "POST" and request.POST.get("test_type") == "post":
            progress.post_test_score = _grade_and_record(request, lesson, request.user)
            progress.is_completed = True
            progress.save(update_fields=["post_test_score", "is_completed"])
            messages.success(request, "Post-test submitted. Lesson completed.")
            return redirect("courses:lesson_detail", slug=lesson.slug)

        if progress.post_test_score is None and show_post_test:
            post_test_questions = list(
                Question.objects.filter(
                    lesson=lesson, test_type=Question.TestType.POST_TEST
                )
                .order_by("?")[:15]
            )

    context = {
        "lesson": lesson,
        "progress": progress,
        "assignment_submission": assignment_submission,
        "assignment_form": assignment_form,
        "pre_test_questions": pre_test_questions,
        "post_test_questions": post_test_questions,
        "show_post_test": show_post_test,
    }
    return render(request, "courses/lesson_detail.html", context)


@login_required
@require_POST
def track_video_time(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, is_active=True)
    seconds = request.POST.get("seconds")
    try:
        seconds_value = int(float(seconds))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "invalid seconds"}, status=400)

    watch_time, _ = VideoWatchTime.objects.get_or_create(
        user=request.user, lesson=lesson
    )
    if seconds_value > watch_time.seconds_watched:
        watch_time.seconds_watched = seconds_value
        watch_time.save(update_fields=["seconds_watched", "updated_at"])
    return JsonResponse({"ok": True, "seconds": watch_time.seconds_watched})


@login_required
def teacher_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Instructor access only.")
        return redirect("courses:lesson_list")

    time_on_task = (
        VideoWatchTime.objects.values("lesson__title")
        .annotate(
            avg_seconds=Avg("seconds_watched"),
            total_seconds=Sum("seconds_watched"),
            student_count=Count("id"),
        )
        .order_by("lesson__title")
    )

    distractor_counts = (
        QuestionResponse.objects.filter(is_correct=False)
        .values("question_id", "selected_choice")
        .annotate(count=Count("id"))
    )
    distractor_map = {}
    for row in distractor_counts:
        distractor_map.setdefault(row["question_id"], {})[row["selected_choice"]] = row[
            "count"
        ]

    question_stats = (
        QuestionResponse.objects.values("question_id")
        .annotate(
            total=Count("id"),
            incorrect=Count("id", filter=Q(is_correct=False)),
        )
        .order_by("-incorrect")[:10]
    )
    questions = {
        q.id: q
        for q in Question.objects.filter(id__in=[row["question_id"] for row in question_stats])
    }
    top_missed = [
        {
            "question": questions.get(row["question_id"]),
            "incorrect": row["incorrect"],
            "total": row["total"],
            "distractors": distractor_map.get(row["question_id"], {}),
        }
        for row in question_stats
    ]

    confusion_rows = (
        QuestionResponse.objects.filter(
            Q(question__text__icontains="isometric")
            | Q(question__text__icontains="oblique")
        )
        .values("question_id", "selected_choice")
        .annotate(count=Count("id"))
    )
    confusion_map = {}
    for row in confusion_rows:
        confusion_map.setdefault(row["question_id"], {})[row["selected_choice"]] = row["count"]
    confusion_questions = Question.objects.filter(id__in=confusion_map.keys())
    confusion_items = [
        {
            "question": question,
            "distractors": confusion_map.get(question.id, {}),
        }
        for question in confusion_questions
    ]

    rubric_averages = (
        AssignmentSubmission.objects.values("lesson__title")
        .annotate(
            avg_angle=Avg("angle_precision_score"),
            avg_scale=Avg("scale_accuracy_score"),
            avg_line=Avg("line_technique_score"),
            avg_ellipse=Avg("elliptical_accuracy_score"),
        )
        .order_by("lesson__title")
    )

    remedial_students = (
        UserProgress.objects.filter(post_test_score__lt=9)
        .select_related("user", "lesson")
        .order_by("lesson__order", "user__username")
    )

    recent_submissions = (
        AssignmentSubmission.objects.select_related("user", "lesson")
        .order_by("-updated_at")[:20]
    )

    context = {
        "time_on_task": time_on_task,
        "top_missed": top_missed,
        "confusion_items": confusion_items,
        "rubric_averages": rubric_averages,
        "remedial_students": remedial_students,
        "recent_submissions": recent_submissions,
    }
    return render(request, "courses/teacher_dashboard.html", context)


@login_required
def grade_submission(request, submission_id):
    if not request.user.is_staff:
        messages.error(request, "Instructor access only.")
        return redirect("courses:lesson_list")

    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    form = AssignmentGradeForm(instance=submission)
    if request.method == "POST":
        form = AssignmentGradeForm(request.POST, instance=submission)
        if form.is_valid():
            graded = form.save(commit=False)
            graded.graded_by = request.user
            graded.graded_at = timezone.now()
            graded.save()
            messages.success(request, "Grades saved.")
            return redirect("courses:grade_submission", submission_id=submission.id)

    context = {"submission": submission, "form": form}
    return render(request, "courses/grade_submission.html", context)

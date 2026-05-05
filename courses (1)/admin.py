from django.contrib import admin

from .models import (
    AssignmentSubmission,
    Lesson,
    Question,
    QuestionResponse,
    UserProgress,
    VideoWatchTime,
)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "standard_ref", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "test_type", "text")
    list_filter = ("test_type", "lesson")
    search_fields = ("text",)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "lesson",
        "pre_test_score",
        "post_test_score",
        "is_completed",
    )
    list_filter = ("lesson", "is_completed")
    search_fields = ("user__username", "user__email")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "lesson",
        "angle_precision_score",
        "scale_accuracy_score",
        "line_technique_score",
        "elliptical_accuracy_score",
        "total_score",
        "updated_at",
    )
    list_filter = ("lesson",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("submitted_at", "updated_at", "total_score")
    fieldsets = (
        (
            "Submission",
            {
                "fields": (
                    "user",
                    "lesson",
                    "file_upload",
                    "submitted_at",
                    "updated_at",
                )
            },
        ),
        (
            "Rubric Scores",
            {
                "fields": (
                    "angle_precision_score",
                    "scale_accuracy_score",
                    "line_technique_score",
                    "elliptical_accuracy_score",
                    "total_score",
                )
            },
        ),
        ("Feedback", {"fields": ("teacher_feedback", "graded_by", "graded_at")}),
    )


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "question", "selected_choice", "is_correct")
    list_filter = ("lesson", "is_correct")
    search_fields = ("user__username", "user__email", "question__text")


@admin.register(VideoWatchTime)
class VideoWatchTimeAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "seconds_watched", "updated_at")
    list_filter = ("lesson",)
    search_fields = ("user__username", "user__email")

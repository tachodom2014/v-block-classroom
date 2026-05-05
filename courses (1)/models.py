from django.conf import settings
from django.db import models


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to="lesson_videos/", blank=True, null=True)
    model_file = models.FileField(
        upload_to="lesson_models/",
        blank=True,
        null=True,
        help_text="Upload .glb, .gltf, or .stl files"
    )
    learning_outcome = models.TextField(verbose_name="Behavioral Learning Outcome", blank=True)
    standard_ref = models.CharField(max_length=100, default="ISO 5456 / ISO 128")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    class TestType(models.TextChoices):
        PRE_TEST = "PRE_TEST", "Pre-test"
        POST_TEST = "POST_TEST", "Post-test"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    choice_1 = models.CharField(max_length=255)
    choice_2 = models.CharField(max_length=255)
    choice_3 = models.CharField(max_length=255, blank=True)
    choice_4 = models.CharField(max_length=255, blank=True)
    correct_answer = models.CharField(
        max_length=1,
        choices=[("1", "Choice 1"), ("2", "Choice 2"), ("3", "Choice 3"), ("4", "Choice 4")],
    )
    test_type = models.CharField(max_length=9, choices=TestType.choices)

    def __str__(self) -> str:
        return f"{self.lesson.title} - {self.get_test_type_display()}"


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    pre_test_score = models.PositiveIntegerField(null=True, blank=True)
    post_test_score = models.PositiveIntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self) -> str:
        return f"{self.user} - {self.lesson}"


class AssignmentSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    file_upload = models.FileField(upload_to="submissions/drawing/")
    angle_precision_score = models.PositiveIntegerField(default=0)
    scale_accuracy_score = models.PositiveIntegerField(default=0)
    line_technique_score = models.PositiveIntegerField(default=0)
    elliptical_accuracy_score = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    teacher_feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self) -> str:
        return f"{self.user} - {self.lesson} submission"

    def save(self, *args, **kwargs):
        self.total_score = (
            self.angle_precision_score
            + self.scale_accuracy_score
            + self.line_technique_score
            + self.elliptical_accuracy_score
        )
        super().save(*args, **kwargs)


class QuestionResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["lesson", "question", "is_correct"]),
        ]


class VideoWatchTime(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    seconds_watched = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "lesson")

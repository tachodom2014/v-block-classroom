from django.urls import path

from . import views


app_name = "courses"

urlpatterns = [
    path("", views.lesson_list, name="lesson_list"),
    path("signup/", views.signup, name="signup"),
    path("lesson/<slug:slug>/", views.lesson_detail, name="lesson_detail"),
    path(
        "lesson/<slug:slug>/track-time/",
        views.track_video_time,
        name="track_video_time",
    ),
    path("instructor/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path(
        "instructor/grade/<int:submission_id>/",
        views.grade_submission,
        name="grade_submission",
    ),
    path("api/lesson/<slug:slug>/", views.api_lesson_detail, name="api_lesson_detail"),
]

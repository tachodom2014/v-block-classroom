from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import AssignmentSubmission

User = get_user_model()


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ["file_upload"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file_upload"].widget.attrs.update({"class": "form-control"})


class AssignmentGradeForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "angle_precision_score",
            "scale_accuracy_score",
            "line_technique_score",
            "elliptical_accuracy_score",
            "teacher_feedback",
        ]
        widgets = {
            "teacher_feedback": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            if name != "teacher_feedback":
                self.fields[name].widget.attrs.update({"class": "form-control"})
        self.fields["teacher_feedback"].widget.attrs.update({"class": "form-control"})


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("full_name", "username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({"class": "form-control"})

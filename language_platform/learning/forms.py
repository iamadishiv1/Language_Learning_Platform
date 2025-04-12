from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import BaseInlineFormSet
from .models import Profile, Course, Lesson, Exercise, Quiz, Question, Answer

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'languages_of_interest')

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'language', 'description', 'difficulty', 'is_active')
        widgets = {
            'language': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'difficulty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('course', 'title', 'content', 'order')

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ('lesson', 'title', 'question', 'answer', 'explanation')

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('lesson', 'title', 'description')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('quiz', 'text', 'order')

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('question', 'text', 'is_correct')

class AnswerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_answers = 0
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    correct_answers += 1
        if correct_answers < 1:
            raise forms.ValidationError('At least one answer must be marked as correct.')
        

from django import forms

class FeedbackForm(forms.Form):
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter constructive feedback...'
        }),
        label='Your Feedback',
        required=True
    )
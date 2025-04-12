from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Profile, Language, Course, Lesson, Exercise, 
    Quiz, Question, Answer, UserProgress,
    UserExerciseAttempt, UserQuizAttempt
)
from .forms import AnswerFormSet

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile', )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

class AnswerInline(admin.TabularInline):
    model = Answer
    formset = AnswerFormSet
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completion_percentage', 'has_feedback', 'feedback_date')
    list_filter = ('course', 'user', 'feedback_date')
    search_fields = ('user__username', 'course__title', 'admin_feedback')
    readonly_fields = ('feedback_date',)
    
    def completion_percentage(self, obj):
        return f"{obj.get_completion_percentage():.0f}%"
    completion_percentage.short_description = 'Progress'
    
    def has_feedback(self, obj):
        return obj.has_feedback()
    has_feedback.boolean = True

# Unregister User if already registered
if User in admin.site._registry:
    admin.site.unregister(User)

# Register all models - NOTE: UserProgress is registered with UserProgressAdmin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Language)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(Exercise)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(UserProgress, UserProgressAdmin)  # Correct registration
admin.site.register(UserExerciseAttempt)
admin.site.register(UserQuizAttempt)

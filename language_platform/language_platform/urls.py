"""
URL configuration for language_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for language_platform project.
"""

from django.contrib import admin
from django.urls import path
from learning import views
from django.conf import settings
from django.conf.urls.static import static

# Authentication URLs
auth_urlpatterns = [
    path('registration/login/', views.user_login, name='login'),
    path('registration/logout/', views.user_logout, name='logout'),
    path('registration/signup/', views.signup, name='signup'),
]

# Profile URLs
profile_urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),  # Changed to hyphen for consistency
]

# Course URLs
course_urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
]

# Lesson URLs
lesson_urlpatterns = [
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('courses/<int:course_id>/lessons/create/', views.create_lesson, name='create_lesson'),
]

# Exercise URLs
exercise_urlpatterns = [
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercises/<int:exercise_id>/edit/', views.edit_exercise, name='edit_exercise'),
    path('exercises/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),
    path('lessons/<int:lesson_id>/exercises/create/', views.create_exercise, name='create_exercise'),
]

# Quiz URLs
quiz_urlpatterns = [
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quizzes/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('questions/<int:question_id>/add-answer/', views.add_answer, name='add_answer'),
    path('lessons/<int:lesson_id>/quizzes/create/', views.create_quiz, name='create_quiz'),
]

# Progress URLs
progress_urlpatterns = [
    path('my-progress/', views.my_progress, name='my_progress'),
]

# Combine all URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-tools/progress/', views.admin_progress_view, name='admin_progress_view'),
    path('admin-tools/progress/<int:progress_id>/feedback/', views.add_feedback, name='add_feedback'),
    path('', views.home, name='home'),
    *auth_urlpatterns,
    *profile_urlpatterns,
    *course_urlpatterns,
    *lesson_urlpatterns,
    *exercise_urlpatterns,
    *quiz_urlpatterns,
    *progress_urlpatterns,

]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
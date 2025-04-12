from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from .forms import (
    SignUpForm, ProfileForm, CourseForm, LessonForm, 
    ExerciseForm, QuizForm, QuestionForm, AnswerForm
)
from .models import (
    Profile, Language, Course, Lesson, Exercise, 
    Quiz, Question, Answer, UserProgress,
    UserExerciseAttempt, UserQuizAttempt
)
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

def is_admin(user):
    return user.is_superuser

# Authentication Views
def home(request):
    courses = Course.objects.filter(is_active=True).order_by('-created_at')[:4]
    return render(request, 'home.html', {'courses': courses})

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists. Please try a different username.")
            return redirect('signup')
            
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered. Please use a different email or login.")
            return redirect('signup')
            
        # Check password match
        if password1 != password2:
            messages.error(request, "Passwords don't match. Please try again.")
            return redirect('signup')
            
        # Create user if validation passes
        try:
            user = User.objects.create_user(username, email, password1)
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            
    return render(request, 'registration/signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_profile')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

# Profile Views
@login_required
def profile(request):
    user_progress = UserProgress.objects.filter(user=request.user).select_related('course')
    
    context = {
        'user': request.user,
        'progress_records': user_progress,
    }
    return render(request, 'profile.html', context)

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    if not request.user.is_superuser:
        return redirect('profile')
    
    courses = Course.objects.all()
    return render(request, 'admin_profile.html', {'courses': courses})

@login_required
@login_required
def edit_profile(request):
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
        
    return render(request, 'edit_profile.html', {'form': form})

# Course Views
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    lessons = course.lesson_set.all().order_by('order')
    
    # Check if user has progress for this course
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            course=course
        )
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'user_progress': user_progress
    })

@login_required
@user_passes_test(is_admin)
def create_course(request):
    if not request.user.is_superuser:
        return redirect('home')
        
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('admin_profile')
    else:
        form = CourseForm()
    
    return render(request, 'courses/create_course.html', {
        'form': form,
        'languages': Language.objects.all()  # Pass languages to template if needed
    })

@login_required
@user_passes_test(is_admin)
def edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/edit_course.html', {
        'form': form,
        'course': course  # Make sure to pass the course to the template
    })
@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('admin_profile')
    return render(request, 'courses/delete_course.html', {'course': course})

# Lesson Views
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    exercises = lesson.exercise_set.all()
    quizzes = lesson.quiz_set.all()
    
    # Mark lesson as completed if user submits the form
    if request.user.is_authenticated:
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            course=lesson.course
        )
        
        if request.method == 'POST' and 'complete_lesson' in request.POST:
            user_progress.completed_lessons.add(lesson)
            messages.success(request, 'Lesson marked as completed!')
            return redirect('lesson_detail', lesson_id=lesson.id)
        
        is_completed = user_progress.completed_lessons.filter(id=lesson.id).exists()
    else:
        is_completed = False
    
    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'exercises': exercises,
        'quizzes': quizzes,
        'is_completed': is_completed
    })

@login_required
@user_passes_test(is_admin)
def create_lesson(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm(initial={'course': course})
    return render(request, 'lessons/create_lesson.html', {'form': form, 'course': course})

@login_required
@user_passes_test(is_admin)
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')
            return redirect('course_detail', course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'lessons/edit_lesson.html', {'form': form, 'lesson': lesson})

@login_required
@user_passes_test(is_admin)
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course_id = lesson.course.id
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    return render(request, 'lessons/delete_lesson.html', {'lesson': lesson})

# Exercise Views
@login_required
def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    user_attempts = UserExerciseAttempt.objects.filter(
        user=request.user,
        exercise=exercise
    ).order_by('-timestamp') if request.user.is_authenticated else None
    
    if request.method == 'POST':
        user_answer = request.POST.get('answer', '')
        is_correct = user_answer.lower() == exercise.answer.lower()
        
        attempt = UserExerciseAttempt(
            user=request.user,
            exercise=exercise,
            attempt=user_answer,
            is_correct=is_correct,
            feedback=exercise.explanation if is_correct else "Try again!"
        )
        attempt.save()
        
        messages.success(request, 'Your answer has been submitted!')
        return redirect('exercise_detail', exercise_id=exercise.id)
    
    return render(request, 'exercises/exercise_detail.html', {
        'exercise': exercise,
        'user_attempts': user_attempts
    })

@login_required
@user_passes_test(is_admin)
def create_exercise(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.lesson = lesson
            exercise.save()
            messages.success(request, 'Exercise created successfully!')
            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = ExerciseForm(initial={'lesson': lesson})
    return render(request, 'exercises/create_exercise.html', {'form': form, 'lesson': lesson})

@login_required
@user_passes_test(is_admin)
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exercise updated successfully!')
            return redirect('lesson_detail', lesson_id=exercise.lesson.id)
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'exercises/edit_exercise.html', {'form': form, 'exercise': exercise})

@login_required
@user_passes_test(is_admin)
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    lesson_id = exercise.lesson.id
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, 'Exercise deleted successfully!')
        return redirect('lesson_detail', lesson_id=lesson_id)
    return render(request, 'exercises/delete_exercise.html', {'exercise': exercise})

# Quiz Views
@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = quiz.question_set.all().prefetch_related('answer_set')
    user_attempts = UserQuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz
    ).order_by('-completed_at') if request.user.is_authenticated else None
    
    if request.method == 'POST':
        score = 0
        total_questions = quiz.question_set.count()
        
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1
        
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        
        attempt = UserQuizAttempt(
            user=request.user,
            quiz=quiz,
            score=percentage
        )
        attempt.save()
        
        messages.success(request, f'Quiz completed! Your score: {percentage:.1f}%')
        return redirect('quiz_detail', quiz_id=quiz.id)
    
    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'user_attempts': user_attempts
    })

@login_required
@user_passes_test(is_admin)
def create_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()
            messages.success(request, 'Quiz created successfully! Now add questions.')
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm(initial={'lesson': lesson})
    return render(request, 'quizzes/create_quiz.html', {'form': form, 'lesson': lesson})

@login_required
@user_passes_test(is_admin)
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added! Add answers now.')
            return redirect('add_answer', question_id=question.id)
    else:
        form = QuestionForm(initial={'quiz': quiz})
    return render(request, 'quizzes/add_question.html', {'form': form, 'quiz': quiz})

@login_required
@user_passes_test(is_admin)
def add_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            messages.success(request, 'Answer added! Add another or go back.')
            return redirect('add_answer', question_id=question.id)
    else:
        form = AnswerForm(initial={'question': question})
    return render(request, 'quizzes/add_answer.html', {'form': form, 'question': question})

@login_required
@user_passes_test(is_admin)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('lesson_detail', lesson_id=quiz.lesson.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quizzes/edit_quiz.html', {'form': form, 'quiz': quiz})

@login_required
@user_passes_test(is_admin)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    lesson_id = quiz.lesson.id
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('lesson_detail', lesson_id=lesson_id)
    return render(request, 'quizzes/delete_quiz.html', {'quiz': quiz})

# Progress Tracking
@login_required
def my_progress(request):
    user_progress = UserProgress.objects.filter(user=request.user)
    exercise_attempts = UserExerciseAttempt.objects.filter(user=request.user)
    quiz_attempts = UserQuizAttempt.objects.filter(user=request.user)
    
    # Calculate some statistics
    courses_completed = 0
    for progress in user_progress:
        total_lessons = progress.course.lesson_set.count()
        completed_lessons = progress.completed_lessons.count()
        if total_lessons > 0 and completed_lessons == total_lessons:
            courses_completed += 1
    
    avg_quiz_score = quiz_attempts.aggregate(Avg('score'))['score__avg'] or 0
    
    return render(request, 'progress/my_progress.html', {
        'user_progress': user_progress,
        'exercise_attempts': exercise_attempts,
        'quiz_attempts': quiz_attempts,
        'courses_completed': courses_completed,
        'avg_quiz_score': avg_quiz_score
    })


from django.contrib.auth.decorators import user_passes_test

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_progress_view(request):
    # Get all user progress records
    progress_records = UserProgress.objects.all().select_related('user', 'course')

    # Filter by course if specified
    course_id = request.GET.get('course_id')
    if course_id:
        progress_records = progress_records.filter(course_id=course_id)
    
    # Filter by user if specified
    user_id = request.GET.get('user_id')
    if user_id:
        progress_records = progress_records.filter(user_id=user_id)

    # Calculate completion percentage for each record
    for record in progress_records:
        total_lessons = record.course.lesson_set.count()
        completed_lessons = record.completed_lessons.count()
    
    return render(request, 'admin/progress_overview.html', {
        'progress_records': progress_records,
        'courses': Course.objects.all(),
        'users': User.objects.filter(is_staff=False)  # Only regular users
    })

from django.core.mail import send_mail
from .forms import FeedbackForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_feedback(request, progress_id):
    progress = get_object_or_404(
        UserProgress.objects.select_related('user', 'course'),
        pk=progress_id
    )
    
    quiz_attempts = UserQuizAttempt.objects.filter(
        user=progress.user,
        quiz__lesson__course=progress.course
    ).select_related('quiz')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            progress.admin_feedback = form.cleaned_data['feedback']
            progress.feedback_date = timezone.now()
            progress.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('admin_progress_view')
    else:
        form = FeedbackForm(initial={'feedback': progress.admin_feedback})
    
    return render(request, 'admin/add_feedback.html', {
        'progress': progress,
        'quiz_attempts': quiz_attempts,
        'form': form
    })
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Exam, Submission, StudentAnswer, ExamQuestion, QuestionOption

@login_required
def exam_list(request):
    """
    Lists exams available for the student based on their enrolled classes.
    """
    # 1. Get classes user is enrolled in
    enrolled_classes = request.user.enrolled_classes.all()
    
    # 2. Get exams for these classes
    # Filter by is_published=True
    exams = Exam.objects.filter(
        class_session__in=enrolled_classes,
        is_published=True
    ).order_by('scheduled_at')
    
    # Check status for each exam (Taken vs Not Taken)
    exam_status = []
    for exam in exams:
        submission = Submission.objects.filter(exam=exam, student=request.user).first()
        status = 'OPEN'
        score = None
        
        if submission:
            status = 'SUBMITTED'
            score = submission.grade
        elif exam.scheduled_at > timezone.now():
            status = 'FUTURE'
            
        exam_status.append({
            'exam': exam,
            'status': status,
            'score': score
        })
        
    return render(request, 'assessments/exam_list.html', {'exam_attempts': exam_status})

@login_required
def take_exam(request, exam_id):
    """
    Interface for taking the exam.
    """
    exam = get_object_or_404(Exam, id=exam_id)
    
    # 1. Validation: Is student enrolled?
    if not request.user.enrolled_classes.filter(id=exam.class_session.id).exists():
        messages.error(request, "Você não está matriculado nesta turma.")
        return redirect('assessments:exam_list')
        
    # 2. Validation: Already submitted?
    if Submission.objects.filter(exam=exam, student=request.user).exists():
        messages.info(request, "Você já realizou esta prova.")
        return redirect('assessments:exam_list')
    
    # 3. POST: Submit Answers
    if request.method == 'POST':
        # Create Submission
        submission = Submission.objects.create(
            exam=exam,
            student=request.user,
        )
        
        total_points = 0
        earned_points = 0
        
        # Process each question
        exam_questions = ExamQuestion.objects.filter(exam=exam)
        
        for eq in exam_questions:
            question_id = eq.question.id
            q_type = eq.question.question_type
            points_possible = eq.points
            total_points += points_possible
            
            answer_points = 0
            is_correct = False
            
            # Create StudentAnswer
            answ = StudentAnswer(
                submission=submission,
                question=eq.question
            )
            
            if q_type in ['MULTIPLE_CHOICE', 'TRUE_FALSE']:
                selected_opt_id = request.POST.get(f'question_{question_id}')
                if selected_opt_id:
                    try:
                        option = QuestionOption.objects.get(id=selected_opt_id)
                        answ.selected_option = option
                        if option.is_correct:
                            is_correct = True
                            answer_points = points_possible
                    except:
                        pass
            
            elif q_type == 'FILL_THE_BLANK':
                text_input = request.POST.get(f'question_{question_id}_text', '').strip().lower()
                answ.text_answer = text_input
                
                # Check against Correct Option (assuming one option holds the correct string)
                correct_option = eq.question.options.filter(is_correct=True).first()
                if correct_option and correct_option.text.strip().lower() == text_input:
                    is_correct = True
                    answer_points = points_possible
            
            elif q_type == 'ESSAY':
                text_input = request.POST.get(f'question_{question_id}_text')
                answ.text_answer = text_input
                # Essay needs manual grading, so is_correct remains None
            
            answ.is_correct = is_correct if q_type != 'ESSAY' else None
            answ.points_awarded = answer_points
            answ.save()
            
            earned_points += answer_points
            
        # Update Submission with preliminary grade (only auto-graded parts)
        submission.grade = earned_points 
        submission.save()
        
        messages.success(request, "Prova enviada com sucesso!")
        return redirect('assessments:view_grade', submission_id=submission.id)

    # 4. GET: Render Form
    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question').order_by('order')
    
    context = {
        'exam': exam,
        'questions': exam_questions
    }
    return render(request, 'assessments/take_exam.html', context)

@login_required
def view_grade(request, submission_id):
    """
    Shows the result of a submission with feedback.
    """
    submission = get_object_or_404(Submission, id=submission_id, student=request.user)
    answers = StudentAnswer.objects.filter(submission=submission).select_related('question', 'selected_option')
    
    context = {
        'submission': submission,
        'answers': answers
    }
    return render(request, 'assessments/view_grade.html', context)

# =============================================================================
# TEACHER / INSTRUCTOR VIEWS
# =============================================================================

@login_required
def teacher_dashboard(request):
    """
    Shows list of exams created by the instructor (or related to their classes).
    """
    # Assuming user is an instructor if they have linked classes
    # Fetch classes where user is instructor
    teaching_classes = request.user.teaching_classes.all()
    
    # Get exams for these classes
    exams = Exam.objects.filter(class_session__in=teaching_classes).order_by('-scheduled_at')
    
    context = {
        'exams': exams
    }
    return render(request, 'assessments/teacher/dashboard.html', context)

@login_required
def exam_results(request, exam_id):
    """
    Shows all submissions for a specific exam.
    """
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Ensure user is instructor of this class (or admin)
    if exam.class_session.instructor != request.user and not request.user.is_superuser:
         messages.error(request, "Permissão negada.")
         return redirect('assessments:teacher_dashboard')

    submissions = Submission.objects.filter(exam=exam).select_related('student').order_by('-submitted_at')
    
    context = {
        'exam': exam,
        'submissions': submissions
    }
    return render(request, 'assessments/teacher/exam_results.html', context)

@login_required
def grade_submission(request, submission_id):
    """
    Interface for manual grading (Essays) and feedback.
    """
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Permission check
    if submission.exam.class_session.instructor != request.user and not request.user.is_superuser:
         messages.error(request, "Permissão negada.")
         return redirect('assessments:teacher_dashboard')

    if request.method == 'POST':
        # Update manual points for specific questions logic
        # For simplicity, we might update the final grade or iterate over answers
        
        # Example: Updating points for specific answers
        for key, value in request.POST.items():
            if key.startswith('points_'):
                answer_id = key.split('_')[1]
                try:
                    points = float(value)
                    stud_answer = StudentAnswer.objects.get(id=answer_id, submission=submission)
                    stud_answer.points_awarded = points
                    stud_answer.is_correct = True # Mark as graded/correct if points > 0
                    stud_answer.save()
                except ValueError:
                    pass
            elif key == 'final_feedback':
                submission.feedback = value

        # Recalculate Total Score
        total_score = sum(a.points_awarded for a in submission.answers.all())
        submission.grade = total_score
        submission.save()
        
        messages.success(request, "Notas atualizadas com sucesso!")
        return redirect('assessments:exam_results', exam_id=submission.exam.id)

    answers = StudentAnswer.objects.filter(submission=submission).select_related('question')
    
    context = {
        'submission': submission,
        'answers': answers
    }
    return render(request, 'assessments/teacher/grade_submission.html', context)

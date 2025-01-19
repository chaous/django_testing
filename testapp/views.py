from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
import datetime

from django.contrib.auth import views as auth_views

from .models import (
    Test, Question, AnswerOption,
    Student, StudentTest, StudentAnswer
)
from .forms import (
    RegisterForm, TestForm, QuestionForm, AnswerOptionForm
)

class MyLogoutView(auth_views.LogoutView):
    http_method_names = ['get','post']
    next_page = 'home'

def home_view(request):
    return render(request, 'testapp/home.html')

def instructions_view(request):
    return render(request, 'testapp/instructions.html')

def register_view(request):
    if request.method=='POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Student.objects.create(user=user)
            login(request,user)
            messages.success(request,'Регистрация ok!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request,'testapp/register.html',{'form':form})

@login_required
def become_admin_view(request):
    request.user.is_staff=True
    request.user.save()
    messages.info(request,'Теперь вы админ!')
    return redirect('home')

@login_required
def list_tests_view(request):
    tests= Test.objects.all()
    return render(request,'testapp/list_tests.html',{
        'tests': tests
    })

@login_required
def create_test_view(request):
    if request.method=='POST':
        form= TestForm(request.POST)
        if form.is_valid():
            new_test= form.save()
            messages.success(request,'Тест создан.')
            return redirect('manage_test', test_id=new_test.id)
    else:
        form= TestForm()
    return render(request,'testapp/create_test.html',{'form':form})

@login_required
def manage_test_view(request, test_id):
    test= get_object_or_404(Test, id=test_id)
    questions= test.questions.all()
    return render(request,'testapp/manage_test.html',{
        'test': test,
        'questions': questions
    })

@login_required
def delete_test_view(request, test_id):
    if not request.user.is_staff:
        messages.error(request,'Нет прав на удаление!')
        return redirect('home')
    test= get_object_or_404(Test, id=test_id)
    test.delete()
    messages.success(request,'Тест удалён.')
    return redirect('list_tests')

@login_required
def create_question_view(request, test_id):
    test= get_object_or_404(Test, id=test_id)
    if request.method=='POST':
        form= QuestionForm(request.POST)
        if form.is_valid():
            q= form.save(commit=False)
            q.test= test
            q.save()
            messages.success(request,'Вопрос добавлен.')
            if q.question_type in ('single','multiple'):
                return redirect('manage_answers', question_id=q.id)
            else:
                return redirect('manage_test', test_id=test.id)
    else:
        form= QuestionForm()
    return render(request,'testapp/create_question.html',{
        'test': test,
        'form': form
    })

@login_required
def manage_answers_view(request, question_id):
    question= get_object_or_404(Question, id=question_id)
    # if question.question_type =='text':
    #     messages.error(request,'text-вопрос не нуждается в вариантах.')
    #     return redirect('manage_test', test_id=question.test.id)
    answers= question.options.all()
    return render(request,'testapp/manage_answers.html',{
        'question': question,
        'answers': answers
    })

@login_required
def create_answer_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Если вопрос text — варианты не нужны
    # if question.question_type == 'text':
    #     messages.error(request, 'text-вопрос не нуждается в вариантах ответов.')
    #     return redirect('manage_test', test_id=question.test.id)

    if request.method == 'POST':
        form = AnswerOptionForm(request.POST)
        if form.is_valid():
            is_correct_new = form.cleaned_data['is_correct']

            # Если это single и новый вариант помечен как правильный, проверяем
            if question.question_type == 'single' and is_correct_new:
                # Уже ли есть правильный?
                already_correct = question.options.filter(is_correct=True).exists()
                if already_correct:
                    form.add_error(
                        'is_correct',
                        'Вопрос типа "single" уже имеет правильный ответ. Нельзя добавить второй.'
                    )
                    # Перерисуем форму
                    return render(request, 'testapp/create_answer.html', {
                        'question': question,
                        'form': form
                    })

            ans = form.save(commit=False)
            ans.question = question
            ans.save()
            messages.success(request, 'Вариант ответа добавлен!')
            return redirect('manage_answers', question_id=question.id)
        else:
            # Форма неверна, заново рендерим
            return render(request, 'testapp/create_answer.html', {
                'question': question,
                'form': form
            })
    else:
        form = AnswerOptionForm()

    return render(request, 'testapp/create_answer.html', {
        'question': question,
        'form': form
    })


@login_required
def delete_question_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    test = question.test
    # Проверяем права (обычно is_staff)
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав удалять вопросы.')
        return redirect('home')

    question.delete()
    messages.success(request, 'Вопрос удалён.')
    return redirect('manage_test', test_id=test.id)


@login_required
def list_results_view(request):
    if not request.user.is_staff:
        messages.error(request,'Нет прав (admin).')
        return redirect('home')
    st_tests= StudentTest.objects.select_related('student','test').order_by('-start_datetime')
    return render(request,'testapp/list_results.html',{
        'all_results': st_tests
    })

def test_access_view(request):
    if request.method=='POST':
        key= request.POST.get('access_key')
        test= Test.objects.filter(access_key=key).first()
        if not test:
            messages.error(request,'Неверный ключ!')
            return redirect('test_access')
        if not test.is_active:
            messages.error(request,'Тест недоступен (время).')
            return redirect('test_access')
        if not request.user.is_authenticated:
            messages.info(request,'Сначала войдите.')
            return redirect('login')
        student,_= Student.objects.get_or_create(user=request.user)
        st_test, _= StudentTest.objects.get_or_create(student=student, test=test)
        messages.success(request,'Доступ к тесту получен!')
        return redirect('test_detail', pk=test.id)
    return render(request,'testapp/test_access.html')

@login_required
def test_detail_view(request, pk):
    test= get_object_or_404(Test, pk=pk)
    student= get_object_or_404(Student, user=request.user)
    try:
        st_test= StudentTest.objects.get(student=student, test=test)
    except StudentTest.DoesNotExist:
        return HttpResponse('Нет доступа. <a href="/test_access/">Ввести ключ</a>.')

    if test.questions.count()==0:
        messages.error(request,'Тест без вопросов.')
        return redirect('test_access')

    if st_test.end_datetime:
        messages.info(request,'Тест уже завершён.')
        return redirect('test_result', st_id=st_test.id)

    now= timezone.now()
    deadline= st_test.start_datetime + datetime.timedelta(minutes=test.duration_minutes)
    if now >= deadline or now >= test.end_time:
        return finish_test(st_test)

    questions= test.questions.all()
    if request.method=='POST':
        # Сохраняем ответы
        for q in questions:
            field_name= f"q_{q.id}"
            if q.question_type == 'single':
                ans_id = request.POST.get(field_name)
                if ans_id:
                    ans_opt= AnswerOption.objects.filter(id=ans_id, question=q).first()
                    StudentAnswer.objects.update_or_create(
                        student_test= st_test,
                        question= q,
                        defaults={'answer_option': ans_opt, 'answer_text': ''}
                    )
            elif q.question_type == 'multiple':
                ans_list = request.POST.getlist(field_name)
                # сначала удалим старые
                StudentAnswer.objects.filter(student_test= st_test, question=q).delete()
                for aid in ans_list:
                    ans_opt= AnswerOption.objects.filter(id=aid, question=q).first()
                    if ans_opt:
                        StudentAnswer.objects.create(
                            student_test= st_test,
                            question= q,
                            answer_option= ans_opt
                        )
            else:
                # text-вопрос
                txt= request.POST.get(field_name) or ''
                StudentAnswer.objects.update_or_create(
                    student_test= st_test,
                    question= q,
                    defaults={'answer_option': None, 'answer_text': txt}
                )
        return finish_test(st_test)

    return render(request, 'testapp/test_detail.html', {
        'test': test,
        'st_test': st_test,
        'questions': questions,
        'deadline': deadline
    })

from django.utils import timezone

def finish_test(st_test):
    test = st_test.test
    questions = test.questions.all()
    user_score = 0

    for q in questions:
        ans_set = StudentAnswer.objects.filter(student_test=st_test, question=q)

        if q.question_type == 'single':
            ans = ans_set.first()
            if ans and ans.answer_option and ans.answer_option.is_correct:
                user_score += q.score

        elif q.question_type == 'multiple':
            correct_ids = set(q.options.filter(is_correct=True).values_list('id', flat=True))
            chosen_ids = set(ans_set.values_list('answer_option_id', flat=True))
            if correct_ids == chosen_ids:
                user_score += q.score

        elif q.question_type == 'text':
            ans = ans_set.first()
            if ans:
                user_text = ans.answer_text.strip().lower()
                correct_opts = q.options.filter(is_correct=True)
                for opt in correct_opts:
                    opt_text = opt.text.strip().lower()
                    if user_text == opt_text:
                        user_score += q.score
                        break

    # После цикла сохраняем результат
    st_test.score = user_score
    st_test.passed = (user_score >= test.pass_score)
    st_test.end_datetime = timezone.now()
    st_test.save()

    return redirect('test_result', st_id=st_test.id)

@login_required
def test_result_view(request, st_id):
    st_test = get_object_or_404(StudentTest, id=st_id)
    if st_test.student.user != request.user and not request.user.is_staff:
        messages.error(request, 'Нет доступа к результату.')
        return redirect('test_access')

    # Собираем данные для подробного отображения
    test = st_test.test
    questions = test.questions.all()

    details = []
    for q in questions:
        # Найдём ответ(ы) пользователя
        student_answers = st_test.answers.filter(question=q)
        # Проверим, верно ли
        if q.question_type == 'single':
            # допустим, один student_answer
            ans_obj = student_answers.first()
            user_text = ans_obj.answer_option.text if (ans_obj and ans_obj.answer_option) else '(нет ответа)'
            correct = (ans_obj and ans_obj.answer_option and ans_obj.answer_option.is_correct)
        elif q.question_type == 'multiple':
            # возможно несколько StudentAnswer
            user_texts = []
            correct = True
            chosen_ids = set(student_answers.values_list('answer_option_id', flat=True))
            correct_ids = set(q.options.filter(is_correct=True).values_list('id', flat=True))
            for sa in student_answers:
                if sa.answer_option:
                    user_texts.append(sa.answer_option.text)
            user_text = ', '.join(user_texts) if user_texts else '(нет ответа)'
            if chosen_ids != correct_ids:
                correct = False
        else:  # text
            ans_obj = student_answers.first()
            if ans_obj:
                user_text = ans_obj.answer_text
                # Проверим, есть ли совпадение
                valid_opts = [opt.text.strip().lower() for opt in q.options.filter(is_correct=True)]
                correct = (user_text.strip().lower() in valid_opts)
            else:
                user_text = '(нет ответа)'
                correct = False

        details.append({
            'question': q,
            'user_text': user_text,
            'correct': correct
        })

    return render(request, 'testapp/test_result.html', {
        'student_test': st_test,
        'details': details  # передаём в шаблон
    })

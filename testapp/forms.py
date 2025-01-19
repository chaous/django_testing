from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Test, Question, AnswerOption

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    class Meta:
        model = User
        fields = ('username','email','password1','password2')

class TestForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
        label='Начало'
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
        label='Окончание'
    )
    class Meta:
        model = Test
        fields = ['title','description','start_time','end_time','duration_minutes','pass_score','access_key']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'correct_text', 'score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qtype = self.initial.get('question_type') or (self.instance.question_type if self.instance.pk else None)
        if not qtype:
            qtype = 'single'  # По умолчанию

        if qtype == 'text':
            # Для текстового вопроса показываем correct_text
            self.fields['correct_text'].widget = forms.TextInput()
            self.fields['correct_text'].required = True
            self.fields['correct_text'].help_text = "Укажите правильный ответ для text-вопроса."
        else:
            # Для single/multiple — скрываем correct_text
            self.fields['correct_text'].required = False
            self.fields['correct_text'].widget = forms.HiddenInput()


class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['text','is_correct']
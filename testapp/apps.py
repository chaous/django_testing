from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
import datetime

class TestappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testapp'

@receiver(post_migrate)
def create_demo_test(sender, **kwargs):
    if sender.name != 'testapp':
        return

    from .models import Test, Question, AnswerOption

    now = timezone.now()
    start_time = now - datetime.timedelta(hours=1)
    end_time   = now + datetime.timedelta(days=1)

    test, created = Test.objects.get_or_create(
        access_key='DEMOKEY',
        defaults={
            'title': 'Demo Conspiracy Test',
            'description': '(DEMOKEY) Active right now.',
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': 10,
            'pass_score': 50
        }
    )
    if created:
        q1 = Question.objects.create(test=test, text='Форма Земли?', question_type='single', score=10)
        AnswerOption.objects.create(question=q1, text='Круглая', is_correct=False)
        AnswerOption.objects.create(question=q1, text='Плоская', is_correct=True)

        q2 = Question.objects.create(test=test, text='2+2=?', question_type='text', correct_text='4', score=40)
        print("[post_migrate] DEMOKEY test created (active).")
    else:
        print("[post_migrate] DEMOKEY already exists.")
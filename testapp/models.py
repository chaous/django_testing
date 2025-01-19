from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    pass_score = models.IntegerField(default=100)
    access_key = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return (self.start_time <= now <= self.end_time)

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('single','Один вариант'),
        ('multiple','Несколько вариантов'),
        ('text','Текст')
    ]
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='single')
    correct_text = models.CharField(max_length=255, blank=True)
    score = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.text[:60]} (score={{self.score}})"

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:60]

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    def __str__(self):
        return self.user.username

class StudentTest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{{self.student}} - {{self.test}}"

class StudentAnswer(models.Model):
    student_test = models.ForeignKey(StudentTest, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    answer_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{{self.student_test.student}} => {{self.question}}"
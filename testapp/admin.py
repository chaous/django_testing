from django.contrib import admin
from .models import Test, Question, AnswerOption, Student, StudentTest, StudentAnswer

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title','start_time','end_time','duration_minutes','access_key')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text','test','question_type','score','correct_text')

@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text','question','is_correct')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(StudentTest)
class StudentTestAdmin(admin.ModelAdmin):
    list_display = ('student','test','score','passed')

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student_test','question','answer_option','answer_text')
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from testapp.views import (
    MyLogoutView,
    home_view,
    instructions_view,
    register_view,
    become_admin_view,
    list_tests_view,
    create_test_view,
    manage_test_view,
    delete_test_view,
    create_question_view,
    manage_answers_view,
    create_answer_view,
    list_results_view,
    test_access_view,
    test_detail_view,
    test_result_view,
    delete_question_view
)

def redirect_home(request):
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', MyLogoutView.as_view(next_page='home'), name='logout'),
    path('delete_question/<int:question_id>/', delete_question_view, name='delete_question'),

    path('', redirect_home, name='root'),
    path('home/', home_view, name='home'),
    path('instructions/', instructions_view, name='instructions'),
    path('register/', register_view, name='register'),
    path('become_admin/', become_admin_view, name='become_admin'),

    path('list_tests/', list_tests_view, name='list_tests'),
    path('create_test/', create_test_view, name='create_test'),
    path('manage_test/<int:test_id>/', manage_test_view, name='manage_test'),
    path('tests/<int:test_id>/delete_test/', delete_test_view, name='delete_test'),

    path('create_question/<int:test_id>/', create_question_view, name='create_question'),
    path('manage_answers/<int:question_id>/', manage_answers_view, name='manage_answers'),
    path('create_answer/<int:question_id>/', create_answer_view, name='create_answer'),

    path('list_results/', list_results_view, name='list_results'),
    path('test_access/', test_access_view, name='test_access'),
    path('test/<int:pk>/', test_detail_view, name='test_detail'),
    path('test_result/<int:st_id>/', test_result_view, name='test_result'),
]
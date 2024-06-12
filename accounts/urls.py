from django.urls import path, include
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView, LoginView, LogoutView
    )
from .views import (
        profile, profile_single, admin_panel, 
        profile_update, change_password, 
        LecturerListView, StudentListView, 
        staff_add_view, edit_staff, 
        delete_staff, student_add_view, 
        edit_student, delete_student, validate_username, register,
        home_view, delete_notification, mark_notification_as_viewed,
        run_check_last_date
    )
from .forms import EmailValidationOnForgotPassword
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', home_view, name='home'),
    path('mark_notification_as_viewed/<int:notification_id>', mark_notification_as_viewed, name='mark_notification_as_viewed'),
    path('delete_notification/<int:notification_id>', delete_notification, name='delete_notification'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/admin_panel/', admin_panel, name='admin_panel'),
    path('accounts/start_mark_chek/', run_check_last_date, name='start_mark_chek'),
    
    

    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/<int:id>/detail/', profile_single, name='profile_single'),
    path('accounts/setting/', profile_update, name='edit_profile'),
    path('accounts/change_password/', change_password, name='change_password'),

    path('accounts/lecturers/', LecturerListView.as_view(), name='lecturer_list'),
    path('accounts/lecturer/add/', staff_add_view, name='add_lecturer'),
    path('accounts/staff/<int:pk>/edit/', edit_staff, name='staff_edit'),
    path('accounts/lecturers/<int:pk>/delete/', delete_staff, name='lecturer_delete'),

    path('accounts/students/', StudentListView.as_view(), name='student_list'),
    path('accounts/student/add/', student_add_view, name='add_student'),
    path('accounts/student/<int:pk>/edit/', edit_student, name='student_edit'),
    path('accounts/students/<int:pk>/delete/', delete_student, name='student_delete'),

    path('accounts/ajax/validate-username/', validate_username, name='validate_username'),

    path('accounts/register/', register, name='register'),

    # ################################################################
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),

    path('accounts/password-reset/', PasswordResetView.as_view(
        form_class=EmailValidationOnForgotPassword,
        template_name='registration/password_reset.html'
    ),
         name='password_reset'),
    path('accounts/password-reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ),
         name='password_reset_done'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ),
         name='password_reset_confirm'),
    path('accounts/password-reset-complete/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ),
         name='password_reset_complete')
    # ################################################################
]

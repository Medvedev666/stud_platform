from django.urls import path
from .views import *


urlpatterns = [
    # urls групп
    path('', group_view, name='groups'),
    path('<int:pk>/detail/', group_detail, name='group_detail'),
    path('add/', group_add, name='add_group'),
    path('<int:pk>/edit/', group_edit, name='edit_group'),
    path('<int:pk>/delete/', group_delete, name='group_delete'),

    # # urls курсов
    # path('course/<slug>/detail/', course_single, name='course_detail'),
    # path('<int:pk>/course/add/', course_add, name='course_add'),
    # path('course/<slug>/edit/', course_edit, name='edit_course'),
    # path('course/delete/<slug>/', course_delete, name='delete_course'),

    # # urls распределения курсов
    # path('course/assign/', CourseAllocationFormView.as_view(), name='course_allocation'),
    # path('course/allocated/', course_allocation_view, name='course_allocation_view'),
    # path('allocated_course/<int:pk>/edit/', edit_allocated_course, name='edit_allocated_course'),
    # path('course/<int:pk>/deallocate/', deallocate_course, name='course_deallocate'),

    # urls загрузки файлов
    path('course/<int:pk>/documentations/upload/', handle_file_upload, name='upload_file_view'),
    path('course/<int:pk>/documentations/<int:file_id>/edit/', handle_file_edit, name='upload_file_edit'),
    path('course/<int:pk>/documentations/<int:file_id>/delete/', handle_file_delete, name='upload_file_delete'),

    path('my_groups/', user_course_list, name="user_course_list"),

    # назначение курса сотруднику
    path('course/show_assignments/<int:pk>', submitted_assignments, name="assignments"),
    path('course/add_assignments/<int:pk>/all/<int:exercise_pk>/', create_add_stud_task, name="add_assignments_all"),
    # path('course/add_assignment/<int:pk>/', create_add_stud_task_one, name="add_assignment"),
    path('course/add_assignment_one/<int:pk>/<int:student_id>/<int:exercise_pk>/', create_add_stud_task_one_choice, name="create_add_stud_task_one_choice"),
    path('course/show_students_task', show_students_task, name="show_students_task"),
    path('course/all_students_for_task/<int:pk>/<int:task_pk>', all_students_for_task, name="all_students_for_task"),
    
    # просмотр результата
    path('show_stud_result/', show_stud_result, name="show_stud_result"),
    path('course/update_mark/<int:pk>/<int:task_id>/<int:new_mark>', update_mark, name="update_mark"),

    # оставить комментарий
    path('<int:pk>/create_comment/<int:task_id>', add_comment, name="create_comment"),
    path('<int:pk>/comment_edit/<int:task_id>/comment/<int:comment_id>', comment_edit, name="comment_edit"),

    # CourseAllocation urls
    path('course/assign/', CourseAllocationFormView.as_view(), name='course_allocation'),
    path('course/allocated/', course_allocation_view, name='course_allocation_view'),
    path('allocated_course/<int:pk>/edit/', edit_allocated_course, name='edit_allocated_course'),
    path('course/<int:pk>/deallocate/', deallocate_course, name='course_deallocate'),
]

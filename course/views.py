from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils import timezone

from accounts.models import User, Student
from accounts.decorators import lecturer_required, student_required
from .forms import (
    GroupForm, UploadFormFile,
    AddStudTaskForm, CommentsForm,
    CourseAllocationForm, EditCourseAllocationForm
)
from .models import (
    Group, CourseAllocation, 
    Upload, AddStudTask, Comments
)


# ########################################################
# Group views
# ########################################################
@login_required
def group_view(request):
    groups = Group.objects.all()
    group_filter = request.GET.get('group_filter')
    if group_filter:
        groups = Group.objects.filter(title__icontains=group_filter)

    if request.user.is_student:
        student = Student.objects.get(student__pk=request.user.id)
        return render(request, 'course/group_list.html', {
            'title': "Группы",
            'groups': groups,
            'student': student,
        })
    else:
        return render(request, 'course/group_list.html', {
            'title': "Группы",
            'groups': groups,
        })


@login_required
@lecturer_required
def group_add(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, request.POST.get('title') + ' программа была создана.')
            return redirect('groups')
        else:
            messages.error(request, 'Исправьте ошибки ниже.')
    else:
        form = GroupForm()

    return render(request, 'course/group_add.html', {
        'title': "Добавить группу",
        'form': form,
    })


@login_required
def group_detail(request, pk):
    print(f'{pk=}')
    group = Group.objects.get(pk=pk)
    courses = Upload.objects.filter(course__pk=pk).order_by('title')

    paginator = Paginator(courses, 10)
    
    if request.user.is_student:
        student = Student.objects.get(student__pk=request.user.id)

        page = request.GET.get('page')
        page = paginator.get_page(page)

        return render(request, 'course/group_single.html', {
            'title': group.title,
            'group': group, 
            'courses': courses, 
        }, )
    elif request.user.is_lecturer:
        students = Student.objects.filter(department=group)
        if CourseAllocation.objects.filter(courses=pk, lecturer=request.user).exists():
            chek = True
        else:
            chek = False
        
        return render(request, 'course/group_single.html', {
            'title': group.title,
            'group': group, 
            'courses': courses, 
            'chek': chek,
            'students': students,
        }, )
    else:
        students = Student.objects.filter(department=group)

        page = request.GET.get('page')

        page = paginator.get_page(page)

        print(f'{courses=}')

        context = {
            'title': group.title,
            'group': group, 
            'courses': courses,
            'students': students,
        }

        return render(request, 'course/group_single.html', context)


@login_required
@lecturer_required
def group_edit(request, pk):
    group = Group.objects.get(pk=pk)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        print(f'{form.errors}')
        if form.is_valid():
            form.save()
            messages.success(request, str(request.POST.get('title')) + ' программа была обновлена.')
            return redirect('groups')
    else:
        form = GroupForm(instance=group)

    return render(request, 'course/group_add.html', {
        'title': "Редактировать группу",
        'form': form
    })

@login_required
@lecturer_required
def group_delete(request, pk):
    group = Group.objects.get(pk=pk)

    title = group.title
    group.delete()
    messages.success(request, 'Программа ' + title + ' была удалена.')

    return redirect('groups')
# ########################################################



# ########################################################
# File Upload views
# ########################################################
@login_required
@lecturer_required
def handle_file_upload(request, pk):
    course = Group.objects.get(pk=pk)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, {'course': course})
        # file_name = request.POST.get('name')
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' был загружен.'))
            return redirect('group_detail', pk=pk)
    else:
        form = UploadFormFile()
    return render(request, 'upload/upload_file_form.html', {
        'title': "Загрузить файл",
        'form': form, 'course': course
    })


@login_required
@lecturer_required
def handle_file_edit(request, pk, file_id):
    course = Group.objects.get(pk=pk)
    instance = Upload.objects.get(pk=file_id)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        # file_name = request.POST.get('name')
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' был обновлен.'))
            return redirect('group_detail', pk=pk)
    else:
        form = UploadFormFile(instance=instance)

    return render(request, 'upload/upload_file_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_file_delete(request, pk, file_id):
    file = Upload.objects.get(pk=file_id)
    # file_name = file.name
    file.delete()

    messages.success(request, (file.title + ' был удален.'))
    return redirect('group_detail', pk=pk)



@login_required
def user_course_list(request):
    title = 'Мои группы'
    if request.user.is_lecturer:
        courses = Group.objects.filter(allocated_course__lecturer__pk=request.user.id)

        # Получаем все аллокации курсов для данного руководителя
        allocations = CourseAllocation.objects.filter(lecturer=request.user)

        # Создаем пустой список для хранения групп
        lecturer_groups = []
        # Для каждой аллокации курса
        for allocation in allocations:
            # Получаем курсы, связанные с текущей аллокацией
            courses = allocation.courses.all()

            for course in courses:
                group = course

                if group not in lecturer_groups:
                    lecturer_groups.append(group)

        context = {
            'title': title,
            'courses': courses,
            'groups': lecturer_groups
        }
        return render(request, 'course/user_course_list.html', context)

    elif request.user.is_student:
        return redirect('groups')
    else:
        title = 'Группы'
        return render(request, 'course/user_course_list.html', {'title': title})

@login_required
def submitted_assignments(request, pk):

    comments = Comments.objects.all()

    if request.user.is_student:
        return redirect('groups')

    course = Group.objects.get(pk=pk)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    # is_user_in_lecturers = lecturers.filter(lecturer=request.user).exists()

    if not request.user.is_lecturer and not request.user.is_superuser:
        return redirect('groups')
    
    sub_task = AddStudTask.objects.filter(lecturer=request.user)
    if request.user.is_superuser:
        sub_task = AddStudTask.objects.filter(exercise__course__pk=pk)

    context = {
        'title': 'Назначенные задания ' + course.title,
        'sub_task': sub_task,
        'course': course,
        'comments': comments
    }

    return render(request, 'course/submitted_tasks.html', context)

@login_required
def create_add_stud_task(request, pk, exercise_pk):
    try:

        group = Group.objects.get(pk=pk)
        students = Student.objects.filter(department=group)

        lecturer = User.objects.get(pk=request.user.pk)
        exercise_instance = Upload.objects.get(pk=exercise_pk)

        # Создание записей для каждого сотрудника
        for student in students:
            # Проверяем, существует ли уже запись для этого сотрудника и задачи
            if not AddStudTask.objects.filter(student=student.student, exercise=exercise_instance).exists():
                # Создание записи
                add_stud_task = AddStudTask.objects.create(
                    student=student.student,
                    exercise=exercise_instance,
                    lecturer=lecturer,
                    upload_time=timezone.now(),
                    mark=0
                )

        messages.success(request, 'Задание успешно отправлено')
        return redirect('group_detail', pk=pk)

    except Group.DoesNotExist:
        messages.error(request, 'Группа не найдена')
        return redirect('group_detail', pk=pk)

    except Exception as e:
        messages.error(request, f'Ошибка: {e}')
        return redirect('group_detail', pk=pk)
    
@login_required
def create_add_stud_task_one(request, pk):


    course = Group.objects.get(pk=pk)
    file_name = Upload.objects.get(course=course)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)
    is_user_in_lecturers = lecturers.filter(lecturer=request.user).exists()

    if not is_user_in_lecturers:
        return redirect('groups')

    if request.user.is_student:
        stud_task = AddStudTask.objects.filter(student=request.user)
        return redirect('groups')
    
    stud_task = AddStudTask.objects.all()
    
    students = Student.objects.filter(department=course)

    context = {
        'title': 'Назначение задания ' + course.title,
        'students': students,
        'course': course,
        'file_name': file_name,
        'stud_task': stud_task
    }

    return render(request, 'course/addsubmitted_tasks.html', context)

@login_required
def create_add_stud_task_one_choice(request, pk, student_id, exercise_pk):
    try:
        student = Student.objects.get(student__pk=student_id)

        lecturer = User.objects.get(pk=request.user.pk)
        exercise_instance = Upload.objects.get(pk=exercise_pk)

        # Проверяем, существует ли уже запись для этого сотрудника и задачи
        if not AddStudTask.objects.filter(student=student.student, exercise=exercise_instance).exists():
            # Создание записи
            add_stud_task = AddStudTask.objects.create(
                student=student.student,
                exercise=exercise_instance,
                lecturer=lecturer,
                upload_time=timezone.now(),
                mark=0
            )

        messages.success(request, 'Задание успешно отправлено')
        return redirect('all_students_for_task', pk=pk, task_pk=exercise_pk)

    except Group.DoesNotExist:
        messages.error(request, 'Группа не найдена')
        return redirect('add_assignment', pk=pk)

    except Exception as e:
        messages.error(request, f'Ошибка: {e}')
        return redirect('add_assignment', pk=pk)

@login_required
def show_students_task(request):

    if not request.user.is_student:
        return redirect('groups')
    
    comments = Comments.objects.all()
    
    stud_task = AddStudTask.objects.filter(student=request.user)

    if request.method == 'POST':
        form = AddStudTaskForm(request.POST, request.FILES)
        if form.is_valid():
            task_id = request.POST.get('task_id')
            task = get_object_or_404(AddStudTask, pk=task_id)
            task.answer = form.cleaned_data['answer']
            task.save()
            messages.success(request, 'Ваше решение успешно загружено')
            return redirect('show_students_task')
        form = AddStudTaskForm()
    else:
        form = AddStudTaskForm()

    context = {
        'title': "Назначенные задания",
        'stud_task': stud_task,
        'comments': comments
    }

    return render(request, 'course/show_students_task.html', context)

@login_required
def update_mark(request, pk, task_id, new_mark):
    if request.user.is_student:
        return redirect('groups')
    

    task = get_object_or_404(AddStudTask, pk=task_id)

    if 2 <= int(new_mark) <= 5:
        # Обновляем поле mark
        task.mark = int(new_mark)
        task.save()

        # Возвращаем успешный ответ
        messages.success(request, f'Оценка {new_mark} установлена')
        return redirect('assignments', pk=pk)
    

def calculate_average(grades):
        valid_grades = [grade for grade in grades if grade > 0 and grade <= 5]
        
        if len(valid_grades) == 0:
            return 0  # Если нет допустимых оценок, возвращаем 0

        # Суммируем все допустимые оценки
        total = sum(valid_grades)

        # Вычисляем средний балл
        average = total / len(valid_grades)

        return average

def show_stud_result(request):
    title = 'Отчёт'
    
    
    if request.user.is_student:
        exercises = AddStudTask.objects.filter(student=request.user)
        grades = AddStudTask.objects.filter(student=request.user).values_list('mark', flat=True)

        ball = calculate_average(grades)

        context = {
            'title': title,
            'tasks': exercises,
            'ball': ball,
        }
        return render(request, 'course/show_stud_result.html', context)
    else:
        exercises = AddStudTask.objects.values_list('student__pk', 
                                                    'student__last_name', 
                                                    'student__first_name', 
                                                    'student__father_name',
                                                    ).distinct()
        formatted_exercises = [{pk: f"{last_name} {first_name} {father_name}"} for pk, last_name, first_name, father_name in exercises]
        # groups = Group.objects.all()
        print(f'{formatted_exercises=}')
        print(f'{request.GET=}')
        if 'exercise' in request.GET:
            print(f'{request.GET.getlist('exercise')[0]=}')
            student_data = request.GET.getlist('exercise')[0]  # Получаем первое значение из списка

            student_data = student_data.split(',')[0].strip()

            # Фильтруем AddStudTask по выбранному сотруднику
            tasks = AddStudTask.objects.filter(student__pk=student_data)

            grades = tasks.values_list('mark', flat=True)
            ball = calculate_average(grades)

            context = {
                'title': title,
                'exercises': formatted_exercises,
                # 'groups': groups,
                'tasks': tasks,
                'ball': ball,
            }
        else:
            context = {
                'title': title,
                'exercises': formatted_exercises,
                # 'groups': groups,
                'tasks': None,
                'ball': '0',
            }

        return render(request, 'course/show_stud_result.html', context)
    
def all_students_for_task(request, pk, task_pk):
    title = 'Выбор обучающегося'
    
    if request.user.is_student:
        return render('group')
    
    course = Group.objects.get(pk=pk)
    
    students = User.objects.filter(is_student=True)

    context = {
        'title': title,
        'students': students,
        'course': course,
        'task_pk': task_pk,
    }
    return render(request, 'course/all_students_for_task.html', context)


@login_required
def add_comment(request, pk, task_id):
    
    if request.user.is_student:
        return render('group')

    task = AddStudTask.objects.get(pk=task_id)

    if request.method == 'POST':
        form = CommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.from_user = request.user
            comment.task = task
            comment.save()

            messages.success(request, 'Комментарий к ' + task.exercise.title + ' создан.')
            return redirect('assignments', pk=pk)
        else:
            messages.error(request, 'Исправьте ошибки ниже.')
    else:
        form = CommentsForm()

    return render(request, 'course/make_comments.html', {
        'title': "Добавить комментарий к " + task.exercise.title,
        'form': form,
        'group_pk': pk,
        'task': task
    })

@login_required
def comment_edit(request, pk, task_id, comment_id):
    
    if request.user.is_student:
        return render('group')

    comment = Comments.objects.get(pk=comment_id)
    task = AddStudTask.objects.get(pk=task_id)

    if request.method == 'POST':
        form = CommentsForm(request.POST, instance=comment)
        print(f'{form.errors}')
        if form.is_valid():
            comment = form.save(commit=False)
            comment.from_user = request.user
            comment.task = task
            comment.save()

            messages.success(request, 'Комментарий к ' + task.exercise.title + ' отредактирован.')
            return redirect('assignments', pk=pk)
    else:
        form = CommentsForm(instance=comment)

    return render(request, 'course/make_comments.html', {
        'title': "Редактировать комментарий к " + task.exercise.title,
        'form': form,
        'group_pk': pk,
        'task': task
    })


@method_decorator([login_required], name='dispatch')
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/course_allocation_form.html'

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # if a staff has been allocated a course before update it else create new
        lecturer = form.cleaned_data['lecturer']
        selected_courses = form.cleaned_data['courses']
        courses = ()
        for course in selected_courses:
            courses += (course.pk,)
        # print(courses)

        try:
            a = CourseAllocation.objects.get(lecturer=lecturer)
        except:
            a = CourseAllocation.objects.create(lecturer=lecturer)
        for i in range(0, selected_courses.count()):
            a.courses.add(courses[i])
            a.save()
        return redirect('course_allocation_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Распределение курсов"
        return context


@login_required
def course_allocation_view(request):
    allocated_courses = CourseAllocation.objects.all()
    return render(request, 'course/course_allocation_view.html', {
        'title': "Распределение курсов",
        "allocated_courses": allocated_courses
    })


@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    allocated = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == 'POST':
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, 'назначенный курс обновлен.')
            return redirect('course_allocation_view')
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(request, 'course/course_allocation_form.html', {
        'title': "Распределение курсов",
        'form': form, 'allocated': pk
    }, )


@login_required
@lecturer_required
def deallocate_course(request, pk):
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, 'курс успешно удален!')
    return redirect("course_allocation_view")
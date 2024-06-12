from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save
from django.db.models import Q

# project import
from .utils import *




class GroupManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(title__icontains=query) | 
                         Q(summary__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class Group(models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name='Название')
    summary = models.TextField(null=True, blank=True, verbose_name='Описание')

    objects = GroupManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'pk': self.pk})





class CourseAllocation(models.Model):
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='allocated_lecturer')
    courses = models.ManyToManyField(Group, related_name='allocated_course')

    def __str__(self):
        return self.lecturer.get_full_name

    def get_absolute_url(self):
        return reverse('edit_allocated_course', kwargs={'pk': self.pk})


class Upload(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Group, on_delete=models.CASCADE)
    file = models.FileField(upload_to='course_files/', validators=[FileExtensionValidator(['pdf', 'docx', 'doc', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', '7zip'])])
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    last_date = models.DateTimeField(blank=True, null=False, verbose_name="Сдать до ")

    def __str__(self):
        return str(self.file)[6:]

    def get_extension_short(self):
        ext = str(self.file).split(".")
        ext = ext[len(ext)-1]

        if ext == 'doc' or ext == 'docx':
            return 'word'
        elif ext == 'pdf':
            return 'pdf'
        elif ext == 'xls' or ext == 'xlsx':
            return 'excel'
        elif ext == 'ppt' or ext == 'pptx':
            return 'powerpoint'
        elif ext == 'zip' or ext == 'rar' or ext == '7zip':
            return 'archive'

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)


class CourseOffer(models.Model):
	"""NOTE: Only department head can offer semester courses"""
	dep_head = models.ForeignKey("accounts.DepartmentHead", on_delete=models.CASCADE)

	def __str__(self):
		return "{}".format(self.dep_head)

class AddStudTask(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addstudent_list')
    exercise = models.ForeignKey(Upload, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='aadstudent_lecturer')
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    answer = models.FileField(upload_to='student_files/', validators=[FileExtensionValidator(['pdf', 'docx', 'doc', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', '7zip'])])
    mark = models.IntegerField(default=0)

    @property
    def answer_filename(self):
        return os.path.basename(self.answer.name)

class Notification(models.Model):
    notif_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_user')
    for_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='for_user')
    exercise_notif = models.ForeignKey(AddStudTask, on_delete=models.CASCADE)
    messages = models.TextField(null=True, blank=True, verbose_name='Сообщение')
    is_viewed = models.BooleanField(default=False, verbose_name='Просмотренно')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    last_date = models.ForeignKey(Upload, on_delete=models.CASCADE, null=False, blank=True, related_name='notifications_date')


class Comments(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(AddStudTask, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    messages = models.TextField(null=True, blank=True, verbose_name='Сообщение')
    


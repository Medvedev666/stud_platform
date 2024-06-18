from django import forms
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from .models import (
    Group, Upload, AddStudTask, Comments,
    CourseAllocation
)
from accounts.models import User




class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control'})




# Upload files to specific course
class UploadFormFile(forms.ModelForm):

    class Meta:
        model = Upload
        fields = ('title', 'file', 'course', 'last_date')
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_date'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%d')
        self.fields['last_date'].required = True

class AddStudTaskForm(forms.ModelForm):
    class Meta:
        model = AddStudTask
        fields = ['answer']  # Поля, которые должны отображаться в форме

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].widget.attrs.update({'class': 'form-control-file', 'accept': '.pdf, .docx, .doc, .xls, .xlsx, .ppt, .pptx, .zip, .rar, .7zip'})

class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('messages',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['messages'].widget.attrs.update({'class': 'form-control'})

class CourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'browser-default checkbox'}),
        required=True
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={'class': 'browser-default custom-select'}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ['lecturer', 'courses']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(is_lecturer=True)


class EditCourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={'class': 'browser-default custom-select'}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ['lecturer', 'courses']

    def __init__(self, *args, **kwargs):
        #    user = kwargs.pop('user')
        super(EditCourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(is_lecturer=True)

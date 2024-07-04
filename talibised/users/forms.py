from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

User = get_user_model()

UserType = [
    ('student', 'Student'),
    ('professor', 'Professor'),
    ('ta', 'TA'),
]

CourseType = [
    ('cn', 'Computer Networks'),
    ('dbms', 'Database Management System'),
    ('se', 'Software Engineering'),
    ('ppl', 'Principles of Programming Language'),
    ('daa', 'Design and Analysis of Algorithms'),
]


class RegisterForm(UserCreationForm):
    # fields we want to include and customize in our form
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                               'class': 'form-control',
                                                               }))
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                              'class': 'form-control',
                                                              }))
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))

    userType = forms.ChoiceField(choices=UserType, required=True,
                                 widget=forms.Select(attrs={'class': 'form-control'
                                                            }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'userType']


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class CreateProjectForm(forms.Form):
    subject_name = forms.ChoiceField(choices=CourseType, required=True,
                                     widget=forms.Select(attrs={'class': 'form-control'
                                                                }))

    project_title = forms.CharField(max_length=50,
                                    widget=forms.TextInput(attrs={'placeholder': 'Project Title',
                                                                  }))
    due_date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                   widget=forms.DateTimeInput(attrs={
                                       'class': 'form-control datetimepicker-input',
                                       'data-target': '#datetimepicker1'
                                   }))
    project_desc = forms.CharField(label='Project Description', widget=forms.Textarea)
    max_marks = forms.IntegerField(label='Maximum Marks')
    document = forms.FileField(required=False)


class StudentProjectSubmission(forms.Form):
    submission_file = forms.FileField(required=True)


class ProfessorProjectSubmission(forms.Form):
    marks_alloted = forms.IntegerField(required=True)
    allotted_ta = forms.ModelChoiceField(queryset=CustomUser.objects.filter(userType='ta'), empty_label=None,required=False)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

        # overriding default form setting and adding bootstrap class

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs = {'placeholder': 'Comment here...', 'class': 'form-control', 'rows': '5'}

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import datetime

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


# Create your models here.
class CustomUser(AbstractUser):
    userType = models.CharField(max_length=20, choices=UserType)


class Project(models.Model):
    subject_name = models.CharField(max_length=50, choices=CourseType)
    project_name = models.CharField(max_length=50)
    due_date = models.DateTimeField()
    posted_date = models.DateField(auto_now_add=True)
    project_desc = models.TextField()
    max_marks = models.IntegerField(default=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='professor')
    allotted_ta = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ta', null=True)
    document = models.FileField(upload_to="document", null=True, blank=True)

    def __str__(self):
        return self.project_name


class Submission(models.Model):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    student_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    submitted_date = models.DateField(auto_now_add=True)
    submitted_time = models.TimeField(auto_now_add=True)
    submitted_on_time = models.BooleanField(default=True)
    marks_alloted = models.IntegerField(default=0)
    submission_file = models.FileField(upload_to='documents', null=True)
    is_submitted = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False)

    # def get_student_name(self):
    #     stud = CustomUser.objects.get(id=self.student_id)
    #     return stud.username
    #
    def __str__(self):
        return str(self.id)

    def get_absolute_url1(self):
        return f"/submit-project-student/{self.id}/"

    def get_absolute_url2(self):
        return f"/view-submission-detail/{self.id}/"


class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    body = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.body

    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)

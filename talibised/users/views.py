from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import RegisterForm, LoginForm, CreateProjectForm, StudentProjectSubmission, ProfessorProjectSubmission, \
    CommentForm
from django.urls import reverse_lazy
import re
from django.contrib.auth.decorators import login_required
from .models import Project, Submission, Comment, CustomUser
from django.views import generic

# Create your views here.


regex = r'\b[A-Za-z0-9._%+-]+@iiita.ac.in\b'


def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def checkEmail(self, email):
        if re.fullmatch(regex, email):
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if self.checkEmail(request.POST.get('email')):
            if form.is_valid():
                form.save()

                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}')

                return redirect(to='login')

        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ClassroomView(View):
    def get(self, request):
        if request.user.is_authenticated:
            currentUser = request.user
            if currentUser.userType == 'student':
                project = Project
                return render(request, 'users/classroom_student.html', {'project': project})

            elif currentUser.userType == 'professor':
                return render(request, 'users/classroom_professor.html')

            elif currentUser.userType == 'ta':
                return render(request, 'users/classroom_ta.html')
            else:
                return HttpResponse('<h1>You are admin</h1>')


class CreateProjectView(View):

    def post(self, request):
        form = CreateProjectForm(request.POST, request.FILES)
        if form.is_valid():
            subject_name = form.cleaned_data.get('subject_name')
            project_name = form.cleaned_data.get('project_title')
            due_date = form.cleaned_data.get('due_date')
            project_desc = form.cleaned_data.get('project_desc')
            max_marks = form.cleaned_data.get('max_marks')
            document = form.cleaned_data.get('document')
            project = Project(subject_name=subject_name, project_name=project_name, due_date=due_date,
                              project_desc=project_desc, max_marks=max_marks, created_by=request.user,
                              document=document)

            project.save()

            return HttpResponseRedirect("/success")

        else:
            return render(request, 'users/createProject.html', {'form': form})

    def get(self, request):
        form = CreateProjectForm()
        return render(request, 'users/createProject.html', {'form': form})


def success(request):
    project = Project()
    return render(request, "users/success.html", {
        'project': project
    })


# class ViewProjectView(generic.ListView):
#     model = Project
#     template_name = "users/viewproject.html"
#     queryset = Project.objects.order_by('-posted_date')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

def ViewProjectView(request):
    if request.user.userType == 'student':
        submission = Submission.objects.filter(is_submitted=True, student_id=request.user)
        project_list = list(Project.objects.all())
        prj_list = []
        for prj in project_list:
            flag = False
            for sub in submission:
                if prj.id == sub.project_id.id:
                    flag = True
            if not flag:
                prj_list.append(prj)

        return render(request, "users/viewproject.html", {'object_list': prj_list, 'submission': submission})

    submission = Submission.objects.all()
    project_list = Project.objects.all()
    return render(request, "users/viewproject.html", {'object_list': project_list, 'submission': submission})


def StudentProjectSubmissionView(request, pk):
    if request.method == 'POST' and 'submit_project' in request.POST:
        # print(args)
        # print(kwargs)
        project = Project.objects.get(pk=pk)
        print(project)
        form = StudentProjectSubmission(request.POST, request.FILES)

        if form.is_valid():
            submission_file = form.cleaned_data.get('submission_file')
            submission = Submission(student_id=request.user, submission_file=submission_file,
                                    project_id=Project.objects.get(pk=pk), is_submitted=True)
            submission.save()
            submission.is_checked = True
            return HttpResponseRedirect('/success')

        else:
            print('hello')
            form = StudentProjectSubmission()
        return render(request, "users/usersubmitproject.html",
                      {'form': form, 'project': project, })

    elif request.method == 'POST' and 'comment_submit' in request.POST:
        form = StudentProjectSubmission()
        project = Project.objects.get(pk=pk)
        try:
            submission = Submission.objects.get(project_id=pk, student_id=request.user)
        except:
            submission = Submission()

        comments = submission.comments.filter(active=True)
        print(comments)
        new_comment = None
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.submission = submission
            new_comment.user = request.user
            new_comment.save()
            # print(comments.objects.all())
            return redirect(request.path_info  + '#' + str(new_comment.id))
        else:
            comment_form = CommentForm()
            return render(request, "users/usersubmitproject.html",
                          {'form': form, 'project': project, 'submission': submission, 'comments': comments,
                           'comment_form': comment_form})

    elif request.method == 'GET':
        print("Ok")
        form = StudentProjectSubmission()
        project = Project.objects.get(pk=pk)
        try:
            submission = Submission.objects.get(project_id=pk, student_id=request.user)
        except:
            submission = Submission()

        return render(request, "users/usersubmitproject.html",
                      {'form': form, 'project': project, 'submission': submission, })


def ProfessorProjectSubmissionView(request, pk):
    if request.method == 'POST' and 'submit_project' in request.POST:
        # print(args)
        # print(kwargs)
        submission = Submission.objects.get(id=pk)
        project_id = submission.project_id.id
        project = Project.objects.get(id=project_id)

        form = ProfessorProjectSubmission(request.POST)

        if form.is_valid():
            marks_alloted = form.cleaned_data.get('marks_alloted')

            submission.marks_alloted = marks_alloted
            submission.is_checked = True
            submission.save()

            return HttpResponseRedirect("/success")

        else:
            form = ProfessorProjectSubmission()
        return render(request, "users/usersubmitproject.html",
                      {'form': form, 'project': project, 'submission': submission})

    elif request.method == 'POST' and 'comment_submit' in request.POST:
        submission = Submission.objects.get(id=pk)
        project_id = submission.project_id.id
        project = Project.objects.get(id=project_id)
        form = ProfessorProjectSubmission()
        comments = submission.comments.filter(active=True)
        print(comments)
        new_comment = None
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.submission = submission
            new_comment.user = request.user
            new_comment.save()
            # print(comments.objects.all())
            return HttpResponseRedirect(request.path_info + '#' + str(new_comment.id))
        else:
            comment_form = CommentForm()
            return render(request, "users/usersubmitproject.html",
                          {'form': form, 'project': project, 'submission': submission, 'comments': comments,
                           'comment_form': comment_form})
    elif request.method == 'GET':
        form = ProfessorProjectSubmission()
        submission = Submission.objects.get(id=pk)
        project_id = submission.project_id.id

        project = Project.objects.get(id=project_id)

        return render(request, "users/usersubmitproject.html",
                      {'form': form, 'project': project, 'submission': submission})


def TAProjectSubmissionView(request, pk):
    if request.method == 'POST' and 'submit_project' in request.POST:
        # print(args)
        # print(kwargs)
        submission = Submission.objects.get(id=pk)
        project_id = submission.project_id.id
        project = Project.objects.get(id=project_id)

        form = ProfessorProjectSubmission(request.POST)

        if form.is_valid():
            marks_alloted = form.cleaned_data.get('marks_alloted')

            submission.marks_alloted = marks_alloted
            submission.is_checked = True
            submission.save()

            return HttpResponseRedirect("/success")

        else:
            form = ProfessorProjectSubmission()
        return render(request, "users/usersubmitproject.html",
                      {'form': form, 'project': project, 'submission': submission})

    elif request.method == 'POST' and 'comment_submit' in request.POST:
        submission = Submission.objects.get(id=pk)
        project_id = submission.project_id.id
        project = Project.objects.get(id=project_id)
        form = ProfessorProjectSubmission()
        comments = submission.comments.filter(active=True)
        print(comments)
        new_comment = None
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.submission = submission
            new_comment.user = request.user
            new_comment.save()
            # print(comments.objects.all())
            return HttpResponseRedirect(request.path_info + '#' + str(new_comment.id))
        else:
            comment_form = CommentForm()
            return render(request, "users/usersubmitproject.html",
                          {'form': form, 'project': project, 'submission': submission, 'comments': comments,
                           'comment_form': comment_form})
    elif request.method == 'GET':
        form = ProfessorProjectSubmission()
        submission = Submission.objects.get(id=pk)
        project_id = submission.project_id.id

        project = Project.objects.get(id=project_id)

        return render(request, "users/usersubmitproject.html",
                      {'form': form, 'project': project, 'submission': submission})


def ViewSubmissionView(request, pk):
    if request.method == 'GET':
        sub_list = Submission.objects.filter(project_id=pk)
        project = Project.objects.get(id=pk)
        user = CustomUser.objects.filter(userType='student')
        submitted = Submission.objects.filter(project_id=pk, is_submitted=True)
        print(sub_list)
        return render(request, "users/viewSubmissions.html",
                      {'sub_list': sub_list, 'project': project, 'user': user, 'submitted': submitted})


def ViewSubmittedProject(request):
    submission = list(Submission.objects.filter(student_id=request.user))
    print(type(submission))
    project = []

    for sub in submission:
        project.append(Project.objects.get(id=sub.project_id.id))

    print(project)
    return render(request, "users/viewsubmittedproject.html", {'submission': submission, 'project': project})


def reply_page(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            submission_id = request.POST.get('submission_id')  # from hidden input
            parent_id = request.POST.get('parent')  # from hidden input
            submission_url = request.POST.get('submission_url')  # from hidden input
            reply = form.save(commit=False)

            reply.submission = Submission(id=submission_id)
            reply.parent = Comment(id=parent_id)
            reply.save()
            return redirect(submission_url + '#' + str(reply.id))
    return redirect("/")


# def AllotTA(request, pk):
#     if request.method == 'POST':
#         project = Project.objects.get(id=pk)
#         form = ProfessorProjectSubmission(request.POST)
#         # print(request.POST.get('allotted_ta'))
#
#         id = request.POST.get('allotted_ta')
#         ta = CustomUser.objects.get(id=id)
#         project.allotted_ta = ta
#         print(project.allotted_ta)
#         project.save()
#         return HttpResponse("/success")
#
#         # else:
#         #     print('hello')
#         #     form = ProfessorProjectSubmission()
#         # return render(request, "users/allot_TA.html",
#         #               {'form': form, 'project': project})
#
#     elif request.method == 'GET':
#         project = Project.objects.get(id=pk)
#         print(project)
#         form = ProfessorProjectSubmission()
#         return render(request, "users/viewprojectdetail.html",
#                       {'form': form, 'project': project})


def ViewProjectDetail(request, pk):
    if request.method == 'POST':
        project = Project.objects.get(id=pk)

        id = request.POST.get('allotted_ta')
        ta = CustomUser.objects.get(id=id)
        project.allotted_ta = ta
        print(project.allotted_ta)
        project.save()
        return HttpResponse("/success")

        # else:
        #     print('hello')
        #     form = ProfessorProjectSubmission()
        # return render(request, "users/allot_TA.html",
        #               {'form': form, 'project': project})

    elif request.method == 'GET':
        project = Project.objects.get(id=pk)
        print(project)
        form = ProfessorProjectSubmission()
        return render(request, "users/viewprojectdetail.html",
                      {'form': form, 'project': project})

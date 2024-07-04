from django.urls import path
from .views import home, RegisterView, ClassroomView, CreateProjectView, success, ViewProjectView, \
    StudentProjectSubmissionView, ViewSubmissionView, ProfessorProjectSubmissionView, ViewSubmittedProject, reply_page, \
     ViewProjectDetail

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('classroom/', ClassroomView.as_view(), name='users-classroom'),
    path('create-project/', CreateProjectView.as_view(), name='users-create-project'),
    path('success/', success, name='users-success'),
    path('view-project/', ViewProjectView, name='users-view-project'),
    path('view-project-detail/<int:pk>', ViewProjectDetail, name='users-view-project-detail'),
    path('submit-project-student/<int:pk>/', StudentProjectSubmissionView, name='users-submit-project-student'),
    path('view-submission/<int:pk>/', ViewSubmissionView, name='users-view-submission'),
    # path('allot-ta/<int:pk>/', AllotTA, name='users-allot-ta'),
    path('view-submitted-project', ViewSubmittedProject, name='users-view-submitted-project'),
    path('view-submission-detail/<int:pk>', ProfessorProjectSubmissionView, name='users-submit-project-professor'),
    path('comment/reply/', reply_page, name="users-reply")

]

from django.urls import path, include, re_path
from knox import views as knox_views
from core.auth.views import ValidatePhoneSendOtp, ValidateOTP, UserRegister, LoginAPI
from core.auth.views import UserDetails , RequestorDetails, GigsterDetails, GigsterSkillsAPIView
from core.api.views import ProjectCreateAPIView, RequestorProfileAPIView, GigsterProfileAPIView, ProjectAPIView, GigsterProjectAPIView, GigsterActiveProjectAPIView

app_name = 'core'

urlpatterns = [
    re_path(r'^validate_phone/', ValidatePhoneSendOtp.as_view(),name='validate_phone'),
    re_path(r'^validate_otp/', ValidateOTP.as_view(),name='validate_otp'),
    re_path(r'^register/', UserRegister.as_view(),name='create_user'),
    re_path(r'^login/', LoginAPI.as_view(),name='user_login'),
    re_path(r'^logout/', knox_views.LogoutView.as_view(),name='user_login'),
    re_path(r'^user_details', UserDetails.as_view(),name='user_details'),
    re_path(r'^requestor_details', RequestorDetails.as_view(),name='requestor_details'),# user details
    re_path(r'^gigster_details', GigsterDetails.as_view(),name='gigster_details'),#user details
    re_path(r'^gigster_skills', GigsterSkillsAPIView.as_view(),name='gigster_skills'),
    re_path(r'^api/requestor/post_project/', ProjectCreateAPIView.as_view(),name='post_project'),
    re_path(r'^api/requestor/profile/', RequestorProfileAPIView.as_view(),name='requestor_profile'),
    re_path(r'^api/gigster/profile/', GigsterProfileAPIView.as_view(),name='gigster_profile'),
    re_path(r'^api/requestor/projects/', ProjectAPIView.as_view(),name='requestor_projects'),
    re_path(r'^api/gigster/accept_projects/', GigsterProjectAPIView.as_view(),name='gigster_projects'),
    re_path(r'^api/gigster/projects/', GigsterActiveProjectAPIView.as_view(),name='gigster_active_projects'),
]

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from core.models import Project, Requestor, Gigster, GigsterProject, User
from .serializers import ProjectCreateSerializer, RequestorProfile, UserProfile, GigsterProfile, ProjectSerializer, GigsterProjectSerializer, GigsterActiveProjects
from knox.auth import TokenAuthentication
from django.http import JsonResponse
import random
import requests


class ProjectCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = request.user
        requestor = user.requestor.pk
        if user.is_active:
            temp_data = {
                        'requestor' : requestor,
                        'project_category' : request.data.get('project_category', None),
                        'project_title' : request.data.get('project_title', None),
                        'project_type' : request.data.get('project_type', None),
                        'no_of_gigsters_required' : request.data.get('no_of_gigsters_required', None),
                        'gender_of_gigsters_required' : request.data.get('gender_of_gigsters_required', None),
                        'requirements' : request.data.get('requirements', None),
                        'special_instruction' : request.data.get('special_instruction', None),
                        'project_location' : request.data.get('project_location', None),
                        'arrival_instructions' : request.data.get('arrival_instructions', None),
                        'project_details' : request.data.get('project_details', None),
                        'duration' : request.data.get('duration', None),
                        'pay' : request.data.get('pay', None),
                        'pay_status' : request.data.get('pay_status', None),
                        'project_subcategory' : request.data.get('project_subcategory', None),
                        'project_status' : request.data.get('project_status', 0),
                        }
            serializer = ProjectCreateSerializer(data=temp_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                        'status' : True,
                        'detail' : 'Project Posted.Wait for the approval from admin!!'
                    })

        else:
            return Response({
                        'status' : False,
                        'detail' : 'Not a valid Requestor.First get approved by admin!!'
                    })


class ProjectAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user = request.user
        requestor = user.requestor
        if user.is_active:
            requestor_projects = Project.objects.filter(requestor_id=requestor.id)
            serializer = ProjectSerializer(requestor_projects, many=True)
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })


    def put(self, request, *args, **kwargs):
        user = request.user
        requestor = user.requestor.pk
        if user.is_active:
            requestor_project = Project.objects.get(id=request.data.get('id'))
            temp_data = {
                        'requestor' : requestor,
                        'project_category' : request.data.get('project_category', None),
                        'project_title' : request.data.get('project_title', None),
                        'project_type' : request.data.get('project_type', None),
                        'no_of_gigsters_required' : request.data.get('no_of_gigsters_required', None),
                        'gender_of_gigsters_required' : request.data.get('gender_of_gigsters_required', None),
                        'requirements' : request.data.get('requirements', None),
                        'special_instruction' : request.data.get('special_instruction', None),
                        'project_location' : request.data.get('project_location', None),
                        'arrival_instructions' : request.data.get('arrival_instructions', None),
                        'project_details' : request.data.get('project_details', None),
                        'duration' : request.data.get('duration', None),
                        'pay' : request.data.get('pay', None),
                        'pay_status' : request.data.get('pay_status', None),
                        'project_subcategory' : request.data.get('project_subcategory', None),
                        'project_status' : request.data.get('project_status', None),
                        }
            serializer = ProjectSerializer(requestor_project, data=temp_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })


class GigsterProjectAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            gigster_projects = Project.objects.filter(project_active=True)
            serializer = ProjectSerializer(gigster_projects, many=True)
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })


    def post(self, request, *args, **kwargs):
        user = request.user
        gigster = user.gigster.pk
        if user.is_active:
            temp_data = {
                        'gigster' : gigster,
                        'gigster_project' : Project.objects.get(id=request.data.get('id')),
                        'gigster_project_choice' : request.data.get('gigster_project_choice', None),
                        'project_status' : request.data.get('project_status', None),
                        }
            serializer = GigsterProjectSerializer(data=temp_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })


class GigsterActiveProjectAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user = request.user
        gigster = user.gigster
        if user.is_active:
            gigster_projects = GigsterProject.objects.filter(gigster=gigster)
            serializer = GigsterActiveProjects(gigster_projects, many=True)
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })


class RequestorProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user = request.user
        requestor = user.requestor
        if user.is_active:
            requestor = Requestor.objects.get(pk=requestor.id)
            serializer = RequestorProfile(requestor)
            
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })

    def put(self, request, *args, **kwargs):
        user = request.user
        requestor = user.requestor
        if user.is_active:
            requestor = Requestor.objects.get(pk=requestor.id)
            temp_data = {
                        'company_name' : request.data.get('company_name', None),
                        'company_location' : request.data.get('company_location', None),
                        'postal_code' : request.data.get('postal_code', None),
                        'company_description' : request.data.get('company_description', None),
                        'company_website' : request.data.get('company_website', None),
                        'designation' : request.data.get('designation', None),
                        'linkedin_profile' : request.data.get('linkedin_profile', None),
                        'logo' : request.data.get('logo', None),
                        'profile_photo' : request.data.get('profile_photo', None),
                        }
            serializer = RequestorProfile(requestor, data=temp_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })

class GigsterProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            gigster = user.gigster
            serializer = GigsterProfile(gigster)
            
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })
    

    def put(self, request, *args, **kwargs):
        user = request.user
        gigster = user.gigster
        if user.is_active:
            gigster = Gigster.objects.get(pk=gigster.pk)
            temp_data = {
                        'bio' : request.data.get('bio', None),
                        'vehicles_owned' : request.data.get('vehicles_owned', None),
                        'profile_photo' : request.data.get('profile_photo', None),
                        
                    }
            serializer = GigsterProfile(gigster, data=temp_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                    'status' : True,
                    'detail' : serializer.data
                })
        else:
            return Response({
                    'status' : False,
                    'detail' : 'Not an active user!!!.Please wait for approval'
                })

   
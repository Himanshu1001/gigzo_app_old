from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny
from core.models import User, PhoneOTP, Requestor, Gigster
from django.shortcuts import get_object_or_404
from .serializer import CreateUserSerializer, LoginSerializer, UserDetailsSerializer, RequestorDetailsSerializer, GigsterDetailsSerializer, GigsterSkillsSerializer
import random
import requests

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication

from django.contrib.auth import login


class ValidatePhoneSendOtp(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if phone_number:
            phone_number = str(phone_number)
            user = User.objects.filter(phone_number__iexact=phone_number)
            if user.exists():
                return Response({
                    'status' : False,
                    'detail' : 'Phone Number already exists'
                })
            else :
                print(phone_number)
                key = send_otp(phone_number)
                if key:
                    old = PhoneOTP.objects.filter(phone_number__iexact = phone_number)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                            return Response({
                            'status' : False,
                            'detail' : 'Sending OTP Error. Limit Exceeded.Please contact Customer Support'
                                })

                        old.count =  count + 1
                        old.otp = key
                        old.save()  
                        return Response({
                        'status' : True,
                        'detail' : 'OTP send successfully!!'
                        })  

                    else:
                        PhoneOTP.objects.create(
                            phone_number = phone_number,
                            otp = key,
                        )
                        return Response({
                            'status' : True,
                            'detail' : 'OTP send successfully!!'
                            })
                else:
                    return Response({
                        'status' : False,
                        'detail' : 'Sending OTP error'
                    })
        
        else:
            return Response({
                'status' : False,
                'detail' : 'Phone Number is not given!'
            })

def send_otp(phone_number):
    if phone_number:
        key = random.randint(999,9999)
        api_key = "a86a24ff-eb05-11e8-a895-0200cd936042"
        template_name = "Kiara"
        link = f"https://2factor.in/API/V1/{api_key}/SMS/{phone_number}/{key}/{template_name}"
        payload = ""
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.request("GET", link, data=payload, headers=headers)
        print (key)
        print(response.text)
        return key
    else :
        return False



class ValidateOTP(APIView):
    """
    If user have recieved the OTP, he/she will post a request with phone and that OTP and then the user 
    will be direct to set the password.
    """
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        otp_sent = request.data.get('otp')

        if phone_number and otp_sent:
            old = PhoneOTP.objects.filter(phone_number__iexact = phone_number)
            if old.exists():
                old = old.latest('count')
                otp = old.otp
                print (otp_sent)
                print (otp)
                if str(otp_sent) == str(otp):
                    old.validated = True
                    old.save()
                    return Response({
                        'status' : True,
                        'detail' : 'OTP Matched.Please proceed for Registration'
                        })
                
                else:
                    return Response({
                        'status' : False,
                        'detail' : 'OTP Incorrect'
                    })
            
            else:
                return Response({
                    'status' : False,
                    'detail' : 'First verify your Phone number'
                })

        else:
            return Response({
                'status' : False,
                'detail' : 'Please provide both Phone number and OTP'
            })


class UserRegister(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', False)
        password = request.data.get('password', False)

        if phone_number and password:
            old = PhoneOTP.objects.filter(phone_number__iexact = phone_number)
            
            if old.exists():
                old = old.first()
                validated = old.validated

                if validated:
                    temp_data = {
                        'phone_number' : phone_number, ##what if user already exists
                        'password' : password,
                    }
                    serializer = CreateUserSerializer(data = temp_data)
                    serializer.is_valid(raise_exception = True)
                    serializer.save()
                    old.delete()
                    return Response({
                        'status' : True,
                        'detail' : 'Account Created'  
                    })
                else:
                    return Response({
                        'status' : False,
                        'detail' : 'Phone not verified'
                    })


            else:
                return Response({
                    'status' : False,
                    'detail' : 'Please verify phone'

                })
        else:
            return Response({
                'status' : False,
                'detail' : 'Both phone and password are not send'
            })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request, user)
        return super().post(request, format=None)


class UserDetails(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if phone_number:
            user_obj = User.objects.filter(phone_number = phone_number)
            if user_obj.exists():
                user = user_obj.first()
                temp_data = {
                            'first_name' : request.data.get('first_name', None),
                            'last_name' : request.data.get('last_name', None),
                            'email' : request.data.get('email', None),
                            'gender' : request.data.get('gender', None),
                            'user_type' : request.data.get('user_type', None),
                        }
                serializer = UserDetailsSerializer(user, data=temp_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            
                return Response({
                    'detail' : serializer.data,
                    'status' : True
                    })

            else:
                return Response({
                    'detail' : "User doesn't exist.First you need to register!!",
                    'status' : False
                    })

        else:
            return Response({
                'detail' : "Phone Number not found in request!!",
                'status' : False
            })
               

class RequestorDetails(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if phone_number:
            user_obj = User.objects.filter(phone_number = phone_number)
            if user_obj.exists():
                user = user_obj.first()
                requestor_obj = Requestor(requestor=user)
                user_type = request.data.get('user_type')
                if (int(user_type) == 1):
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
                    serializer = RequestorDetailsSerializer(requestor_obj, data=temp_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                
                    return Response({
                        'detail' : serializer.data,
                        'status' : True
                        })
                else:
                    return Response({
                        'detail' : "Invalid user Type",
                        'status' : False
                        })
            else:
                return Response({
                    'detail' : "User doesn't exist.First you need to register!!",
                    'status' : False
                    })

        else:
            return Response({
                'detail' : "Phone Number not found in request!!",
                'status' : False
            })


class GigsterDetails(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if phone_number:
            user_obj = User.objects.filter(phone_number = phone_number)
            if user_obj.exists():
                user = user_obj.first()
                print (user)
                gigster_obj = Gigster(gigster=user)
                user_type = request.data.get('user_type')
                if (int(user_type) == 2):
                    temp_data = {
                        'dob' : request.data.get('dob', None),
                        'aadhar_front' : request.data.get('aadhar_front', None),
                        'aadhar_back' : request.data.get('aadhar_back', None),
                        'pan_card' : request.data.get('pan_card', None),
                        'profile_photo' : request.data.get('profile_photo', None),
                    }
                    serializer = GigsterDetailsSerializer(gigster_obj, data=temp_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                
                    return Response({
                        'detail' : serializer.data,
                        'status' : True
                        })
                else:
                    return Response({
                        'detail' : "Invalid user Type",
                        'status' : False
                        })
            else:
                return Response({
                    'detail' : "User doesn't exist.First you need to register!!",
                    'status' : False
                    })

        else:
            return Response({
                'detail' : "Phone Number not found in request!!",
                'status' : False
            })          
        


class GigsterSkillsAPIView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if phone_number:
            user_obj = User.objects.filter(phone_number = phone_number)
            if user_obj.exists():
                user = user_obj.first()
                print (user)
                gigster_obj = Gigster(gigster=user)
                user_type = request.data.get('user_type')
                if (int(user_type) == 2):
                    temp_data = {
                        'gigster' : gigster_obj.pk,
                        'skill' : request.data.get('skill'),
                        'experience' : request.data.get('experience'),
                        'certificate' : request.data.get('certificate', None),
                        'experience_in_word' : request.data.get('experience_in_word', None),
                    }
                    serializer = GigsterSkillsSerializer(data=temp_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                
                    return Response({
                        'detail' : serializer.data,
                        'status' : True
                        })
                else:
                    return Response({
                        'detail' : "Invalid user Type",
                        'status' : False
                        })
            else:
                return Response({
                    'detail' : "User doesn't exist.First you need to register!!",
                    'status' : False
                    })

        else:
            return Response({
                'detail' : "Phone Number not found in request!!",
                'status' : False
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





























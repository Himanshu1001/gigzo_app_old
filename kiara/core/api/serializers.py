from rest_framework import serializers
from core.models import Project, Requestor, Gigster, GigsterProject
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError

User = get_user_model()

class ProjectCreateSerializer(serializers.ModelSerializer):

   class Meta:
       model  = Project
       exclude = ('requestor_rating', )


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        exclude = ('requestor_rating', )

    def update(self, instance, validated_data):
        instance.project_category = validated_data.get('project_category', None)
        instance.project_title = validated_data.get('project_title', None)
        instance.project_type = validated_data.get('project_type', None)
        instance.no_of_gigsters_required = validated_data.get('no_of_gigsters_required', None)
        instance.gender_of_gigsters_required = validated_data.get('gender_of_gigsters_required', None)
        instance.requirements = validated_data.get('requirements', None)
        instance.special_instruction = validated_data.get('special_instruction', None)
        instance.project_location = validated_data.get('project_location', None)
        instance.arrival_instructions = validated_data.get('arrival_instructions', None)
        instance.project_details = validated_data.get('project_details', None)
        instance.duration = validated_data.get('duration', None)
        instance.pay = validated_data.get('pay', None)
        instance.pay_status = validated_data.get('pay_status', None)
        instance.project_subcategory = validated_data.get('project_subcategory', None)
        instance.save()
        return instance

class GigsterProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = GigsterProject
        fields = '__all__'
    
    def create(self, instance):
        return instance

class GigsterActiveProjects(serializers.ModelSerializer):

    project = ProjectSerializer()

    class Meta:
        model = GigsterProject
        fields = '__all__'

class UserProfile(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'phone_number', 'gender', 'email', 'last_name', 'id',)


class RequestorProfile(serializers.ModelSerializer):
    
    requestor = UserProfile()

    class Meta:
        model = Requestor 
        exclude = ('created_at', 'updated_at',)
    

    def update(self, instance, validated_data):
        instance.company_name = validated_data.get('company_name', None)
        instance.company_location = validated_data.get('company_location', None)
        instance.postal_code = validated_data.get('postal_code', None)
        instance.company_description = validated_data.get('company_description', None)
        instance.company_website = validated_data.get('company_website', None)
        instance.designation = validated_data.get('designation', None)
        instance.linkedin_profile = validated_data.get('linkedin_profile', None)
        instance.logo = validated_data.get('logo', None)
        instance.profile_photo = validated_data.get('profile_photo', None)
        instance.save()
        return instance



class GigsterProfile(serializers.ModelSerializer):
    
    gigster = UserProfile(required=True)

    class Meta:
        model = Gigster 
        exclude = ('created_at', 'updated_at', 'aadhar_front', 'aadhar_back', 'pan_card', 'driving_licence', )
    
    def update(self, instance, validated_data):
        instance.bio = validated_data.get('bio', None)
        instance.vehicles_owned = validated_data.get('vehicles_owned', None)
        instance.profile_photo = validated_data.get('profile_photo', None)
        instance.save()
        return instance
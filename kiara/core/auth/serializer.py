from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from django.contrib.auth import authenticate
from core.models import Project, Requestor, Gigster, GigsterSkills

User = get_user_model()

        
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            'phone_number',
            'password',
        ]
        extra_kwargs = {"password":
                        {"write_only" : True},
                        }

    
    def create(self, validated_data): 
        user = User.objects.create(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ('id', 'phone_number', 'first_login')


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(
        style = {'input_type' : 'password'}, trim_whitespace = False
    )

    def validate(self, data):
        print (data)
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            if User.objects.filter(phone_number = phone_number).exists():
                print(phone_number,password)
                user = authenticate(request = self.context.get('request'),phone_number=phone_number, password=password)
                print (user)

            else:
                msg = {
                    'detail' : 'Phone Number not found!!',
                    'status' : False
                }
                raise serializers.ValidationError(msg)
            
            if not user:
                msg = {
                    'detail' : "Phone Number and Password don't match. Try again!!!",
                    'status' : False
                }
                raise serializers.ValidationError(msg, code='authorization')


        else:
            msg = {
                    'detail' : "Phone Number and Password not found in request!!",
                    'status' : False
                }
            raise serializers.ValidationError(msg, code='authorization') 

        data['user'] = user
        return data


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'gender', 'user_type', 'created_at', 'updated_at')
         
    def create(self, validated_data, instance):
        return instance


class RequestorDetailsSerializer(serializers.ModelSerializer):

    requestor = UserDetailsSerializer()
    
    class Meta:
        model  = Requestor
        exclude = ('rating','requestor',)

    def create(self, validated_data, instance):
        return instance

    
class GigsterDetailsSerializer(serializers.ModelSerializer):
    
    gigster = UserDetailsSerializer()

    class Meta:
        model = Gigster
        exclude = ('vehicles_owned', 'bio', 'rating', 'driving_licence', 'skills', )

    def create(self, validated_data, instance):
        return instance

class GigsterSkillsSerializer(serializers.ModelSerializer):

    class Meta:
        model = GigsterSkills
        exclude = ('updated_at',) 

    def create(self, instance):
        return instance

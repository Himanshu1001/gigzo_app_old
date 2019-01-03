"""
###########################################################################################################
This is 'GIGZO' models module. Anything that is stored in the database is present in this module only.
###########################################################################################################
"""

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser
from .manager import UserManager
from django.db.models import Q
from django.db.models.signals import pre_save, post_save    
from django.dispatch import receiver
import random
import os
import requests
import logging

logger = logging.getLogger(__name__)  # Get an instance of logger
default_value = 1

class CommonInfo(models.Model):
    """
    #######################################################################################################
    CommonInfo refers to an abstract model that provides 2 fields in every inherited model.
    created_at: Sets up the create date of any object
    updated_at: Sets up the last update date of any object
    #######################################################################################################
    """
	
    created_at = models.DateTimeField(verbose_name='Created Date',auto_now_add=True, blank=True, null=True, 
                                    help_text="Auto added at the time of creation only.")
    updated_at = models.DateTimeField(verbose_name='Updated Date',auto_now=True, blank=True, null=True,
                                    help_text="Auto added everytime model is updated.")
    
    objects = models.Manager()

    class Meta:         
        abstract            = True
        verbose_name        = 'Common Info'
        verbose_name_plural = 'Common Infos'
        db_table            = 'Common Info'

    def __str__(self):
        logger.info('CommonInfo model called')
        return '%s | | %s' %(self.created_at, self.updated_at)


class PhoneOTP(CommonInfo):
    """
    #######################################################################################################
    This model keeps a record of OTP Validation and which destinations have been successfully validated.
    #######################################################################################################
    """

    phone_regex     = RegexValidator(regex=r'^\+?1?\d{9,14}$', message="Phone number must be entered in the format: '999999999'")
    phone_number    = models.CharField(verbose_name='phone_number', validators=[phone_regex], unique=False, max_length=15, blank=True, help_text="Phone number to be validated") # validators should be a list
    otp             = models.CharField(verbose_name='OTP', max_length=6, help_text="otp to be send to the Phone number")
    count           = models.IntegerField(verbose_name='Attempted count', default=0, help_text='Number of OTP send.')
    is_verified     = models.BooleanField(verbose_name='is_verified', default=False, help_text='If it is true, this means user has validated otp correctly')
    
    objects = models.Manager()

    class Meta:
        managed             = True
        verbose_name        = 'Phone OTP'
        verbose_name_plural = 'Phone OTPs'
        db_table            = 'PhoneOTP'
    
    def __str__(self):
        return "%s" %(self.phone_number)
    

class User(AbstractBaseUser, CommonInfo):
    """
    #######################################################################################################
    Gigzo User model
        A Gigzo User represents a person, who is registered on Gigzo Platform. He/She can post/complete the gig
        using the platform. Here, we are extending the django user model and making our own cutomised user model.     
    #######################################################################################################
    """
    GENDER_CHOICE = [('M', "M - MALE"),
                     ('F', "F - FEMALE"),
                     ('O', "O - OTHER"),
                    ]
    USER_TYPE_CHOICE = [('R', "R - REQUESTOR"),
                        ('G', "G - GIGSTER"),
                    ]

    phone_regex       = RegexValidator(regex=r'^\+?1?\d{9,14}$', message="Phone number must be entered in the format: '999999999'")
    phone_number      = models.CharField(verbose_name='phone_number', validators=[phone_regex], unique=True, max_length=15, blank=True, help_text="Phone number of the user") # validators should be a list
    first_name        = models.CharField(verbose_name='first_name', max_length=255, blank=True, null=True, help_text="User's first name")
    last_name         = models.CharField(verbose_name='last_name', max_length=255, blank=True, null=True, help_text="User's last name")
    active            = models.BooleanField(verbose_name='is_active', default=True, help_text="Is user active")
    staff             = models.BooleanField(verbose_name='is_staff', default=False, help_text="Is user a staff member")
    admin             = models.BooleanField(verbose_name='is_admin', default=False, help_text="Is user a superuser/admin")
    email             = models.EmailField(verbose_name='email_id',max_length=255, unique=True, blank=True, null=True, help_text="User email Id")
    gender            = models.CharField(verbose_name='gender', choices=GENDER_CHOICE, max_length=255, blank=True, null=True, help_text="User gender")
    user_type         = models.CharField(verbose_name='user_type', choices= USER_TYPE_CHOICE, max_length=255, blank=True, null=True, help_text="Is user a Requestor/Gigster")
    user_rating       = models.FloatField(verbose_name='User Rating', blank=True, null=True, help_text="User overall Rating")
    suspended         = models.BooleanField(verbose_name='is_user_suspended', default=False, help_text="Is user suspended by the admin")
    suspended_date    = models.DateTimeField(verbose_name='Suspended Date',auto_now=True, blank=True, null=True,
                                    help_text="Auto added when the user is suspended")
    city              = models.CharField(verbose_name='City', max_length=255, blank=True, null=True, help_text="User's City")

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        managed             = True
        verbose_name_plural = 'Users'
        verbose_name        = 'User'
        db_table            = 'Users'

    def __str__(self):
        logger.info('User Model Called')
        return "%s - %s - %s" %(self.first_name, self.last_name, self.phone_number)

    def get_full_name(self):
        if self.first_name and self.last_name:
            return "%s - %s" %(self.first_name, self.last_name)  
        else:
            return self.phone_number 

    def get_short_name(self):
        if self.first_name:
            return "%s" %(self.first_name)
        else:
            return self.phone_number

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class InviteUser(CommonInfo):
    """
    #######################################################################################################
    A model that keeps the record of all the invited users in the system.

    ToDo-
        Make an API for this
    #######################################################################################################
    """
    user            = models.OneToOneField(User, on_delete=models.CASCADE, help_text="Instance of User Model, who is invited other user to the system") 
    first_name      = models.CharField(verbose_name='first_name', max_length=255, blank=True, null=True, help_text="User's first name, who is being invited")
    last_name       = models.CharField(verbose_name='last_name', max_length=255, blank=True, null=True, help_text="User's last name, who is being invited")
    phone_regex     = RegexValidator(regex=r'^\+?1?\d{9,14}$', message="Phone number must be entered in the format: '999999999'")
    phone_number    = models.CharField(verbose_name='phone_number', validators=[phone_regex], unique=True, max_length=15, blank=True, help_text="Phone number of the user") # validators should be a list 

    objects = models.Manager()

    class Meta:         
        abstract            = True
        verbose_name        = 'Invite User'
        verbose_name_plural = 'Invite Users'
        db_table            = 'Invite Users'

    def __str__(self):
        logger.info('Invited Users model called')
        return '%s | | %s' %(self.phone_number, self.first_name)


class Requestor(CommonInfo):
    """
    #######################################################################################################
    A Requestor is a user(client) who posts the project on the gigzo platform.
    TODO
        * Nothing
    FIXME
        * Nothing
    #######################################################################################################
    """
    COMPANY_TYPE_CHOICE = [(1, "Private Limited Company"),
                     (2, "Partnership"),
                     (3, "Limited Liability Partnership"),
                     (4, "Proprietorship"),
                     (5, "One Person Company"),
                     (6, "Section 8 Company"),
                    ]
    
    user                = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE, help_text="Instance of User Model")
    company_name        = models.CharField(verbose_name='Company_name', max_length=255, blank =True, null=True, help_text="Requestor's Company name ")
    company_location    = models.TextField(verbose_name='Company_location', blank=True, null=True, help_text="Requestor's Company Address")
    postal_code         = models.CharField(verbose_name='Postal_code', max_length=255, blank=True, null=True, help_text="Pin Code")
    company_description = models.TextField(verbose_name='Company_description', blank=True, null=True, help_text="Company Description")
    company_website     = models.CharField(verbose_name='Company_website', max_length=255, blank=True, null=True, help_text="Company Website")
    company_type        = models.IntegerField(verbose_name='company_type', choices=COMPANY_TYPE_CHOICE, blank=True, null=True, help_text="Company type of User")
    designation         = models.CharField(verbose_name='Requestor_designation', max_length=255, blank=True, null=True, help_text="Designation of Requestor")
    linkedin_profile    = models.URLField(verbose_name='Requestor_linkedin', max_length=255, blank=True, null=True, help_text="Requestor Linkedin Profile")
    #logo               = models.ImageField(upload_to=upload_logo , blank=True, null=True, help_text="Company Logo")
    #profile_photo      = models.ImageField(upload_to=upload_requestor_profile_photo , blank=True, null=True, help_text="Requestor profile photo")
    is_valid            = models.BooleanField(default=False, help_text="Is Requestor verified by the admin")
    #pan_card_number
    
    objects = models.Manager()

    class Meta:
        managed             = True
        verbose_name        = 'Requestor'
        verbose_name_plural = 'Requestors'
        db_table            = 'Requestor'

    def __str__(self):
        logger.info('Requestor model called')
        return '%s - %s' %(self.requestor.first_name, self.requestor.phone_number)





class Skills(CommonInfo):
    """
    #######################################################################################################
    Gigzo Skill model
    Here skills refers to all the skills possesed by gigster.

    TODO
        * Nothing
    FIXME
        * Nothing
        
    #######################################################################################################
    """    
    skill_name = models.CharField(verbose_name='Skill',max_length=255, blank=True, null=True)

    class Meta:
        managed             = True
        verbose_name_plural = 'Skills'
        verbose_name        = 'Skill'
        db_table            = 'Skills'

    def __str__(self):
        logger.info('Skills model called')
        return '%s' %(self.skill_name)


def upload_aadhar_front(instance, filename):
    return "%s/%s" %(instance.gigster, filename)

def upload_aadhar_back(instance, filename):
    return "%s/%s" %(instance.gigster, filename)

def upload_pan_card(instance, filename):
    return "%s/%s" %(instance.gigster, filename)

def upload_driving_licence(instance, filename):
    return "%s/%s" %(instance.gigster, filename)

def upload_gigster_profile_photo(instance, filename):
    return "%s/%s" %(instance.gigster, filename)


class Gigster(CommonInfo):
    """
    #######################################################################################################
    A Gigster is a user(flexible workforce) on the Gigzo platform who gives his/her services to the Requestor
    and makes money out of it.He/She has the option of accepting/rejecting the project.
    TODO
        * Nothing
    FIXME
        *
    #######################################################################################################
    """
    VEHICLES_CHOICE = [(1, "B - BIKE"),
                       (2, "S - SCOOTY"),
                       (3, "C - CAR"),
                    ]

    gigster         = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    vehicles_owned  = models.IntegerField(choices=VEHICLES_CHOICE, blank=True, null=True)
    dob             = models.DateField(blank=True, null=True)
    bio             = models.TextField(blank=True, null=True, help_text="Gigster's bio")
    skills          = models.ManyToManyField(Skills, through='GigsterSkills')
    aadhar_front    = models.ImageField(upload_to=upload_aadhar_front , blank=True, null=True)
    aadhar_back     = models.ImageField(upload_to=upload_aadhar_back , blank=True, null=True)
    pan_card        = models.ImageField(upload_to=upload_pan_card , blank=True, null=True)
    profile_photo   = models.ImageField(upload_to=upload_gigster_profile_photo, blank=True, null=True)
    driving_licence = models.ImageField(upload_to=upload_driving_licence , blank=True, null=True)
    rating          = models.FloatField(verbose_name='Gigster Rating', blank=True, null=True, help_text="Gigster overall Rating")
    
    objects = models.Manager()

    class Meta:
        managed             = True
        verbose_name_plural = 'Gigsters'
        verbose_name        = 'Gigster'
        db_table            = 'Gigster'

    def __str__(self):
        logger.info('Gigster model called')
        return '%s' %(self.gigster.first_name)


def upload_certificate(instance, filename):
    return "%s/%s" %(instance.gigster, filename)


class GigsterSkills(CommonInfo):
    """
    #######################################################################################################
    Gigzo Gigster Skill model
    All attributes for relation between gigster and skills is present in this model.

    TODO
        * Nothing 
    FIXME
        * Nothing
        
    #######################################################################################################
    """
    EXPERIENCE_CHOICE = [(1, "NO EXPERIENCE"),
                        (2, "3-6 MONTHS EXPERIENCE "),
                        (3, "6+ MONTHS EXPERIENCE "),
                    ]
    gigster            = models.ForeignKey(Gigster, on_delete=models.CASCADE, default = default_value)
    skill              = models.ForeignKey(Skills, on_delete=models.CASCADE, default = default_value)   
    experience         = models.IntegerField(verbose_name='experience',choices=EXPERIENCE_CHOICE, blank=True, null=True)
    certificate        = models.ImageField(upload_to = upload_certificate, blank=True, null=True)
    experience_in_word = models.TextField(verbose_name='experience_in_word',blank=True,null=True)

    objects = models.Manager()
    
    class Meta:
        managed             = True
        verbose_name_plural = 'Gigster Skills'
        verbose_name        = 'Gigster Skill'
        db_table            = 'Gigster Skills'

    def __str__(self):
        logger.info('Gigster Skill Model called')
        return '%s-%s' %(self.gigster.gigster.first_name,self.skill.skill_name)


class Project(CommonInfo):
   
    
    PROJECT_CATEGORY    = [(1, "Events"),
                            ]
    GENDER_CHOICE       = [(1, "M - MALE"),
                            (2, "F - FEMALE"),
                            (3, "N - NO PARTICULAR CHOICE"),
                        ]
    PROJECT_TYPE_CHOICE = [(1, "S - SINGLE-DAY-JOB"),
                            (2, "M - MULTI-DAY-JOB"),
                        ]
    PAY_STATUS_CHOICE = [(1, "P - PAID"),
                            (2, "U - UNPAID"),
                        ]
    PROJECT_STATUS_CHOICE = [(0, "P - PENDING"),  # unfilled, unassigned, posted, filled, in_progress, completed, approved, cancelled.
                            (1, "O - OPEN"),
                            (2, "F - FILLED"),
                            (3, "C - CLOSED "),
                            (4, "S- STARTED"),
                            (5, "E- ENDED"),
                            (6, "A - APPROVED"),
                            (7, "R - RATED"),
                            
                        ]
    requestor                   = models.ForeignKey(Requestor,on_delete=models.CASCADE, default = default_value)
    project_category            = models.IntegerField(choices=PROJECT_CATEGORY, blank=True, null=True)
    project_title               = models.CharField(max_length=255, blank=True, null=True)
    project_type                = models.IntegerField(choices=PROJECT_TYPE_CHOICE, blank=True, null=True)
    no_of_gigsters_required     = models.CharField(max_length=255, blank=True, null=True)
    gender_of_gigsters_required = models.IntegerField(choices=GENDER_CHOICE, blank=True, null=True)
    requirements                = models.TextField(blank=True, null=True)
    special_instruction         = models.TextField(blank=True, null=True)
    project_location            = models.TextField(blank=True, null=True)
    arrival_instructions        = models.TextField(blank=True, null=True)
    project_details             = models.TextField(blank=True, null=True)
    project_active              = models.BooleanField(default=False)
    duration                    = models.CharField(max_length=255, blank=True, null=True)
    pay                         = models.CharField(max_length=255, blank=True, null=True)
    requestor_rating            = models.DecimalField(decimal_places=1, max_digits=2, blank=True, null=True)
    project_subcategory         = models.CharField(max_length=255, blank=True, null=True)
    pay_status                  = models.IntegerField(choices=PAY_STATUS_CHOICE, blank=True, null=True)
    project_status              = models.IntegerField(choices=PROJECT_STATUS_CHOICE, blank=True, null=True, default=0)
    
    objects = models.Manager()


    class Meta:
        managed             = True
        verbose_name_plural = 'Projects'
        verbose_name        = 'Project'
        db_table            = 'Project'

    def __str__(self):
        logger.info('Project model called')
        return '%s          -           %s          -%s' %(self.project_title, self.requestor, self.project_status)



class GigsterProject(CommonInfo):
    """
    #######################################################################################################
    A project represents the job posted by the requestor and completed by gigster. All the 
    relationship attributes between gigster and job is present in this model
    TODO
        * ADD PROJECT STATUS
        * ADD PAY STATUS

    FIXME
        * Nothing
    #######################################################################################################
    """

    GIGSTER_PROJECT_OPTION = [(1, "A - ACCEPT"),
                              (2, "R - REJECT"),
                        ]

    PAY_STATUS_CHOICE = [(1, "P - PAID"),
                            (2, "U - UNPAID"),
                        ]

    PROJECT_STATUS_CHOICE = [
                            (1, "O - OPEN"),
                            (2, "A - ACCEPTED"),
                            (3, "C - CLOSED "),
                            (4, "S - STARTED"),
                            (5, "E - ENDED"),
                            (6, "A - APPROVED"),
                            (7, "R - RATED"),
                            (8, "P - PAID"),
                        ]
    
    project                = models.ForeignKey(Project, on_delete=models.CASCADE, default = default_value)
    gigster                = models.ForeignKey(Gigster, on_delete=models.CASCADE, default = default_value)
    gigster_project_choice = models.IntegerField(verbose_name='gigster_project_choice',choices=GIGSTER_PROJECT_OPTION, blank=False, null=True)
    gigster_rating         = models.DecimalField(verbose_name='gigster_rating',decimal_places=1,max_digits=2, blank=True, null=True)
    project_status         = models.IntegerField(choices=PROJECT_STATUS_CHOICE, blank=True, null=True)
    pay_status             = models.IntegerField(choices=PAY_STATUS_CHOICE, blank=True, null=True)
    
    objects = models.Manager()

    class Meta:
        managed = True
        verbose_name_plural = 'Gigster Projects'
        verbose_name = 'Gigster Project'
        db_table = 'Gigster_Project'

    def __str__(self):
        logger.info('Gigster Project model called')
        return '%s-%s' %(self.gigster.gigster.first_name, self.project.project_title)





class UserDevices(models.Model):
    """
    #######################################################################################################

    This model keeps a record of all the user devices
    TODO
        * Nothing
    FIXME
        * Nothing
        
    #######################################################################################################

    """
    REGISTRATION_SOURCE = [(1, "PLAYSTORE - Android Playstore source"),
                           (2, "APPSTORE - Apple App Store"),
                           (3, "ADMIN- Added to the system by the Admin"),
                          ]
    PLATFORM_CHOICE = [(1, "A- Android"),
    					(2, "I- IOS"),
    				]
    user                = models.ForeignKey(User, on_delete=models.CASCADE, default = default_value)
    mac_address         = models.CharField(verbose_name='mac_address',max_length=255)
    platform            = models.IntegerField(verbose_name='Platform',choices=PLATFORM_CHOICE, blank=True, null=True)
    version             = models.CharField(verbose_name='version',max_length=255, blank=True, null=True)
    device_id           = models.BigIntegerField(verbose_name='device_id',default=default_value)
    registration_source = models.IntegerField(verbose_name='registration_source',choices=REGISTRATION_SOURCE, blank=True, null=True)
    
    class Meta:
        managed             = True
        verbose_name_plural = 'User Devices'
        verbose_name        = 'User Device'
        db_table            = 'user_devices'
        

    def __str__(self):
        return "%s-%s" %(self.user.first_name,self.platform)


from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    #######################################################################################################
    Here, we are extending the django user manager according to the application needs.
    UserManager class for Custom User Model.
    To create a user use User.Objects.create_user(phone_number='1212121212', password='#password, is_admin=True)

    TODO
        * Nothing
    FIXME
        * Nothing
    #######################################################################################################
    """

    def create_user(self, phone_number, password=None, is_active=False, is_staff=False, is_admin=False):
        if not phone_number:
            raise ValueError('Phone number is required for registration!')
        if not password:
            raise ValueError('Password is required!')

        user_obj = self.model(
            phone_number = phone_number,
            )
        user_obj.set_password(password)
        user_obj.active  = is_active
        user_obj.staff   = is_staff
        user_obj.admin   = is_admin
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone_number, password=None, is_active=False):
            user = self.create_user(
                phone_number,
                password   = password,
                is_staff   = True,
                is_active  = True
            )
            return user

    def create_superuser(self, phone_number, password=None, is_active=False):
            user = self.create_user(
                phone_number,
                password     = password,
                is_staff     = True,
                is_admin     = True,
                is_active     = True,
            )
            return user

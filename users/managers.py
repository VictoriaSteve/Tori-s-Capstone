# from django.contrib.auth.models import BaseUserManager


# class UserManager(BaseUserManager):
#     def create_user(self, email, first_name, last_name, password, address, **extra_fields):
#         if not email:
#             raise ValueError('You must write an email')
        
#         email = self.normalize_email(email)
        
#         user = self.model(email=email, first_name=first_name, last_name=last_name, address=address, **extra_fields)
#         user.set_password(password)
#         user.save(using=self.db)
#         return user
    
#     def create_superuser(self, email, first_name, last_name, password, address, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
        
#         return self.create_user(email, first_name, last_name, password, address, **extra_fields)





from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('You must provide an email')

        email = self.normalize_email(email)

        # Set defaults if not provided
        extra_fields.setdefault('first_name', '')
        extra_fields.setdefault('last_name', '')
        extra_fields.setdefault('address', '')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        # Ensure required fields exist
        if not extra_fields.get('first_name'):
            extra_fields['first_name'] = 'Admin'
        if not extra_fields.get('last_name'):
            extra_fields['last_name'] = 'User'
        if not extra_fields.get('address'):
            extra_fields['address'] = 'Admin Address'

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
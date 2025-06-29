from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Debe ingresar un email")
        if not name:
            raise ValueError("Debe ingresar un nombre para el usuario")

        user = self.model(
            email = self.normalize_email(email),
            name = name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, name, password, **extra_fields):
        user = self.create_user(email, name, password, **extra_fields)

        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.role = 0


        user.save(using = self._db)
        return user
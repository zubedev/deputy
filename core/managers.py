from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import UserManager as DjangoUserManager

if TYPE_CHECKING:
    from core.models import User


class UserManager(DjangoUserManager["User"]):
    """User Manager based from Django's UserManager"""

    def _create_user(self, name: str, email: str, password: str | None, **extra_fields: Any) -> "User":
        """
        Create and save user with the given email and password.

        :param name: name of the user
        :type name: str
        :param email: email address of the user
        :type email: str
        :param password: password for the user
        :type password: str
        :param is_staff: whether user is a staff member (default=False)
        :type is_staff: bool
        :param is_superuser: where user os an admin member (default=False)
        :type is_superuser: bool
        :return: User with given email and password
        :rtype: User
        :raises ValueError: if `name` not provided
        :raises ValueError: if `email` address not provided
        """
        if not name:
            raise ValueError("Must provide `name`")
        if not email:
            raise ValueError("Must provide `email` address")
        email = self.normalize_email(email)

        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(  # type: ignore
        self,
        name: str,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """
        Create a User with given email and password.
        By default, sets `is_staff=False` and `is_superuser=False`.

        :param name: name of the user
        :type name: str
        :param email: email address of the user
        :type email: str
        :param password: password for the user (default=None)
        :type password: str
        :return: User with given email and password
        :rtype: User
        """
        return self._create_user(name, email, password, **extra_fields)

    def create_staffuser(self, name: str, email: str, password: str | None = None, **extra_fields: Any) -> "User":
        """
        Create a staff User with the given email and password. Sets `is_staff=True` and `is_superuser=False`.

        :param name: name of the user
        :type name: str
        :param email: email address of the user
        :type email: str
        :param password: password for the user
        :type password: str
        :return: staff User with given email and password
        :rtype: User
        """
        extra_fields.update({"is_staff": True, "is_superuser": False})
        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(  # type: ignore
        self,
        name: str,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """
        Create an admin User with the given email and password. Sets `is_staff=True` and `is_superuser=True`.

        :param name: name of the user
        :type name: str
        :param email: email address of the user
        :type email: str
        :param password: password for the user
        :type password: str
        :return: admin User with given email and password
        :rtype: User
        """
        extra_fields.update({"is_staff": True, "is_superuser": True})
        return self._create_user(name, email, password, **extra_fields)

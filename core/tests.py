import os

import pytest
from _pytest.capture import CaptureFixture
from django.contrib.admin.models import LogEntry
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from core.factories import StaffuserFactory, SuperuserFactory, UserFactory
from core.models import User


@pytest.mark.django_db()
class TestLogEntryAdmin:
    def test_logentry_add(self, admin_client: Client) -> None:
        """Test LogEntry add"""
        url = reverse("admin:admin_logentry_add")
        res = admin_client.post(url)

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_logentry_changelist_and_search(self, admin_client: Client, user: User) -> None:
        """Test LogEntry changelist"""
        url = reverse("admin:admin_logentry_changelist")
        res1 = admin_client.get(url)

        assert res1.status_code == status.HTTP_200_OK

        res2 = admin_client.get(url, data={"q": "test"}, follow=True)
        assert res2.status_code == status.HTTP_200_OK

        admin_client.force_login(user)
        res3 = admin_client.get(url)

        assert res3.status_code == status.HTTP_302_FOUND
        assert "/admin/login/" in res3.url  # type: ignore

    def test_logentry_change_and_delete(self, admin_client: Client, superuser: User) -> None:
        """Test LogEntry change"""
        user_change_url = reverse("admin:core_user_change", args=(superuser.id,))

        admin_client.force_login(superuser)
        res1 = admin_client.get(user_change_url)
        assert res1.status_code == status.HTTP_200_OK

        res2 = admin_client.post(
            user_change_url, data={"name": "Superuser", "email": "superuser@test.local"}, follow=True
        )
        assert res2.status_code == status.HTTP_200_OK

        assert LogEntry.objects.count() == 1
        logentry = LogEntry.objects.get(id=1)

        logentry_change_url = reverse("admin:admin_logentry_change", args=(logentry.id,))
        res3 = admin_client.get(logentry_change_url)
        assert res3.status_code == status.HTTP_302_FOUND
        assert "/admin/login/" in res3.url  # type: ignore

        res4 = admin_client.post(logentry_change_url)
        assert res4.status_code == status.HTTP_302_FOUND
        assert "/admin/login/" in res4.url  # type: ignore

        logentry_delete_url = reverse("admin:admin_logentry_delete", args=(logentry.id,))
        res5 = admin_client.post(logentry_delete_url)
        assert res5.status_code == status.HTTP_302_FOUND
        assert "/admin/login/" in res5.url  # type: ignore


@pytest.mark.django_db()
class TestUserManager:
    def setup_method(self) -> None:
        self.faker = Faker()
        self.email: str = self.faker.email()
        self.password: str = self.faker.password()
        self.name: str = self.faker.name()

    def test_create_user(self) -> None:
        """Test creating a new regular user"""
        user: User = User.objects.create_user(name=self.name, email=self.email, password=self.password)

        assert user.name == self.name
        assert user.email == self.email
        assert user.check_password(self.password)
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_no_password(self) -> None:
        """Test creating a new regular user without password"""
        user: User = User.objects.create_user(name=self.name, email=self.email)

        assert user.name == self.name
        assert user.email == self.email
        assert not user.has_usable_password()
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_inactive(self) -> None:
        """Test creating a new regular user with inactive status"""
        user: User = User.objects.create_user(name=self.name, email=self.email, password=self.password, is_active=False)

        assert user.name == self.name
        assert user.email == self.email
        assert user.check_password(self.password)
        assert not user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_invalid_name(self) -> None:
        """Test creating a new regular user with invalid name"""
        with pytest.raises(ValueError, match="Must provide `name`"):
            User.objects.create_user(name="", email=self.email)
        with pytest.raises(ValueError, match="Must provide `name`"):
            User.objects.create_user(name=None, email=self.email)  # type: ignore

    def test_create_user_invalid_email(self) -> None:
        """Test creating a new regular user with invalid email"""
        with pytest.raises(ValueError, match="Must provide `email` address"):
            User.objects.create_user(name=self.name, email="")
        with pytest.raises(ValueError, match="Must provide `email` address"):
            User.objects.create_user(name=self.name, email=None)  # type: ignore

    def test_create_staffuser(self) -> None:
        """Test creating a new staff user"""
        user: User = User.objects.create_staffuser(name=self.name, email=self.email, password=self.password)

        assert user.name == self.name
        assert user.email == self.email
        assert user.check_password(self.password)
        assert user.is_active
        assert user.is_staff
        assert not user.is_superuser

    def test_create_staffuser_with_incorrect_is_superuser_flag(self) -> None:
        """Test creating a new staff user with incorrect is_superuser flag"""
        user: User = User.objects.create_staffuser(
            name=self.name, email=self.email, password=self.password, is_superuser=True
        )

        assert user.name == self.name
        assert user.email == self.email
        assert user.check_password(self.password)
        assert user.is_active
        assert user.is_staff
        assert not user.is_superuser  # should be set to False during creation

    def test_create_superuser(self) -> None:
        """Test creating a new superuser"""
        user: User = User.objects.create_superuser(name=self.name, email=self.email, password=self.password)

        assert user.name == self.name
        assert user.email == self.email
        assert user.check_password(self.password)
        assert user.is_active
        assert user.is_staff
        assert user.is_superuser

    def test_create_superuser_with_incorrect_is_staff_flag(self) -> None:
        """Test creating a new superuser with incorrect is_staff flag"""
        user: User = User.objects.create_superuser(
            name=self.name, email=self.email, password=self.password, is_staff=False
        )

        assert user.name == self.name
        assert user.email == self.email
        assert user.check_password(self.password)
        assert user.is_active
        assert user.is_staff  # should be set to True during creation
        assert user.is_superuser

    def test_createsuperuser_command(self, capsys: CaptureFixture[str]) -> None:
        """Test createsuperuser command"""
        # set password in environment variable
        if not os.environ.get("DJANGO_SUPERUSER_PASSWORD"):
            os.environ["DJANGO_SUPERUSER_PASSWORD"] = self.password

        command_result = call_command(
            "createsuperuser",
            "--name",
            self.name,
            "--email",
            self.email,
            interactive=False,
        )

        assert command_result is None
        captured = capsys.readouterr()
        assert captured.out == "Superuser created successfully.\n"

        user = User.objects.get(email=self.email)
        assert user.name == self.name
        assert user.email == self.email
        assert user.has_usable_password()
        assert user.is_active
        assert user.is_staff
        assert user.is_superuser


@pytest.mark.django_db()
class TestUserFactory:
    def test_user_factory(self, user_factory: type[UserFactory]) -> None:
        """Test UserFactory"""
        assert user_factory == UserFactory

        user: User = user_factory()
        assert isinstance(user, User)

        assert user.name
        assert user.email
        assert user.has_usable_password()
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_factory_params(self, user_factory: type[UserFactory]) -> None:
        """Test UserFactory"""
        name = "Test User"
        email = "testuser@test.local"
        password = "testPass123#"

        user: User = user_factory(name=name, email=email, password=password)

        assert user.name == name
        assert user.email == email
        assert user.check_password(password)

        # get user using factory, do not create. Should use `django_get_or_create` Meta option
        existing_user = user_factory(email=email)

        assert existing_user == user
        assert existing_user.id == user.id
        assert existing_user.email == user.email

    def test_user_instance(self, user: User) -> None:
        """Test UserFactory"""
        assert isinstance(user, User)

        assert user.name
        assert user.email
        assert user.has_usable_password()
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    @pytest.mark.parametrize(
        ("user__name", "user__email", "user__password"), [("Test User", "testuser@test.local", "testPass123#")]
    )
    def test_user_instance_params(self, user: User) -> None:
        """Test UserFactory"""
        assert user.name == "Test User"
        assert user.email == "testuser@test.local"
        assert user.check_password("testPass123#")

    def test_staffuser_factory(self, staffuser_factory: type[StaffuserFactory]) -> None:
        """Test StaffUserFactory"""
        assert staffuser_factory == StaffuserFactory

        user: User = staffuser_factory()
        assert isinstance(user, User)

        assert user.name
        assert user.email
        assert user.has_usable_password()
        assert user.is_active
        assert user.is_staff
        assert not user.is_superuser

    def test_staffuser_instance(self, staffuser: User) -> None:
        """Test StaffUserFactory"""
        assert isinstance(staffuser, User)

        assert staffuser.name
        assert staffuser.email
        assert staffuser.has_usable_password()
        assert staffuser.is_active
        assert staffuser.is_staff
        assert not staffuser.is_superuser

    def test_superuser_factory(self, superuser_factory: type[SuperuserFactory]) -> None:
        """Test SuperUserFactory"""
        assert superuser_factory == SuperuserFactory

        user: User = superuser_factory()
        assert isinstance(user, User)

        assert user.name
        assert user.email
        assert user.has_usable_password()
        assert user.is_active
        assert user.is_staff
        assert user.is_superuser

    def test_superuser_instance(self, superuser: User) -> None:
        """Test SuperUserFactory"""
        assert isinstance(superuser, User)

        assert superuser.name
        assert superuser.email
        assert superuser.has_usable_password()
        assert superuser.is_active
        assert superuser.is_staff
        assert superuser.is_superuser


@pytest.mark.django_db()
class TestUserModel:
    def test_user_str(self, user: User) -> None:
        """Test the user string representation"""
        assert str(user) == f"{user.name} <{user.email}>"

    def test_user_repr(self, user: User) -> None:
        """Test the user string representation"""
        assert repr(user) == f"<User: id={user.id} name='{user.name}' email='{user.email}'>"


@pytest.mark.django_db()
class TestUserAdmin:
    def test_user_changelist(self, admin_client: Client) -> None:
        """Test UserAdmin changelist"""
        url = reverse("admin:core_user_changelist")
        response = admin_client.get(url)

        assert response.status_code == 200

    def test_user_changelist_search(self, admin_client: Client) -> None:
        """Test UserAdmin changelist search"""
        url = reverse("admin:core_user_changelist")
        response = admin_client.get(url, data={"q": "test"})

        assert response.status_code == 200

    def test_user_add(self, admin_client: Client) -> None:
        """Test UserAdmin add"""
        url = reverse("admin:core_user_add")
        response = admin_client.post(url)

        assert response.status_code == 200

        response = admin_client.post(
            url,
            data={
                "name": "Test User",
                "email": "testuser@test.local",
                "password1": "testPass123#",
                "password2": "testPass123#",
            },
        )

        assert response.status_code == 302

        user = User.objects.get(email="testuser@test.local")
        assert user.name == "Test User"
        assert user.check_password("testPass123#")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_change(self, admin_client: Client, user: User) -> None:
        """Test UserAdmin change"""
        url = reverse("admin:core_user_change", args=(user.id,))
        response = admin_client.get(url)

        assert response.status_code == 200

        response = admin_client.post(
            url,
            data={
                "name": "Test User",
                "email": "testuser@test.local",
            },
        )

        assert response.status_code == 302

        user.refresh_from_db()
        assert user.name == "Test User"
        assert user.email == "testuser@test.local"

    def test_user_delete(self, admin_client: Client, user: User) -> None:
        user_id = user.id

        assert User.objects.count() == 2  # admin user + test user

        url = reverse("admin:core_user_delete", args=(user_id,))
        response = admin_client.post(url, data={"post": "yes"})

        assert response.status_code == 302

        with pytest.raises(User.DoesNotExist):
            User.objects.get(id=user_id)

        assert User.objects.count() == 1  # just the admin user left


@pytest.mark.django_db()
class TestUserViews:
    def setup_method(self) -> None:
        self.faker = Faker()
        self.name = self.faker.name()
        self.email = self.faker.email()
        self.password = self.faker.password()

    def test_user_create(self, api_client: APIClient, user: User, staffuser: User) -> None:
        """Test User create view"""
        url = reverse("user-list")

        # anonymous users can not create users
        res1: Response = api_client.post(url)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not create users
        api_client.force_login(user)
        res2: Response = api_client.post(url)
        assert res2.status_code == status.HTTP_403_FORBIDDEN

        # staff users can create users
        api_client.force_login(staffuser)
        data = {"name": self.name, "email": self.email, "password": self.password}
        res3: Response = api_client.post(path=url, data=data)
        assert res3.status_code == status.HTTP_201_CREATED

        user = User.objects.get(email=self.email)
        assert user.name == self.name
        assert user.email == self.email
        assert user.has_usable_password()
        assert user.check_password(self.password)
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_list(self, api_client: APIClient, user: User, staffuser: User) -> None:
        """Test User list view"""
        url = reverse("user-list")

        # anonymous users can not list users
        res1: Response = api_client.get(url)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not list users
        api_client.force_login(user)
        res2: Response = api_client.get(url)
        assert res2.status_code == status.HTTP_403_FORBIDDEN

        # staff users can list users
        api_client.force_login(staffuser)
        res3: Response = api_client.get(url)
        assert res3.status_code == status.HTTP_200_OK
        assert res3.data["count"] == 2

        results = res3.data["results"]
        assert len(results) == 2
        assert results[0]["id"] == user.id
        assert results[1]["id"] == staffuser.id

    def test_user_detail(self, api_client: APIClient, user: User, staffuser: User) -> None:
        """Test User detail view"""
        user_url = user.get_absolute_url()
        staffuser_url = staffuser.get_absolute_url()

        # anonymous users can not view users
        res1: Response = api_client.get(user_url)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not view other users
        api_client.force_login(user)
        res2: Response = api_client.get(staffuser_url)
        assert res2.status_code == status.HTTP_403_FORBIDDEN

        # regular users can view themselves
        res3: Response = api_client.get(user_url)
        assert res3.status_code == status.HTTP_200_OK
        assert res3.data["id"] == user.id

        # staff users can view other users
        api_client.force_login(staffuser)
        res4: Response = api_client.get(user_url)
        assert res4.status_code == status.HTTP_200_OK
        assert res4.data["id"] == user.id

        # staff users can view themselves
        res5: Response = api_client.get(staffuser_url)
        assert res5.status_code == status.HTTP_200_OK
        assert res5.data["id"] == staffuser.id

    def test_user_me(self, api_client: APIClient, user: User, staffuser: User) -> None:
        """Test User me view"""
        url = reverse("user-me")

        # anonymous users can not view me
        res1: Response = api_client.get(url, follow=True)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can view themselves
        api_client.force_login(user)
        res2: Response = api_client.get(url, follow=True)
        assert res2.status_code == status.HTTP_200_OK
        assert res2.data["id"] == user.id

        # staff users can view themselves
        api_client.force_login(staffuser)
        res3: Response = api_client.get(url, follow=True)
        assert res3.status_code == status.HTTP_200_OK
        assert res3.data["id"] == staffuser.id

    def test_user_partial_update(self, api_client: APIClient, user: User, staffuser: User) -> None:
        user_url = user.get_absolute_url()
        staffuser_url = staffuser.get_absolute_url()

        # anonymous users can not update users
        res1: Response = api_client.patch(user_url)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not update other users
        api_client.force_login(user)
        res2: Response = api_client.patch(staffuser_url)
        assert res2.status_code == status.HTTP_403_FORBIDDEN

        # regular users can update themselves
        data3 = {"name": self.faker.name()}
        res3: Response = api_client.patch(user_url, data=data3)
        assert res3.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.name == data3["name"]

        # regular users can update password only
        data4 = {"password": self.faker.password()}
        res4: Response = api_client.patch(user_url, data=data4)
        assert res4.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password(data4["password"])
        assert user.has_usable_password()

        # staff users can update other users
        api_client.force_login(staffuser)
        data5 = {"name": self.faker.name()}
        res5: Response = api_client.patch(user_url, data=data5)
        assert res5.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.name == data5["name"]

        # staff users can update themselves
        data6 = {"name": self.faker.name()}
        res6: Response = api_client.patch(staffuser_url, data=data6)
        assert res6.status_code == status.HTTP_200_OK
        staffuser.refresh_from_db()
        assert staffuser.name == data6["name"]

    def test_user_update(self, api_client: APIClient, user: User, staffuser: User) -> None:
        user_url = user.get_absolute_url()
        staffuser_url = staffuser.get_absolute_url()

        # anonymous users can not update users
        res1: Response = api_client.put(user_url)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not update other users
        api_client.force_login(user)
        res2: Response = api_client.put(staffuser_url)
        assert res2.status_code == status.HTTP_403_FORBIDDEN

        # regular users can update themselves
        data3 = {"name": self.faker.name(), "email": self.faker.email(), "password": self.faker.password()}
        res3: Response = api_client.put(user_url, data=data3)
        assert res3.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.name == data3["name"]
        assert user.email == data3["email"]
        assert user.check_password(data3["password"])
        assert user.has_usable_password()

        # staff users can update other users
        api_client.force_login(staffuser)
        data4 = {"name": self.faker.name(), "email": self.faker.email(), "password": self.faker.password()}
        res4: Response = api_client.put(user_url, data=data4)
        assert res4.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.name == data4["name"]
        assert user.email == data4["email"]
        assert user.check_password(data4["password"])
        assert user.has_usable_password()

        # staff users can update themselves
        data5 = {"name": self.faker.name(), "email": self.faker.email(), "password": self.faker.password()}
        res5: Response = api_client.put(staffuser_url, data=data5)
        assert res5.status_code == status.HTTP_200_OK
        staffuser.refresh_from_db()
        assert staffuser.name == data5["name"]
        assert staffuser.email == data5["email"]
        assert staffuser.check_password(data5["password"])
        assert staffuser.has_usable_password()

    def test_user_destroy(self, api_client: APIClient, user_factory: type[UserFactory], staffuser: User) -> None:
        user = user_factory()
        user_url = user.get_absolute_url()
        staffuser_url = staffuser.get_absolute_url()

        # anonymous users can not delete users
        res1: Response = api_client.delete(user_url)
        assert res1.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not delete other users
        api_client.force_login(user)
        res2: Response = api_client.delete(staffuser_url)
        assert res2.status_code == status.HTTP_403_FORBIDDEN

        # regular users can not delete themselves
        res3: Response = api_client.delete(user_url)
        assert res3.status_code == status.HTTP_204_NO_CONTENT

        # staff users can delete other users
        api_client.force_login(staffuser)
        res4: Response = api_client.delete(user_factory().get_absolute_url())
        assert res4.status_code == status.HTTP_204_NO_CONTENT

        # staff users can delete themselves
        res5: Response = api_client.delete(staffuser_url)
        assert res5.status_code == status.HTTP_204_NO_CONTENT

        assert User.objects.count() == 0

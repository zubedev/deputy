from django.db import migrations, models

import core.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        max_length=128,
                        verbose_name="password",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="last login",
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date time on which the object was created.",
                        verbose_name="created at",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Date time on which the object was last updated.",
                        verbose_name="updated at",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Active status of the object.",
                        verbose_name="active status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Email address of the user (required, max length = 254 chars).",
                        max_length=254,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the user (required, max length = 254 chars).",
                        max_length=254,
                        verbose_name="name",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into the admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[
                ("objects", core.managers.UserManager()),
            ],
        ),
    ]

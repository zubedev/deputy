from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import EmailField
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# admin site customizations
admin.sites.AdminSite.site_title = "deputy Admin"
admin.sites.AdminSite.site_header = "deputy Admin"
admin.sites.AdminSite.index_title = "Admin Home"

UserModel = get_user_model()


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin[LogEntry]):
    """Django Admin Log Entries"""

    date_hierarchy = "action_time"
    list_display = ("id", "action_time", "user_link", "content_type", "object_link", "action_flag", "change_message")
    list_display_links = ("id", "action_time")
    list_filter = ("action_flag", "content_type")
    ordering = ("-id",)
    search_fields = ("user__name", "user__email", "object_repr", "change_message")

    def has_view_permission(self, request: HttpRequest, obj: LogEntry | None = None) -> bool:
        """Permission to VIEW a LogEntry"""
        return bool(request.user.is_staff)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Permission to ADD a LogEntry"""
        return False

    def has_change_permission(self, request: HttpRequest, obj: LogEntry | None = None) -> bool:
        """Permission to CHANGE a LogEntry"""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: LogEntry | None = None) -> bool:
        """Permission to DELETE a LogEntry"""
        return False

    @admin.display(description="user", ordering="user")
    def user_link(self, obj: LogEntry) -> str:
        """Show link to the User"""
        try:
            url = reverse("admin:core_user_change", args=[obj.user_id])
            link = mark_safe(f'<a href="{url}">{obj.user}</a>')
        except Exception:
            link = obj.user
        return format_html("{link}", link=link)

    @admin.display(description="object", ordering="object_repr")
    def object_link(self, obj: LogEntry) -> str:
        """Show link to the object"""
        if obj.action_flag == DELETION:
            link = obj.object_repr
        else:
            try:
                ct = obj.content_type
                url = reverse(f"admin:{ct.app_label}_{ct.model}_change", args=[obj.object_id])
                link = mark_safe(f'<a href="{url}">{obj.object_repr}</a>')
            except Exception:
                link = obj.object_repr
        return format_html("{link}", link=link)


class UserAdminChangeForm(UserChangeForm[AbstractBaseUser]):
    """Form for updating users in admin"""

    class Meta(UserChangeForm.Meta):
        model = UserModel
        field_classes = {"email": EmailField}


class UserAdminCreationForm(UserCreationForm[AbstractBaseUser]):
    """Form for creating users in admin"""

    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ("email", "name")
        field_classes = {"email": EmailField}
        error_messages = {"email": {"unique": "This email has already been taken."}}


@admin.register(UserModel)
class UserAdmin(DjangoUserAdmin):
    # list view
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "name",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "last_login",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "name", "email")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("id",)
    search_fields = ("id", "name", "email")

    # change view
    form = UserAdminChangeForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("last_login", "created_at", "updated_at")

    # add view
    add_form = UserAdminCreationForm
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("name", "email", "password1", "password2")}),)

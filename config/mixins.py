from django.db import models


class TimeStampedMixin(models.Model):
    """Model mixin class to add `created_at` and `updated_at` fields to a model"""

    created_at = models.DateTimeField(
        "created at",
        auto_now_add=True,
        editable=False,
        help_text="Date time on which the object was created.",
    )
    updated_at = models.DateTimeField(
        "updated at",
        auto_now=True,
        editable=False,
        help_text="Date time on which the object was last updated.",
    )

    class Meta:
        abstract = True


class ActiveStatusMixin(models.Model):
    """Model mixin class to add `is_active` field to a model"""

    is_active = models.BooleanField("active status", default=True, help_text="Active status of the object.")

    class Meta:
        abstract = True


class BaseModel(TimeStampedMixin, ActiveStatusMixin):
    """A BaseModel containing attributes `created_at`, `updated_at`, and `is_active` fields added to a model"""

    class Meta:
        abstract = True

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# ---------------------------------------------
# Company Model
# ---------------------------------------------
class Company(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ---------------------------------------------
# Director Model
# ---------------------------------------------
class Director(models.Model):
    full_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='directors/photos/')
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='directors',
        null=True,    # allow null for old records
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

# ---------------------------------------------
# Shareholder Model
# ---------------------------------------------
class Shareholder(models.Model):
    full_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='shareholders/photos/')
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='shareholders',
        null=True,    # allow null for old records
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"

# ---------------------------------------------
# ShareLedger Model
# ---------------------------------------------
class ShareLedger(models.Model):
    TRANSACTION_TYPES = (
        ('ADD', 'Add Shares'),
        ('REMOVE', 'Remove Shares'),
    )

    shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.CASCADE,
        related_name='ledger_entries'
    )
    shares = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.shares} for {self.shareholder.full_name}"

# ---------------------------------------------
# Audit Log Model
# ---------------------------------------------
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"

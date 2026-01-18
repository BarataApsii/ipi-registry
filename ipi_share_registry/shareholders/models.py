from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Shareholder(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="shareholders"
    )
    full_name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=100, unique=True)
    photo = models.ImageField(upload_to="shareholders/photos/", blank=True, null=True)
    total_shares = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"


class Director(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="directors"
    )
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    appointed_date = models.DateField()

    def __str__(self):
        return self.full_name


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ("ISSUE", "Share Issue"),
        ("TRANSFER", "Transfer"),
        ("ADJUSTMENT", "Adjustment"),
    )

    shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )
    shares = models.IntegerField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.shares}"

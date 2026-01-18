from django.contrib import admin
from .models import Company, Shareholder, Director, Transaction


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number", "created_at")
    search_fields = ("name",)


@admin.register(Shareholder)
class ShareholderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "id_number", "company", "total_shares")
    search_fields = ("full_name", "id_number")
    list_filter = ("company",)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "position", "appointed_date")
    list_filter = ("company",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("shareholder", "transaction_type", "shares", "created_at")
    list_filter = ("transaction_type", "created_at")

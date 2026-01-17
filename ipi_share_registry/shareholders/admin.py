from django.contrib import admin
from .models import Shareholder, ShareLedger


@admin.register(Shareholder)
class ShareholderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_number', 'created_at')
    search_fields = ('full_name', 'id_number')


@admin.register(ShareLedger)
class ShareLedgerAdmin(admin.ModelAdmin):
    list_display = ('shareholder', 'transaction_type', 'shares', 'created_at', 'updated_by')
    list_filter = ('transaction_type',)

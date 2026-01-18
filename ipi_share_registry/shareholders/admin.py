from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Company, Shareholder, Director, Transaction, ShareTransfer


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number", "email", "phone", "updated_at")
    search_fields = ("name", "registration_number", "tax_id")
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'registration_number', 'tax_id', 'fiscal_year_end')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Shareholder)
class ShareholderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "id_number", "total_shares", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("full_name", "id_number", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name', 'id_number', 'date_of_birth', 'gender',
                'nationality', 'tax_identification_number'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email', 'phone', 'address', 'city', 'state',
                'postal_code', 'country'
            )
        }),
        ('Share Information', {
            'fields': (
                'total_shares', 'share_certificate_number',
                'date_joined', 'is_active'
            )
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "director_type", "is_active", "appointed_date")
    list_filter = ("director_type", "is_active", "appointed_date")
    search_fields = ("full_name", "id_number", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ('Director Information', {
            'fields': (
                'full_name', 'director_type', 'position',
                'id_number', 'nationality'
            )
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Appointment Details', {
            'fields': (
                'appointed_date', 'resignation_date',
                'is_active', 'biography'
            )
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "shareholder_link", "transaction_type", "shares", "transaction_date", "status")
    list_filter = ("transaction_type", "status", "transaction_date")
    search_fields = ("shareholder__full_name", "reference_number", "certificate_number")
    readonly_fields = ("created_at", "updated_at", "created_by", "approved_by", "approval_date")
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'transaction_type', 'status', 'shares',
                'price_per_share', 'total_amount', 'transaction_date'
            )
        }),
        ('Shareholder Information', {
            'fields': ('shareholder',)
        }),
        ('Documentation', {
            'fields': ('reference_number', 'certificate_number', 'attachment')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approval_date', 'completion_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def shareholder_link(self, obj):
        if obj.shareholder_id:
            url = reverse('admin:shareholders_shareholder_change', args=[obj.shareholder_id])
            return mark_safe(f'<a href="{url}">{obj.shareholder}</a>')
        return "-"
    shareholder_link.short_description = 'Shareholder'
    shareholder_link.admin_order_field = 'shareholder__full_name'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        if 'status' in form.changed_data and form.cleaned_data['status'] == 'APPROVED':
            obj.approved_by = request.user
            obj.approval_date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ShareTransfer)
class ShareTransferAdmin(admin.ModelAdmin):
    list_display = ("id", "from_shareholder_link", "to_shareholder_link", "shares", "status", "transfer_date")
    list_filter = ("status", "transfer_date")
    search_fields = ("from_shareholder__full_name", "to_shareholder__full_name", "reference_number")
    readonly_fields = ("created_at", "updated_at", "created_by", "approved_by", "completed_by")
    fieldsets = (
        ('Transfer Details', {
            'fields': (
                'status', 'shares', 'price_per_share', 'total_amount',
                'transfer_date', 'reference_number', 'certificate_number'
            )
        }),
        ('Parties', {
            'fields': ('from_shareholder', 'to_shareholder')
        }),
        ('Documentation', {
            'fields': ('terms', 'attachment')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approved_at', 'completed_by', 'completed_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def from_shareholder_link(self, obj):
        if obj.from_shareholder_id:
            url = reverse('admin:shareholders_shareholder_change', args=[obj.from_shareholder_id])
            return mark_safe(f'<a href="{url}">{obj.from_shareholder}</a>')
        return "-"
    from_shareholder_link.short_description = 'From Shareholder'
    from_shareholder_link.admin_order_field = 'from_shareholder__full_name'

    def to_shareholder_link(self, obj):
        if obj.to_shareholder_id:
            url = reverse('admin:shareholders_shareholder_change', args=[obj.to_shareholder_id])
            return mark_safe(f'<a href="{url}">{obj.to_shareholder}</a>')
        return "-"
    to_shareholder_link.short_description = 'To Shareholder'
    to_shareholder_link.admin_order_field = 'to_shareholder__full_name'

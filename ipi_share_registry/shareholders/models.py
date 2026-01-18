from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse


class Company(models.Model):
    name = models.CharField(max_length=255, default='IPI Group')
    registration_number = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    fiscal_year_end = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Company"
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='single_company_constraint'
            )
        ]

    def save(self, *args, **kwargs):
        # Ensure only one company can exist
        if Company.objects.exists() and not self.pk:
            raise ValidationError('Only one company can be created')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @classmethod
    def get_company(cls):
        """Get the single company instance, create if it doesn't exist"""
        company, created = cls.objects.get_or_create(
            name='IPI Group',
            defaults={
                'registration_number': ''  # Set default values for other required fields
            }
        )
        return company


class Shareholder(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="shareholders"
    )
    full_name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=100, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Share Information
    share_certificate_number = models.CharField(max_length=50, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    total_shares = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Additional Fields
    photo = models.ImageField(upload_to="shareholders/photos/", blank=True, null=True)
    notes = models.TextField(blank=True)
    
    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shareholders'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shareholder'
        verbose_name_plural = 'Shareholders'
        indexes = [
            models.Index(fields=['id_number']),
            models.Index(fields=['full_name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shareholders:shareholder_detail', args=[str(self.id)])
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.country} {self.postal_code}".strip(', ')


class Director(models.Model):
    DIRECTOR_TYPE_CHOICES = [
        ('EXECUTIVE', 'Executive Director'),
        ('NON_EXECUTIVE', 'Non-Executive Director'),
        ('INDEPENDENT', 'Independent Director'),
        ('CHAIRPERSON', 'Chairperson'),
        ('MANAGING', 'Managing Director'),
        ('ALTERNATE', 'Alternate Director'),
    ]
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="directors"
    )
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='director_profile'
    )
    full_name = models.CharField(max_length=255)
    director_type = models.CharField(
        max_length=20,
        choices=DIRECTOR_TYPE_CHOICES,
        default='EXECUTIVE'
    )
    position = models.CharField(max_length=100)
    id_number = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    appointed_date = models.DateField()
    resignation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    biography = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', 'director_type', 'full_name']
        verbose_name = 'Director'
        verbose_name_plural = 'Directors'

    def __str__(self):
        return f"{self.full_name} ({self.get_director_type_display()})"
        
    @property
    def current_position(self):
        if self.resignation_date:
            return f"Former {self.position}"
        return self.position


class Transaction(models.Model):
    """
    Represents a share transaction in the system.
    """
    TRANSACTION_TYPE_CHOICES = [
        ("ISSUE", "Share Issue"),
        ("PURCHASE", "Share Purchase"),
        ("TRANSFER_IN", "Transfer In"),
        ("TRANSFER_OUT", "Transfer Out"),
        ("BONUS", "Bonus Issue"),
        ("RIGHTS", "Rights Issue"),
        ("BUYBACK", "Share Buyback"),
        ("CONVERSION", "Conversion"),
        ("ADJUSTMENT", "Adjustment"),
        ("DIVIDEND", "Dividend"),
        ("SPLIT", "Stock Split"),
        ("OTHER", "Other"),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('REVERSED', 'Reversed'),
    ]

    # Core Fields
    shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True
    )
    
    # Transaction Details
    shares = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Number of shares involved in the transaction"
    )
    price_per_share = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price per share at the time of transaction"
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total transaction amount (shares * price_per_share)"
    )
    
    # Dates
    transaction_date = models.DateField(
        default=timezone.now,
        help_text="Effective date of the transaction"
    )
    entry_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When this transaction was recorded"
    )
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this transaction was approved"
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this transaction was completed"
    )
    
    # References
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference number or identifier"
    )
    certificate_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Share certificate number if applicable"
    )
    
    # Relationships
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transactions'
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_transactions'
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='transactions/attachments/',
        null=True,
        blank=True,
        help_text="Any supporting document for this transaction"
    )
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['-transaction_date', '-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['shareholder']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.shareholder} ({self.shares} shares)"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if price_per_share is provided
        if self.price_per_share is not None and self.shares is not None:
            self.total_amount = self.price_per_share * self.shares
            
        # Set approval date when status changes to APPROVED
        if self.pk:
            old_instance = Transaction.objects.get(pk=self.pk)
            if old_instance.status != self.status and self.status == 'APPROVED':
                self.approval_date = timezone.now()
            if old_instance.status != self.status and self.status == 'COMPLETED':
                self.completion_date = timezone.now()
                
        super().save(*args, **kwargs)
    
    def can_be_approved(self):
        """Check if the transaction can be approved."""
        return self.status in ['DRAFT', 'PENDING']
    
    def can_be_completed(self):
        """Check if the transaction can be marked as completed."""
        return self.status in ['APPROVED', 'PENDING']
    
    def can_be_cancelled(self):
        """Check if the transaction can be cancelled."""
        return self.status in ['DRAFT', 'PENDING', 'APPROVED']
    
    def update_shareholder_balance(self):
        """Update the shareholder's total shares based on this transaction."""
        if self.status != 'COMPLETED':
            return False
            
        with transaction.atomic():
            shareholder = self.shareholder
            if self.transaction_type in ['ISSUE', 'PURCHASE', 'TRANSFER_IN', 'BONUS', 'RIGHTS']:
                shareholder.total_shares += self.shares
            elif self.transaction_type in ['BUYBACK', 'TRANSFER_OUT']:
                shareholder.total_shares -= self.shares
                if shareholder.total_shares < 0:
                    raise ValidationError("Shareholder cannot have negative shares")
            
            shareholder.save(update_fields=['total_shares'])
            self.status = 'COMPLETED'
            self.save(update_fields=['status'])
            
        return True


class ShareTransfer(models.Model):
    """
    Represents a transfer of shares between two shareholders.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Transfer Details
    transfer_date = models.DateField(
        default=timezone.now,
        help_text="Effective date of the transfer"
    )
    shares = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Number of shares to transfer"
    )
    price_per_share = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price per share for this transfer (if applicable)"
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total transfer amount (shares * price_per_share)"
    )
    
    # References
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference number or identifier"
    )
    certificate_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="New share certificate number if applicable"
    )
    
    # Relationships
    from_shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.PROTECT,
        related_name='outgoing_transfers',
        help_text="Shareholder transferring the shares"
    )
    to_shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.PROTECT,
        related_name='incoming_transfers',
        help_text="Shareholder receiving the shares"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='share_transfers'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True
    )
    
    # Tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_transfers'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transfers'
    )
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_transfers'
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    terms = models.TextField(
        blank=True,
        help_text="Terms and conditions of the transfer"
    )
    attachment = models.FileField(
        upload_to='transfers/attachments/',
        null=True,
        blank=True,
        help_text="Any supporting document for this transfer"
    )
    
    class Meta:
        ordering = ['-transfer_date', '-created_at']
        verbose_name = 'Share Transfer'
        verbose_name_plural = 'Share Transfers'
        indexes = [
            models.Index(fields=['transfer_date']),
            models.Index(fields=['status']),
            models.Index(fields=['from_shareholder']),
            models.Index(fields=['to_shareholder']),
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return f"Transfer of {self.shares} shares from {self.from_shareholder} to {self.to_shareholder} ({self.get_status_display()})"
    
    def clean(self):
        # Ensure from and to shareholders are different
        if self.from_shareholder_id and self.to_shareholder_id and self.from_shareholder_id == self.to_shareholder_id:
            raise ValidationError("Transferor and transferee cannot be the same shareholder")
        
        # Ensure sufficient shares are available
        if self.status != 'COMPLETED' and self.from_shareholder and self.shares:
            if self.from_shareholder.total_shares < self.shares:
                raise ValidationError("Insufficient shares available for transfer")
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if price_per_share is provided
        if self.price_per_share is not None and self.shares is not None:
            self.total_amount = self.price_per_share * self.shares
        
        # Update timestamps based on status changes
        if self.pk:
            old_instance = ShareTransfer.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                if self.status == 'APPROVED':
                    self.approved_at = timezone.now()
                elif self.status == 'COMPLETED':
                    self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def execute_transfer(self, approved_by=None):
        """
        Execute the share transfer by creating the necessary transactions.
        Returns a tuple of (from_transaction, to_transaction)
        """
        if self.status != 'PENDING' and self.status != 'APPROVED':
            raise ValidationError("Only pending or approved transfers can be executed")
        
        with transaction.atomic():
            # Create transfer out transaction
            from_tx = Transaction.objects.create(
                shareholder=self.from_shareholder,
                transaction_type='TRANSFER_OUT',
                shares=self.shares,
                price_per_share=self.price_per_share,
                total_amount=self.total_amount,
                transaction_date=self.transfer_date,
                reference_number=f"TRANSFER-OUT-{self.id}",
                certificate_number=self.certificate_number,
                notes=f"Transfer to {self.to_shareholder.full_name}",
                created_by=self.created_by,
                status='COMPLETED'
            )
            
            # Create transfer in transaction
            to_tx = Transaction.objects.create(
                shareholder=self.to_shareholder,
                transaction_type='TRANSFER_IN',
                shares=self.shares,
                price_per_share=self.price_per_share,
                total_amount=self.total_amount,
                transaction_date=self.transfer_date,
                reference_number=f"TRANSFER-IN-{self.id}",
                certificate_number=self.certificate_number,
                notes=f"Transfer from {self.from_shareholder.full_name}",
                created_by=self.created_by,
                status='COMPLETED'
            )
            
            # Update transfer status
            self.status = 'COMPLETED'
            self.completed_by = approved_by or self.approved_by
            self.completed_at = timezone.now()
            self.save()
            
            return from_tx, to_tx
    
    def can_be_approved(self):
        """Check if the transfer can be approved."""
        return self.status in ['DRAFT', 'PENDING']
    
    def can_be_completed(self):
        """Check if the transfer can be marked as completed."""
        return self.status in ['APPROVED', 'PENDING']
    
    def can_be_cancelled(self):
        """Check if the transfer can be cancelled."""
        return self.status in ['DRAFT', 'PENDING', 'APPROVED']

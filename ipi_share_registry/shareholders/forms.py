# shareholders/forms.py
from django import forms
from .models import Shareholder
import logging

logger = logging.getLogger(__name__)

class ShareholderForm(forms.ModelForm):
    class Meta:
        model = Shareholder
        fields = [
            'full_name', 'id_number', 'date_of_birth', 'gender', 'nationality',
            'email', 'phone_number', 'address', 'city', 'country', 'postal_code',
            'share_certificate_number', 'photo', 'notes'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter any additional notes about the shareholder'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@domain.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (123) 456-7890'
            })
        }
        help_texts = {
            'id_number': 'National ID or Passport number',
            'email': 'A valid email address',
            'phone_number': 'Include country code if international',
            'photo': 'Maximum file size: 2MB. Allowed formats: JPG, PNG',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            field.required = field_name in ['full_name', 'id_number']
            
            # Add placeholder for required fields
            if field.required and not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = f'Enter {field.label.lower()}'
            
            # Add required attribute for client-side validation
            if field.required:
                field.widget.attrs['required'] = ''
                
            # Add aria attributes for accessibility
            field.widget.attrs.update({
                'aria-label': field.label,
                'aria-required': 'true' if field.required else 'false'
            })

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Form cleaned data: {cleaned_data}")
        return cleaned_data

    def save(self, commit=True):
        try:
            logger.info("Starting to save shareholder form")
            shareholder = super().save(commit=False)
            
            if commit:
                logger.debug("Committing shareholder to database")
                shareholder.save()
                self.save_m2m()  # For any many-to-many fields
                logger.info(f"Successfully saved shareholder with ID: {shareholder.id}")
            return shareholder
        except Exception as e:
            logger.error(f"Error saving shareholder: {str(e)}", exc_info=True)
            raise
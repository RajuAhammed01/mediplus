from django.db import models
from mediplus.apps.accounts.models import User
import uuid

class Patient(models.Model):
    """Patient model extending user"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    allergies = models.TextField(blank=True)
    chronic_diseases = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

class MedicalRecord(models.Model):
    """Patient medical records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    record_type = models.CharField(max_length=50, choices=[
        ('prescription', 'Prescription'),
        ('lab_report', 'Lab Report'),
        ('imaging', 'Imaging (X-Ray, MRI, etc.)'),
        ('surgery', 'Surgery Record'),
        ('vaccination', 'Vaccination Record'),
        ('other', 'Other')
    ])
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='medical_records/%Y/%m/%d/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_records')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_shared = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.record_type} - {self.title}"

class FamilyMember(models.Model):
    """Family members linked to patient account"""
    RELATIONSHIPS = [
        ('self', 'Self'),
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('other', 'Other')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIPS)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.relationship})"
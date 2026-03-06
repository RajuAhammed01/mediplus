from django.db import models
from mediplus.apps.accounts.models import User
from mediplus.apps.patients.models import Patient
from mediplus.apps.doctors.models import Doctor
import uuid

class Appointment(models.Model):
    """Appointment booking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show')
    ]
    
    TYPE_CHOICES = [
        ('online', 'Online Consultation'),
        ('in_person', 'In-Person Visit')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-start_time']
        indexes = [
            models.Index(fields=['doctor', 'appointment_date', 'status']),
            models.Index(fields=['patient', 'appointment_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Generate unique appointment ID
            last_appointment = Appointment.objects.order_by('-created_at').first()
            if last_appointment and last_appointment.appointment_id:
                last_num = int(last_appointment.appointment_id.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1000
            self.appointment_id = f"APT-{new_num}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"

class Prescription(models.Model):
    """Doctor's prescription for patient"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis = models.TextField()
    advice = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription for {self.patient.user.get_full_name()} - Dr. {self.doctor.user.get_full_name()}"

class PrescriptionItem(models.Model):
    """Individual medicine in prescription"""
    FREQUENCY_CHOICES = [
        ('od', 'Once Daily'),
        ('bd', 'Twice Daily'),
        ('tds', 'Three Times Daily'),
        ('qds', 'Four Times Daily'),
        ('hs', 'At Bedtime'),
        ('ac', 'Before Meals'),
        ('pc', 'After Meals'),
        ('sos', 'As Needed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    strength = models.CharField(max_length=50, help_text="e.g., 500mg")
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration = models.CharField(max_length=50, help_text="e.g., 7 days")
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.strength}"
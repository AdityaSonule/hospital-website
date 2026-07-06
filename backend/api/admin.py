from django.contrib import admin
from .models import Department, Doctor, Appointment, TreatmentSupportDonation


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "icon",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "department",
        "specialization",
        "experience_years",
        "consultation_fee",
        "available_days",
        "available_time",
        "available_start_time",
        "available_end_time",
    )

    list_display_links = (
        "id",
        "name",
    )

    fields = (
        "department",
        "name",
        "specialization",
        "qualification",
        "experience_years",
        "consultation_fee",
        "available_days",
        "available_time",
        "available_start_time",
        "available_end_time",
        "image_url",
    )

    list_filter = (
        "department",
        "available_days",
    )

    search_fields = (
        "name",
        "specialization",
        "qualification",
        "department__name",
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "appointment_type",
        "patient_name",
        "phone",
        "doctor",
        "department",
        "appointment_date",
        "time_slot",
        "status",
        "user",
        "created_at",
    )

    list_display_links = (
        "id",
        "patient_name",
    )

    fields = (
        "user",
        "appointment_type",
        "doctor",
        "department",
        "patient_name",
        "age",
        "phone",
        "appointment_date",
        "time_slot",
        "reason",
        "cancellation_reason",
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    list_filter = (
        "appointment_type",
        "status",
        "department",
        "appointment_date",
    )

    search_fields = (
        "patient_name",
        "phone",
        "doctor__name",
        "department__name",
        "user__username",
    )


@admin.register(TreatmentSupportDonation)
class TreatmentSupportDonationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "donor_name",
        "phone",
        "email",
        "amount",
        "created_at",
    )

    list_display_links = (
        "id",
        "donor_name",
    )

    fields = (
        "donor_name",
        "email",
        "phone",
        "amount",
        "message",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    search_fields = (
        "donor_name",
        "phone",
        "email",
    )
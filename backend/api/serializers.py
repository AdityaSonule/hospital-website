from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Department, Doctor, Appointment, TreatmentSupportDonation

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"]
        )


class DepartmentSerializer(serializers.ModelSerializer):
    doctors_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ["id", "name", "description", "icon", "doctors_count"]

    def get_doctors_count(self, obj):
        return obj.doctors.count()


class DoctorSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source="department.name")

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "department",
            "department_name",
            "specialization",
            "qualification",
            "experience_years",
            "consultation_fee",
            "available_days",
            "available_time",
            "available_start_time",
            "available_end_time",
            "image_url",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    doctor_name = serializers.ReadOnlyField(source="doctor.name")
    department_name = serializers.ReadOnlyField(source="department.name")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "user",
            "appointment_type",
            "doctor",
            "doctor_name",
            "department",
            "department_name",
            "patient_name",
            "age",
            "phone",
            "appointment_date",
            "time_slot",
            "reason",
            "cancellation_reason",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def validate_age(self, value):
        if value <= 0 or value > 120:
            raise serializers.ValidationError("Enter a valid age.")
        return value

    def validate_phone(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

def validate(self, data):
    appointment_type = data.get("appointment_type")
    doctor = data.get("doctor")
    department = data.get("department")
    appointment_date = data.get("appointment_date")
    time_slot = data.get("time_slot")

    if appointment_type == "doctor":
        if not doctor:
            raise serializers.ValidationError("Doctor is required for doctor appointments.")

        if not department:
            raise serializers.ValidationError("Department is required for doctor appointments.")

        if doctor.department != department:
            raise serializers.ValidationError("Selected doctor does not belong to selected department.")

        day_map = {
            "Mon": 0,
            "Tue": 1,
            "Wed": 2,
            "Thu": 3,
            "Fri": 4,
            "Sat": 5,
            "Sun": 6,
        }

        doctor_days = [
            day.strip()
            for day in doctor.available_days.split(",")
            if day.strip()
        ]

        allowed_weekdays = [
            day_map[day]
            for day in doctor_days
            if day in day_map
        ]

        if appointment_date.weekday() not in allowed_weekdays:
            raise serializers.ValidationError(
                f"Doctor is only available on {doctor.available_days}."
            )

        if not doctor.available_start_time or not doctor.available_end_time:
            raise serializers.ValidationError("Doctor availability time is not configured.")

        if time_slot < doctor.available_start_time or time_slot >= doctor.available_end_time:
            raise serializers.ValidationError("Selected slot is outside doctor's available time.")

        if time_slot.minute % 15 != 0:
            raise serializers.ValidationError("Appointments must be booked in 15-minute slots.")

        slot_taken = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            time_slot=time_slot,
            status__in=["pending", "confirmed"],
        ).exists()

        if slot_taken:
            raise serializers.ValidationError("This slot is already booked.")

    return data
    
class TreatmentSupportDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentSupportDonation
        fields = [
            "id",
            "donor_name",
            "email",
            "phone",
            "amount",
            "message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Donation amount must be greater than 0.")
        return value
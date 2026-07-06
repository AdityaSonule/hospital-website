from datetime import datetime, timedelta

from rest_framework import generics, viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Department, Doctor, Appointment, TreatmentSupportDonation
from .serializers import (
    RegisterSerializer,
    DepartmentSerializer,
    DoctorSerializer,
    AppointmentSerializer,
    TreatmentSupportDonationSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.select_related("department").all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "specialization", "department__name"]


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TreatmentSupportDonationViewSet(viewsets.ModelViewSet):
    queryset = TreatmentSupportDonation.objects.all().order_by("-created_at")
    serializer_class = TreatmentSupportDonationSerializer
    permission_classes = [AllowAny]

@api_view(["GET"])
@permission_classes([AllowAny])
def available_slots(request):
    try:
        doctor_id = request.query_params.get("doctor")
        date_value = request.query_params.get("date")

        if not doctor_id or not date_value:
            return Response(
                {"error": "doctor and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doctor = Doctor.objects.filter(id=doctor_id).first()

        if not doctor:
            return Response(
                {
                    "error": "Doctor not found",
                    "received_doctor_id": doctor_id,
                    "existing_doctor_ids": list(
                        Doctor.objects.values_list("id", flat=True)
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doctor.available_start_time or not doctor.available_end_time:
            return Response(
                {
                    "error": "Doctor availability time is not configured",
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.name,
                    "available_start_time": str(doctor.available_start_time),
                    "available_end_time": str(doctor.available_end_time),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        day_map = {
            "Mon": 0,
            "Monday": 0,
            "Tue": 1,
            "Tuesday": 1,
            "Wed": 2,
            "Wednesday": 2,
            "Thu": 3,
            "Thursday": 3,
            "Fri": 4,
            "Friday": 4,
            "Sat": 5,
            "Saturday": 5,
            "Sun": 6,
            "Sunday": 6,
        }

        doctor_days = [
            day.strip()
            for day in (doctor.available_days or "").split(",")
            if day.strip()
        ]

        allowed_weekdays = [
            day_map[day]
            for day in doctor_days
            if day in day_map
        ]

        if allowed_weekdays and appointment_date.weekday() not in allowed_weekdays:
            return Response(
                {
                    "error": f"Doctor is only available on {doctor.available_days}.",
                    "selected_date": date_value,
                    "selected_weekday_number": appointment_date.weekday(),
                    "allowed_weekday_numbers": allowed_weekdays,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_datetime = datetime.combine(
            appointment_date,
            doctor.available_start_time,
        )

        end_datetime = datetime.combine(
            appointment_date,
            doctor.available_end_time,
        )

        if start_datetime >= end_datetime:
            return Response(
                {"error": "Doctor end time must be after start time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booked_slots = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=["pending", "confirmed"],
        ).values_list("time_slot", flat=True)

        booked_slot_strings = set()

        for booked_slot in booked_slots:
            if booked_slot is None:
                continue

            if hasattr(booked_slot, "strftime"):
                booked_slot_strings.add(booked_slot.strftime("%H:%M"))
            else:
                booked_slot_strings.add(str(booked_slot)[:5])

        slots = []
        current = start_datetime

        while current < end_datetime:
            slot_value = current.time().strftime("%H:%M")

            if slot_value not in booked_slot_strings:
                slots.append(
                    {
                        "value": slot_value,
                        "label": current.strftime("%I:%M %p"),
                    }
                )

            current += timedelta(minutes=15)

        return Response(slots)

    except Exception as error:
        return Response(
            {
                "error": str(error),
                "message": "Unexpected error while generating slots.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        doctor_id = request.query_params.get("doctor")
        date_value = request.query_params.get("date")

        if not doctor_id or not date_value:
            return Response(
                {"error": "doctor and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doctor = Doctor.objects.filter(id=doctor_id).first()

        if not doctor:
            return Response(
                {
                    "error": "Doctor not found",
                    "received_doctor_id": doctor_id,
                    "existing_doctor_ids": list(
                        Doctor.objects.values_list("id", flat=True)
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doctor.available_start_time or not doctor.available_end_time:
            return Response(
                {
                    "error": "Doctor availability time is not configured",
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.name,
                    "available_start_time": str(doctor.available_start_time),
                    "available_end_time": str(doctor.available_end_time),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        day_map = {
            "Mon": 0,
            "Monday": 0,
            "Tue": 1,
            "Tuesday": 1,
            "Wed": 2,
            "Wednesday": 2,
            "Thu": 3,
            "Thursday": 3,
            "Fri": 4,
            "Friday": 4,
            "Sat": 5,
            "Saturday": 5,
            "Sun": 6,
            "Sunday": 6,
        }

        available_days_text = doctor.available_days or ""

        doctor_days = [
            day.strip()
            for day in available_days_text.split(",")
            if day.strip()
        ]

        allowed_weekdays = [
            day_map[day]
            for day in doctor_days
            if day in day_map
        ]

        if allowed_weekdays and appointment_date.weekday() not in allowed_weekdays:
            return Response(
                {
                    "error": f"Doctor is only available on {doctor.available_days}.",
                    "selected_date": date_value,
                    "selected_weekday_number": appointment_date.weekday(),
                    "allowed_weekday_numbers": allowed_weekdays,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_datetime = datetime.combine(
            appointment_date,
            doctor.available_start_time,
        )

        end_datetime = datetime.combine(
            appointment_date,
            doctor.available_end_time,
        )

        if start_datetime >= end_datetime:
            return Response(
                {"error": "Doctor end time must be after start time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booked_slots = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=["pending", "confirmed"],
        ).values_list("time_slot", flat=True)

        booked_slot_strings = set()

        for booked_slot in booked_slots:
            if booked_slot is None:
                continue

            if hasattr(booked_slot, "strftime"):
                booked_slot_strings.add(booked_slot.strftime("%H:%M"))
            else:
                booked_slot_strings.add(str(booked_slot)[:5])

        slots = []
        current = start_datetime

        while current < end_datetime:
            slot_value = current.time().strftime("%H:%M")

            if slot_value not in booked_slot_strings:
                slots.append(
                    {
                        "value": slot_value,
                        "label": current.strftime("%I:%M %p"),
                    }
                )

            current += timedelta(minutes=15)

        return Response(slots)

    except Exception as error:
        return Response(
            {
                "error": str(error),
                "message": "Unexpected error while generating slots.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        doctor_id = request.query_params.get("doctor")
        date_value = request.query_params.get("date")

        if not doctor_id or not date_value:
            return Response(
                {"error": "doctor and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doctor.available_start_time or not doctor.available_end_time:
            return Response(
                {"error": "Doctor availability time is not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment_date = dt.datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        day_map = {
            "Mon": 0,
            "Monday": 0,
            "Tue": 1,
            "Tuesday": 1,
            "Wed": 2,
            "Wednesday": 2,
            "Thu": 3,
            "Thursday": 3,
            "Fri": 4,
            "Friday": 4,
            "Sat": 5,
            "Saturday": 5,
            "Sun": 6,
            "Sunday": 6,
        }

        available_days_text = doctor.available_days or ""

        doctor_days = [
            day.strip()
            for day in available_days_text.split(",")
            if day.strip()
        ]

        allowed_weekdays = []

        for day in doctor_days:
            if day in day_map:
                allowed_weekdays.append(day_map[day])

        if allowed_weekdays and appointment_date.weekday() not in allowed_weekdays:
            return Response(
                {
                    "error": f"Doctor is only available on {doctor.available_days}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_time = doctor.available_start_time
        end_time = doctor.available_end_time

        if isinstance(start_time, str):
            start_time = dt.datetime.strptime(start_time[:5], "%H:%M").time()

        if isinstance(end_time, str):
            end_time = dt.datetime.strptime(end_time[:5], "%H:%M").time()

        start_datetime = dt.datetime.combine(appointment_date, start_time)
        end_datetime = dt.datetime.combine(appointment_date, end_time)

        if start_datetime >= end_datetime:
            return Response(
                {"error": "Doctor end time must be after start time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booked_slots_raw = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=["pending", "confirmed"],
        ).values_list("time_slot", flat=True)

        booked_slot_strings = set()

        for slot in booked_slots_raw:
            if slot is None:
                continue

            if hasattr(slot, "strftime"):
                booked_slot_strings.add(slot.strftime("%H:%M"))
            else:
                booked_slot_strings.add(str(slot)[:5])

        slots = []
        current = start_datetime

        while current < end_datetime:
            slot_value = current.time().strftime("%H:%M")

            if slot_value not in booked_slot_strings:
                slots.append(
                    {
                        "value": slot_value,
                        "label": current.strftime("%I:%M %p"),
                    }
                )

            current += dt.timedelta(minutes=15)

        return Response(slots)

    except Exception as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        doctor_id = request.query_params.get("doctor")
        date_value = request.query_params.get("date")

        if not doctor_id or not date_value:
            return Response(
                {"error": "doctor and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doctor.available_start_time or not doctor.available_end_time:
            return Response(
                {"error": "Doctor availability time is not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            appointment_date = dt.datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        day_map = {
            "Mon": 0,
            "Monday": 0,
            "Tue": 1,
            "Tuesday": 1,
            "Wed": 2,
            "Wednesday": 2,
            "Thu": 3,
            "Thursday": 3,
            "Fri": 4,
            "Friday": 4,
            "Sat": 5,
            "Saturday": 5,
            "Sun": 6,
            "Sunday": 6,
        }

        available_days_text = doctor.available_days or ""

        doctor_days = [
            day.strip()
            for day in available_days_text.split(",")
            if day.strip()
        ]

        allowed_weekdays = []

        for day in doctor_days:
            if day in day_map:
                allowed_weekdays.append(day_map[day])

        if allowed_weekdays and appointment_date.weekday() not in allowed_weekdays:
            return Response(
                {
                    "error": f"Doctor is only available on {doctor.available_days}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_time = doctor.available_start_time
        end_time = doctor.available_end_time

        if isinstance(start_time, str):
            start_time = dt.datetime.strptime(start_time[:5], "%H:%M").time()

        if isinstance(end_time, str):
            end_time = dt.datetime.strptime(end_time[:5], "%H:%M").time()

        start_datetime = dt.datetime.combine(appointment_date, start_time)
        end_datetime = dt.datetime.combine(appointment_date, end_time)

        if start_datetime >= end_datetime:
            return Response(
                {"error": "Doctor end time must be after start time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booked_slots_raw = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=["pending", "confirmed"],
        ).values_list("time_slot", flat=True)

        booked_slot_strings = set()

        for slot in booked_slots_raw:
            if slot is None:
                continue

            if hasattr(slot, "strftime"):
                booked_slot_strings.add(slot.strftime("%H:%M"))
            else:
                booked_slot_strings.add(str(slot)[:5])

        slots = []
        current = start_datetime

        while current < end_datetime:
            slot_value = current.time().strftime("%H:%M")

            if slot_value not in booked_slot_strings:
                slots.append(
                    {
                        "value": slot_value,
                        "label": current.strftime("%I:%M %p"),
                    }
                )

            current += dt.timedelta(minutes=15)

        return Response(slots)

    except Exception as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
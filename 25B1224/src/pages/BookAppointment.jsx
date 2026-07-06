import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import axiosInstance from "../api/axiosInstance";

function BookAppointment() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();

  const initialType = searchParams.get("type") || "doctor";

  const [appointmentType, setAppointmentType] = useState(initialType);
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [department, setDepartment] = useState("");
  const [doctor, setDoctor] = useState("");
  const [appointmentDate, setAppointmentDate] = useState("");
  const [timeSlot, setTimeSlot] = useState("");
  const [availableSlots, setAvailableSlots] = useState([]);
  const [slotMessage, setSlotMessage] = useState("");

  useEffect(() => {
    async function loadInitialData() {
      try {
        const departmentsResponse = await axiosInstance.get("/departments/");
        const doctorsResponse = await axiosInstance.get("/doctors/");

        const departmentsData = Array.isArray(departmentsResponse.data)
          ? departmentsResponse.data
          : departmentsResponse.data.results || [];

        const doctorsData = Array.isArray(doctorsResponse.data)
          ? doctorsResponse.data
          : doctorsResponse.data.results || [];

        setDepartments(departmentsData);
        setDoctors(doctorsData);
      } catch (error) {
        console.error("Initial data load error:", error);
      }
    }

    loadInitialData();
  }, []);

  const filteredDoctors = doctors.filter((doctorItem) => {
    if (!department) return false;
    return String(doctorItem.department) === String(department);
  });

  const selectedDoctor = doctors.find(
    (doctorItem) => String(doctorItem.id) === String(doctor)
  );

  useEffect(() => {
    async function loadSlots() {
      setAvailableSlots([]);
      setSlotMessage("");
      setTimeSlot("");

      if (!appointmentDate) {
        return;
      }

      if (appointmentType !== "doctor") {
        setAvailableSlots([
          { value: "09:00", label: "09:00 AM" },
          { value: "09:15", label: "09:15 AM" },
          { value: "09:30", label: "09:30 AM" },
          { value: "09:45", label: "09:45 AM" },
          { value: "10:00", label: "10:00 AM" },
          { value: "10:15", label: "10:15 AM" },
          { value: "10:30", label: "10:30 AM" },
          { value: "10:45", label: "10:45 AM" },
          { value: "11:00", label: "11:00 AM" },
          { value: "11:15", label: "11:15 AM" },
          { value: "11:30", label: "11:30 AM" },
          { value: "11:45", label: "11:45 AM" },
        ]);
        return;
      }

      if (!doctor) {
        return;
      }

      try {
        console.log("Fetching slots for:", {
          doctor,
          appointmentDate,
          url: `/available-slots/?doctor=${doctor}&date=${appointmentDate}`,
        });
        const response = await axiosInstance.get(
          `/available-slots/?doctor=${doctor}&date=${appointmentDate}`
        );

        const slots = Array.isArray(response.data) ? response.data : [];
        setAvailableSlots(slots);

        if (slots.length === 0) {
          setSlotMessage("No slots available for the selected date.");
        }
      } catch (error) {
        console.error("Slots error:", error.response?.data || error);

        const message =
          error.response?.data?.error ||
          "No slots available for the selected date.";

        setSlotMessage(message);
      }
    }

    loadSlots();
  }, [appointmentType, doctor, appointmentDate]);

  function handleAppointmentTypeChange(event) {
    const value = event.target.value;

    setAppointmentType(value);
    setDepartment("");
    setDoctor("");
    setAppointmentDate("");
    setTimeSlot("");
    setAvailableSlots([]);
    setSlotMessage("");
  }

  function handleDepartmentChange(event) {
    const value = event.target.value;

    setDepartment(value);
    setDoctor("");
    setTimeSlot("");
    setAvailableSlots([]);
    setSlotMessage("");
  }

  function handleDoctorChange(event) {
    const value = event.target.value;

    setDoctor(value);
    setTimeSlot("");
    setAvailableSlots([]);
    setSlotMessage("");
  }

  function handleDateChange(event) {
    const value = event.target.value;

    setAppointmentDate(value);
    setTimeSlot("");
    setAvailableSlots([]);
    setSlotMessage("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const token = localStorage.getItem("accessToken");

    if (!token) {
      alert("Please login before booking a service.");

      const currentPage = location.pathname + location.search;
      navigate(`/login?next=${encodeURIComponent(currentPage)}`);

      return;
    }

    const formData = new FormData(event.currentTarget);

    const patientName = formData.get("patient_name");
    const age = formData.get("age");
    const phone = formData.get("phone");
    const reason = formData.get("reason");

    if (!patientName || !age || !phone || !appointmentDate) {
      alert("Please fill all required details.");
      return;
    }

    if (!timeSlot) {
      alert("Please select an available time slot.");
      return;
    }

    if (appointmentType === "doctor" && (!department || !doctor)) {
      alert("Please select department and doctor.");
      return;
    }

    try {
      const payload = {
        appointment_type: appointmentType,
        patient_name: patientName,
        age: Number(age),
        phone: phone,
        appointment_date: appointmentDate,
        time_slot: timeSlot,
        reason: reason || "",
      };

      if (appointmentType === "doctor") {
        payload.department = Number(department);
        payload.doctor = Number(doctor);
      } else {
        payload.department = null;
        payload.doctor = null;
      }

      await axiosInstance.post("/appointments/", payload);

      alert("Booking submitted successfully. You can view it in My Appointments.");

      event.currentTarget.reset();

      setAppointmentType("doctor");
      setDepartment("");
      setDoctor("");
      setAppointmentDate("");
      setTimeSlot("");
      setAvailableSlots([]);
      setSlotMessage("");
    } catch (error) {
      console.error("Booking error:", error.response?.data || error);

      const backendError =
        error.response?.data?.non_field_errors?.[0] ||
        error.response?.data?.detail ||
        "Booking failed. Please check the selected details and login status.";

      alert(backendError);
    }
  }

  return (
    <section className="form-page">
      <form className="form-card wide" onSubmit={handleSubmit}>
        <h1>Book a Service</h1>

        <p className="form-subtitle">
          Book doctor appointments, body checkups, blood donation, or organ
          donation counselling.
        </p>

        <select
          name="appointment_type"
          value={appointmentType}
          onChange={handleAppointmentTypeChange}
          required
        >
          <option value="doctor">Doctor Appointment</option>
          <option value="body_checkup">Body Checkup</option>
          <option value="blood_donation">Blood Donation</option>
          <option value="organ_donation">Organ Donation Counselling</option>
        </select>

        <input
          name="patient_name"
          placeholder="Full name"
          required
        />

        <input
          name="age"
          type="number"
          placeholder="Age"
          required
        />

        <input
          name="phone"
          placeholder="Phone number"
          required
        />

        {appointmentType === "doctor" && (
          <>
            <select
              name="department"
              value={department}
              onChange={handleDepartmentChange}
              required
            >
              <option value="">Select department</option>

              {departments.map((departmentItem) => (
                <option value={departmentItem.id} key={departmentItem.id}>
                  {departmentItem.name}
                </option>
              ))}
            </select>

            <select
              name="doctor"
              value={doctor}
              onChange={handleDoctorChange}
              required
              disabled={!department}
            >
              <option value="">
                {department ? "Select doctor" : "Select department first"}
              </option>

              {filteredDoctors.map((doctorItem) => (
                <option value={doctorItem.id} key={doctorItem.id}>
                  {doctorItem.name} - {doctorItem.specialization}
                </option>
              ))}
            </select>

            {selectedDoctor && (
              <p className="doctor-availability-note">
                Available on: {selectedDoctor.available_days} | Time:{" "}
                {selectedDoctor.available_time}
              </p>
            )}
          </>
        )}

        <input
          name="appointment_date"
          type="date"
          value={appointmentDate}
          onChange={handleDateChange}
          required
        />

        {slotMessage && <p className="slot-message">{slotMessage}</p>}

        <select
          name="time_slot"
          value={timeSlot}
          onChange={(event) => setTimeSlot(event.target.value)}
          required
          disabled={!appointmentDate || availableSlots.length === 0}
        >
          <option value="">
            {availableSlots.length === 0
              ? "No slots available"
              : "Select available slot"}
          </option>

          {availableSlots.map((slot) => (
            <option value={slot.value} key={slot.value}>
              {slot.label}
            </option>
          ))}
        </select>

        <textarea
          name="reason"
          placeholder={
            appointmentType === "doctor"
              ? "Reason for visit"
              : "Additional details"
          }
        />

        <button className="primary-button">Submit Booking</button>
      </form>
    </section>
  );
}

export default BookAppointment;
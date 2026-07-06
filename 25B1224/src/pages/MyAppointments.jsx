import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../api/axiosInstance";

function MyAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const navigate = useNavigate();

  async function loadAppointments() {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      setLoading(false);
      alert("Please login to view your appointments.");
      navigate("/login?next=/my-appointments");
      return;
    }

    try {
      setLoading(true);
      setErrorMessage("");

      const response = await axiosInstance.get("/appointments/");

      const data = Array.isArray(response.data)
        ? response.data
        : response.data.results || [];

      setAppointments(data);
    } catch (error) {
      console.error("Appointments loading error:", error.response?.data || error);

      setErrorMessage(
        "Could not load appointments. Please logout, login again, and try once more."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAppointments();
  }, []);

  async function cancelAppointment(id) {
    const reason = window.prompt(
      "Please enter the reason for cancelling this appointment:"
    );

    if (reason === null) {
      return;
    }

    if (!reason.trim()) {
      alert("Cancellation reason is required.");
      return;
    }

    try {
      await axiosInstance.patch(`/appointments/${id}/`, {
        status: "cancelled",
        cancellation_reason: reason.trim(),
      });

      alert("Appointment cancelled.");
      loadAppointments();
    } catch (error) {
      console.error("Cancel appointment error:", error.response?.data || error);
      alert("Could not cancel appointment.");
    }
  }

  function formatServiceType(type) {
    if (type === "doctor") return "Doctor Appointment";
    if (type === "body_checkup") return "Body Checkup";
    if (type === "blood_donation") return "Blood Donation";
    if (type === "organ_donation") return "Organ Donation Counselling";
    return type;
  }

  if (loading) {
    return <p className="page-padding">Loading appointments...</p>;
  }

  return (
    <section className="page-padding">
      <h1>My Appointments</h1>
      <p>View your booked appointments and service requests.</p>

      {errorMessage && (
        <div className="empty-message">
          <p>{errorMessage}</p>
          <button
            className="primary-button small"
            onClick={() => {
              localStorage.clear();
              navigate("/login?next=/my-appointments");
            }}
          >
            Login Again
          </button>
        </div>
      )}

      {!errorMessage && appointments.length === 0 ? (
        <p className="empty-message">No appointments found.</p>
      ) : (
        <div className="grid">
          {appointments.map((appointment) => (
            <div className="card" key={appointment.id}>
              <h3>{appointment.patient_name}</h3>

              <p>
                <strong>Service:</strong>{" "}
                {formatServiceType(appointment.appointment_type)}
              </p>

              {appointment.doctor_name && (
                <p>
                  <strong>Doctor:</strong> {appointment.doctor_name}
                </p>
              )}

              {appointment.department_name && (
                <p>
                  <strong>Department:</strong> {appointment.department_name}
                </p>
              )}

              <p>
                <strong>Date:</strong> {appointment.appointment_date}
              </p>

              <p>
                <strong>Time:</strong> {appointment.time_slot}
              </p>

              <p>
                <strong>Status:</strong> {appointment.status}
              </p>
                {appointment.status === "cancelled" && appointment.cancellation_reason && (
                  <p>
                    <strong>Cancellation reason:</strong> {appointment.cancellation_reason}
                  </p>
              )}

              {appointment.reason && (
                <p>
                  <strong>Reason:</strong> {appointment.reason}
                </p>
              )}

              {appointment.status !== "cancelled" && (
                <button
                  className="danger-button"
                  onClick={() => cancelAppointment(appointment.id)}
                >
                  Cancel Appointment
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default MyAppointments;
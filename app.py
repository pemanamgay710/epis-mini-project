import streamlit as st
from db.connection import get_connection
from auth import auth
from dashboard import doctor, patient, nurse, lab_technician, receptionist

conn = get_connection()

# Initialize Session State 
if "page" not in st.session_state:
    st.session_state["page"] = "role_selection"  # starting page
if "selected_role" not in st.session_state:
    st.session_state["selected_role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None


# Page Functions 
def role_selection_page():
    st.title("ePIS Hospital Management System")
    st.write("Select your role:")
    roles = ["Patient", "Doctor", "Nurse", "Lab_Tech", "Receptionist"]

    cols = st.columns(len(roles))
    for i, role in enumerate(roles):
        if cols[i].button(role):
            st.session_state["selected_role"] = role.lower()
            st.session_state["page"] = "login_page"



def login_page(conn):
    # --- Top Header with Back Button ---
    col1, col2 = st.columns([6, 1])
    with col1:
        pass
    with col2:
        if st.button("Dashboard"):
            st.session_state["selected_role"] = None
            st.session_state["page"] = "role_selection"
            st.rerun()

    # --- Login Form ---
    auth.login_form(conn, st.session_state["selected_role"])

    st.markdown("---")
    if st.button("Sign Up Instead"):
        st.session_state["page"] = "signup_page"


def signup_page(conn):
    # --- Top Header with Back Button ---
    col1, col2 = st.columns([6, 1])
    with col1:
        pass
    with col2:
        if st.button("Dashboard"):
            st.session_state["selected_role"] = None
            st.session_state["page"] = "role_selection"
            st.rerun()

    # --- Signup Form ---
    auth.signup_form(conn, st.session_state["selected_role"])

    st.markdown("---")
    if st.button("Back to Login"):
        st.session_state["page"] = "login_page"


def dashboard_page(conn):
    user = st.session_state["user"]
    if user["role"] == "doctor":
        doctor.doctor_dashboard(conn)
    elif user["role"] == "patient":
        patient.patient_dashboard(conn)
    elif user["role"] == "nurse":
        nurse.nurse_dashboard(conn)
    elif user["role"] == "lab_tech":
        lab_technician.lab_technician_dashboard(conn)  
    elif user["role"] == "receptionist":
        receptionist.receptionist_dashboard(conn)


# Page Routing
if st.session_state["page"] == "role_selection":
    role_selection_page()
elif st.session_state["page"] == "login_page":
    login_page(conn)
elif st.session_state["page"] == "signup_page":
    signup_page(conn)
elif st.session_state["user"]:  # logged-in users
    dashboard_page(conn)

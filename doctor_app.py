"""
Streamlit Frontend for Doctor Interface
Clinical Health System
"""

import streamlit as st
import requests
# import json
from datetime import datetime
# import pandas as pd

# API Base URL
API_BASE = "http://localhost:5000/api"

# Page configuration
st.set_page_config(
    page_title="Clinical Health System - Doctor Portal",
    page_icon="stethoscope",
    layout="wide"
)

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# ==================== API FUNCTIONS ====================

def api_call(method, endpoint, data=None, params=None):
    """Make API call"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the server. Please make sure the Flask API is running.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# ==================== AUTHENTICATION PAGES ====================

def login_page():
    """Login page"""
    st.title("Doctor Login")
    st.write("Enter your credentials to login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if email and password:
                result = api_call("POST", "/login", {"email": email, "password": password})
                
                if result:
                    user = result['user']
                    if user['user_type'] == 'doctor':
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("This portal is for doctors only. Please use the patient portal.")
            else:
                st.error("Please fill all fields")

def signup_page():
    """Signup page"""
    st.title("Doctor Registration")
    st.write("Create a new doctor account")
    
    with st.form("signup_form"):
        st.subheader("Personal Information")
        name = st.text_input("Full Name", placeholder="Dr. John Smith")
        email = st.text_input("Email", placeholder="doctor@clinic.com")
        phone_no = st.text_input("Phone Number", placeholder="+1-555-0123")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        st.subheader("Professional Information")
        specialization = st.text_input("Specialization", placeholder="e.g., Cardiology, Neurology")
        consultancy = st.number_input("Consultancy Fee ($)", min_value=0.0, step=10.0, value=150.0)
        
        st.subheader("Available Time Slots")
        st.write("Enter comma-separated time slots (e.g., 09:00,10:00,11:00,14:00,15:00)")
        available_slots = st.text_input("Time Slots", placeholder="09:00,10:00,11:00,14:00,15:00,16:00")
        
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if all([name, email, phone_no, password, confirm_password, specialization, consultancy, available_slots]):
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    data = {
                        "name": name,
                        "email": email,
                        "phone_no": phone_no,
                        "password": password,
                        "user_type": "doctor",
                        "specialization": specialization,
                        "consultancy": consultancy,
                        "available_slots": available_slots
                    }
                    
                    result = api_call("POST", "/signup", data)
                    
                    if result:
                        st.success("Registration successful! Please login.")
            else:
                st.error("Please fill all fields")

# ==================== MAIN APP PAGES ====================

def dashboard_page():
    """Doctor dashboard"""
    st.title(f"Welcome, Dr. {st.session_state.user['name']}!")
    st.write("Doctor Dashboard")
    
    # Get doctor profile
    profile_result = api_call("GET", f"/doctor/profile", params={"user_id": st.session_state.user['user_id']})
    
    if profile_result:
        profile = profile_result['profile']
        
        # Profile summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Specialization", profile['specialization'])
        
        with col2:
            st.metric("Consultancy Fee", f"${profile['consultancy']}")
        
        with col3:
            st.metric("Profile Status", profile['profile_status'])
        
        # Profile details
        st.subheader("Profile Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Email:** {profile['email']}")
            st.write(f"**Specialization:** {profile['specialization']}")
        
        with col2:
            st.write(f"**Consultancy Fee:** ${profile['consultancy']}")
            st.write(f"**Available Slots:** {profile['available_slots']}")
    
    # Get doctor appointments
    appointments_result = api_call("GET", f"/appointments/doctor/{st.session_state.user['user_id']}")
    
    if appointments_result:
        appointments = appointments_result['appointments']
        
        # Appointment summary
        st.subheader("Appointment Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_appointments = len(appointments)
            st.metric("Total Appointments", total_appointments)
        
        with col2:
            booked = len([a for a in appointments if a['status'] == 'Booked'])
            st.metric("Booked", booked)
        
        with col3:
            completed = len([a for a in appointments if a['status'] == 'Completed'])
            st.metric("Completed", completed)
        
        # Today's appointments
        today = datetime.now().strftime("%Y-%m-%d")
        today_appointments = [a for a in appointments if a['date'] == today and a['status'] == 'Booked']
        
        if today_appointments:
            st.subheader(f"Today's Appointments ({len(today_appointments)})")
            
            for appointment in today_appointments:
                with st.expander(f"{appointment['time']} - {appointment['patient_name']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Patient:** {appointment['patient_name']}")
                        st.write(f"**Email:** {appointment['patient_email']}")
                        st.write(f"**Phone:** {appointment['patient_phone']}")
                        st.write(f"**Time:** {appointment['time']}")
                        if appointment.get('problem_description'):
                            st.write(f"**Problem:** {appointment['problem_description']}")
                    
                    with col2:
                        if st.button("Start Consultation", key=f"consult_{appointment['appointment_id']}"):
                            st.session_state.selected_appointment = appointment
                            st.session_state.show_consultation = True
        else:
            st.info("No appointments scheduled for today")

def appointments_page():
    """View and manage appointments"""
    st.title("My Appointments")
    st.write("View and manage your appointments")
    
    appointments_result = api_call("GET", f"/appointments/doctor/{st.session_state.user['user_id']}")
    
    if appointments_result:
        appointments = appointments_result['appointments']
        
        if appointments:
            # Filter by status
            status_filter = st.selectbox("Filter by Status", ["All", "Booked", "Completed", "Cancelled"])
            
            if status_filter != "All":
                appointments = [a for a in appointments if a['status'] == status_filter]
            
            # Sort by date and time
            appointments.sort(key=lambda x: (x['date'], x['time']))
            
            # Display appointments
            for appointment in appointments:
                with st.expander(f"Appointment #{appointment['appointment_id']} - {appointment['date']} {appointment['time']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Patient:** {appointment['patient_name']}")
                        st.write(f"**Email:** {appointment['patient_email']}")
                        st.write(f"**Phone:** {appointment['patient_phone']}")
                        st.write(f"**Date:** {appointment['date']}")
                        st.write(f"**Time:** {appointment['time']}")
                        st.write(f"**Status:** {appointment['status']}")
                        if appointment.get('problem_description'):
                            st.write(f"**Problem:** {appointment['problem_description']}")
                    
                    with col2:
                        # Check payment status
                        payment_result = api_call("GET", f"/payments/appointment/{appointment['appointment_id']}")
                        
                        if payment_result:
                            st.write(f"**Payment:** ${payment_result['payment']['amount']}")
                            st.write(f"**Mode:** {payment_result['payment']['mode']}")
                            
                            # Start consultation button for paid appointments
                            if appointment['status'] == 'Booked':
                                if st.button("Start Consultation", key=f"consult_{appointment['appointment_id']}"):
                                    st.session_state.selected_appointment = appointment
                                    st.session_state.show_consultation = True
                        else:
                            st.write("**Payment:** Pending")
                            st.info("Consultation cannot be started until payment is completed")
        else:
            st.info("No appointments found")

def consultation_page():
    """Complete consultation"""
    if not st.session_state.get('show_consultation', False):
        st.warning("No appointment selected for consultation")
        return
    
    appointment = st.session_state.selected_appointment
    
    st.title("Complete Consultation")
    st.write(f"Consultation for {appointment['patient_name']}")
    
    # Appointment details
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Patient:** {appointment['patient_name']}")
        st.write(f"**Email:** {appointment['patient_email']}")
        st.write(f"**Phone:** {appointment['patient_phone']}")
    
    with col2:
        st.write(f"**Date:** {appointment['date']}")
        st.write(f"**Time:** {appointment['time']}")
        st.write(f"**Appointment ID:** {appointment['appointment_id']}")
    
    # Show problem description if available
    if appointment.get('problem_description'):
        st.subheader("Patient's Problem Description")
        st.info(appointment['problem_description'])
    
    # Consultation form
    with st.form("consultation_form"):
        st.subheader("Consultation Details")
        
        notes = st.text_area(
            "Consultation Notes",
            placeholder="Enter detailed notes about the patient's condition, symptoms, diagnosis, etc.",
            height=200
        )
        
        prescription = st.text_area(
            "Prescription",
            placeholder="Enter prescription details, medications, dosage, instructions, etc.",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button("Complete Consultation")
        
        with col2:
            cancel_button = st.form_submit_button("Cancel")
        
        if submit_button:
            if notes and prescription:
                consultation_data = {
                    "appointment_id": appointment['appointment_id'],
                    "doctor_id": st.session_state.user['user_id'],
                    "notes": notes,
                    "prescription": prescription
                }
                
                result = api_call("POST", "/consultations", consultation_data)
                
                if result:
                    st.success("Consultation completed successfully!")
                    st.session_state.show_consultation = False
                    st.rerun()
            else:
                st.error("Please fill both notes and prescription fields")
        
        if cancel_button:
            st.session_state.show_consultation = False
            st.rerun()

def profile_page():
    """View and manage profile"""
    st.title("My Profile")
    st.write("View and manage your doctor profile")
    
    # Get doctor profile
    profile_result = api_call("GET", f"/doctor/profile", params={"user_id": st.session_state.user['user_id']})
    
    if profile_result:
        profile = profile_result['profile']
        
        # Profile information
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** Dr. {profile['name']}")
            st.write(f"**Email:** {profile['email']}")
        
        with col2:
            st.write(f"**Specialization:** {profile['specialization']}")
            st.write(f"**Profile Status:** {profile['profile_status']}")
        
        st.subheader("Professional Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Consultancy Fee:** ${profile['consultancy']}")
            st.metric("Consultancy Fee", f"${profile['consultancy']}")
        
        with col2:
            st.write(f"**Available Time Slots:**")
            slots = profile['available_slots'].split(',')
            for slot in slots:
                st.write(f"  - {slot.strip()}")
        
        # Statistics
        st.subheader("Practice Statistics")
        
        appointments_result = api_call("GET", f"/appointments/doctor/{st.session_state.user['user_id']}")
        
        if appointments_result:
            appointments = appointments_result['appointments']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_appointments = len(appointments)
                st.metric("Total Appointments", total_appointments)
            
            with col2:
                completed = len([a for a in appointments if a['status'] == 'Completed'])
                st.metric("Completed Consultations", completed)
            
            with col3:
                if total_appointments > 0:
                    completion_rate = (completed / total_appointments) * 100
                    st.metric("Completion Rate", f"{completion_rate:.1f}%")
                else:
                    st.metric("Completion Rate", "0%")

# ==================== MAIN APP ====================

def main():
    """Main application"""
    # Sidebar navigation
    if st.session_state.logged_in:
        st.sidebar.title(f"Doctor Portal")
        st.sidebar.write(f"Welcome, Dr. {st.session_state.user['name']}")
        
        page = st.sidebar.selectbox("Navigate", [
            "Dashboard",
            "Appointments",
            "Profile"
        ])
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.show_consultation = False
            st.rerun()
    else:
        st.sidebar.title("Clinical Health System")
        page = st.sidebar.selectbox("Navigate", ["Login", "Sign Up"])
    
    # Page routing
    if not st.session_state.logged_in:
        if page == "Login":
            login_page()
        elif page == "Sign Up":
            signup_page()
    else:
        if page == "Dashboard":
            dashboard_page()
        elif page == "Appointments":
            appointments_page()
        elif page == "Profile":
            profile_page()
    
    # Show consultation modal if active
    if st.session_state.get('show_consultation', False):
        consultation_page()

if __name__ == "__main__":
    main()

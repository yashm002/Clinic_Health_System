"""
Streamlit Frontend for Patient Interface
Clinical Health System
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd

# API Base URL
API_BASE = "http://localhost:5000/api"

# Page configuration
st.set_page_config(
    page_title="Clinical Health System - Patient Portal",
    page_icon="hospital",
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
    st.title("Patient Login")
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
                    if user['user_type'] == 'patient':
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("This portal is for patients only. Please use the doctor portal.")
            else:
                st.error("Please fill all fields")

def signup_page():
    """Signup page"""
    st.title("Patient Registration")
    st.write("Create a new patient account")
    
    with st.form("signup_form"):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email")
        phone_no = st.text_input("Phone Number", placeholder="Enter your phone number")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if name and email and phone_no and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    data = {
                        "name": name,
                        "email": email,
                        "phone_no": phone_no,
                        "password": password,
                        "user_type": "patient"
                    }
                    
                    result = api_call("POST", "/signup", data)
                    
                    if result:
                        st.success("Registration successful! Please login.")
            else:
                st.error("Please fill all fields")

# ==================== MAIN APP PAGES ====================

def dashboard_page():
    """Patient dashboard"""
    st.title(f"Welcome, {st.session_state.user['name']}!")
    st.write("Patient Dashboard")
    
    # Get patient appointments
    appointments_result = api_call("GET", f"/appointments/patient/{st.session_state.user['user_id']}")
    
    if appointments_result:
        appointments = appointments_result['appointments']
        
        # Summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_appointments = len(appointments)
            st.metric("Total Appointments", total_appointments)
        
        with col2:
            upcoming = len([a for a in appointments if a['status'] == 'Booked'])
            st.metric("Upcoming", upcoming)
        
        with col3:
            completed = len([a for a in appointments if a['status'] == 'Completed'])
            st.metric("Completed", completed)
        
        # Recent appointments
        if appointments:
            st.subheader("Recent Appointments")
            
            df = pd.DataFrame(appointments)
            df = df[['appointment_id', 'doctor_name', 'specialization', 'date', 'time', 'status']]
            df.columns = ['ID', 'Doctor', 'Specialization', 'Date', 'Time', 'Status']
            
            # Status color coding
            def color_status(val):
                if val == 'Booked':
                    return 'background-color: #e3f2fd'
                elif val == 'Completed':
                    return 'background-color: #e8f5e8'
                elif val == 'Cancelled':
                    return 'background-color: #ffebee'
                return ''
            
            styled_df = df.style.applymap(color_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No appointments found")

def browse_doctors_page():
    """Browse and search doctors"""
    st.title("Browse Doctors")
    st.write("Find and book appointments with doctors")
    
    # Search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("Search by specialization", placeholder="e.g., Cardiology, Neurology")
    
    with col2:
        search_button = st.button("Search")
    
    # Get doctors
    if search_term and search_button:
        doctors_result = api_call("GET", "/doctors", params={"specialization": search_term})
    else:
        doctors_result = api_call("GET", "/doctors")
    
    if doctors_result:
        doctors = doctors_result['doctors']
        
        if doctors:
            st.subheader(f"Found {len(doctors)} doctor(s)")
            
            for doctor in doctors:
                with st.expander(f"Dr. {doctor['name']} - {doctor['specialization']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Specialization:** {doctor['specialization']}")
                        st.write(f"**Consultancy Fee:** ${doctor['consultancy']}")
                        st.write(f"**Available Slots:** {doctor['available_slots']}")
                        st.write(f"**Email:** {doctor['email']}")
                    
                    with col2:
                        if st.button(f"Book Appointment", key=f"book_{doctor['doctor_profile_id']}"):
                            st.session_state.selected_doctor = doctor
                            st.session_state.show_booking = True
        else:
            st.info("No doctors found")
    
    # Booking modal
    if st.session_state.get('show_booking', False):
        st.markdown("---")
        st.subheader("Book Appointment")
        
        doctor = st.session_state.selected_doctor
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Doctor:** Dr. {doctor['name']}")
            st.write(f"**Specialization:** {doctor['specialization']}")
            st.write(f"**Fee:** ${doctor['consultancy']}")
        
        with col2:
            # Date selection
            tomorrow = datetime.now() + timedelta(days=1)
            selected_date = st.date_input("Select Date", min_value=tomorrow)
            
            # Time slot selection
            available_slots = doctor['available_slots'].split(',')
            selected_time = st.selectbox("Select Time", available_slots)
            
            # Problem description
            problem_description = st.text_area(
                "Describe your problem or symptoms",
                placeholder="Please briefly describe your health issue or symptoms...",
                height=100
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Confirm Booking"):
                booking_data = {
                    "doctor_profile_id": doctor['doctor_profile_id'],
                    "patient_id": st.session_state.user['user_id'],
                    "date": selected_date.strftime("%Y-%m-%d"),
                    "time": selected_time,
                    "problem_description": problem_description
                }
                
                result = api_call("POST", "/appointments", booking_data)
                
                if result:
                    st.success("Appointment booked successfully!")
                    st.session_state.appointment = result['appointment']
                    st.session_state.show_payment = True
                    st.session_state.show_booking = False
        
        with col2:
            if st.button("Cancel"):
                st.session_state.show_booking = False
                st.rerun()
    
    # Payment modal
    if st.session_state.get('show_payment', False):
        st.markdown("---")
        st.subheader("Process Payment")
        
        appointment = st.session_state.appointment
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Appointment ID:** {appointment['appointment_id']}")
            st.write(f"**Doctor:** Dr. {appointment['doctor_name']}")
            st.write(f"**Date:** {appointment['date']}")
            st.write(f"**Time:** {appointment['time']}")
        
        with col2:
            st.write(f"**Amount:** ${appointment['consultancy']}")
            
            payment_mode = st.selectbox("Payment Mode", ["Credit Card", "Debit Card", "UPI", "Cash"])
            
            if st.button("Process Payment"):
                payment_data = {
                    "appointment_id": appointment['appointment_id'],
                    "amount": appointment['consultancy'],
                    "mode": payment_mode
                }
                
                result = api_call("POST", "/payments", payment_data)
                
                if result:
                    st.success("Payment processed successfully!")
                    st.session_state.show_payment = False
                    st.rerun()

def appointments_page():
    """View appointments"""
    st.title("My Appointments")
    st.write("View and manage your appointments")
    
    appointments_result = api_call("GET", f"/appointments/patient/{st.session_state.user['user_id']}")
    
    if appointments_result:
        appointments = appointments_result['appointments']
        
        if appointments:
            # Filter by status
            status_filter = st.selectbox("Filter by Status", ["All", "Booked", "Completed", "Cancelled"])
            
            if status_filter != "All":
                appointments = [a for a in appointments if a['status'] == status_filter]
            
            # Display appointments
            for appointment in appointments:
                with st.expander(f"Appointment #{appointment['appointment_id']} - {appointment['date']} {appointment['time']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Doctor:** Dr. {appointment['doctor_name']}")
                        st.write(f"**Specialization:** {appointment['specialization']}")
                        st.write(f"**Date:** {appointment['date']}")
                        st.write(f"**Time:** {appointment['time']}")
                        st.write(f"**Status:** {appointment['status']}")
                    
                    with col2:
                        # Check payment status
                        payment_result = api_call("GET", f"/payments/appointment/{appointment['appointment_id']}")
                        
                        if payment_result:
                            st.write(f"**Payment:** ${payment_result['payment']['amount']}")
                            st.write(f"**Mode:** {payment_result['payment']['mode']}")
                        else:
                            st.write("**Payment:** Pending")
                        
                        # Cancel button for booked appointments
                        if appointment['status'] == 'Booked':
                            if st.button("Cancel Appointment", key=f"cancel_{appointment['appointment_id']}"):
                                result = api_call("PUT", f"/appointments/{appointment['appointment_id']}/status", {"status": "Cancelled"})
                                
                                if result:
                                    st.success("Appointment cancelled successfully!")
                                    st.rerun()
        else:
            st.info("No appointments found")

def consultations_page():
    """View consultations"""
    st.title("My Consultations")
    st.write("View your consultation history")
    
    consultations_result = api_call("GET", f"/consultations/patient/{st.session_state.user['user_id']}")
    
    if consultations_result:
        consultations = consultations_result['consultations']
        
        if consultations:
            for consultation in consultations:
                with st.expander(f"Consultation - {consultation['date']} {consultation['time']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Doctor:** Dr. {consultation['doctor_name']}")
                        st.write(f"**Specialization:** {consultation['specialization']}")
                        st.write(f"**Date:** {consultation['date']}")
                        st.write(f"**Time:** {consultation['time']}")
                        st.write(f"**Notes:** {consultation['notes']}")
                        st.write(f"**Prescription:** {consultation['prescription']}")
                    
                    with col2:
                        st.write("**Status:** Completed")
        else:
            st.info("No consultations found")

# ==================== MAIN APP ====================

def main():
    """Main application"""
    # Sidebar navigation
    if st.session_state.logged_in:
        st.sidebar.title(f"Patient Portal")
        st.sidebar.write(f"Welcome, {st.session_state.user['name']}")
        
        page = st.sidebar.selectbox("Navigate", [
            "Dashboard",
            "Browse Doctors", 
            "My Appointments",
            "My Consultations"
        ])
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
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
        elif page == "Browse Doctors":
            browse_doctors_page()
        elif page == "My Appointments":
            appointments_page()
        elif page == "My Consultations":
            consultations_page()

if __name__ == "__main__":
    main()

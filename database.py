"""
Database module for Clinical Health System
SQLite database with all required tables and functions
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Database file
DB_FILE = 'clinic_health_system.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize all database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop tables if they exist (for fresh start)
    cursor.executescript("""
        DROP TABLE IF EXISTS consultations;
        DROP TABLE IF EXISTS payments;
        DROP TABLE IF EXISTS appointments;
        DROP TABLE IF EXISTS doctor_profiles;
        DROP TABLE IF EXISTS users;
    """)
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_no TEXT NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('doctor', 'patient')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create doctor_profiles table
    cursor.execute('''
        CREATE TABLE doctor_profiles (
            doctor_profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            specialization TEXT NOT NULL,
            consultancy REAL NOT NULL,
            available_slots TEXT NOT NULL,
            profile_status TEXT NOT NULL DEFAULT 'Active' CHECK(profile_status IN ('Active', 'Inactive')),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create appointments table
    cursor.execute('''
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_profile_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            problem_description TEXT,
            status TEXT NOT NULL DEFAULT 'Booked' CHECK(status IN ('Booked', 'Cancelled', 'Completed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_profile_id) REFERENCES doctor_profiles (doctor_profile_id),
            FOREIGN KEY (patient_id) REFERENCES users (user_id),
            UNIQUE(doctor_profile_id, date, time)
        )
    ''')
    
    # Create payments table
    cursor.execute('''
        CREATE TABLE payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            mode TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Success' CHECK(status IN ('Success', 'Failed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
        )
    ''')
    
    # Create consultations table
    cursor.execute('''
        CREATE TABLE consultations (
            consultation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            notes TEXT,
            prescription TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id),
            FOREIGN KEY (doctor_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== USER FUNCTIONS ====================

def create_user(name: str, email: str, phone_no: str, password: str, user_type: str) -> int:
    """Create new user and return user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (name, email, phone_no, password, user_type) VALUES (?, ?, ?, ?, ?)',
        (name, email, phone_no, hash_password(password), user_type)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user and return user data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE email = ? AND password = ?',
        (email, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# ==================== DOCTOR PROFILE FUNCTIONS ====================

def create_doctor_profile(user_id: int, specialization: str, consultancy: float, available_slots: str) -> int:
    """Create doctor profile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO doctor_profiles (user_id, specialization, consultancy, available_slots) VALUES (?, ?, ?, ?)',
        (user_id, specialization, consultancy, available_slots)
    )
    profile_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return profile_id

def get_doctor_profile_by_user_id(user_id: int) -> Optional[Dict]:
    """Get doctor profile by user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT dp.*, u.name, u.email 
        FROM doctor_profiles dp 
        JOIN users u ON dp.user_id = u.user_id 
        WHERE dp.user_id = ?
    ''', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return dict(profile) if profile else None

def get_all_doctors() -> List[Dict]:
    """Get all active doctors with their profiles"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT dp.*, u.name, u.email 
        FROM doctor_profiles dp 
        JOIN users u ON dp.user_id = u.user_id 
        WHERE dp.profile_status = 'Active'
    ''')
    doctors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return doctors

def search_doctors(specialization: str = None) -> List[Dict]:
    """Search doctors by specialization"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if specialization:
        cursor.execute('''
            SELECT dp.*, u.name, u.email 
            FROM doctor_profiles dp 
            JOIN users u ON dp.user_id = u.user_id 
            WHERE dp.profile_status = 'Active' AND dp.specialization LIKE ?
        ''', (f'%{specialization}%',))
    else:
        cursor.execute('''
            SELECT dp.*, u.name, u.email 
            FROM doctor_profiles dp 
            JOIN users u ON dp.user_id = u.user_id 
            WHERE dp.profile_status = 'Active'
        ''')
    
    doctors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return doctors

# ==================== APPOINTMENT FUNCTIONS ====================

def create_appointment(doctor_profile_id: int, patient_id: int, date: str, time: str, problem_description: str = None) -> int:
    """Create new appointment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO appointments (doctor_profile_id, patient_id, date, time, problem_description) VALUES (?, ?, ?, ?, ?)',
        (doctor_profile_id, patient_id, date, time, problem_description)
    )
    appointment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return appointment_id

def get_appointment_by_id(appointment_id: int) -> Optional[Dict]:
    """Get appointment by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, u.name as patient_name, u.email as patient_email,
               dp.specialization, dp.consultancy, u2.name as doctor_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.user_id
        JOIN doctor_profiles dp ON a.doctor_profile_id = dp.doctor_profile_id
        JOIN users u2 ON dp.user_id = u2.user_id
        WHERE a.appointment_id = ?
    ''', (appointment_id,))
    appointment = cursor.fetchone()
    conn.close()
    return dict(appointment) if appointment else None

def get_patient_appointments(patient_id: int) -> List[Dict]:
    """Get all appointments for a patient"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, u.name as doctor_name, dp.specialization, dp.consultancy
        FROM appointments a
        JOIN doctor_profiles dp ON a.doctor_profile_id = dp.doctor_profile_id
        JOIN users u ON dp.user_id = u.user_id
        WHERE a.patient_id = ?
        ORDER BY a.date DESC, a.time DESC
    ''', (patient_id,))
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return appointments

def get_doctor_appointments(doctor_user_id: int) -> List[Dict]:
    """Get all appointments for a doctor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, u.name as patient_name, u.email as patient_email, u.phone_no as patient_phone
        FROM appointments a
        JOIN doctor_profiles dp ON a.doctor_profile_id = dp.doctor_profile_id
        JOIN users u ON a.patient_id = u.user_id
        WHERE dp.user_id = ?
        ORDER BY a.date DESC, a.time DESC
    ''', (doctor_user_id,))
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return appointments

def check_slot_availability(doctor_profile_id: int, date: str, time: str) -> bool:
    """Check if slot is available"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) as count FROM appointments WHERE doctor_profile_id = ? AND date = ? AND time = ? AND status != "Cancelled"',
        (doctor_profile_id, date, time)
    )
    result = cursor.fetchone()
    conn.close()
    return result['count'] == 0

def update_appointment_status(appointment_id: int, status: str) -> bool:
    """Update appointment status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE appointments SET status = ? WHERE appointment_id = ?',
        (status, appointment_id)
    )
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

# ==================== PAYMENT FUNCTIONS ====================

def create_payment(appointment_id: int, amount: float, mode: str) -> int:
    """Create payment record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO payments (appointment_id, amount, mode) VALUES (?, ?, ?)',
        (appointment_id, amount, mode)
    )
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return payment_id

def get_payment_by_appointment(appointment_id: int) -> Optional[Dict]:
    """Get payment for appointment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments WHERE appointment_id = ?', (appointment_id,))
    payment = cursor.fetchone()
    conn.close()
    return dict(payment) if payment else None

def check_payment_exists(appointment_id: int) -> bool:
    """Check if payment exists for appointment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) as count FROM payments WHERE appointment_id = ? AND status = "Success"',
        (appointment_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result['count'] > 0

# ==================== CONSULTATION FUNCTIONS ====================

def create_consultation(appointment_id: int, doctor_id: int, notes: str, prescription: str) -> int:
    """Create consultation record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO consultations (appointment_id, doctor_id, notes, prescription) VALUES (?, ?, ?, ?)',
        (appointment_id, doctor_id, notes, prescription)
    )
    consultation_id = cursor.lastrowid
    
    # Update appointment status to completed
    cursor.execute(
        'UPDATE appointments SET status = "Completed" WHERE appointment_id = ?',
        (appointment_id,)
    )
    
    conn.commit()
    conn.close()
    return consultation_id

def get_consultation_by_appointment(appointment_id: int) -> Optional[Dict]:
    """Get consultation by appointment ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.name as doctor_name
        FROM consultations c
        JOIN users u ON c.doctor_id = u.user_id
        WHERE c.appointment_id = ?
    ''', (appointment_id,))
    consultation = cursor.fetchone()
    conn.close()
    return dict(consultation) if consultation else None

def get_patient_consultations(patient_id: int) -> List[Dict]:
    """Get all consultations for a patient"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, a.date, a.time, u.name as doctor_name, dp.specialization
        FROM consultations c
        JOIN appointments a ON c.appointment_id = a.appointment_id
        JOIN users u ON c.doctor_id = u.user_id
        JOIN doctor_profiles dp ON a.doctor_profile_id = dp.doctor_profile_id
        WHERE a.patient_id = ?
        ORDER BY a.date DESC, a.time DESC
    ''', (patient_id,))
    consultations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return consultations

# ==================== INITIAL DATA ====================

def insert_initial_data():
    """Insert initial doctors and patients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert doctors
    doctors = [
        ('Dr. Sarah Johnson', 'sarah.j@clinic.com', '555-0101', 'doctor123', 'doctor', 'Cardiology', 'General Cardiology', 150.0, '09:00,10:00,11:00,14:00,15:00,16:00'),
        ('Dr. Michael Chen', 'michael.c@clinic.com', '555-0102', 'doctor123', 'doctor', 'Neurology', 'Neurological Disorders', 200.0, '09:00,11:00,14:00,16:00'),
        ('Dr. Emily Davis', 'emily.d@clinic.com', '555-0103', 'doctor123', 'doctor', 'Pediatrics', 'Child Healthcare', 120.0, '08:00,09:00,10:00,11:00,14:00,15:00'),
        ('Dr. James Wilson', 'james.w@clinic.com', '555-0104', 'doctor123', 'doctor', 'Orthopedics', 'Bone and Joint Care', 180.0, '10:00,11:00,14:00,15:00,16:00,17:00')
    ]
    
    for name, email, phone, password, user_type, specialization_desc, specialization, consultancy, slots in doctors:
        user_id = create_user(name, email, phone, password, user_type)
        create_doctor_profile(user_id, specialization, consultancy, slots)
    
    # Insert patients
    patients = [
        ('John Smith', 'john.s@email.com', '555-0201', 'patient123'),
        ('Mary Johnson', 'mary.j@email.com', '555-0202', 'patient123'),
        ('Robert Brown', 'robert.b@email.com', '555-0203', 'patient123'),
        ('Lisa Anderson', 'lisa.a@email.com', '555-0204', 'patient123'),
        ('David Miller', 'david.m@email.com', '555-0205', 'patient123'),
        ('Jennifer Taylor', 'jennifer.t@email.com', '555-0206', 'patient123'),
        ('William Garcia', 'william.g@email.com', '555-0207', 'patient123'),
        ('Patricia Martinez', 'patricia.m@email.com', '555-0208', 'patient123'),
        ('Christopher Lee', 'chris.l@email.com', '555-0209', 'patient123'),
        ('Amanda White', 'amanda.w@email.com', '555-0210', 'patient123')
    ]
    
    for name, email, phone, password in patients:
        create_user(name, email, phone, password, 'patient')
    
    conn.close()

# Initialize database
if __name__ == '__main__':
    init_database()
    insert_initial_data()
    print("Database initialized with initial data!")

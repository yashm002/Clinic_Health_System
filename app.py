"""
Flask Backend API for Clinical Health System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import database as db

app = Flask(__name__)
CORS(app)


# ==================== AUTHENTICATION ====================

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register new user (Patient or Doctor)"""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'phone_no', 'password', 'user_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    if data['user_type'] not in ['doctor', 'patient']:
        return jsonify({'error': 'user_type must be doctor or patient'}), 400
    
    # Check if email already exists
    if db.get_user_by_email(data['email']):
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        user_id = db.create_user(
            data['name'],
            data['email'],
            data['phone_no'],
            data['password'],
            data['user_type']
        )
        
        # If doctor, create doctor profile
        if data['user_type'] == 'doctor':
            required_doctor_fields = ['specialization', 'consultancy', 'available_slots']
            for field in required_doctor_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required for doctors'}), 400
            
            db.create_doctor_profile(
                user_id,
                data['specialization'],
                float(data['consultancy']),
                data['available_slots']
            )
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'user_type': data['user_type']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = db.authenticate_user(data['email'], data['password'])
    
    if user:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'user_type': user['user_type']
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401


# ==================== DOCTOR PROFILE ====================

@app.route('/api/doctor/profile', methods=['GET'])
def get_doctor_profile():
    """Get doctor profile by user_id"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    profile = db.get_doctor_profile_by_user_id(int(user_id))
    
    if profile:
        return jsonify({'profile': profile}), 200
    else:
        return jsonify({'error': 'Doctor profile not found'}), 404

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """Get all active doctors"""
    specialization = request.args.get('specialization')
    
    if specialization:
        doctors = db.search_doctors(specialization)
    else:
        doctors = db.get_all_doctors()
    
    return jsonify({'doctors': doctors}), 200


# ==================== APPOINTMENTS ====================

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create new appointment"""
    data = request.get_json()
    
    required_fields = ['doctor_profile_id', 'patient_id', 'date', 'time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check slot availability
    if not db.check_slot_availability(
        int(data['doctor_profile_id']), 
        data['date'], 
        data['time']
    ):
        return jsonify({'error': 'Slot not available'}), 400
    
    try:
        appointment_id = db.create_appointment(
            int(data['doctor_profile_id']),
            int(data['patient_id']),
            data['date'],
            data['time'],
            data.get('problem_description')
        )
        
        appointment = db.get_appointment_by_id(appointment_id)
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    """Get appointment by ID"""
    appointment = db.get_appointment_by_id(appointment_id)
    
    if appointment:
        return jsonify({'appointment': appointment}), 200
    else:
        return jsonify({'error': 'Appointment not found'}), 404

@app.route('/api/appointments/patient/<int:patient_id>', methods=['GET'])
def get_patient_appointments(patient_id):
    """Get all appointments for a patient"""
    appointments = db.get_patient_appointments(patient_id)
    return jsonify({'appointments': appointments}), 200

@app.route('/api/appointments/doctor/<int:doctor_user_id>', methods=['GET'])
def get_doctor_appointments(doctor_user_id):
    """Get all appointments for a doctor"""
    appointments = db.get_doctor_appointments(doctor_user_id)
    return jsonify({'appointments': appointments}), 200

@app.route('/api/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    """Update appointment status"""
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'status is required'}), 400
    
    if data['status'] not in ['Booked', 'Cancelled', 'Completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    success = db.update_appointment_status(appointment_id, data['status'])
    
    if success:
        return jsonify({'message': 'Appointment status updated successfully'}), 200
    else:
        return jsonify({'error': 'Appointment not found'}), 404


# ==================== PAYMENTS ====================

@app.route('/api/payments', methods=['POST'])
def create_payment():
    """Create payment for appointment"""
    data = request.get_json()
    
    required_fields = ['appointment_id', 'amount', 'mode']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if payment already exists
    if db.check_payment_exists(int(data['appointment_id'])):
        return jsonify({'error': 'Payment already exists for this appointment'}), 400
    
    try:
        payment_id = db.create_payment(
            int(data['appointment_id']),
            float(data['amount']),
            data['mode']
        )
        
        payment = db.get_payment_by_appointment(int(data['appointment_id']))
        return jsonify({
            'message': 'Payment processed successfully',
            'payment': payment
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/appointment/<int:appointment_id>', methods=['GET'])
def get_payment_by_appointment(appointment_id):
    """Get payment for appointment"""
    payment = db.get_payment_by_appointment(appointment_id)
    
    if payment:
        return jsonify({'payment': payment}), 200
    else:
        return jsonify({'error': 'Payment not found'}), 404


# ==================== CONSULTATIONS ====================

@app.route('/api/consultations', methods=['POST'])
def create_consultation():
    """Create consultation record"""
    data = request.get_json()
    
    required_fields = ['appointment_id', 'doctor_id', 'notes', 'prescription']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        consultation_id = db.create_consultation(
            int(data['appointment_id']),
            int(data['doctor_id']),
            data['notes'],
            data['prescription']
        )
        
        consultation = db.get_consultation_by_appointment(int(data['appointment_id']))
        return jsonify({
            'message': 'Consultation completed successfully',
            'consultation': consultation
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/consultations/appointment/<int:appointment_id>', methods=['GET'])
def get_consultation_by_appointment(appointment_id):
    """Get consultation by appointment ID"""
    consultation = db.get_consultation_by_appointment(appointment_id)
    
    if consultation:
        return jsonify({'consultation': consultation}), 200
    else:
        return jsonify({'error': 'Consultation not found'}), 404

@app.route('/api/consultations/patient/<int:patient_id>', methods=['GET'])
def get_patient_consultations(patient_id):
    """Get all consultations for a patient"""
    consultations = db.get_patient_consultations(patient_id)
    return jsonify({'consultations': consultations}), 200


# ==================== UTILITY ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Clinical Health System API is running'}), 200

@app.route('/api/init', methods=['POST'])
def initialize_database():
    """Initialize database with initial data"""
    try:
        db.init_database()
        db.insert_initial_data()
        return jsonify({'message': 'Database initialized successfully with initial data'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

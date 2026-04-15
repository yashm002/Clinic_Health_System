# Clinical Health System

A comprehensive end-to-end appointment and consultation management system for clinics.

## Features

- **User Authentication**: Secure signup and login for patients and doctors
- **Doctor Profiles**: Specialization, consultancy fees, and available time slots
- **Appointment Booking**: Browse doctors and book appointments based on availability
- **Payment System**: Simulated payment processing for appointments
- **Consultation Management**: Doctors can complete consultations with notes and prescriptions
- **History Tracking**: View appointment, payment, and consultation history

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Streamlit
- **Database**: SQLite
- **API**: RESTful API with CORS support

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Initialize Database

First, initialize the database with initial data:

```bash
python database.py
```

This will create the SQLite database and insert:
- 4 doctors with different specializations
- 10 patients

### 2. Start the Backend API

Run the Flask API server:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 3. Start the Frontend Applications

**Patient Portal:**
```bash
streamlit run patient_app.py
```

**Doctor Portal:**
```bash
streamlit run doctor_app.py
```

## Default Login Credentials

### Doctors
- **Dr. Sarah Johnson** (Cardiology)
  - Email: sarah.j@clinic.com
  - Password: doctor123

- **Dr. Michael Chen** (Neurology)
  - Email: michael.c@clinic.com
  - Password: doctor123

- **Dr. Emily Davis** (Pediatrics)
  - Email: emily.d@clinic.com
  - Password: doctor123

- **Dr. James Wilson** (Orthopedics)
  - Email: james.w@clinic.com
  - Password: doctor123

### Patients
- **John Smith**
  - Email: john.s@email.com
  - Password: patient123

- **Mary Johnson**
  - Email: mary.j@email.com
  - Password: patient123

(Additional patients with similar email pattern and same password)

## API Endpoints

### Authentication
- `POST /api/signup` - Register new user
- `POST /api/login` - User login

### Doctors
- `GET /api/doctors` - Get all doctors (with optional specialization filter)
- `GET /api/doctor/profile` - Get doctor profile

### Appointments
- `POST /api/appointments` - Create appointment
- `GET /api/appointments/<id>` - Get appointment by ID
- `GET /api/appointments/patient/<id>` - Get patient appointments
- `GET /api/appointments/doctor/<id>` - Get doctor appointments
- `PUT /api/appointments/<id>/status` - Update appointment status

### Payments
- `POST /api/payments` - Create payment
- `GET /api/payments/appointment/<id>` - Get payment by appointment

### Consultations
- `POST /api/consultations` - Create consultation
- `GET /api/consultations/appointment/<id>` - Get consultation by appointment
- `GET /api/consultations/patient/<id>` - Get patient consultations

### Utility
- `GET /api/health` - Health check
- `POST /api/init` - Initialize database with initial data

## System Flow

1. **Registration**: Users sign up as either patient or doctor
2. **Profile Creation**: Doctors create professional profiles
3. **Browse & Book**: Patients browse doctors and book appointments
4. **Payment**: Patients process payment for appointments
5. **Consultation**: Doctors complete consultations with notes and prescriptions
6. **History**: Users view their complete history

## Database Schema

- **users**: User authentication and basic information
- **doctor_profiles**: Professional information for doctors
- **appointments**: Appointment scheduling and status
- **payments**: Payment records for appointments
- **consultations**: Consultation notes and prescriptions

## Features Implemented

- [x] User authentication (signup/login)
- [x] Doctor profiles with specializations
- [x] Appointment booking with slot availability
- [x] Payment processing (simulated)
- [x] Consultation management
- [x] History tracking for patients and doctors
- [x] Double booking prevention
- [x] Payment validation (one per appointment)
- [x] Doctor authorization for consultations
- [x] Initial data seeding

## Security Features

- Password hashing using SHA-256
- Input validation and sanitization
- Role-based access control
- Appointment authorization checks
- Payment validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

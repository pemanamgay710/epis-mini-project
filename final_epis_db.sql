-- Create and select the database
CREATE DATABASE final_epis_db;
USE final_epis_db;

-- ==========================================================
-- 1️⃣ Users Table
-- ==========================================================
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient','doctor','nurse','lab_tech','receptionist') NOT NULL,
    linked_cid BIGINT DEFAULT NULL,      -- only for patients
    linked_emp_id INT DEFAULT NULL,      -- for staff (doctor, nurse, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from Users;

-- ==========================================================
-- 2️⃣ Patient Table
-- ==========================================================
CREATE TABLE Patient (
    CID_no BIGINT PRIMARY KEY,
    name VARCHAR(100),
    DOB DATE,
    gender VARCHAR(10),
    contact BIGINT,
    address VARCHAR(255),
    CONSTRAINT chk_cid_length CHECK (CID_no BETWEEN 10000000000 AND 99999999999),
    CONSTRAINT chk_contact_length CHECK (contact BETWEEN 10000000 AND 99999999)
);

-- ==========================================================
-- 3️⃣ Doctor Table
-- ==========================================================
CREATE TABLE Doctor (
    doctor_emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    contact BIGINT
);

-- Sample Doctor
INSERT INTO Doctor (doctor_emp_id, name, specialization, contact)
VALUES (1, 'Dorji', 'Neurosurgeon', 17268001);

-- ==========================================================
-- 4️⃣ Receptionist Table
-- ==========================================================
CREATE TABLE Receptionist (
    receptionist_emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    contact BIGINT
);

-- ==========================================================
-- 5️⃣ Appointment Table
-- ==========================================================
CREATE TABLE Appointment (
    appointment_id INT PRIMARY KEY,
    date DATE,
    time TIME,
    status VARCHAR(20),
    CID_no BIGINT,
    doctor_emp_id INT,
    FOREIGN KEY (CID_no) REFERENCES Patient(CID_no) ON DELETE CASCADE,
    FOREIGN KEY (doctor_emp_id) REFERENCES Doctor(doctor_emp_id) ON DELETE SET NULL
);

-- ==========================================================
-- 6️⃣ Diagnosis Table
-- ==========================================================
CREATE TABLE Diagnosis (
    diagnosis_id INT PRIMARY KEY,
    description TEXT,
    date DATE,
    appointment_id INT,
    doctor_emp_id INT,
    CID_no BIGINT,
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_emp_id) REFERENCES Doctor(doctor_emp_id) ON DELETE SET NULL,
    FOREIGN KEY (CID_no) REFERENCES Patient(CID_no) ON DELETE CASCADE
);

-- ==========================================================
-- 7️⃣ Prescription Table
-- ==========================================================
CREATE TABLE Prescription (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    stock_qty INT DEFAULT 0,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    date DATE,
    frequency ENUM('Morning','Afternoon','Evening') NOT NULL,
    time_of_day VARCHAR(10),
    appointment_id INT,
    doctor_emp_id INT,
    CID_no BIGINT,
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_emp_id) REFERENCES Doctor(doctor_emp_id) ON DELETE SET NULL,
    FOREIGN KEY (CID_no) REFERENCES Patient(CID_no) ON DELETE CASCADE
);

-- Sample Prescriptions
#INSERT INTO Prescription 
#(name, dosage, stock_qty, start_date, end_date, date, frequency, appointment_id, doctor_emp_id, CID_no)
#VALUES 
#('Paracetamol', '500mg', 30, '2025-10-10', '2025-10-20', '2025-10-10', 'Morning', NULL, 1, 11111111111),
#('Amoxicillin', '250mg', 30, '2025-10-10', '2025-10-20', '2025-10-10', 'Afternoon', NULL, 1, 11111111111);

-- ==========================================================
-- 8️⃣ Pharmacist Table
-- ==========================================================
CREATE TABLE Pharmacist (
    pharmacist_emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    designation VARCHAR(100),
    contact BIGINT
);

-- ==========================================================
-- 9️⃣ Medicine Dispense Table
-- ==========================================================
CREATE TABLE Medicine_Dispense (
    dispense_id INT PRIMARY KEY,
    medicine_name VARCHAR(100),
    quantity INT,
    dispense_date DATE,
    prescription_id INT,
    pharmacist_emp_id INT,
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id) ON DELETE CASCADE,
    FOREIGN KEY (pharmacist_emp_id) REFERENCES Pharmacist(pharmacist_emp_id) ON DELETE SET NULL
);

-- ==========================================================
-- 🔟 Nurse Table
-- ==========================================================
CREATE TABLE Nurse (
    nurse_emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    contact BIGINT
);

-- Sample Nurse
INSERT INTO Nurse (nurse_emp_id, name, contact)
VALUES (1, 'Dawa', 17389801);

-- ==========================================================
-- 1️⃣1️⃣ Medicine Administration Table
-- ==========================================================
CREATE TABLE Medicine_Administration (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    nurse_emp_id INT NOT NULL,
    admin_time DATETIME DEFAULT NOW(),
    status ENUM('Given', 'Pending', 'Skipped') DEFAULT 'Pending',
    remarks VARCHAR(255),
    frequency ENUM('Morning','Afternoon','Evening') NOT NULL,
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_emp_id) REFERENCES Nurse(nurse_emp_id) ON DELETE CASCADE
);

-- ==========================================================
-- 1️⃣2️⃣ Admission to Ward Table
-- ==========================================================
CREATE TABLE Admission_to_Ward (
    admission_id INT AUTO_INCREMENT PRIMARY KEY,
    admit_date DATE,
    discharge_date DATE,
    ward_no INT,
    status VARCHAR(20),
    CID_no BIGINT,
    doctor_emp_id INT,
    nurse_emp_id INT,
    FOREIGN KEY (CID_no) REFERENCES Patient(CID_no) ON DELETE CASCADE,
    FOREIGN KEY (doctor_emp_id) REFERENCES Doctor(doctor_emp_id) ON DELETE SET NULL,
    FOREIGN KEY (nurse_emp_id) REFERENCES Nurse(nurse_emp_id) ON DELETE SET NULL
);

-- ==========================================================
-- 1️⃣3️⃣ Lab Technician Table
-- ==========================================================
CREATE TABLE Lab_Technician (
    technician_emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(100)
);

-- ==========================================================
-- 1️⃣4️⃣ Lab Test Table
-- ==========================================================
CREATE TABLE Lab_Test (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    test_name VARCHAR(100),
    date_ordered DATE,
    appointment_id INT,
    CID_no BIGINT,
    doctor_emp_id INT,
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (CID_no) REFERENCES Patient(CID_no) ON DELETE CASCADE,
    FOREIGN KEY (doctor_emp_id) REFERENCES Doctor(doctor_emp_id) ON DELETE SET NULL
);

-- ==========================================================
-- 1️⃣5️⃣ Test Report Table
-- ==========================================================
CREATE TABLE Test_Report (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255),
    date_uploaded DATE,
    test_id INT,
    technician_emp_id INT,
    FOREIGN KEY (test_id) REFERENCES Lab_Test(test_id) ON DELETE CASCADE,
    FOREIGN KEY (technician_emp_id) REFERENCES Lab_Technician(technician_emp_id) ON DELETE SET NULL
);

-- ==========================================================
-- 1️⃣6️⃣ Views
-- ==========================================================

-- Patient Lab Report View
CREATE VIEW Patient_Lab_Report_View AS
SELECT 
    p.CID_no,
    p.name AS patient_name,
    lt.test_id,
    lt.test_name,
    tr.report_id,
    tr.file_path,
    tr.date_uploaded,
    d.name AS doctor_name,
    lt.date_ordered
FROM 
    Patient p
JOIN Lab_Test lt ON p.CID_no = lt.CID_no
LEFT JOIN Test_Report tr ON lt.test_id = tr.test_id
LEFT JOIN Doctor d ON lt.doctor_emp_id = d.doctor_emp_id;

-- Doctor Patient Detail View
CREATE VIEW Doctor_Patient_Detail_View AS
SELECT 
    d.doctor_emp_id,
    d.name AS doctor_name,
    p.CID_no,
    p.name AS patient_name,
    a.appointment_id,
    a.date AS appointment_date,
    a.status
FROM 
    Doctor d
JOIN Appointment a ON d.doctor_emp_id = a.doctor_emp_id
JOIN Patient p ON a.CID_no = p.CID_no;

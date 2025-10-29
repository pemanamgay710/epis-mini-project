import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, date, timedelta

# ----------------- Helper Functions -----------------
def validate_cid(cid_str):
    """Ensure CID is numeric and 11 digits."""
    try:
        cid_int = int(cid_str)
        if 10000000000 <= cid_int <= 99999999999:
            return cid_int
        else:
            st.error("CID must be 11 digits.")
            return None
    except ValueError:
        st.error("CID must be numeric.")
        return None


# ----------------- Doctor Dashboard -----------------
def doctor_dashboard(conn):
    # ------------------- HEADER + LOGOUT -------------------
    col1, col2 = st.columns([6, 1])
    with col1:
        st.header("Doctor Panel - Manage Patients")
    with col2:
        if st.button("Logout"):
            for key in ["user", "page", "doctor_id", "patient_admitted", "last_admitted_cid"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["page"] = "login_page"
            st.success("You have been logged out.")
            st.rerun()

    # ---------------- SESSION STATE ----------------
    if "patient_admitted" not in st.session_state:
        st.session_state.patient_admitted = False
    if "last_admitted_cid" not in st.session_state:
        st.session_state.last_admitted_cid = ""

    # --- Collapsible section to view registered patients ---
    with st.expander("View Registered Patients"):
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM Patient")
                patients = cur.fetchall()
            if patients:
                df_patients = pd.DataFrame(patients)
                st.dataframe(df_patients)
            else:
                st.info("No patients registered yet.")
        except mysql.connector.Error as e:
            st.error(f"Database Error: {e}")

    # --- Admit Patient Form ---
    st.subheader("Admit Patient to Ward")
    with st.form("admit_form"):
        cid_admit_str = st.text_input("Enter Patient CID to Admit")
        ward_no = st.text_input("Ward Number")
        doctor_id_admit = st.text_input("Your Doctor Employee ID")
        nurse_id = st.text_input("Assign Nurse Employee ID")
        submitted_admit = st.form_submit_button("Admit Patient")

    if submitted_admit:
        cid_admit = validate_cid(cid_admit_str)
        if not cid_admit or not ward_no.strip():
            st.error("Provide valid patient CID and ward number.")
        else:
            try:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("SELECT CID_no FROM Patient WHERE CID_no = %s", (cid_admit,))
                    patient = cur.fetchone()
                if not patient:
                    st.error("Patient with this CID does not exist.")
                else:
                    with conn.cursor() as cur_insert:
                        cur_insert.execute("""
                            INSERT INTO Admission_to_Ward 
                            (admit_date, ward_no, status, CID_no, doctor_emp_id, nurse_emp_id)
                            VALUES (%s, %s, 'Admitted', %s, %s, %s)
                        """, (date.today(), ward_no, cid_admit, doctor_id_admit or None, nurse_id or None))
                        conn.commit()
                    st.success("Patient admitted to ward successfully.")
                    st.session_state.patient_admitted = True
                    st.session_state.last_admitted_cid = cid_admit
            except mysql.connector.Error as err:
                st.error(f"Database Error: {err}")
                conn.rollback()

    # --- Prescription Form (simplified) ---
    st.subheader("Upload Prescription for Admitted Patient")
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT CID_no, ward_no, nurse_emp_id FROM Admission_to_Ward WHERE status='Admitted'")
        admitted_patients = cur.fetchall()

    if admitted_patients:
        with st.form("prescription_form"):
            patient_cid_pres = st.selectbox(
                "Select Admitted Patient",
                options=[p["CID_no"] for p in admitted_patients],
                format_func=lambda x: f"{x} - Ward {next(p['ward_no'] for p in admitted_patients if p['CID_no']==x)}"
            )
            prescription_name = st.text_input("Medicine Name")
            dosage = st.text_input("Dosage (e.g., 500mg)")
            frequency = st.multiselect("Select Medication Timing", ["Morning", "Afternoon", "Evening"])
            start_date = st.date_input("Start Date", min_value=date.today())
            end_date = st.date_input("End Date", min_value=start_date)
            doctor_id = st.text_input("Your Doctor Employee ID")
            submitted_pres = st.form_submit_button("Upload Prescription")

        if submitted_pres:
            if not prescription_name.strip() or not doctor_id.strip() or not frequency:
                st.error("Provide Medicine Name, Doctor ID, and select at least one timing.")
            else:
                try:
                    with conn.cursor(dictionary=True) as cur:
                        cur.execute("""
                            SELECT admission_id, nurse_emp_id 
                            FROM Admission_to_Ward 
                            WHERE CID_no=%s AND status='Admitted'
                        """, (patient_cid_pres,))
                        admission = cur.fetchone()

                    if not admission:
                        st.error("Patient not admitted. Admit patient first.")
                    else:
                        with conn.cursor() as cur_insert:
                            for freq in frequency:
                                normalized_freq = freq.strip().capitalize()
                                cur_insert.execute("""
                                    INSERT INTO Prescription
                                    (name, dosage, start_date, end_date, frequency, doctor_emp_id, CID_no)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                                """, (
                                    prescription_name, dosage, start_date, end_date,
                                    normalized_freq, doctor_id, patient_cid_pres
                                ))
                            conn.commit()
                        st.success("Prescription uploaded successfully for all selected timings.")
                except mysql.connector.Error as err:
                    st.error(f"Database Error: {err}")
                    conn.rollback()
    else:
        st.info("No patients currently admitted to the ward.")

    # --- Lab Test Form ---
    st.subheader("Order Lab Test for Patient")
    with st.form("lab_order_form"):
        cid_lab_str = st.text_input("Enter Patient CID")  
        test_name = st.text_input("Lab Test Name (e.g., Blood Test, X-Ray)")
        doctor_id_lab = st.text_input("Your Doctor Employee ID")
        submitted_lab = st.form_submit_button("Order Lab Test")

    if submitted_lab:
        cid_lab = validate_cid(cid_lab_str)  
        if not cid_lab or not test_name.strip() or not doctor_id_lab.strip():
            st.error("Provide valid CID, test name, and doctor ID.")
        else:
            try:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("SELECT CID_no FROM Patient WHERE CID_no=%s", (cid_lab,))
                    patient = cur.fetchone()
                if not patient:
                    st.error("Patient with this CID does not exist.")
                else:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO Lab_Test (test_name, date_ordered, CID_no, doctor_emp_id)
                            VALUES (%s,%s,%s,%s)
                        """, (test_name, date.today(), cid_lab, doctor_id_lab))
                        conn.commit()
                    st.success("Lab test ordered successfully.")
            except mysql.connector.Error as err:
                st.error(f"Database Error: {err}")
                conn.rollback()

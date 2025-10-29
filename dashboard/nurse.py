import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, date

def nurse_dashboard(conn):

    col1, col2 = st.columns([6, 1])
    with col1:
        st.header("Nurse Panel - Ward & Medication Management")
    with col2:
        if st.button("Logout"):
            for key in ["user", "page", "nurse_id"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["page"] = "login_page"
            st.success("You have been logged out.")
            st.rerun()

    # NURSE AUTH 
    nurse_id = st.text_input("Enter Your Nurse Employee ID to View Assigned Patients")
    if not nurse_id.strip():
        st.warning("Please enter your Nurse Employee ID to get started.")
        return

    # LOAD ASSIGNED PATIENTS 
    st.subheader("Currently Admitted Patients Under Your Care")
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.admission_id, p.CID_no, p.name AS patient_name, 
               a.ward_no, a.status AS admission_status
        FROM Admission_to_Ward a
        JOIN Patient p ON a.CID_no = p.CID_no
        WHERE a.nurse_emp_id = %s AND a.status = 'Admitted'
    """, (nurse_id,))
    admitted_patients = pd.DataFrame(cur.fetchall())
    cur.close()

    if admitted_patients.empty:
        st.info("No patients currently admitted under your care.")
    else:
        st.dataframe(admitted_patients, width='stretch')

    # SEARCH MEDICATIONS 
    st.divider()
    st.subheader("Search Scheduled Medications")

    with st.form("smart_search_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            search_date = st.date_input("Select Date", value=date.today())
        with col2:
            patient_name = st.text_input("Search by Patient Name (optional)")

        submitted_search = st.form_submit_button("Search Medications")

    if submitted_search:
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT 
                p.CID_no AS patient_id,
                p.name AS patient_name,
                pr.prescription_id,
                pr.name AS medication_name,
                pr.dosage,
                pr.frequency,
                COALESCE(ma.status, 'Pending') AS status
            FROM Prescription pr
            JOIN Patient p ON pr.CID_no = p.CID_no
            JOIN Admission_to_Ward a ON p.CID_no = a.CID_no
            LEFT JOIN Medicine_Administration ma 
                ON ma.prescription_id = pr.prescription_id
                AND DATE(ma.admin_time) = %s
            WHERE a.nurse_emp_id = %s
            AND %s BETWEEN pr.start_date AND pr.end_date
        """

        params = [search_date, nurse_id, search_date]

        if patient_name.strip():
            query += " AND p.name LIKE %s"
            params.append(f"%{patient_name}%")

        query += " ORDER BY p.name ASC, pr.name ASC"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()

        if rows:
            result = pd.DataFrame(rows)

            st.success(f"Found {len(result)} medication record(s) for {search_date}.")

            # Create pivot table (one row per prescription)
            pivoted = (
                result
                .pivot_table(
                    index=["patient_id", "patient_name", "medication_name", "dosage"],
                    columns="frequency",
                    values="status",
                    aggfunc="first"
                )
                .reset_index()
            )

            # Ensure all standard time slots exist as columns
            for slot in ["Morning", "Afternoon", "Evening"]:
                if slot not in pivoted.columns:
                    pivoted[slot] = None  # leave blank if not prescribed

            # Fill 'Pending' only for prescribed frequencies that have no status
            for _, row in result.iterrows():
                freq = row["frequency"]
                mask = (
                    (pivoted["patient_id"] == row["patient_id"]) &
                    (pivoted["medication_name"] == row["medication_name"])
                )
                pivoted.loc[mask, freq] = (
                    pivoted.loc[mask, freq].fillna("Pending")
                )

            # Clean display: replace None/NaN with blank string
            display_df = pivoted.fillna("")

            st.dataframe(
                display_df.rename(columns={
                    "patient_id": "Patient ID",
                    "patient_name": "Patient Name",
                    "medication_name": "Medication Name",
                    "dosage": "Dosage"
                }),
                width='stretch'
            )
        else:
            st.info("No medication records found for the selected filters.")

        # UPDATE MEDICATION STATUS 
    st.divider()
    st.subheader("Update Medication Status by Time Slot")

    # Step 1: Enter patient ID
    patient_id = st.text_input("Enter Patient ID (CID)")
    remarks = st.text_area("Remarks (optional)")

    # Step 2: Only fetch prescriptions if patient ID is entered
    selected_prescription_id = None
    if patient_id.strip():
        try:
            cid_val = int(patient_id)
            cur = conn.cursor(dictionary=True)

            # Fetch all prescriptions for this patient (include frequency to show doctor-prescribed frequency)
            cur.execute("""
                SELECT prescription_id, name AS med_name, frequency
                FROM Prescription
                WHERE CID_no = %s
            """, (cid_val,))
            prescriptions = cur.fetchall()
            cur.close()

            if prescriptions:
                # Step 3: Selectbox for all medications (include frequency in label to avoid confusion)
                med_options = {
                    f"{p['med_name']} ({p['frequency']})": (p['prescription_id'], p['frequency'])
                    for p in prescriptions
                }
                selected_med_label = st.selectbox("Select Medication to Update", list(med_options.keys()))
                selected_prescription_id, prescribed_frequency = med_options[selected_med_label]

                # Step 4: Pick date, time slot, and status
                col1, col2, col3 = st.columns(3)
                with col1:
                    selected_date = st.date_input("Select Date", value=date.today())
                with col2:
                    # allow nurse to choose time slot but show the prescribed one in parentheses
                    time_slot = st.selectbox(
                        "Select Time Slot",
                        ["Morning", "Afternoon", "Evening"],
                        index=["Morning", "Afternoon", "Evening"].index(prescribed_frequency)
                        if prescribed_frequency in ["Morning", "Afternoon", "Evening"] else 0
                    )
                with col3:
                    status = st.selectbox("Status", ["Given", "Pending", "Skipped"])

                # Step 5: Update button
                if st.button("Update Record"):
                    if selected_prescription_id:
                        cur = conn.cursor(dictionary=True)

                        # Combine selected date with current time for timestamp to store admin_time
                        timestamp = datetime.combine(selected_date, datetime.now().time())

                        # Create explicit date bounds (safer than DATE(...) equality)
                        start_of_day = datetime.combine(selected_date, datetime.min.time())
                        next_day = start_of_day + pd.Timedelta(days=1)  # using pandas Timedelta for simplicity

                        # Use string formatted date-times for predictable param passing
                        start_str = start_of_day.strftime("%Y-%m-%d %H:%M:%S")
                        next_str = next_day.strftime("%Y-%m-%d %H:%M:%S")

                        # Check if record already exists for that prescription + frequency + nurse on that date
                        cur.execute("""
                            SELECT admin_id FROM Medicine_Administration
                            WHERE prescription_id = %s
                              AND frequency = %s
                              AND nurse_emp_id = %s
                              AND admin_time >= %s
                              AND admin_time < %s
                        """, (selected_prescription_id, time_slot, nurse_id, start_str, next_str))
                        existing = cur.fetchone()

                        if existing:
                            cur.execute("""
                                UPDATE Medicine_Administration
                                SET status = %s, remarks = %s, admin_time = %s
                                WHERE admin_id = %s
                            """, (status, remarks, timestamp, existing["admin_id"]))
                            st.success(f" Updated {selected_med_label} for {selected_date} ({time_slot}).")
                        else:
                            cur.execute("""
                                INSERT INTO Medicine_Administration
                                    (prescription_id, nurse_emp_id, admin_time, status, remarks, frequency)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (selected_prescription_id, nurse_id, timestamp, status, remarks, time_slot))
                            st.success(f" Inserted {selected_med_label} for {selected_date} ({time_slot}).")

                        conn.commit()
                        cur.close()
            else:
                st.info("No prescriptions found for this patient.")
        except ValueError:
            st.error("Patient ID (CID) should be numeric. Remove spaces/letters.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

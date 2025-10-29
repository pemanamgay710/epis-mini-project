import streamlit as st
import pandas as pd
import mysql.connector
import os

def patient_dashboard(conn):
    # HEADER + LOGOUT 
    col1, col2 = st.columns([6, 1])
    with col1:
        st.header("Patient Panel - View Reports & Prescriptions")
    with col2:
        if st.button("Logout"):
            for key in ["user", "page", "cid", "prescriptions", "reports"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["page"] = "login_page"  # Redirect to login
            st.success("You have been logged out.")
            st.rerun()  #  Refresh to apply logout immediately

    # Preserve CID in session state 
    if 'cid' not in st.session_state:
        st.session_state.cid = ""
    cid_input = st.text_input("Enter your CID to view your records", value=st.session_state.cid)
    
    if st.button("Fetch My Data"):
        st.session_state.cid = cid_input  # Save CID to session state

        cur = conn.cursor(dictionary=True)

        # PRESCRIPTIONS 
        cur.execute("""
            SELECT 
                prescription_id, 
                name AS medicine, 
                dosage, 
                start_date, 
                end_date, 
                frequency, 
                doctor_emp_id
            FROM Prescription 
            WHERE CID_no = %s
        """, (st.session_state.cid,))
        prescriptions = pd.DataFrame(cur.fetchall())
        st.session_state.prescriptions = prescriptions  # Save to session state

        # LAB REPORTS 
        cur.execute("""
            SELECT 
                tr.report_id, 
                tr.file_path, 
                tr.date_uploaded, 
                lt.test_name
            FROM Test_Report tr
            JOIN Lab_Test lt ON tr.test_id = lt.test_id
            WHERE lt.CID_no = %s
            ORDER BY tr.date_uploaded DESC
        """, (st.session_state.cid,))
        reports = pd.DataFrame(cur.fetchall())
        st.session_state.reports = reports  # Save to session state

        cur.close()

    # Display PRESCRIPTIONS 
    if 'prescriptions' in st.session_state and not st.session_state.prescriptions.empty:
        st.subheader("Prescriptions")
        prescriptions_grouped = (
            st.session_state.prescriptions.groupby(
                ["medicine", "dosage", "start_date", "end_date", "doctor_emp_id"],
                as_index=False
            )
            .agg({"frequency": lambda x: ", ".join(sorted(set(x)))})
        )
        st.dataframe(prescriptions_grouped, use_container_width=True)
    elif 'prescriptions' in st.session_state:
        st.info("No prescriptions found for this CID.")

    # Display LAB REPORTS 
    if 'reports' in st.session_state and not st.session_state.reports.empty:
        st.subheader("Test Reports")
        st.write("All available reports:")
        for idx, row in st.session_state.reports.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(row['test_name'])
            col2.write(str(row['date_uploaded']))
            
            file_path = row['file_path']
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    col3.download_button(
                        label="Download",
                        data=f,
                        file_name=os.path.basename(file_path)
                    )
            else:
                col3.write("File missing")
    elif 'reports' in st.session_state:
        st.info("No reports found for this CID.")

import streamlit as st
import pandas as pd
import mysql.connector
import os


def lab_technician_dashboard(conn):
    
    # ------------------- HEADER + LOGOUT -------------------
    col1, col2 = st.columns([6, 1])
    with col1:
        st.header("Lab Technician Panel")
    with col2:
        if st.button("Logout"):
            for key in ["user", "page", "lab_id"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["page"] = "login_page"
            st.success("You have been logged out.")
            st.rerun()


    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT lt.test_id, p.name AS patient_name, lt.test_name, lt.date_ordered, d.name AS doctor_name
        FROM Lab_Test lt
        JOIN Patient p ON lt.CID_no = p.CID_no
        LEFT JOIN Doctor d ON lt.doctor_emp_id = d.doctor_emp_id
        WHERE lt.test_id NOT IN (SELECT test_id FROM Test_Report)
    """)
    pending_tests = pd.DataFrame(cur.fetchall())
    st.subheader("Pending Lab Tests")
    st.dataframe(pending_tests)

    # --- Upload Report ---
    # lab_technician.py snippet
    with st.form("upload_form"):
        test_id = st.text_input("Enter Test ID")
        report_file = st.file_uploader("Upload PDF Report", type=["pdf"])
        submitted = st.form_submit_button("Upload Report")

        if submitted:
            if not test_id.strip():
                st.error("Enter Test ID.")
            elif not report_file:
                st.error("Choose a PDF report file to upload.")
            else:
                os.makedirs("reports", exist_ok=True)
                file_path = os.path.join("reports", report_file.name)
                with open(file_path, "wb") as f:
                    f.write(report_file.getbuffer())

                cur.execute(
                    "INSERT INTO Test_Report (file_path, date_uploaded, test_id) VALUES (%s, CURDATE(), %s)",
                    (file_path, test_id)
                )
                conn.commit()
                st.success("Report uploaded successfully.")

    cur.close()
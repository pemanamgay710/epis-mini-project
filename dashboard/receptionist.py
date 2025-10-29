import streamlit as st
import pandas as pd
import mysql.connector
import datetime

def receptionist_dashboard(conn):

    col1, col2 = st.columns([6, 1])
    with col1:
        st.header("Receptionist Panel - Register New Patient")
    with col2:
        if st.button("Logout"):
            for key in ["user", "page", "refresh"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["page"] = "login_page"
            st.success("You have been logged out.")
            st.rerun()

    dzongkhags = [
        "Thimphu", "Paro", "Punakha", "Wangdue Phodrang", "Bumthang", "Trongsa",
        "Zhemgang", "Sarpang", "Tsirang", "Dagana", "Chhukha", "Samtse",
        "Haa", "Mongar", "Trashigang", "Trashiyangtse", "Pemagatshel",
        "Samdrup Jongkhar", "Lhuentse", "Gasa"
    ]

    # Collapsible section for viewing registered patients 
    with st.expander("View Registered Patients"):
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT CID_no, name, DOB, gender, contact, address FROM Patient")
                patients = cur.fetchall()
            if patients:
                df_patients = pd.DataFrame(patients)
                st.dataframe(df_patients)
            else:
                st.info("No patients registered yet.")
        except mysql.connector.Error as e:
            st.error(f"Database Error: {e}")

    # --- Registration Form ---
    st.subheader("Register New Patient")
    
    if "refresh" not in st.session_state:
        st.session_state.refresh = 0

    with st.form("register_form"):
        cid = st.text_input("CID No (11 digits only)")
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        contact = st.text_input("Contact Number")

        # Dzongkhag selection only
        dzongkhag = st.selectbox("Dzongkhag", ["Select Dzongkhag"] + dzongkhags)

        # Address is just Dzongkhag
        address = ""
        if dzongkhag != "Select Dzongkhag":
            address = dzongkhag
            

        submitted = st.form_submit_button("💾 Register Patient")

        if submitted:
            # --- Validation ---
            if not cid.isdigit():
                st.error("CID must be numeric.")
            elif len(cid) != 11:
                st.error(" CID must be exactly 11 digits.")
            elif not name.strip():
                st.error(" Name cannot be empty.")
            elif not contact.isdigit():
                st.error(" Contact must be numeric.")
            elif dzongkhag == "-- Select Dzongkhag --":
                st.error(" Please select a Dzongkhag.")
            else:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO Patient (CID_no, name, DOB, gender, contact, address)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (cid, name, dob, gender, contact, address)
                    )
                    conn.commit()
                    st.success(f"Patient '{name}' from {address} registered successfully.")
                    st.session_state.refresh += 1
                except mysql.connector.IntegrityError:
                    st.error("A patient with this CID already exists.")
                except Exception as e:
                    st.error(f"Database error: {e}")
                finally:
                    cur.close()

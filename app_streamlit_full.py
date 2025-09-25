# ----------------------------
# app_streamlit_full_clean.py
# ----------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3
from datetime import datetime
from joblib import load
import os

# ----------------------------
# Session State Defaults
# ----------------------------
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# ----------------------------
# SQLite Database Setup
# ----------------------------
DB_NAME = "maternal_health.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            age INTEGER,
            diastolic_bp REAL,
            bs REAL,
            body_temp REAL,
            risk_level TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ----------------------------
# Database Operations
# ----------------------------
def add_user(username, password, role):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (username,password,role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def save_history(username, age, diastolic_bp, bs, body_temp, risk_level):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO history (username, age, diastolic_bp, bs, body_temp, risk_level, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, age, diastolic_bp, bs, body_temp, risk_level, date_str))
    conn.commit()
    conn.close()

def get_patient_history(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT age, diastolic_bp, bs, body_temp, risk_level, date FROM history WHERE username=? ORDER BY date ASC", (username,))
    data = c.fetchall()
    conn.close()
    decoded_data = []
    for row in data:
        age, bp, bs_val, temp, risk, date = row
        if isinstance(risk, bytes):
            risk = risk.decode('utf-8')
        decoded_data.append((age, bp, bs_val, temp, risk, date))
    return decoded_data

def get_all_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, age, diastolic_bp, bs, body_temp, risk_level, date FROM history ORDER BY date ASC")
    data = c.fetchall()
    conn.close()
    decoded_data = []
    for row in data:
        username, age, bp, bs_val, temp, risk, date = row
        if isinstance(risk, bytes):
            risk = risk.decode('utf-8')
        decoded_data.append((username, age, bp, bs_val, temp, risk, date))
    return decoded_data

# ----------------------------
# Load Model and Scaler
# ----------------------------
BASE_DIR = os.path.dirname(__file__)
scaler = load(os.path.join(BASE_DIR, "scaler.pkl"))
model = load(os.path.join(BASE_DIR, "final_model.pkl"))

# ----------------------------
# Personalized Advice
# ----------------------------
def get_personalized_advice(age, diastolic, bs, body_temp, risk_level):
    advice = []

    if diastolic > 90:
        advice.append("⚠️ Your blood pressure is high. Monitor regularly and consult your doctor.")
    elif diastolic < 60:
        advice.append("⚠️ Your blood pressure is low. Stay hydrated and rest adequately.")

    if bs > 20:
        advice.append("⚠️ Your blood sugar is high. Avoid sugary foods and monitor regularly.")
    elif bs < 4:
        advice.append("⚠️ Your blood sugar is low. Eat small frequent meals.")

    if body_temp > 100.4:
        advice.append("⚠️ You have a high body temperature. Monitor for fever.")
    elif body_temp < 97:
        advice.append("⚠️ Your body temperature is low. Keep warm.")

    general_advice = {
        "Low": ["✅ Maintain a healthy diet and regular prenatal check-ups."],
        "Medium": ["⚠️ Monitor vital signs more frequently."],
        "High": ["❌ Seek immediate consultation with your doctor."]
    }

    advice.extend(general_advice.get(risk_level, []))
    return advice

# ----------------------------
# Login / Signup
# ----------------------------
def login_page():
    st.title("👩‍⚕️ Maternal Health Risk Dashboard")
    st.subheader("🔐 Login / Signup")
    menu = ["Login","Signup"]
    choice = st.radio("Select Action", menu)
    if choice=="Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            role = check_user(username,password)
            if role:
                st.session_state["username"] = username
                st.session_state["role"] = role
                st.success(f"Logged in as {role}")
                st.stop()
            else:
                st.error("❌ Invalid username or password")
    else:
        username = st.text_input("New Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["patient","nurse","doctor"])
        if st.button("Signup"):
            try:
                add_user(username,password,role)
                st.success("✅ Signup successful! Please login.")
            except:
                st.error("❌ Username already exists")

# ----------------------------
# Dashboard
# ----------------------------
def dashboard():
    username = st.session_state["username"]
    role = st.session_state["role"]

    # Sidebar
    st.sidebar.title("👩‍⚕️ Dashboard")
    if role=="patient":
        menu_items = ["🏠 Home","🩺 Predict Risk","📜 History & Trends","🚪 Logout"]
    elif role=="doctor":
        menu_items = ["🏠 Home","🩺 All Patients","🚪 Logout"]
    elif role=="nurse":
        menu_items = ["🏠 Home","🩺 Predict Risk","📜 Patient History","🚪 Logout"]

    menu = st.sidebar.radio("Menu", menu_items)

    # --- Home ---
    if menu=="🏠 Home":
        st.title(f"Welcome, {username.capitalize()} ({role})")
        st.info("Use the sidebar to navigate through the dashboard.")

    # --- Predict Risk ---
    elif menu=="🩺 Predict Risk":
        st.title("🩺 Predict Maternal Health Risk")
        age = st.number_input("Age", 10, 60)
        diastolic = st.number_input("Diastolic BP", 40, 120)
        bs = st.number_input("Blood Sugar Level", 0.0, 30.0)
        body_temp = st.number_input("Body Temperature", 95.0, 105.0)

        if st.button("Predict Risk"):
            data = np.array([[age, diastolic, bs, body_temp]])
            X_scaled = scaler.transform(data)
            pred_code = model.predict(X_scaled)[0]
            risk_map = {0: "Low", 1: "Medium", 2: "High"}
            pred_label = risk_map.get(pred_code, "Unknown")

            st.subheader(f"⚠️ Predicted Risk Level: {pred_label}")

            personalized_tips = get_personalized_advice(age, diastolic, bs, body_temp, pred_label)
            color_map = {"Low":"green","Medium":"orange","High":"red"}
            with st.expander("💡 Personalized Recommendations", expanded=True):
                for tip in personalized_tips:
                    st.markdown(f"<span style='color:{color_map[pred_label]}; font-weight:bold'>{tip}</span>", unsafe_allow_html=True)

            save_history(username, age, diastolic, bs, body_temp, pred_label)
            st.success("✅ Record saved to history.")

    # --- History & Trends ---
    elif menu=="📜 History & Trends" or menu=="📜 Patient History":
        st.title("📜 Patient History & Trends")
        history = get_patient_history(username)
        if history:
            df_patient = pd.DataFrame(history, columns=["Age","Blood Pressure","Glucose","BodyTemp","Risk Level","Date"])
            df_patient["Date"] = pd.to_datetime(df_patient["Date"])
            st.subheader("🗂 Latest Records")

            def highlight_risk(val):
                color = ""
                if val=="High": color="red"
                elif val=="Medium": color="orange"
                elif val=="Low": color="green"
                return f"color: {color}; font-weight:bold"

            st.dataframe(df_patient.style.applymap(highlight_risk, subset=['Risk Level']))

            # Metrics Cards
            avg_bp = df_patient["Blood Pressure"].mean()
            avg_glucose = df_patient["Glucose"].mean()
            high_risk = df_patient["Risk Level"].value_counts().get("High",0)
            medium_risk = df_patient["Risk Level"].value_counts().get("Medium",0)
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("Avg BP", f"{avg_bp:.1f}")
            col2.metric("Avg Glucose", f"{avg_glucose:.1f}")
            col3.metric("High Risk Count", f"{high_risk}")
            col4.metric("Medium Risk Count", f"{medium_risk}")

            # Interactive Charts
            col1, col2 = st.columns(2)
            fig_bp = px.line(
                df_patient, x="Date", y="Blood Pressure", markers=True,
                title="🩺 BP Trend", color="Risk Level",
                color_discrete_map={"Low":"green","Medium":"orange","High":"red"},
                hover_data={"Age": True, "Blood Pressure": True, "Risk Level": True}
            )
            fig_bp.update_traces(mode="lines+markers", line_shape="spline")
            fig_bp.update_layout(hovermode="x unified", autosize=True)
            col1.plotly_chart(fig_bp, use_container_width=True)

            fig_glucose = px.line(
                df_patient, x="Date", y="Glucose", markers=True,
                title="🍬 Glucose Trend", color="Risk Level",
                color_discrete_map={"Low":"green","Medium":"orange","High":"red"},
                hover_data={"Age": True, "Glucose": True, "Risk Level": True}
            )
            fig_glucose.update_traces(mode="lines+markers", line_shape="spline")
            fig_glucose.update_layout(hovermode="x unified", autosize=True)
            col2.plotly_chart(fig_glucose, use_container_width=True)

        else:
            st.info("No patient history available yet.")

    # --- Doctor Dashboard ---
    elif menu=="🩺 All Patients" and role=="doctor":
        st.title("🩺 All Patients Dashboard")
        all_history = get_all_history()
        if all_history:
            df_all = pd.DataFrame(all_history, columns=["Username","Age","Blood Pressure","Glucose","BodyTemp","Risk Level","Date"])
            df_all["Date"] = pd.to_datetime(df_all["Date"])

            risk_filter = st.selectbox("Filter by Risk Level", ["All","Low","Medium","High"])
            if risk_filter != "All":
                df_all = df_all[df_all["Risk Level"] == risk_filter]

            def highlight_risk_doctor(val):
                color = ""
                if val=="High": color="red"
                elif val=="Medium": color="orange"
                elif val=="Low": color="green"
                return f"color: {color}; font-weight:bold"

            st.dataframe(df_all.style.applymap(highlight_risk_doctor, subset=["Risk Level"]))
        else:
            st.info("No patient records found yet.")

    # --- Logout ---
    elif menu=="🚪 Logout":
        st.session_state["username"] = None
        st.session_state["role"] = None
        st.success("Logged out successfully!")
        st.stop()

# ----------------------------
# Run App
# ----------------------------
if st.session_state["username"] is None:
    login_page()
else:
    dashboard()

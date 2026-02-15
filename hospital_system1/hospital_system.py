import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display


# ---------------- إعداد الصفحة ----------------
st.set_page_config(
    page_title="نظام المستشفى",
    layout="wide",
    page_icon="🏥"
)


# ---------------- قاعدة البيانات ----------------
conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()


def setup_db():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Patients(
        id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Doctors(
        id INTEGER PRIMARY KEY,
        name TEXT,
        spec TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Appointments(
        id INTEGER PRIMARY KEY,
        patient TEXT,
        doctor TEXT,
        date TEXT,
        time TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pharmacy(
        id INTEGER PRIMARY KEY,
        medicine TEXT,
        price REAL,
        quantity INTEGER
    )
    """)

    conn.commit()


setup_db()


# ---------------- PDF عربي ----------------

class ArabicPDF(FPDF):

    def header(self):
        self.set_font("Arial", "", 14)
        self.cell(0, 10, txt="تقرير المستشفى", ln=True, align="C")
        self.ln(5)


def ar(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def generate_pdf(title, df):

    pdf = ArabicPDF()
    pdf.add_page()

    pdf.add_font("Arial", "", fname="arial.ttf", uni=True)
    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 10, ar(title), ln=True, align="C")
    pdf.ln(5)

    for col in df.columns:
        pdf.cell(45, 8, ar(col), border=1)

    pdf.ln()

    for row in df.values:
        for item in row:
            pdf.cell(45, 8, ar(str(item)), border=1)
        pdf.ln()

    file = f"report_{datetime.now().strftime('%H%M%S')}.pdf"

    pdf.output(file)

    return file


# ---------------- الواجهة ----------------

st.title("🏥 نظام إدارة المستشفى")

tabs = st.tabs([
    "👥 المرضى",
    "👨‍⚕️ الأطباء",
    "📅 الحجوزات",
    "💊 الصيدلية",
    "📄 التقارير"
])


# ================= المرضى =================

with tabs[0]:

    st.subheader("إضافة مريض")

    with st.form("add_patient"):
        name = st.text_input("اسم المريض")
        phone = st.text_input("الهاتف")

        if st.form_submit_button("حفظ"):

            cursor.execute(
                "INSERT INTO Patients VALUES(NULL,?,?)",
                (name, phone)
            )

            conn.commit()
            st.success("تمت الإضافة")


    st.divider()
    st.subheader("قائمة المرضى")

    search = st.text_input("🔍 بحث عن مريض")

    df = pd.read_sql("SELECT * FROM Patients", conn)

    if search:
        df = df[df["name"].str.contains(search, case=False)]

    st.dataframe(df, use_container_width=True)


# ================= الأطباء =================

with tabs[1]:

    st.subheader("إضافة طبيب")

    with st.form("add_doctor"):

        name = st.text_input("اسم الطبيب")
        spec = st.text_input("التخصص")

        if st.form_submit_button("حفظ"):

            cursor.execute(
                "INSERT INTO Doctors VALUES(NULL,?,?)",
                (name, spec)
            )

            conn.commit()

            st.success("تم الحفظ")


    df = pd.read_sql("SELECT * FROM Doctors", conn)
    st.dataframe(df, use_container_width=True)


# ================= الحجوزات =================

with tabs[2]:

    patients = pd.read_sql("SELECT name FROM Patients", conn)["name"]
    doctors = pd.read_sql("SELECT name FROM Doctors", conn)["name"]

    with st.form("add_app"):

        p = st.selectbox("المريض", patients)
        d = st.selectbox("الطبيب", doctors)

        date = st.date_input("التاريخ")
        time = st.time_input("الوقت")

        if st.form_submit_button("حجز"):

            cursor.execute("""
            INSERT INTO Appointments VALUES(NULL,?,?,?,?)
            """, (p, d, str(date), str(time)))

            conn.commit()

            st.success("تم الحجز")


    df = pd.read_sql("SELECT * FROM Appointments", conn)
    st.dataframe(df, use_container_width=True)


# ================= الصيدلية =================

with tabs[3]:

    st.subheader("إضافة دواء")

    with st.form("add_med"):

        name = st.text_input("اسم الدواء")
        price = st.number_input("السعر", 0.0)
        qty = st.number_input("الكمية", 1)

        if st.form_submit_button("إضافة"):

            cursor.execute("""
            INSERT INTO Pharmacy VALUES(NULL,?,?,?)
            """, (name, price, qty))

            conn.commit()

            st.success("تمت الإضافة")


    df = pd.read_sql("SELECT * FROM Pharmacy", conn)
    st.dataframe(df, use_container_width=True)


# ================= التقارير =================

with tabs[4]:

    st.subheader("طباعة التقارير PDF")

    option = st.selectbox(
        "اختر التقرير",
        ["المرضى", "الأطباء", "الحجوزات", "الصيدلية"]
    )

    if option == "المرضى":
        df = pd.read_sql("SELECT * FROM Patients", conn)

    elif option == "الأطباء":
        df = pd.read_sql("SELECT * FROM Doctors", conn)

    elif option == "الحجوزات":
        df = pd.read_sql("SELECT * FROM Appointments", conn)

    else:
        df = pd.read_sql("SELECT * FROM Pharmacy", conn)


    st.dataframe(df, use_container_width=True)


    if st.button("📄 إنشاء PDF"):

        file = generate_pdf(option, df)

        with open(file, "rb") as f:

            st.download_button(
                "تحميل التقرير",
                f,
                file_name=file
            )

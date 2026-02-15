import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نظام إدارة المستشفى الذكي", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم البنفسجي المتقدم (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #ffffff; }
    h1, h2, h3, h4, p, label { color: #6d28d9 !important; font-weight: 700; }
    .custom-card {
        background: #ffffff; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #ddd6fe; box-shadow: 0 4px 10px rgba(109, 40, 217, 0.05);
        transition: all 0.3s ease-in-out; margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%) !important;
        color: white !important; border-radius: 15px !important; height: 55px !important;
        font-weight: bold !important; border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. إدارة البيانات ---
conn = sqlite3.connect("hospital_system_v21.db", check_same_thread=False)
cursor = conn.cursor()

def repair_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    conn.commit()

repair_db()

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align:center;'>🏥 نظام إدارة المستشفى الذكي</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الملخص", "👥 المرضى", "👨‍⚕️ الأطباء", "📅 الحجوزات", "💊 الصيدلية", "🩸 مصرف الدم"])

# -- 1. الملخص الإحصائي --
with tabs[0]:
    p_num = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_num = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_num = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='custom-card'><h3>👤 المرضى</h3><h1>{p_num}</h1></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='custom-card'><h3>👨‍⚕️ الأطباء</h3><h1>{d_num}</h1></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='custom-card'><h3>📅 الحجوزات</h3><h1>{a_num}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (تعديل: الجدول يظهر تحت الإضافة مباشرة) --
with tabs[1]:
    st.markdown("### 📝 تسجيل مريض جديد")
    
    # نموذج الإضافة
    with st.form("p_form", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        name = col_in1.text_input("اسم المريض الكامل")
        phone = col_in2.text_input("رقم الهاتف")
        submit_p = st.form_submit_button("إضافة المريض ✅")
        
        if submit_p:
            if name and phone:
                cursor.execute("INSERT INTO Patients (name, phone) VALUES (?,?)", (name, phone))
                conn.commit()
                st.success(f"تم تسجيل المريض: {name}")
                st.rerun() # تحديث الصفحة لظهور المريض في الجدول بالأسفل
            else:
                st.warning("يرجى إدخال كافة البيانات")

    st.markdown("---")
    st.markdown("### 📋 قائمة المرضى المسجلين")
    
    # جلب وعرض الجدول أسفل النموذج مباشرة
    df_patients = pd.read_sql("SELECT id as 'التسلسل', name as 'اسم المريض', phone as 'رقم الهاتف' FROM Patients ORDER BY id DESC", conn)
    if not df_patients.empty:
        st.dataframe(df_patients, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين حالياً.")

# -- (بقية التبويبات تبقى كما هي لضمان استقرار النظام) --
with tabs[2]:
    st.markdown("### 👨‍⚕️ الكادر الطبي")
    # ... نفس كود الأطباء السابق ...
    docs = cursor.execute("SELECT name, spec, status FROM Doctors").fetchall()
    for doc in docs:
        st.markdown(f"<div style='background:#f5f3ff; border-right:6px solid #7c3aed; padding:15px; margin-bottom:10px; border-radius:10px;'><h4> د. {doc[0]}</h4><p>{doc[1]} - {doc[2]}</p></div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("### 📅 الحجوزات")
    # ... كود المواعيد ...
    df_app = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ' FROM Appointments", conn)
    st.dataframe(df_app, use_container_width=True)

with tabs[4]:
    st.markdown("### 💊 الصيدلية")
    df_pharm = pd.read_sql("SELECT med_name as 'الدواء', price as 'السعر', quantity as 'الكمية' FROM Pharmacy", conn)
    st.dataframe(df_pharm, use_container_width=True)

with tabs[5]:
    st.markdown("### 🩸 مصرف الدم")
    df_blood = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المتوفر' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_blood, use_container_width=True)

conn.close()

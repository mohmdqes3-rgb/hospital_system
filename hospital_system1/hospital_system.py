import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نظام إدارة المستشفى الذكي", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم والتحكم في اتجاه الجداول (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #ffffff; }

    /* تنسيق الجداول لتكون من اليمين لليسار */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    h1, h2, h3, h4, p, label { color: #6d28d9 !important; font-weight: 700; }

    .custom-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 2px solid #ddd6fe;
        box-shadow: 0 4px 10px rgba(109, 40, 217, 0.05);
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
    }

    .doc-card {
        background: #f5f3ff;
        border-right: 6px solid #7c3aed;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        transition: 0.3s;
    }

    .stButton>button {
        background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        height: 55px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
    }

    .stTabs [data-baseweb="tab-list"] { background-color: #f5f3ff; border-radius: 15px; direction: rtl; }
    .stTabs [aria-selected="true"] { background-color: #7c3aed !important; color: white !important; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. إدارة البيانات (إضافة حقل العمر) ---
conn = sqlite3.connect("hospital_complete_v22.db", check_same_thread=False)
cursor = conn.cursor()

def setup_db():
    # جدول المرضى مع حقل العمر
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    conn.commit()

setup_db()

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align:center;'>🏥 نظام إدارة المستشفى العالمي</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الملخص", "👥 المرضى", "👨‍⚕️ الأطباء", "📅 الحجوزات", "💊 الصيدلية", "🩸 مصرف الدم"])

# -- 1. الملخص الإحصائي --
with tabs[0]:
    p_num = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_num = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_num = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_num = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='custom-card'><h3>👤 المرضى</h3><h1>{p_num}</h1></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='custom-card'><h3>👨‍⚕️ الأطباء</h3><h1>{d_num}</h1></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='custom-card'><h3>📅 الحجوزات</h3><h1>{a_num}</h1></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='custom-card'><h3>💊 الأدوية</h3><h1>{m_num}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (مع العمر والجدول بالأسفل RTL) --
with tabs[1]:
    st.markdown("### 📝 تسجيل مريض جديد")
    with st.form("p_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 2])
        p_name = col1.text_input("اسم المريض")
        p_age = col2.number_input("العمر", min_value=1, max_value=120)
        p_phone = col3.text_input("رقم الهاتف")
        
        if st.form_submit_button("إضافة المريض ✅"):
            if p_name and p_phone:
                cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (p_name, p_age, p_phone))
                conn.commit()
                st.success(f"تمت إضافة المريض {p_name}")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 جدول بيانات المرضى")
    df_p = pd.read_sql("SELECT id as 'ID', name as 'الاسم', age as 'العمر', phone as 'الهاتف' FROM Patients ORDER BY id DESC", conn)
    st.dataframe(df_p, use_container_width=True)

# -- 3. الأطباء --
with tabs[2]:
    st.markdown("### 👨‍⚕️ إدارة الكادر الطبي")
    c_add, c_view = st.columns([1, 2])
    with c_add:
        with st.form("d_form"):
            dn = st.text_input("اسم الدكتور")
            ds = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية", "أخرى"])
            dst = st.selectbox("الحالة", ["متوفر", "في عملية", "إجازة"])
            if st.form_submit_button("حفظ الطبيب"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?,?)", (dn, ds, dst))
                conn.commit()
                st.rerun()
    with c_view:
        docs = cursor.execute("SELECT name, spec, status FROM Doctors").fetchall()
        for doc in docs:
            st.markdown(f"<div class='doc-card'><h4>👨‍⚕️ د. {doc[0]}</h4><p>التخصص: {doc[1]} | الحالة: {doc[2]}</p></div>", unsafe_allow_html=True)

# -- 4. الحجوزات --
with tabs[3]:
    st.markdown("### 📅 جدولة المواعيد")
    patients = [r[0] for r in cursor.execute("SELECT name FROM Patients").fetchall()]
    doctors = [r[0] for r in cursor.execute("SELECT name FROM Doctors").fetchall()]
    
    with st.form("app_form"):
        cc1, cc2, cc3, cc4 = st.columns(4)
        ps = cc1.selectbox("المريض", patients if patients else ["لا يوجد"])
        ds = cc2.selectbox("الطبيب", doctors if doctors else ["لا يوجد"])
        ad = cc3.date_input("التاريخ")
        at = cc4.time_input("الوقت")
        if st.form_submit_button("تأكيد الحجز"):
            cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", (ps, ds, str(ad), str(at)))
            conn.commit()
            st.rerun()
    
    df_a = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ', time as 'الوقت' FROM Appointments", conn)
    st.dataframe(df_a, use_container_width=True)

# -- 5. الصيدلية --
with tabs[4]:
    st.markdown("### 💊 إدارة الصيدلية")
    with st.form("med_form"):
        mc1, mc2, mc3 = st.columns(3)
        mn = mc1.text_input("اسم الدواء")
        mp = mc2.number_input("السعر")
        mq = mc3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة الدواء"):
            cursor.execute("INSERT INTO Pharmacy (med_name, price, quantity) VALUES (?,?,?)", (mn, mp, mq))
            conn.commit()
            st.rerun()
    df_m = pd.read_sql("SELECT med_name as 'الدواء', price as 'السعر', quantity as 'الكمية' FROM Pharmacy", conn)
    st.dataframe(df_m, use_container_width=True)

# -- 6. مصرف الدم --
with tabs[5]:
    st.markdown("### 🩸 بنك الدم")
    with st.form("blood_form"):
        bc1, bc2, bc3 = st.columns(3)
        bd = bc1.text_input("المتبرع")
        bt = bc2.selectbox("الفصيلة", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        bb = bc3.number_input("عدد الأكياس", min_value=1)
        if st.form_submit_button("تحديث بنك الدم"):
            cursor.execute("INSERT INTO BloodBank (donor, type, bags) VALUES (?,?,?)", (bd, bt, bb))
            conn.commit()
            st.rerun()
    df_b = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المتوفر' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_b, use_container_width=True)

conn.close()

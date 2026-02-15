import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="HOSPITAL OS | نظام المستشفى المتكامل", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم العالمي والتأثيرات الحركية (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* إعدادات الاتجاه والخط */
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #fcfaff; }

    /* توسيط نصوص الجدول وجعلها عريضة */
    [data-testid="stDataFrame"] div[data-testid="stTable"] div {
        text-align: center !important;
        justify-content: center !important;
    }
    
    /* CSS لتوسيط محتوى الخلايا في جداول المساعدة */
    th, td { text-align: center !important; vertical-align: middle !important; padding: 15px !important; }

    /* تأثيرات الكروت (تتحرك وتتوهج) */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        border: 1px solid #e9e4ff;
        box-shadow: 0 10px 20px rgba(109, 40, 217, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .custom-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 40px rgba(109, 40, 217, 0.15);
        border-color: #7c3aed;
    }

    /* كروت الأطباء التفاعلية */
    .doc-card {
        background: linear-gradient(145deg, #ffffff, #f5f3ff);
        border-right: 8px solid #7c3aed;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.02);
        transition: 0.3s ease;
    }
    .doc-card:hover {
        background: #7c3aed;
        color: white !important;
        transform: translateX(-10px);
    }
    .doc-card:hover h4, .doc-card:hover p { color: white !important; }

    /* الأزرار الفخمة */
    .stButton>button {
        background: linear-gradient(90deg, #7c3aed, #4c1d95) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 50px !important;
        transition: 0.4s !important;
        border: none !important;
        font-size: 18px !important;
    }
    .stButton>button:hover {
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
        transform: scale(1.02) !important;
    }

    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f3f0ff;
        border-radius: 10px 10px 0 0;
        padding: 10px 30px;
        transition: 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect("hospital_global_v23.db", check_same_thread=False)
cursor = conn.cursor()

def setup_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    conn.commit()

setup_db()

# --- 4. الواجهة البرمجية ---
st.markdown("<h1 style='text-align:center; font-size: 50px; margin-bottom: 30px;'>🏥 HOSPITAL <span style='color:#7c3aed'>PRO</span></h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الإحصائيات", "👥 شؤون المرضى", "👨‍⚕️ الكادر الطبي", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم"])

# -- 1. الملخص الإحصائي (مع التأثيرات الحركية) --
with tabs[0]:
    p_num = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_num = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_num = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_num = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='custom-card'><h3>👥 المرضى</h3><h1 style='font-size:50px;'>{p_num}</h1></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><h3>👨‍⚕️ الأطباء</h3><h1 style='font-size:50px;'>{d_num}</h1></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><h3>📅 الحجوزات</h3><h1 style='font-size:50px;'>{a_num}</h1></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='custom-card'><h3>💊 الأدوية</h3><h1 style='font-size:50px;'>{m_num}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (جدول عريض، بيانات مركزية) --
with tabs[1]:
    st.markdown("### 📝 إضافة سجل مريض")
    with st.expander("اضغط هنا لفتح نموذج التسجيل", expanded=True):
        with st.form("p_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([3, 1, 2])
            p_name = f1.text_input("الاسم الثلاثي")
            p_age = f2.number_input("العمر", 1, 120)
            p_phone = f3.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة مريض جديد ✅"):
                if p_name and p_phone:
                    cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (p_name, p_age, p_phone))
                    conn.commit()
                    st.rerun()

    st.markdown("### 📋 قاعدة بيانات المرضى")
    df_p = pd.read_sql("SELECT id as 'ت', name as 'اسم المريض', age as 'العمر', phone as 'الهاتف' FROM Patients ORDER BY id DESC", conn)
    st.dataframe(df_p, use_container_width=True)

# -- 3. الأطباء (تأثير Hover) --
with tabs[2]:
    st.markdown("### 👨‍⚕️ إدارة الفريق الطبي")
    ca, cv = st.columns([1, 2])
    with ca:
        with st.form("d_form"):
            dn = st.text_input("اسم الطبيب")
            ds = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية", "أعصاب"])
            dst = st.selectbox("الحالة الحالية", ["متوفر", "في عملية", "خارج الخدمة"])
            if st.form_submit_button("حفظ"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?,?)", (dn, ds, dst))
                conn.commit()
                st.rerun()
    with cv:
        docs = cursor.execute("SELECT name, spec, status FROM Doctors").fetchall()
        for doc in docs:
            st.markdown(f"<div class='doc-card'><h4>د. {doc[0]}</h4><p>{doc[1]} | <b>الحالة: {doc[2]}</b></p></div>", unsafe_allow_html=True)

# -- 4. الحجوزات --
with tabs[3]:
    st.markdown("### 📅 نظام الجدولة")
    patients = [r[0] for r in cursor.execute("SELECT name FROM Patients").fetchall()]
    doctors = [r[0] for r in cursor.execute("SELECT name FROM Doctors").fetchall()]
    
    with st.form("app_form"):
        ac1, ac2, ac3, ac4 = st.columns(4)
        p_sel = ac1.selectbox("اختر المريض", patients)
        d_sel = ac2.selectbox("اختر الطبيب", doctors)
        dt = ac3.date_input("تاريخ الموعد")
        tm = ac4.time_input("الوقت")
        if st.form_submit_button("تثبيت الحجز 📅"):
            cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", (p_sel, d_sel, str(dt), str(tm)))
            conn.commit()
            st.rerun()
    
    df_a = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الدكتور', date as 'التاريخ', time as 'الوقت' FROM Appointments", conn)
    st.dataframe(df_a, use_container_width=True)

# -- 5. الصيدلية --
with tabs[4]:
    st.markdown("### 💊 مخزون الصيدلية")
    with st.form("med_form"):
        mc1, mc2, mc3 = st.columns(3)
        mn = mc1.text_input("اسم الدواء")
        mp = mc2.number_input("السعر")
        mq = mc3.number_input("الكمية")
        if st.form_submit_button("إضافة"):
            cursor.execute("INSERT INTO Pharmacy (med_name, price, quantity) VALUES (?,?,?)", (mn, mp, mq))
            conn.commit()
            st.rerun()
    df_m = pd.read_sql("SELECT med_name as 'الدواء', price as 'السعر', quantity as 'المخزون' FROM Pharmacy", conn)
    st.dataframe(df_m, use_container_width=True)

# -- 6. مصرف الدم --
with tabs[5]:
    st.markdown("### 🩸 مصرف الدم المركزي")
    with st.form("blood_form"):
        bc1, bc2, bc3 = st.columns(3)
        donor = bc1.text_input("اسم المتبرع")
        btype = bc2.selectbox("الفصيلة", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        bags = bc3.number_input("أكياس الدم", 1)
        if st.form_submit_button("تسجيل"):
            cursor.execute("INSERT INTO BloodBank (donor, type, bags) VALUES (?,?,?)", (donor, btype, bags))
            conn.commit()
            st.rerun()
    df_b = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المجموع المتاح' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_b, use_container_width=True)

conn.close()

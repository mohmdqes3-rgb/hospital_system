import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="🏥 نظام إدارة المستشفى", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم المتقدم (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* إعدادات الاتجاه والخط العربي */
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f8f7ff; }

    /* تحسين شكل الجداول وجعل البيانات في المنتصف */
    div[data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid #e0d9ff;
    }
    
    /* توسيط نصوص الخلايا وإجبارها على المحاذاة المركزية */
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        text-align: center !important;
        vertical-align: middle !important;
    }

    /* تأثيرات الكروت التفاعلية */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        border: 1px solid #e9e4ff;
        box-shadow: 0 10px 20px rgba(109, 40, 217, 0.05);
        transition: all 0.4s ease;
    }
    .custom-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(109, 40, 217, 0.12);
        border-color: #7c3aed;
    }

    /* كروت الأطباء التفاعلية */
    .doc-card {
        background: white;
        border-right: 8px solid #7c3aed;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        transition: 0.3s ease;
    }
    .doc-card:hover {
        transform: scale(1.02);
        background: #f5f3ff;
    }

    /* الأزرار الفخمة */
    .stButton>button {
        background: linear-gradient(90deg, #7c3aed, #4c1d95) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.01);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect("hospital_final_pro.db", check_same_thread=False)
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
st.markdown("<h1 style='text-align:center;'>🏥 نظام إدارة المستشفى</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الإحصائيات", "👥 شؤون المرضى", "👨‍⚕️ الأطباء", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم"])

# -- 1. الملخص الإحصائي --
with tabs[0]:
    p_num = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_num = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_num = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_num = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='custom-card'><h3>👥 المرضى</h3><h1>{p_num}</h1></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><h3>👨‍⚕️ الأطباء</h3><h1>{d_num}</h1></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><h3>📅 الحجوزات</h3><h1>{a_num}</h1></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='custom-card'><h3>💊 الأدوية</h3><h1>{m_num}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (مع البحث والجدول المطور) --
with tabs[1]:
    st.markdown("### 📝 إضافة مريض جديد")
    with st.expander("فتح نموذج التسجيل"):
        with st.form("p_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([2, 1, 2])
            p_name = f1.text_input("الاسم الكامل")
            p_age = f2.number_input("العمر", 1, 120)
            p_phone = f3.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة المريض ✅"):
                if p_name and p_phone:
                    cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (p_name, p_age, p_phone))
                    conn.commit()
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 البحث وعرض البيانات")
    
    # حقل البحث الذكي
    search_query = st.text_input("ابحث عن مريض (بالاسم أو رقم الهاتف)...")
    
    # جلب البيانات
    query = "SELECT id as 'ت', name as 'اسم المريض', age as 'العمر', phone as 'رقم التواصل' FROM Patients"
    df_p = pd.read_sql(query, conn)
    
    if search_query:
        df_p = df_p[df_p['اسم المريض'].str.contains(search_query, na=False) | df_p['رقم التواصل'].str.contains(search_query, na=False)]
    
    # عرض الجدول بتنسيق عريض وموسط
    st.dataframe(df_p.sort_values(by='ت', ascending=False), use_container_width=True)

# -- 3. الأطباء --
with tabs[2]:
    st.markdown("### 👨‍⚕️ إدارة الفريق الطبي")
    ca, cv = st.columns([1, 2])
    with ca:
        with st.form("d_form"):
            dn = st.text_input("اسم الدكتور")
            ds = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية", "أخرى"])
            dst = st.selectbox("الحالة", ["متوفر", "في عملية", "إجازة"])
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
    st.markdown("### 📅 نظام المواعيد")
    patients_list = [r[0] for r in cursor.execute("SELECT name FROM Patients").fetchall()]
    doctors_list = [r[0] for r in cursor.execute("SELECT name FROM Doctors").fetchall()]
    
    with st.form("app_form"):
        ac1, ac2, ac3, ac4 = st.columns(4)
        p_sel = ac1.selectbox("المريض", patients_list if patients_list else ["لا يوجد"])
        d_sel = ac2.selectbox("الطبيب", doctors_list if doctors_list else ["لا يوجد"])
        dt = ac3.date_input("التاريخ")
        tm = ac4.time_input("الوقت")
        if st.form_submit_button("تثبيت الحجز"):
            cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", (p_sel, d_sel, str(dt), str(tm)))
            conn.commit()
            st.rerun()
    
    df_a = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ', time as 'الوقت' FROM Appointments", conn)
    st.dataframe(df_a, use_container_width=True)

# -- 5. الصيدلية --
with tabs[4]:
    st.markdown("### 💊 إدارة الأدوية")
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
    st.markdown("### 🩸 بنك الدم")
    with st.form("blood_form"):
        bc1, bc2, bc3 = st.columns(3)
        donor = bc1.text_input("المتبرع")
        btype = bc2.selectbox("الفصيلة", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        bags = bc3.number_input("عدد الأكياس", 1)
        if st.form_submit_button("تسجيل"):
            cursor.execute("INSERT INTO BloodBank (donor, type, bags) VALUES (?,?,?)", (donor, btype, bags))
            conn.commit()
            st.rerun()
    df_b = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المتوفر' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_b, use_container_width=True)

conn.close()

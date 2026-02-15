import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="🏥 نظام إدارة المستشفى", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم المطور (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* إعدادات اللغة والخط */
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #fcfaff; }

    /* تصميم الجدول الاحترافي */
    .stDataFrame {
        border: 1px solid #e0d9ff !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
    }
    
    /* إجبار الخلايا على التوسط التام */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        text-align: center !important;
        vertical-align: middle !important;
        padding: 12px !important;
    }

    /* كروت الإحصائيات مع أنيميشن خفيف */
    .custom-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border-bottom: 4px solid #7c3aed;
        box-shadow: 0 10px 25px rgba(109, 40, 217, 0.05);
        transition: 0.3s;
    }
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(109, 40, 217, 0.1);
    }

    /* كروت الأطباء - أنيقة وبدون ألوان مزعجة عند اللمس */
    .doc-card {
        background: white;
        border-right: 6px solid #7c3aed;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: 0.3s ease;
    }
    .doc-card:hover {
        transform: scale(1.01);
        border-right-color: #4c1d95;
        background: #fdfcff;
    }

    /* الأزرار الاحترافية */
    .stButton>button {
        background: linear-gradient(90deg, #7c3aed, #4c1d95) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 48px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect("hospital_final_v3.db", check_same_thread=False)
cursor = conn.cursor()

def setup_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    conn.commit()

setup_db()

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align:center;'>🏥 نظام إدارة المستشفى</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الإحصائيات", "👥 شؤون المرضى", "👨‍⚕️ الأطباء", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم"])

# -- 1. الإحصائيات --
with tabs[0]:
    p_num = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_num = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_num = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_num = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='custom-card'><h3>👥 المرضى</h3><h1>{p_num}</h1></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><h3>👨‍⚕️ الأطباء</h3><h1>{d_num}</h1></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><h3>📅 المواعيد</h3><h1>{a_num}</h1></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='custom-card'><h3>💊 الأدوية</h3><h1>{m_num}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (تصحيح اتجاه الجدول وترتيبه) --
with tabs[1]:
    st.markdown("### 📝 تسجيل مريض جديد")
    with st.expander("اضغط لفتح النموذج"):
        with st.form("p_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([3, 1, 2])
            p_name = f1.text_input("اسم المريض")
            p_age = f2.number_input("العمر", 1, 120)
            p_phone = f3.text_input("رقم التواصل")
            if st.form_submit_button("حفظ البيانات ✅"):
                if p_name and p_phone:
                    cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (p_name, p_age, p_phone))
                    conn.commit()
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 البحث وجدول البيانات")
    
    search_q = st.text_input("ابحث بالاسم أو رقم الهاتف...")
    
    # جلب البيانات وترتيبها برمجياً لتبدأ من اليمين: تسلسل -> اسم -> عمر -> هاتف
    df_p = pd.read_sql("SELECT id as 'التسلسل', name as 'اسم المريض', age as 'العمر', phone as 'رقم الهاتف' FROM Patients", conn)
    
    if search_q:
        df_p = df_p[df_p['اسم المريض'].str.contains(search_q, na=False) | df_p['رقم الهاتف'].str.contains(search_q, na=False)]
    
    # عكس ترتيب الأعمدة لضمان ظهورها من اليمين لليسار في الواجهة
    cols = ['التسلسل', 'اسم المريض', 'العمر', 'رقم الهاتف']
    df_p = df_p[cols]

    # عرض الجدول (البيانات تظهر الآن: التسلسل أقصى اليمين، الهاتف أقصى اليسار)
    st.dataframe(df_p.sort_values('التسلسل', ascending=False), use_container_width=True, hide_index=True)

# -- 3. الأطباء --
with tabs[2]:
    st.markdown("### 👨‍⚕️ الكادر الطبي")
    col_a, col_v = st.columns([1, 2])
    with col_a:
        with st.form("d_form"):
            dn = st.text_input("اسم الدكتور")
            ds = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية", "أخرى"])
            dst = st.selectbox("الحالة", ["متوفر", "في عملية", "إجازة"])
            if st.form_submit_button("إضافة"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?,?)", (dn, ds, dst))
                conn.commit()
                st.rerun()
    with col_v:
        docs = cursor.execute("SELECT name, spec, status FROM Doctors").fetchall()
        for doc in docs:
            st.markdown(f"<div class='doc-card'><b>د. {doc[0]}</b><br><small>{doc[1]} | {doc[2]}</small></div>", unsafe_allow_html=True)

# -- 4. المواعيد --
with tabs[3]:
    st.markdown("### 📅 جدول المواعيد")
    patients = [r[0] for r in cursor.execute("SELECT name FROM Patients").fetchall()]
    doctors = [r[0] for r in cursor.execute("SELECT name FROM Doctors").fetchall()]
    with st.form("app"):
        c1, c2, c3, c4 = st.columns(4)
        ps = c1.selectbox("المريض", patients)
        ds = c2.selectbox("الطبيب", doctors)
        dt = c3.date_input("التاريخ")
        tm = c4.time_input("الوقت")
        if st.form_submit_button("حفظ الحجز"):
            cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", (ps, ds, str(dt), str(tm)))
            conn.commit()
            st.rerun()
    df_app = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ', time as 'الوقت' FROM Appointments", conn)
    st.dataframe(df_app, use_container_width=True, hide_index=True)

# -- 5. الصيدلية --
with tabs[4]:
    st.markdown("### 💊 الصيدلية")
    with st.form("pharm"):
        m1, m2, m3 = st.columns(3)
        mn = m1.text_input("الدواء")
        mp = m2.number_input("السعر")
        mq = m3.number_input("الكمية")
        if st.form_submit_button("إضافة"):
            cursor.execute("INSERT INTO Pharmacy (med_name, price, quantity) VALUES (?,?,?)", (mn, mp, mq))
            conn.commit()
            st.rerun()
    df_ph = pd.read_sql("SELECT med_name as 'الدواء', price as 'السعر', quantity as 'الكمية' FROM Pharmacy", conn)
    st.dataframe(df_ph, use_container_width=True, hide_index=True)

# -- 6. بنك الدم --
with tabs[5]:
    st.markdown("### 🩸 بنك الدم")
    with st.form("blood"):
        b1, b2, b3 = st.columns(3)
        dn = b1.text_input("المتبرع")
        ft = b2.selectbox("الفصيلة", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        bg = b3.number_input("الأكياس", 1)
        if st.form_submit_button("تسجيل"):
            cursor.execute("INSERT INTO BloodBank (donor, type, bags) VALUES (?,?,?)", (dn, ft, bg))
            conn.commit()
            st.rerun()
    df_bl = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المتوفر' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_bl, use_container_width=True, hide_index=True)

conn.close()

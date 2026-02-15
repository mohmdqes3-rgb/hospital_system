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
        background: #ffffff;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 2px solid #ddd6fe;
        box-shadow: 0 4px 10px rgba(109, 40, 217, 0.05);
        transition: all 0.3s ease-in-out;
        margin-bottom: 20px;
    }
    .custom-card:hover {
        transform: translateY(-8px);
        border-color: #7c3aed;
        box-shadow: 0 15px 30px rgba(109, 40, 217, 0.15);
    }

    .doc-card {
        background: #f5f3ff;
        border-right: 6px solid #7c3aed;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .doc-card:hover { transform: scale(1.02); background: #ede9fe; }

    .stButton>button {
        background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        height: 55px !important;
        font-weight: bold !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab-list"] { background-color: #f5f3ff; border-radius: 15px; }
    .stTabs [aria-selected="true"] { background-color: #7c3aed !important; color: white !important; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. إدارة البيانات (إضافة جدول الصيدلية) ---
conn = sqlite3.connect("hospital_system_v20.db", check_same_thread=False)
cursor = conn.cursor()

def repair_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    # إضافة جدول الصيدلية
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    
    conn.commit()

repair_db()

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align:center;'>🏥 نظام إدارة المستشفى الذكي</h1>", unsafe_allow_html=True)

# إضافة الصيدلية إلى التبويبات
tabs = st.tabs(["📊 الملخص", "👥 المرضى", "👨‍⚕️ الأطباء", "📅 الحجوزات", "💊 الصيدلية", "🩸 مصرف الدم"])

# -- 1. الملخص الإحصائي --
with tabs[0]:
    p_num = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_num = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_num = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_num = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0] # إحصائية الأدوية
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='custom-card'><h3>👤 المرضى</h3><h1>{p_num}</h1></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='custom-card'><h3>👨‍⚕️ الأطباء</h3><h1>{d_num}</h1></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='custom-card'><h3>📅 الحجوزات</h3><h1>{a_num}</h1></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='custom-card'><h3>💊 الأدوية</h3><h1>{m_num}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى --
with tabs[1]:
    st.markdown("### 📝 تسجيل مريض")
    with st.form("p_form", clear_on_submit=True):
        name = st.text_input("اسم المريض")
        phone = st.text_input("رقم الهاتف")
        if st.form_submit_button("إضافة المريض ✅"):
            if name and phone:
                cursor.execute("INSERT INTO Patients (name, phone) VALUES (?,?)", (name, phone))
                conn.commit()
                st.balloons()
                st.rerun()
            else:
                st.error("يرجى ملء جميع الحقول")

# -- 3. الأطباء --
with tabs[2]:
    st.markdown("### 👨‍⚕️ إدارة الكادر الطبي")
    col_add, col_view = st.columns([1, 2])
    with col_add:
        with st.form("d_form", clear_on_submit=True):
            d_name = st.text_input("اسم الدكتور")
            d_spec = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية", "أخرى"])
            d_status = st.selectbox("الحالة", ["متوفر", "في عملية", "إجازة"])
            if st.form_submit_button("حفظ الطبيب ✨"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?,?)", (d_name, d_spec, d_status))
                conn.commit()
                st.rerun()
    with col_view:
        docs = cursor.execute("SELECT name, spec, status FROM Doctors").fetchall()
        for doc in docs:
            st.markdown(f"<div class='doc-card'><h4>👨‍⚕️ د. {doc[0]}</h4><p><b>التخصص:</b> {doc[1]} | <b>الحالة:</b> {doc[2]}</p></div>", unsafe_allow_html=True)

# -- 4. الحجوزات --
with tabs[3]:
    st.markdown("### 📅 نظام المواعيد")
    col_res, col_table = st.columns([1, 2])
    with col_res:
        patients = [r[0] for r in cursor.execute("SELECT name FROM Patients").fetchall()]
        doctors = [r[0] for r in cursor.execute("SELECT name FROM Doctors").fetchall()]
        with st.form("app_form", clear_on_submit=True):
            p_sel = st.selectbox("المريض", patients if patients else ["أضف مريض أولاً"])
            d_sel = st.selectbox("الطبيب", doctors if doctors else ["أضف دكتور أولاً"])
            a_date = st.date_input("التاريخ")
            a_time = st.time_input("الوقت")
            if st.form_submit_button("تأكيد الحجز 📅"):
                if patients and doctors:
                    cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", 
                                   (p_sel, d_sel, str(a_date), str(a_time)))
                    conn.commit()
                    st.balloons()
                    st.rerun()
    with col_table:
        df_app = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ', time as 'الوقت' FROM Appointments", conn)
        st.dataframe(df_app, use_container_width=True)

# -- 5. الصيدلية (القسم الجديد) --
with tabs[4]:
    st.markdown("### 💊 إدارة المخزون الدوائي")
    col_med, col_stock = st.columns([1, 2])
    
    with col_med:
        with st.form("med_form", clear_on_submit=True):
            m_name = st.text_input("اسم الدواء")
            m_price = st.number_input("سعر الوحدة", min_value=0.0, step=0.5)
            m_qty = st.number_input("الكمية المتوفرة", min_value=1, step=1)
            if st.form_submit_button("إضافة الدواء 💊"):
                if m_name:
                    cursor.execute("INSERT INTO Pharmacy (med_name, price, quantity) VALUES (?,?,?)", (m_name, m_price, m_qty))
                    conn.commit()
                    st.success("تم إضافة الدواء بنجاح")
                    st.rerun()

    with col_stock:
        df_med = pd.read_sql("SELECT med_name as 'اسم الدواء', price as 'السعر', quantity as 'الكمية' FROM Pharmacy", conn)
        if not df_med.empty:
            st.dataframe(df_med, use_container_width=True)
            total_val = (df_med['السعر'] * df_med['الكمية']).sum()
            st.info(f"إجمالي قيمة المخزون الحالي: {total_val:,.2f} دينار")
        else:
            st.warning("لا توجد أدوية مسجلة في المخزن حالياً.")

# -- 6. مصرف الدم --
with tabs[5]:
    st.markdown("### 🩸 بنك الدم")
    with st.form("b_form"):
        c1, c2, c3 = st.columns(3)
        donor = c1.text_input("المتبرع")
        b_type = c2.selectbox("الفصيلة", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        bags = c3.number_input("الأكياس", 1)
        if st.form_submit_button("تحديث 🩸"):
            cursor.execute("INSERT INTO BloodBank (donor, type, bags) VALUES (?,?,?)", (donor, b_type, bags))
            conn.commit()
            st.snow()
    
    df_blood = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المتوفر' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_blood, use_container_width=True)

conn.close()

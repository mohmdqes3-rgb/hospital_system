import streamlit as st
import sqlite3
import pandas as pd

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="🏥 نظام إدارة المستشفى", layout="wide", page_icon="🏥")

# --- 2. التصميم (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f8f9ff; }
    
    /* توسيط البيانات في الجداول إجبارياً */
    [data-testid="stDataFrame"] div[data-testid="stTable"] div, 
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        text-align: center !important;
        justify-content: center !important;
    }

    /* كروت الإحصائيات */
    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        border-bottom: 5px solid #6d28d9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* الأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #6d28d9, #4c1d95) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect("hospital_final_v5.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    conn.commit()

init_db()

# --- 4. الواجهة ---
st.markdown("<h1 style='text-align:center; color:#6d28d9;'>🏥 نظام إدارة المستشفى</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الملخص", "👥 المرضى", "👨‍⚕️ الأطباء", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم"])

# -- 1. الملخص --
with tabs[0]:
    p_c = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_c = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_c = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_c = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='stat-card'><h3>👥 المرضى</h3><h1>{p_c}</h1></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='stat-card'><h3>👨‍⚕️ الأطباء</h3><h1>{d_c}</h1></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='stat-card'><h3>📅 المواعيد</h3><h1>{a_c}</h1></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='stat-card'><h3>💊 الأدوية</h3><h1>{m_c}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (حل مشكلة الجدول) --
with tabs[1]:
    st.markdown("### ➕ إضافة مريض")
    with st.form("p_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 1, 2])
        name = col1.text_input("الاسم")
        age = col2.number_input("العمر", 1, 120)
        phone = col3.text_input("الهاتف")
        if st.form_submit_button("حفظ ✅"):
            if name and phone:
                cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (name, age, phone))
                conn.commit()
                st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 قائمة المرضى")
    search = st.text_input("ابحث بالاسم...")
    
    # جلب البيانات وترتيب الأعمدة برمجياً لضمان الـ RTL
    df = pd.read_sql("SELECT id as 'التسلسل', name as 'اسم المريض', age as 'العمر', phone as 'رقم الهاتف' FROM Patients ORDER BY id DESC", conn)
    
    if search:
        df = df[df['اسم المريض'].str.contains(search, na=False)]
    
    # عرض الجدول باستخدام st.dataframe مع تفعيل عرض العرض الكامل والتوسط
    st.dataframe(df, use_container_width=True, hide_index=True)

# -- 3. الأطباء --
with tabs[2]:
    st.markdown("### 👨‍⚕️ الكادر الطبي")
    with st.form("d_form"):
        c1, c2 = st.columns(2)
        dn = c1.text_input("اسم الدكتور")
        ds = c2.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية"])
        if st.form_submit_button("إضافة"):
            cursor.execute("INSERT INTO Doctors (name, spec) VALUES (?,?)", (dn, ds))
            conn.commit()
            st.rerun()
    df_d = pd.read_sql("SELECT name as 'الدكتور', spec as 'التخصص' FROM Doctors", conn)
    st.dataframe(df_d, use_container_width=True, hide_index=True)

# -- 4. المواعيد --
with tabs[3]:
    st.markdown("### 📅 المواعيد")
    df_a = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ' FROM Appointments", conn)
    st.dataframe(df_a, use_container_width=True, hide_index=True)

# -- 5. الصيدلية --
with tabs[4]:
    st.markdown("### 💊 الصيدلية")
    with st.form("ph_form"):
        c1, c2, c3 = st.columns(3)
        mn = c1.text_input("الدواء")
        mp = c2.number_input("السعر")
        mq = c3.number_input("الكمية")
        if st.form_submit_button("إضافة دواء"):
            cursor.execute("INSERT INTO Pharmacy (med_name, price, quantity) VALUES (?,?,?)", (mn, mp, mq))
            conn.commit()
            st.rerun()
    df_m = pd.read_sql("SELECT med_name as 'الدواء', price as 'السعر', quantity as 'الكمية' FROM Pharmacy", conn)
    st.dataframe(df_m, use_container_width=True, hide_index=True)

# -- 6. بنك الدم --
with tabs[5]:
    st.markdown("### 🩸 بنك الدم")
    df_b = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'الأكياس' FROM BloodBank GROUP BY type", conn)
    st.dataframe(df_b, use_container_width=True, hide_index=True)

conn.close()

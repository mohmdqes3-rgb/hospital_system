import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="🏥 نظام إدارة المستشفى", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم المتقدم (إصلاح شامل للجدول والاتجاه) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* إعدادات الموقع العام */
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #fcfaff; }

    /* تصميم الجدول الاحترافي المعدل */
    .reportview-container .main .block-container { padding-top: 2rem; }
    
    /* تنسيق الجداول لتكون من اليمين لليسار إجبارياً */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 18px;
        text-align: center;
        border-radius: 15px 15px 0 0;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
        direction: rtl;
    }
    .styled-table font { font-weight: bold; color: #7c3aed; }
    .styled-table thead tr {
        background-color: #7c3aed;
        color: #ffffff;
        text-align: center;
    }
    .styled-table th, .styled-table td { padding: 15px 20px; text-align: center; border-bottom: 1px solid #f3f0ff; }
    .styled-table tbody tr:nth-of-type(even) { background-color: #f9f8ff; }
    .styled-table tbody tr:hover { background-color: #f1ecff; cursor: pointer; transition: 0.3s; }

    /* كروت الإحصائيات الفخمة */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        border-right: 10px solid #7c3aed;
        box-shadow: 0 10px 25px rgba(109, 40, 217, 0.07);
        transition: 0.4s;
    }
    .custom-card:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(109, 40, 217, 0.15); }

    /* كروت الأطباء */
    .doc-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #eee;
        transition: 0.3s;
    }
    .doc-card:hover { border-color: #7c3aed; transform: translateX(-10px); }

    /* الأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #7c3aed, #4c1d95) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. قاعدة البيانات ---
conn = sqlite3.connect("hospital_master_v5.db", check_same_thread=False)
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

tabs = st.tabs(["📊 الملخص", "👥 المرضى", "👨‍⚕️ الأطباء", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم"])

# -- 1. الملخص --
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

# -- 2. شؤون المرضى (الجدول الاحترافي RTL) --
with tabs[1]:
    st.markdown("### 📝 إضافة مريض جديد")
    with st.expander("فتح استمارة التسجيل"):
        with st.form("p_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([3, 1, 2])
            p_name = f1.text_input("الاسم الكامل")
            p_age = f2.number_input("العمر", 1, 120)
            p_phone = f3.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة السجل الآن ✅"):
                if p_name and p_phone:
                    cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (p_name, p_age, p_phone))
                    conn.commit()
                    st.success("تمت الإضافة بنجاح")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 البحث وجدول البيانات (من اليمين لليسار)")
    
    search_val = st.text_input("ابحث عن مريض بالاسم أو الهاتف...")
    
    # جلب البيانات وترتيبها يدوياً
    data = cursor.execute("SELECT id, name, age, phone FROM Patients ORDER BY id DESC").fetchall()
    
    # فلترة البحث برمجياً
    if search_val:
        data = [row for row in data if search_val in str(row[1]) or search_val in str(row[3])]

    # بناء الجدول بنظام HTML لضمان الاتجاه الصحيح تماماً
    table_html = """
    <table class="styled-table">
        <thead>
            <tr>
                <th>التسلسل</th>
                <th>اسم المريض</th>
                <th>العمر</th>
                <th>رقم الهاتف</th>
            </tr>
        </thead>
        <tbody>
    """
    for row in data:
        table_html += f"""
            <tr>
                <td><b>{row[0]}</b></td>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
                <td>{row[3]}</td>
            </tr>
        """
    table_html += "</tbody></table>"
    
    st.markdown(table_html, unsafe_allow_html=True)

# -- بقية السكشنات (الأطباء، المواعيد، الصيدلية، بنك الدم) --
with tabs[2]:
    st.markdown("### 👨‍⚕️ الفريق الطبي")
    col_a, col_v = st.columns([1, 2])
    with col_a:
        with st.form("d_form"):
            dn = st.text_input("اسم الطبيب")
            ds = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية"])
            if st.form_submit_button("حفظ"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?, 'متوفر')", (dn, ds))
                conn.commit()
                st.rerun()
    with col_v:
        docs = cursor.execute("SELECT name, spec FROM Doctors").fetchall()
        for d in docs:
            st.markdown(f"<div class='doc-card'><b>د. {d[0]}</b> - {d[1]}</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("### 📅 الحجوزات")
    df_app = pd.read_sql("SELECT p_name as 'المريض', d_name as 'الطبيب', date as 'التاريخ' FROM Appointments", conn)
    st.table(df_app) # استخدام table التقليدي هنا للتبسيط

with tabs[4]:
    st.markdown("### 💊 الصيدلية")
    df_ph = pd.read_sql("SELECT med_name as 'الدواء', price as 'السعر', quantity as 'المخزون' FROM Pharmacy", conn)
    st.table(df_ph)

with tabs[5]:
    st.markdown("### 🩸 بنك الدم")
    df_bl = pd.read_sql("SELECT type as 'الفصيلة', SUM(bags) as 'المتوفر' FROM BloodBank GROUP BY type", conn)
    st.table(df_bl)

conn.close()

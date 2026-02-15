import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="🏥 نظام إدارة المستشفى", layout="wide", page_icon="🏥")

# --- 2. محرك التصميم العالمي (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* ضبط الخط والاتجاه العام */
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f8f9ff; }

    /* تصميم الجدول الاحترافي العريض */
    .hospital-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 18px;
        border-radius: 12px;
        overflow: hidden;
        background-color: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    .hospital-table thead tr {
        background-color: #6d28d9;
        color: #ffffff;
        text-align: center;
        font-weight: bold;
    }
    .hospital-table th, .hospital-table td {
        padding: 15px 25px;
        text-align: center !important; /* توسيط البيانات */
        border-bottom: 1px solid #eee;
    }
    .hospital-table tbody tr:hover {
        background-color: #f3f0ff;
        transition: 0.3s;
    }

    /* كروت الإحصائيات الفاخرة */
    .stat-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border-bottom: 6px solid #6d28d9;
        box-shadow: 0 10px 25px rgba(109, 40, 217, 0.08);
        transition: 0.4s;
        margin-bottom: 20px;
    }
    .stat-card:hover { transform: translateY(-10px); box-shadow: 0 15px 35px rgba(109, 40, 217, 0.15); }

    /* كروت الأطباء */
    .doctor-item {
        background: white;
        padding: 15px;
        margin-bottom: 10px;
        border-right: 5px solid #6d28d9;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .doctor-item:hover { transform: scale(1.02); background: #fdfcff; }

    /* الأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #6d28d9, #4c1d95) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-weight: 900 !important;
        border: none !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. إدارة قاعدة البيانات ---
conn = sqlite3.connect("hospital_database_pro.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med_name TEXT, price REAL, quantity INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, donor TEXT, type TEXT, bags INTEGER)")
    conn.commit()

init_db()

# --- 4. واجهة المستخدم الرئيسية ---
st.markdown("<h1 style='text-align:center; color:#6d28d9; font-size:45px;'>🏥 نظام إدارة المستشفى</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📊 الملخص الإحصائي", "👥 سجل المرضى", "👨‍⚕️ الكادر الطبي", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم"])

# -- 1. الملخص --
with tabs[0]:
    p_count = cursor.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    d_count = cursor.execute("SELECT COUNT(*) FROM Doctors").fetchone()[0]
    a_count = cursor.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    m_count = cursor.execute("SELECT COUNT(*) FROM Pharmacy").fetchone()[0]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='stat-card'><h3>👥 المرضى</h3><h1 style='color:#6d28d9;'>{p_count}</h1></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat-card'><h3>👨‍⚕️ الأطباء</h3><h1 style='color:#6d28d9;'>{d_count}</h1></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat-card'><h3>📅 المواعيد</h3><h1 style='color:#6d28d9;'>{a_count}</h1></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='stat-card'><h3>💊 الأدوية</h3><h1 style='color:#6d28d9;'>{m_count}</h1></div>", unsafe_allow_html=True)

# -- 2. المرضى (البحث والجدول الاحترافي RTL) --
with tabs[1]:
    st.markdown("### ➕ إضافة مريض جديد")
    with st.expander("فتح نموذج التسجيل", expanded=False):
        with st.form("p_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([3, 1, 2])
            name = col1.text_input("اسم المريض")
            age = col2.number_input("العمر", 1, 120)
            phone = col3.text_input("رقم الهاتف")
            if st.form_submit_button("حفظ السجل ✅"):
                if name and phone:
                    cursor.execute("INSERT INTO Patients (name, age, phone) VALUES (?,?,?)", (name, age, phone))
                    conn.commit()
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 قائمة المرضى المسجلين")
    search_query = st.text_input("ابحث عن مريض بالاسم أو الهاتف...")
    
    # جلب البيانات من القاعدة
    cursor.execute("SELECT id, name, age, phone FROM Patients ORDER BY id DESC")
    rows = cursor.fetchall()
    
    if search_query:
        rows = [r for r in rows if search_query in str(r[1]) or search_query in str(r[3])]

    # بناء جدول HTML احترافي لضمان الترتيب والتوسيط
    table_html = """
    <table class="hospital-table">
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
    for r in rows:
        table_html += f"""
        <tr>
            <td><b>{r[0]}</b></td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

# -- 3. الأطباء --
with tabs[2]:
    st.markdown("### 👨‍⚕️ إدارة الأطباء")
    ca, cv = st.columns([1, 2])
    with ca:
        with st.form("d_form"):
            dn = st.text_input("اسم الدكتور")
            ds = st.selectbox("التخصص", ["باطنية", "جراحة", "أطفال", "قلبية", "أعصاب"])
            if st.form_submit_button("إضافة طبيب"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?, 'متوفر')", (dn, ds))
                conn.commit()
                st.rerun()
    with cv:
        docs = cursor.execute("SELECT name, spec FROM Doctors").fetchall()
        for d in docs:
            st.markdown(f"<div class='doctor-item'><b>د. {d[0]}</b> - {d[1]}</div>", unsafe_allow_html=True)

# -- 4. المواعيد --
with tabs[3]:
    st.markdown("### 📅 جدول المواعيد")
    p_list = [r[0] for r in cursor.execute("SELECT name FROM Patients").fetchall()]
    d_list = [r[0] for r in cursor.execute("SELECT name FROM Doctors").fetchall()]
    with st.form("app_form"):
        cc1, cc2, cc3, cc4 = st.columns(4)
        psel = cc1.selectbox("المريض", p_list if p_list else ["أضف مريضاً"])
        dsel = cc2.selectbox("الطبيب", d_list if d_list else ["أضف طبيباً"])
        date_sel = cc3.date_input("التاريخ")
        time_sel = cc4.time_input("الوقت")
        if st.form_submit_button("تثبيت الموعد"):
            cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", (psel, dsel, str(date_sel), str(time_sel)))
            conn.commit()
            st.rerun()
    
    app_data = cursor.execute("SELECT p_name, d_name, date, time FROM Appointments ORDER BY id DESC").fetchall()
    app_html = "<table class='hospital-table'><thead><tr><th>المريض</th><th>الطبيب</th><th>التاريخ</th><th>الوقت</th></tr></thead><tbody>"
    for a in app_data:
        app_html += f"<tr><td>{a[0]}</td><td>{a[1]}</td><td>{a[2]}</td><td>{a[3]}</td></tr>"
    app_html += "</tbody></table>"
    st.markdown(app_html, unsafe_allow_html=True)

# -- 5. الصيدلية --
with tabs[4]:
    st.markdown("### 💊 مخزون الأدوية")
    with st.form("m_form"):
        m1, m2, m3 = st.columns(3)
        mn = m1.text_input("اسم الدواء")
        mp = m2.number_input("السعر")
        mq = m3.number_input("الكمية")
        if st.form_submit_button("إضافة دواء"):
            cursor.execute("INSERT INTO Pharmacy (med_name, price, quantity) VALUES (?,?,?)", (mn, mp, mq))
            conn.commit()
            st.rerun()
    
    med_data = cursor.execute("SELECT med_name, price, quantity FROM Pharmacy").fetchall()
    med_html = "<table class='hospital-table'><thead><tr><th>الدواء</th><th>السعر</th><th>الكمية</th></tr></thead><tbody>"
    for m in med_data:
        med_html += f"<tr><td>{m[0]}</td><td>{m[1]}</td><td>{m[2]}</td></tr>"
    med_html += "</tbody></table>"
    st.markdown(med_html, unsafe_allow_html=True)

# -- 6. بنك الدم --
with tabs[5]:
    st.markdown("### 🩸 مصرف الدم")
    with st.form("b_form"):
        b1, b2, b3 = st.columns(3)
        donor_name = b1.text_input("المتبرع")
        blood_type = b2.selectbox("الفصيلة", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        bags_num = b3.number_input("عدد الأكياس", 1)
        if st.form_submit_button("تسجيل المتبرع"):
            cursor.execute("INSERT INTO BloodBank (donor, type, bags) VALUES (?,?,?)", (donor_name, blood_type, bags_num))
            conn.commit()
            st.rerun()
    
    blood_data = cursor.execute("SELECT type, SUM(bags) FROM BloodBank GROUP BY type").fetchall()
    blood_html = "<table class='hospital-table'><thead><tr><th>الفصيلة</th><th>المتوفر (أكياس)</th></tr></thead><tbody>"
    for b in blood_data:
        blood_html += f"<tr><td>{b[0]}</td><td>{b[1]}</td></tr>"
    blood_html += "</tbody></table>"
    st.markdown(blood_html, unsafe_allow_html=True)

conn.close()

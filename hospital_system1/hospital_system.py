import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

# 1. إعدادات الصفحة والتصميم الفاخر
st.set_page_config(page_title="HOSPITAL OS | نظام المستشفى الذكي", layout="wide", page_icon="🏥")

# CSS مخصص للواجهة العالمية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background-color: #f8f9fa; }
    .main-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(108, 92, 231, 0.1); border-top: 5px solid #6c5ce7; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border-right: 5px solid #6c5ce7; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #6c5ce7; color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #a29bfe; transform: translateY(-2px); }
    .doctor-card { background: #ffffff; border-radius: 15px; padding: 20px; border: 1px solid #e0e0e0; text-align: center; transition: 0.3s; }
    .doctor-card:hover { border-color: #6c5ce7; box-shadow: 0 5px 15px rgba(108,92,231,0.2); }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات
conn = sqlite3.connect("global_hospital.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, gender TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY, p_name TEXT, d_name TEXT, date TEXT, time TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Pharmacy (id INTEGER PRIMARY KEY, med TEXT, price REAL, stock INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS BloodBank (id INTEGER PRIMARY KEY, type TEXT, units INTEGER)")
    
    # تعبئة بيانات بنك الدم لو كانت فارغة
    cursor.execute("SELECT COUNT(*) FROM BloodBank")
    if cursor.fetchone()[0] == 0:
        for t in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
            cursor.execute("INSERT INTO BloodBank (type, units) VALUES (?, 10)", (t,))
    conn.commit()

init_db()

# 3. الدوال المساعدة
def ar(text): return get_display(arabic_reshaper.reshape(text))

# 4. الشريط الجانبي (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3306/3306567.png", width=100)
    st.title("Hospital OS")
    st.markdown("---")
    menu = ["📊 لوحة التحكم", "👥 المرضى", "👨‍⚕️ الأطباء", "📅 المواعيد", "💊 الصيدلية", "🩸 بنك الدم", "📄 التقارير"]
    choice = st.radio("القائمة الرئيسية", menu)
    st.info(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}")

# ---------------- الأقسام ----------------

if choice == "📊 لوحة التحكم":
    st.title("📊 نظرة عامة على النظام")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        p_num = pd.read_sql("SELECT COUNT(*) FROM Patients", conn).values[0][0]
        st.markdown(f"<div class='metric-card'><h3>👥 المرضى</h3><h2>{p_num}</h2></div>", unsafe_allow_html=True)
    with col2:
        d_num = pd.read_sql("SELECT COUNT(*) FROM Doctors", conn).values[0][0]
        st.markdown(f"<div class='metric-card'><h3>👨‍⚕️ الأطباء</h3><h2>{d_num}</h2></div>", unsafe_allow_html=True)
    with col3:
        a_num = pd.read_sql("SELECT COUNT(*) FROM Appointments WHERE date=?", (str(datetime.now().date()),), conn).shape[0]
        st.markdown(f"<div class='metric-card'><h3>📅 مواعيد اليوم</h3><h2>{a_num}</h2></div>", unsafe_allow_html=True)
    with col4:
        b_num = pd.read_sql("SELECT SUM(units) FROM BloodBank", conn).values[0][0]
        st.markdown(f"<div class='metric-card'><h3>🩸 وحدات الدم</h3><h2>{b_num}</h2></div>", unsafe_allow_html=True)

    st.markdown("### 📈 نشاط الحجوزات")
    df_app = pd.read_sql("SELECT date, count(id) as count FROM Appointments GROUP BY date", conn)
    st.line_chart(df_app.set_index('date'))

elif choice == "👥 المرضى":
    st.subheader("👥 إدارة شؤون المرضى")
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("add_p"):
            name = st.text_input("اسم المريض")
            phone = st.text_input("رقم التواصل")
            gen = st.selectbox("الجنس", ["ذكر", "أنثى"])
            if st.form_submit_button("إضافة مريض جديد"):
                cursor.execute("INSERT INTO Patients (name, phone, gender) VALUES (?,?,?)", (name, phone, gen))
                conn.commit()
                st.success("تم الحفظ")
    with c2:
        search = st.text_input("🔍 بحث عن مريض بالاسم")
        df_p = pd.read_sql("SELECT * FROM Patients", conn)
        if search: df_p = df_p[df_p['name'].str.contains(search)]
        st.dataframe(df_p, use_container_width=True)

elif choice == "👨‍⚕️ الأطباء":
    st.subheader("👨‍⚕️ الطاقم الطبي")
    with st.expander("➕ إضافة طبيب جديد"):
        with st.form("d_f"):
            dn = st.text_input("اسم الطبيب")
            ds = st.selectbox("التخصص", ["باطنية", "أطفال", "قلب", "جراحة", "جلدية"])
            if st.form_submit_button("حفظ"):
                cursor.execute("INSERT INTO Doctors (name, spec, status) VALUES (?,?, 'نشط')", (dn, ds))
                conn.commit()
    
    docs = pd.read_sql("SELECT * FROM Doctors", conn)
    cols = st.columns(3)
    for i, row in docs.iterrows():
        with cols[i%3]:
            st.markdown(f"""
            <div class='doctor-card'>
                <img src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" width="60">
                <h3>د. {row['name']}</h3>
                <p style="color: #6c5ce7;"><b>{row['spec']}</b></p>
                <small>الحالة: {row['status']}</small>
            </div>
            """, unsafe_allow_html=True)

elif choice == "📅 المواعيد":
    st.subheader("📅 جدولة المواعيد والتحقق")
    tab1, tab2 = st.tabs(["🆕 حجز جديد", "🔍 تأكيد الموعد"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        patients = pd.read_sql("SELECT name FROM Patients", conn)['name'].tolist()
        doctors = pd.read_sql("SELECT name FROM Doctors", conn)['name'].tolist()
        
        with col_a:
            with st.form("app_f"):
                p = st.selectbox("المريض", patients if patients else ["سجل مريضاً أولاً"])
                d = st.selectbox("الطبيب", doctors if doctors else ["سجل طبيباً أولاً"])
                dt = st.date_input("تاريخ الموعد", min_value=datetime.now().date())
                tm = st.time_input("الوقت")
                if st.form_submit_button("تثبيت الحجز"):
                    cursor.execute("INSERT INTO Appointments (p_name, d_name, date, time) VALUES (?,?,?,?)", 
                                   (p, d, str(dt), tm.strftime("%H:%M")))
                    conn.commit()
                    st.balloons()
        with col_b:
            st.image("https://cdn-icons-png.flaticon.com/512/2693/2693507.png", width=200)

    with tab2:
        st.markdown("### 🗓️ التحقق من جدول يوم معين")
        check_date = st.date_input("اختر التاريخ للبحث")
        res = pd.read_sql(f"SELECT p_name as 'المريض', d_name as 'الطبيب', time as 'الوقت' FROM Appointments WHERE date='{check_date}'", conn)
        if not res.empty:
            st.success(f"يوجد {len(res)} مواعيد في هذا التاريخ")
            st.table(res)
        else:
            st.info("لا توجد مواعيد محجوزة لهذا التاريخ.")

elif choice == "🩸 بنك الدم":
    st.subheader("🩸 مخزون بنك الدم المركزي")
    df_b = pd.read_sql("SELECT type, units FROM BloodBank", conn)
    
    col_chart, col_edit = st.columns([2, 1])
    with col_chart:
        st.bar_chart(df_b.set_index('type'))
    with col_edit:
        st.markdown("### تعديل المخزون")
        b_type = st.selectbox("الفصيلة", df_b['type'])
        new_val = st.number_input("الكمية الجديدة", 0, 500)
        if st.button("تحديث"):
            cursor.execute("UPDATE BloodBank SET units=? WHERE type=?", (new_val, b_type))
            conn.commit()
            st.rerun()

elif choice == "💊 الصيدلية":
    st.subheader("💊 إدارة الصيدلية")
    with st.form("med"):
        m1, m2, m3 = st.columns(3)
        m_name = m1.text_input("اسم الدواء")
        m_price = m2.number_input("السعر", 0.0)
        m_qty = m3.number_input("الكمية المضافة", 1)
        if st.form_submit_button("إضافة للمخزن"):
            cursor.execute("INSERT INTO Pharmacy (med, price, stock) VALUES (?,?,?)", (m_name, m_price, m_qty))
            conn.commit()
    
    st.table(pd.read_sql("SELECT * FROM Pharmacy", conn))

elif choice == "📄 التقارير":
    st.subheader("📄 مركز التقارير الذكي")
    rep_type = st.selectbox("نوع التقرير", ["المرضى", "الأطباء", "الحجوزات", "الصيدلية"])
    
    if rep_type == "المرضى": df = pd.read_sql("SELECT * FROM Patients", conn)
    elif rep_type == "الأطباء": df = pd.read_sql("SELECT * FROM Doctors", conn)
    elif rep_type == "الحجوزات": df = pd.read_sql("SELECT * FROM Appointments", conn)
    else: df = pd.read_sql("SELECT * FROM Pharmacy", conn)
    
    st.dataframe(df, use_container_width=True)
    if st.button("توليد ملف PDF (تجريبي)"):
        st.warning("تأكد من وجود خط arial.ttf لتفعيل الطباعة بالعربي")

# إغلاق الاتصال عند الانتهاء
conn.close()

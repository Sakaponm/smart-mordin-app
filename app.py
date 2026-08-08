import streamlit as st
from durian_calculator import calculate_durian_fertilizer_api

# ตั้งค่าหน้าตาของเว็บแอป
st.set_page_config(page_title="หมอดินอัจฉริยะ - สวนทุเรียน", page_icon="🌱", layout="centered")

st.title("🌱 หมอดินอัจฉริยะ: คำนวณปุ๋ยทุเรียนสั่งตัด")
st.caption("ระบบคำนวณอัตราปุ๋ยเคมีร่วมกับชุดฟื้นฟูดินชีวภาพ BioMax & BioSoil")

st.divider()

# --- ส่วนที่ 1: กรอกข้อมูลแปลง ---
st.header("1. ข้อมูลแปลงและต้นทุเรียน")
col1, col2 = st.columns(2)

with col1:
    canopy = st.number_input("ขนาดทรงพุ่มโดยเฉลี่ย (เมตร)", min_value=1.0, max_value=15.0, value=6.0, step=0.5)
    tree_count = st.number_input("จำนวนต้นทุเรียนในแปลง (ต้น)", min_value=1, max_value=5000, value=100)

with col2:
    stage = st.selectbox(
        "ระยะการเจริญเติบโตปัจจุบัน",
        options=["stage_1", "stage_2", "stage_3", "stage_4"],
        format_func=lambda x: {
            "stage_1": "ระยะที่ 1: ฟื้นฟูต้น / ทำใบอ่อน (หลังเก็บเกี่ยว)",
            "stage_2": "ระยะที่ 2: สะสมอาหารทำดอก (ก่อนบาน 1-2 เดือน)",
            "stage_3": "ระยะที่ 3: ขยายขนาดผล (ติดผล 30-70 วัน)",
            "stage_4": "ระยะที่ 4: ทำหวานก่อนเก็บเกี่ยว (20-30 วัน)"
        }[x]
    )
    use_bio = st.checkbox("ใช้ชุดฟื้นฟูดินกู้ชีพ BioMax + BioSoil (ลดปุ๋ยเคมี 50%)", value=True)

# --- ส่วนที่ 2: กรอกผลตรวจดิน ---
st.header("2. ข้อมูลผลวิเคราะห์ดิน (ถ้ามี)")
col3, col4 = st.columns(2)

with col3:
    soil_ph = st.number_input("ค่าความเป็นกรด-ด่าง (pH)", min_value=3.0, max_value=9.0, value=4.8, step=0.1)
    soil_om = st.number_input("อินทรียวัตถุ (OM %)", min_value=0.1, max_value=10.0, value=1.2, step=0.1)

with col4:
    soil_p = st.number_input("ฟอสฟอรัสที่เป็นประโยชน์ (P ppm)", min_value=1.0, max_value=200.0, value=20.0, step=1.0)
    soil_k = st.number_input("โพแทสเซียมที่แลกเปลี่ยนได้ (K ppm)", min_value=1.0, max_value=500.0, value=80.0, step=5.0)

st.divider()

# --- ปุ่มประมวลผล ---
if st.button("🧮 คำนวณสูตรปุ๋ยอัจฉริยะ", type="primary", use_container_width=True):
    res = calculate_durian_fertilizer_api(
        canopy_diameter_m=canopy,
        tree_count=tree_count,
        stage=stage,
        soil_ph=soil_ph,
        soil_om=soil_om,
        soil_p_ppm=soil_p,
        soil_k_ppm=soil_k,
        use_bio_duo=use_bio
    )

    st.subheader(f"📊 ผลคำนวณเฉพาะรอบปัจจุบัน: {res['stage_name']}")
    
    # แจ้งเตือนสุขภาพดิน
    if res["soil_diagnostics"]["soil_ph"] < 5.0:
        st.warning(res["soil_diagnostics"]["alert_message"])

    # แสดงผลปุ๋ยต่อ 1 ต้น (รอบปัจจุบัน)
    st.markdown("### 🥣 ปริมาณปุ๋ยสั่งตัดตักใส่ต่อ 1 ต้น (ใส่รอบนี้)")
    c1, c2, c3 = st.columns(3)
    c1.metric("ปุ๋ยยูเรีย (46-0-0)", f"{res['per_tree_chemical_g']['urea_46_0_0']} กรัม")
    c2.metric("ปุ๋ยแดป (18-46-0)", f"{res['per_tree_chemical_g']['dap_18_46_0']} กรัม")
    c3.metric("ปุ๋ยป๊อป (0-0-60)", f"{res['per_tree_chemical_g']['mop_0_0_60']} กรัม")

    # แสดงคำแนะนำการใส่ BioMax / BioSoil
    if use_bio:
        biosoil_per_round = round(0.25 * canopy, 1)
        total_biosoil_kg = biosoil_per_round * tree_count
        water_liters = 20 * tree_count
        biomax_liters = water_liters / 1000.0

        st.markdown("### 🟤 🟢 ปริมาณชุดชีวภาพ ( Bio-Duo Set ) ที่ต้องใส่รอบนี้")
        st.info(f"**BioSoil (ไบโอซอย):** โรยโคนต้นละ **{biosoil_per_round} กิโลกรัม** (รวมใช้ทั้งสวนรอบนี้ {total_biosoil_kg} กก. / ประมาณ {round(total_biosoil_kg/50, 1)} ถุง)")
        st.success(f"**BioMax (ไบโอแม็ก):** ผสมน้ำ **{water_liters} ลิตร** ใช้ BioMax **{biomax_liters} ลิตร**[cite: 1] (ราดโคนหรือใส่ระบบน้ำ)")

        # --- ตารางแนะนำตารางการใส่ปุ๋ยตลอดทั้งปี (3 รอบหลัก) ---
        st.divider()
        st.markdown("## 📅 คำแนะนำตารางการแบ่งใส่ BioSoil และ BioMax ตลอดปี (3 รอบหลัก)")
        st.caption("การแบ่งใส่เป็นรอบ ช่วยให้ดินอุ้มปุ๋ยได้ดีและพืชดูดซึมธาตุอาหารได้ต่อเนื่องที่สุด")

        # สร้างตารางการใส่ปุ๋ยประจำปี
        st.markdown(f"""
        | รอบที่ / ระยะพืช | BioSoil (ไบโอซอย) | BioMax (ไบโอแม็ก)[cite: 1] | วัตถุประสงค์หลัก |
        | :--- | :--- | :--- | :--- |
        | **รอบที่ 1:** ฟื้นฟูต้น / ทำใบอ่อน (หลังเก็บเกี่ยว) | **{biosoil_per_round} กก./ต้น** | 1 ลิตร : น้ำ 1,000 ลิตร (ราดโคน) | ฟื้นฟูดินกระด้าง เติมอินทรียวัตถุ เร่งรากใหม่[cite: 2, 3] |
        | **รอบที่ 2:** สะสมอาหารทำดอก (ก่อนบาน 1-2 เดือน) | **{round(biosoil_per_round * 0.7, 1)} กก./ต้น** | 1 ลิตร : น้ำ 1,000 ลิตร (ราดโคน) | ปรับสมดุล pH กระตุ้นการตาดอก[cite: 2, 3] |
        | **รอบที่ 3:** ขยายขนาดผล (ติดผล 30-70 วัน) | **{biosoil_per_round} กก./ต้น** | 1 ลิตร : น้ำ 1,000 ลิตร (ราดโคน) | ช่วยอุ้มปุ๋ยเคมี ขยายขนาดผล เพิ่มความหวาน[cite: 2, 3] |
        """)

    # สรุปยอดแม่ปุ๋ยเคมีที่ต้องใช้ทั้งสวนในรอบนี้
    st.divider()
    st.markdown("### 📦 สรุปยอดสั่งซื้อแม่ปุ๋ยเคมีรวมทั้งสวน (เฉพาะรอบนี้)")
    st.write(f"- **46-0-0 รวม:** {res['total_farm_chemical_kg']['urea_46_0_0_kg']} กิโลกรัม")
    st.write(f"- **18-46-0 รวม:** {res['total_farm_chemical_kg']['dap_18_46_0_kg']} กิโลกรัม")
    st.write(f"- **0-0-60 รวม:** {res['total_farm_chemical_kg']['mop_0_0_60_kg']} กิโลกรัม")

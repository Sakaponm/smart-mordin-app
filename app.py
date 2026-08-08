import streamlit as st
import math
from durian_calculator import calculate_durian_fertilizer_api

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

# --- ส่วนที่ 2: กรอกค่าตรวจวัดจากเครื่องวัดดิน ---
st.header("2. ค่าที่วัดได้จากเครื่องตรวจวัดดิน")
col3, col4 = st.columns(2)

with col3:
    soil_ph = st.number_input("ค่าความเป็นกรด-ด่าง (pH)", min_value=3.0, max_value=9.0, value=4.8, step=0.1)
    soil_n = st.number_input("ค่าไนโตรเจน N (ppm)", min_value=0.0, max_value=200.0, value=25.0, step=1.0)

with col4:
    soil_p = st.number_input("ค่าฟอสฟอรัส P (ppm)", min_value=0.0, max_value=200.0, value=20.0, step=1.0)
    soil_k = st.number_input("ค่าโพแทสเซียม K (ppm)", min_value=0.0, max_value=500.0, value=80.0, step=5.0)

st.divider()

if st.button("🧮 คำนวณสูตรปุ๋ยอัจฉริยะ", type="primary", use_container_width=True):
    res = calculate_durian_fertilizer_api(
        canopy_diameter_m=canopy,
        tree_count=tree_count,
        stage=stage,
        soil_ph=soil_ph,
        soil_n_ppm=soil_n,
        soil_p_ppm=soil_p,
        soil_k_ppm=soil_k,
        use_bio_duo=use_bio
    )

    st.subheader(f"📊 ผลคำนวณเฉพาะรอบปัจจุบัน: {res['stage_name']}")
    
    if res["soil_diagnostics"]["soil_ph"] < 5.0:
        st.warning(res["soil_diagnostics"]["alert_message"])

    # แสดงผลทางเลือกปุ๋ยสูตรสำเร็จ (ที่เกษตรกรคุ้นเคย)
    st.markdown("### 🔵 ทางเลือกที่ 1: ใช้ปุ๋ยสูตรสำเร็จรูป (หาซื้อง่าย)")
    comm = res["commercial_option"]
    st.success(f"**ปุ๋ยที่แนะนำ:** {comm['formula']}\n\n**อัตราใส่ต่อต้น:** ใส่ต้นละ **{comm['kg_per_tree']} กิโลกรัม** (สั่งซื้อทั้งสวนประมาณ {comm['total_bags_50kg']} กระสอบ [50 กก.])")

    # แสดงผลแม่ปุ๋ยเดี่ยวผสมเอง
    st.markdown("### 🥣 ทางเลือกที่ 2: ใช้แม่ปุ๋ยเดี่ยวตักผสมเอง (ประหยัดกว่า)")
    c1, c2, c3 = st.columns(3)
    c1.metric("ปุ๋ยยูเรีย (46-0-0)", f"{res['per_tree_chemical_g']['urea_46_0_0']} กรัม")
    c2.metric("ปุ๋ยแดป (18-46-0)", f"{res['per_tree_chemical_g']['dap_18_46_0']} กรัม")
    c3.metric("ปุ๋ยป๊อป (0-0-60)", f"{res['per_tree_chemical_g']['mop_0_0_60']} กรัม")

    # แสดงคำแนะนำ BioMax / BioSoil
    if use_bio:
        biosoil_per_round = round(0.25 * canopy, 1)
        total_biosoil_kg = biosoil_per_round * tree_count
        biosoil_bags = math.ceil(total_biosoil_kg / 15.0)

        water_liters = 20 * tree_count
        biomax_liters = round(water_liters / 1000.0, 2)
        biomax_bottles = math.ceil(biomax_liters) if biomax_liters >= 1 else 1

        st.markdown("### 🟤 🟢 ปริมาณชุดชีวภาพ ( Bio-Duo Set ) ที่ต้องใส่รอบนี้")
        st.info(f"**BioSoil (ไบโอซอย):** โรยโคนต้นละ **{biosoil_per_round} กิโลกรัม** (รวมใช้ทั้งสวนรอบนี้ {total_biosoil_kg} กก. / สั่งซื้อ **{biosoil_bags} ถุง** [ถุงละ 15 กก.])")
        st.success(f"**BioMax (ไบโอแม็ก):** ผสมน้ำ **{water_liters} ลิตร** ใช้ BioMax **{biomax_liters} ลิตร** (สั่งซื้อ **{biomax_bottles} ขวด**) (ราดโคนหรือใส่ระบบน้ำ)")

        # สรุปยอดสั่งซื้อ BioDuo
        st.divider()
        st.markdown("## 🛒 สรุปยอดสั่งซื้อชุดชีวภาพ & ช่องทางติดต่อ")
        
        price_biomax = 500
        price_biosoil = 300
        cost_biomax = biomax_bottles * price_biomax
        cost_biosoil = biosoil_bags * price_biosoil
        total_bio_cost = cost_biomax + cost_biosoil

        col_cost1, col_cost2 = st.columns(2)
        with col_cost1:
            st.write(f"- 🟢 **BioMax ({biomax_bottles} ขวด):** {cost_biomax:,} บาท")
            st.write(f"- 🟤 **BioSoil ({biosoil_bags} ถุง 15 กก.):** {cost_biosoil:,} บาท")
        with col_cost2:
            st.metric("💰 รวมประมาณการชุดกู้ชีพดินรอบนี้", f"{total_bio_cost:,} บาท")

        st.markdown("### 📲 สนใจสั่งซื้อ หรือปรึกษาหมอดินเพิ่มเติม")
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            st.link_button("💬 สั่งซื้อผ่าน LINE Official", "https://lin.ee/ZyddN1x", use_container_width=True, type="primary")    
        with c_btn2:
            st.link_button("📞 โทรปรึกษาผู้เชี่ยวชาญ", "tel:0626323246", use_container_width=True)

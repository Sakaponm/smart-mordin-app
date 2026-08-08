import streamlit as st
import math
from durian_calculator import calculate_durian_fertilizer_api, calculate_rice_awd_api

st.set_page_config(page_title="หมอดินอัจฉริยะ", page_icon="🌱", layout="centered")

st.title("🌱 หมอดินอัจฉริยะ (Smart Farmer App)")
st.caption("ระบบคำนวณอัตราปุ๋ยสั่งตัดและชุดชีวภัณฑ์กู้ชีพดิน BioDuo & ReSoil")

# แถบเลือกประเภทพืช
plant_type = st.radio("🌾 เลือกประเภทพืชที่ต้องการคำนวณ:", ["🌳 สวนทุเรียน", "🌾 นาข้าวเปียกสลับแห้ง (AWD)"], horizontal=True)

st.divider()

# ==========================================
# โหมดที่ 1: สวนทุเรียน
# ==========================================
if plant_type == "🌳 สวนทุเรียน":
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

    st.header("2. ค่าที่วัดได้จากเครื่องตรวจวัดดิน")
    col3, col4 = st.columns(2)

    with col3:
        soil_ph = st.number_input("ค่าความเป็นกรด-ด่าง (pH)", min_value=3.0, max_value=9.0, value=4.8, step=0.1)
        soil_n = st.number_input("ค่าไนโตรเจน N (ppm)", min_value=0.0, max_value=200.0, value=25.0, step=1.0)

    with col4:
        soil_p = st.number_input("ค่าฟอสฟอรัส P (ppm)", min_value=0.0, max_value=200.0, value=20.0, step=1.0)
        soil_k = st.number_input("ค่าโพแทสเซียม K (ppm)", min_value=0.0, max_value=500.0, value=80.0, step=5.0)

    st.divider()

    if st.button("🧮 คำนวณสูตรปุ๋ยทุเรียนอัจฉริยะ", type="primary", use_container_width=True):
        res = calculate_durian_fertilizer_api(
            canopy_diameter_m=canopy, tree_count=tree_count, stage=stage,
            soil_ph=soil_ph, soil_n_ppm=soil_n, soil_p_ppm=soil_p, soil_k_ppm=soil_k, use_bio_duo=use_bio
        )

        st.subheader(f"📊 ผลคำนวณเฉพาะรอบปัจจุบัน: {res['stage_name']}")
        
        if res["soil_diagnostics"]["soil_ph"] < 5.0:
            st.warning(res["soil_diagnostics"]["alert_message"])

        st.markdown("### 🔵 ทางเลือกที่ 1: ใช้ปุ๋ยสูตรสำเร็จรูป")
        comm = res["commercial_option"]
        st.success(f"**ปุ๋ยที่แนะนำ:** {comm['formula']}\n\n**อัตราใส่ต่อต้น:** ใส่ต้นละ **{comm['kg_per_tree']} กิโลกรัม** (สั่งซื้อทั้งสวนประมาณ {comm['total_bags_50kg']} กระสอบ [50 กก.])")

        st.markdown("### 🥣 ทางเลือกที่ 2: ใช้แม่ปุ๋ยเดี่ยวตักผสมเอง")
        c1, c2, c3 = st.columns(3)
        c1.metric("ปุ๋ยยูเรีย (46-0-0)", f"{res['per_tree_chemical_g']['urea_46_0_0']} กรัม")
        c2.metric("ปุ๋ยแดป (18-46-0)", f"{res['per_tree_chemical_g']['dap_18_46_0']} กรัม")
        c3.metric("ปุ๋ยป๊อป (0-0-60)", f"{res['per_tree_chemical_g']['mop_0_0_60']} กรัม")

        if use_bio:
            biosoil_per_round = round(0.25 * canopy, 1)
            total_biosoil_kg = biosoil_per_round * tree_count
            biosoil_bags = math.ceil(total_biosoil_kg / 15.0)

            water_liters = 20 * tree_count
            biomax_liters = round(water_liters / 1000.0, 2)
            biomax_bottles = math.ceil(biomax_liters) if biomax_liters >= 1 else 1

            st.markdown("### 🟤 🟢 ปริมาณชุดชีวภาพ ( Bio-Duo Set ) ที่ต้องใส่รอบนี้")
            st.info(f"**BioSoil (ไบโอซอย):** โรยโคนต้นละ **{biosoil_per_round} กิโลกรัม** (รวมใช้ทั้งสวนรอบนี้ {total_biosoil_kg} กก. / สั่งซื้อ **{biosoil_bags} ถุง** [ถุงละ 15 กก.])")
            st.success(f"**BioMax (ไบโอแม็ก):** ผสมน้ำ **{water_liters} ลิตร** ใช้ BioMax **{biomax_liters} ลิตร** (สั่งซื้อ **{biomax_bottles} ขวด**)")

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

# ==========================================
# โหมดที่ 2: นาข้าวเปียกสลับแห้ง (AWD)
# ==========================================
else:
    st.header("1. ข้อมูลแปลงนาข้าว")
    col1, col2 = st.columns(2)

    with col1:
        rai_area = st.number_input("จำนวนพื้นที่แปลงนา (ไร่)", min_value=1.0, max_value=500.0, value=10.0, step=1.0)
        use_resoil = st.checkbox("🌱 ใช้ ReSoil (รีซอย) ย่อยสลายตอซังฟางข้าว (ลดปุ๋ยเคมีได้อีก 20-30%)", value=True)

    with col2:
        rice_stage = st.selectbox(
            "ระยะของการทำนาข้าว",
            options=["stage_0", "stage_1", "stage_2", "stage_3", "stage_4"],
            format_func=lambda x: {
                "stage_0": "ระยะที่ 0: เตรียมดิน / หมักตอซัง (ก่อนหมัก 7-15 วัน)",
                "stage_1": "ระยะที่ 1: แตกลำต้น / ตั้งตัว (0-20 วัน)",
                "stage_2": "ระยะที่ 2: เร่งแตกกอ & เริ่มทำ AWD (20-45 วัน)",
                "stage_3": "ระยะที่ 3: รับรวง / ข้าวตั้งท้อง (45-75 วัน)",
                "stage_4": "ระยะที่ 4: พลับพลึง / ก่อนเก็บเกี่ยว (75+ วัน)"
            }[x]
        )
        use_bio = st.checkbox("ใช้ชุดชีวภาพ BioMax + BioSoil (ลดปุ๋ยเคมี 50%)", value=True)
        use_pest = st.checkbox("🌿 ใช้ชีวภัณฑ์สมุนไพรไล่แมลง 7 ชนิด (ป้องกันเพลี้ย/หนอน)", value=True)

    st.header("2. ค่าตรวจวัดคุณภาพดิน (ถ้ามี)")
    col3, col4 = st.columns(2)
    with col3:
        soil_ph = st.number_input("ค่าความเป็นกรด-ด่าง (pH)", min_value=3.0, max_value=9.0, value=5.5, step=0.1)
        soil_n = st.number_input("ค่าไนโตรเจน N (ppm)", min_value=0.0, max_value=200.0, value=20.0, step=1.0)
    with col4:
        soil_p = st.number_input("ค่าฟอสฟอรัส P (ppm)", min_value=0.0, max_value=200.0, value=15.0, step=1.0)
        soil_k = st.number_input("ค่าโพแทสเซียม K (ppm)", min_value=0.0, max_value=500.0, value=60.0, step=5.0)

    st.divider()

    if st.button("🧮 คำนวณระบบทำนาข้าว AWD & ปุ๋ยสั่งตัด", type="primary", use_container_width=True):
        res_rice = calculate_rice_awd_api(
            rai_area=rai_area, stage=rice_stage, soil_ph=soil_ph,
            soil_n_ppm=soil_n, soil_p_ppm=soil_p, soil_k_ppm=soil_k,
            use_bio_duo=use_bio, use_resoil=use_resoil, use_pest_repellent=use_pest
        )

        st.subheader(f"📊 {res_rice['stage_name']}")
        
        # คำแนะนำการบริหารจัดการน้ำ AWD
        st.info(f"**💧 การบริหารจัดการน้ำในแปลงนา:**\n\n{res_rice['water_management']}")

        # ปุ๋ยเคมีที่ต้องใช้
        st.markdown("### 🌾 ปริมาณปุ๋ยเคมีที่แนะนำสำหรับรอบนี้")
        st.success(f"**ปุ๋ยสูตรสำเร็จ:** {res_rice['commercial_recommendation']}")
        
        st.markdown("**หรือใช้แม่ปุ๋ยเดี่ยวรวมทั้งแปลง:**")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("ปุ๋ยยูเรีย (46-0-0)", f"{res_rice['chemical_kg']['urea_46_0_0']} กก.")
        rc2.metric("ปุ๋ยแดป (18-46-0)", f"{res_rice['chemical_kg']['dap_18_46_0']} กก.")
        rc3.metric("ปุ๋ยป๊อป (0-0-60)", f"{res_rice['chemical_kg']['mop_0_0_60']} กก.")

        # สรุปยอดสินค้าชีวภัณฑ์สำหรับนาข้าว
        st.divider()
        st.markdown("## 🛒 สรุปรายการชีวภัณฑ์สำหรับนาข้าว & ยอดสั่งซื้อ")
        
        price_resoil = 350      # ReSoil บาท/ขวด (ย่อยสลายตอซัง)
        price_biomax = 500      # BioMax บาท/ขวด
        price_biosoil = 300     # BioSoil บาท/ถุง (15 กก.)
        price_pest = 350        # สมุนไพรไล่แมลง บาท/ขวด

        bio_items = res_rice["bio_products"]
        total_rice_cost = 0

        if use_resoil:
            cost_r = bio_items['resoil_bottles'] * price_resoil
            total_rice_cost += cost_r
            st.write(f"- 🍂 **ReSoil ย่อยตอซัง 10 วัน ({bio_items['resoil_bottles']} ขวด):** {cost_r:,} บาท *(ย่อยซากฟางข้าว คืนปุ๋ย 10-10-10 ไม่ต้องเผา)*")

        if use_bio:
            cost_bm = bio_items['biomax_bottles'] * price_biomax
            cost_bs = bio_items['biosoil_bags_15kg'] * price_biosoil
            total_rice_cost += (cost_bm + cost_bs)
            st.write(f"- 🟢 **BioMax ({bio_items['biomax_bottles']} ขวด):** {cost_bm:,} บาท")
            st.write(f"- 🟤 **BioSoil ({bio_items['biosoil_bags_15kg']} ถุง 15 กก.):** {cost_bs:,} บาท")

        if use_pest:
            cost_p = bio_items['pest_repellent_bottles'] * price_pest
            total_rice_cost += cost_p
            st.write(f"- 🌿 **ชีวภัณฑ์สมุนไพรไล่แมลง 7 ชนิด ({bio_items['pest_repellent_bottles']} ขวด):** {cost_p:,} บาท *(ป้องกันเพลี้ย/หนอน ตัดวงจรศัตรูพืช)*")

        st.metric("💰 รวมยอดสั่งซื้อผลิตภัณฑ์ชีวภาพสำหรับแปลงนี้", f"{total_rice_cost:,} บาท")

        st.markdown("### 📲 สนใจสั่งซื้อ หรือปรึกษาหมอดินเพิ่มเติม")
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            st.link_button("💬 สั่งซื้อผ่าน LINE Official", "https://lin.ee/ZyddN1x", use_container_width=True, type="primary")
        with c_btn2:
            st.link_button("📞 โทรปรึกษาผู้เชี่ยวชาญ", "tel:0626323246", use_container_width=True)

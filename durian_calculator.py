def calculate_durian_fertilizer_api(
    canopy_diameter_m: float,
    tree_count: int,
    stage: str,
    soil_ph: float,
    soil_n_ppm: float,
    soil_p_ppm: float,
    soil_k_ppm: float,
    use_bio_duo: bool = True
) -> dict:
    """ฟังก์ชันคำนวณปุ๋ยทุเรียนอัจฉริยะ"""
    BASE_REQUIREMENTS = {
        "stage_1": {"N": 300, "P": 100, "K": 150, "name": "ฟื้นฟูต้น/ทำใบอ่อน"},
        "stage_2": {"N": 100, "P": 300, "K": 300, "name": "สะสมอาหารทำดอก"},
        "stage_3": {"N": 200, "P": 100, "K": 300, "name": "ขยายขนาดผล"},
        "stage_4": {"N": 50,  "P": 50,  "K": 400, "name": "ทำหวานก่อนเก็บเกี่ยว"}
    }
    
    stage_data = BASE_REQUIREMENTS.get(stage, BASE_REQUIREMENTS["stage_1"])
    size_factor = canopy_diameter_m / 5.0
    
    base_n = stage_data["N"] * size_factor
    base_p = stage_data["P"] * size_factor
    base_k = stage_data["K"] * size_factor
    
    f_n = 1.2 if soil_n_ppm < 20 else (0.8 if soil_n_ppm > 50 else 1.0)
    f_p = 1.2 if soil_p_ppm < 15 else (0.5 if soil_p_ppm > 45 else 1.0)
    f_k = 1.2 if soil_k_ppm < 60 else (0.75 if soil_k_ppm > 120 else 1.0)
    
    eff_ph = 0.5 if (soil_ph < 5.0 or soil_ph > 7.5) else 1.0
    
    target_n = (base_n * f_n) / eff_ph
    target_p = (base_p * f_p) / eff_ph
    target_k = (base_k * f_k) / eff_ph
    
    if use_bio_duo:
        target_n *= 0.5
        target_p *= 0.5
        target_k *= 0.5

    mop_g = (target_k / 60.0) * 100.0
    dap_g = (target_p / 46.0) * 100.0
    n_from_dap = dap_g * 0.18
    remaining_n = max(0.0, target_n - n_from_dap)
    urea_g = (remaining_n / 46.0) * 100.0

    commercial_recommendation = ""
    commercial_kg_per_tree = 0.0
    
    if stage == "stage_1":
        commercial_recommendation = "สูตร 15-15-15 หรือ 16-16-16 (เน้นเร่งต้น-ใบ)"
        commercial_kg_per_tree = round((target_n / 15.0) * 100 / 1000.0, 2)
    elif stage == "stage_2":
        commercial_recommendation = "สูตร 8-24-24 หรือ 9-25-25 (เน้นสะสมอาหารทำดอก)"
        commercial_kg_per_tree = round((target_p / 24.0) * 100 / 1000.0, 2)
    elif stage == "stage_3":
        commercial_recommendation = "สูตร 15-5-20 หรือ 15-15-15 (เน้นขยายผล)"
        commercial_kg_per_tree = round((target_k / 20.0) * 100 / 1000.0, 2)
    else:
        commercial_recommendation = "สูตร 0-0-60 หรือ 13-13-21 (เน้นทำหวาน)"
        commercial_kg_per_tree = round((target_k / 21.0) * 100 / 1000.0, 2)

    soil_alert = "สภาพดินปกติ"
    if soil_ph < 5.0:
        soil_alert = f"ดินกรดจัด (pH {soil_ph}) ทำให้ปุ๋ยละลายได้ไม่ดี แนะนำใส่โดโลไมต์ {round(0.5 * canopy_diameter_m, 1)} กก./ต้น ก่อนใส่ปุ๋ย 15 วัน"

    return {
        "stage_name": stage_data["name"],
        "per_tree_chemical_g": {
            "urea_46_0_0": round(urea_g, 1),
            "dap_18_46_0": round(dap_g, 1),
            "mop_0_0_60": round(mop_g, 1)
        },
        "commercial_option": {
            "formula": commercial_recommendation,
            "kg_per_tree": commercial_kg_per_tree,
            "total_bags_50kg": round((commercial_kg_per_tree * tree_count) / 50.0, 1)
        },
        "total_farm_chemical_kg": {
            "urea_46_0_0_kg": round((urea_g * tree_count) / 1000.0, 2),
            "dap_18_46_0_kg": round((dap_g * tree_count) / 1000.0, 2),
            "mop_0_0_60_kg": round((mop_g * tree_count) / 1000.0, 2)
        },
        "soil_diagnostics": {"soil_ph": soil_ph, "alert_message": soil_alert}
    }


def calculate_rice_awd_api(
    rai_area: float,
    stage: str,
    soil_ph: float,
    soil_n_ppm: float,
    soil_p_ppm: float,
    soil_k_ppm: float,
    use_bio_duo: bool = True,
    use_resoil: bool = True,
    use_pest_repellent: bool = True
) -> dict:
    """
    ฟังก์ชันคำนวณปุ๋ย การจัดการน้ำ AWD ย่อยสลายตอซัง (ReSoil) และสารไล่แมลงสมุนไพร
    """
    RICE_STAGES = {
        "stage_0": {
            "name": "ระยะเตรียมดิน / ย่อยสลายตอซัง (ก่อนทำนา 10-15 วัน)",
            "water_advice": "🌾 **ย่อยสลายตอซัง:** ปล่อยน้ำขังท่วมตอซัง นำ ReSoil ฉีดพ่นให้ทั่วแปลง แล้วหมักไว้ 7-15 วัน ก่อนไถกลบ",
            "commercial": "ไม่ต้องใส่ปุ๋ยเคมี (ใช้ ReSoil คืนปุ๋ยธรรมชาติ 10-10-10)",
            "base_n_kg": 0.0, "base_p_kg": 0.0, "base_k_kg": 0.0
        },
        "stage_1": {
            "name": "ระยะที่ 1: แตกลำต้น/ตั้งตัว (0-20 วัน)",
            "water_advice": "ขังน้ำสูง 3-5 ซม. เพื่อคุมวัชพืชและช่วยให้ต้นข้าวตั้งตัว",
            "commercial": "สูตร 16-20-0 หรือ 16-16-8 (อัตรา 20-25 กก./ไร่)",
            "base_n_kg": 10.0, "base_p_kg": 8.0, "base_k_kg": 0.0
        },
        "stage_2": {
            "name": "ระยะที่ 2: เร่งแตกกอ & เริ่มทำ AWD (20-45 วัน)",
            "water_advice": "💧 **เริ่มทำ AWD:** ปล่อยให้น้ำแห้งจนระดับน้ำต่ำกว่าผิวดิน 15 ซม. (ดูในท่อแว็ด) แล้วค่อยสูบน้ำเข้าสูง 5 ซม.",
            "commercial": "สูตร 46-0-0 (ยูเรีย) (อัตรา 10-15 กก./ไร่)",
            "base_n_kg": 12.0, "base_p_kg": 0.0, "base_k_kg": 0.0
        },
        "stage_3": {
            "name": "ระยะที่ 3: รับรวง / ข้าวตั้งท้อง (45-75 วัน)",
            "water_advice": "⚠️ **ห้ามขาดน้ำ:** ขังน้ำสูง 5-7 ซม. ตลอดช่วงนี้เพื่อป้องกันเมล็ดลีบ",
            "commercial": "สูตร 15-15-15 ร่วมกับ 0-0-60 (อัตรา 15-20 กก./ไร่)",
            "base_n_kg": 8.0, "base_p_kg": 4.0, "base_k_kg": 8.0
        },
        "stage_4": {
            "name": "ระยะที่ 4: พลับพลึง / ก่อนเก็บเกี่ยว (75+ วัน)",
            "water_advice": "🚜 ระบายน้ำออกจากแปลงให้แห้งสนิทก่อนเก็บเกี่ยว 10-15 วัน เพื่อให้รถเกี่ยวทำงานสะดวก",
            "commercial": "ไม่ต้องใส่ปุ๋ยเคมีเพิ่มในระยะนี้",
            "base_n_kg": 0.0, "base_p_kg": 0.0, "base_k_kg": 0.0
        }
    }

    s_data = RICE_STAGES.get(stage, RICE_STAGES["stage_1"])
    
    target_n = s_data["base_n_kg"] * rai_area
    target_p = s_data["base_p_kg"] * rai_area
    target_k = s_data["base_k_kg"] * rai_area

    # ปรับลดปุ๋ยเคมีถ้าใช้ชุดชีวภาพ / ReSoil
    bio_discount = 0.5 if use_bio_duo else 1.0
    if use_resoil and stage != "stage_0":
        bio_discount *= 0.8  # ลดปุ๋ยเคมีเพิ่มอีก 20% จากการหมักตอซังคืนปุ๋ย 10-10-10

    target_n *= bio_discount
    target_p *= bio_discount
    target_k *= bio_discount

    mop_kg = (target_k / 60.0) * 100.0
    dap_kg = (target_p / 46.0) * 100.0
    n_from_dap = dap_kg * 0.18
    rem_n = max(0.0, target_n - n_from_dap)
    urea_kg = (rem_n / 46.0) * 100.0

    # คำนวณปริมาณสินค้าชีวภัณฑ์สำหรับนาข้าว
    import math
    resoil_bottles = math.ceil(rai_area * 0.2) if use_resoil else 0  # ReSoil 1 ลิตร ใช้ได้ 5 ไร่ (200cc/ไร่)
    if use_resoil and resoil_bottles < 1:
        resoil_bottles = 1

    biosoil_bags = math.ceil(rai_area * 1.0) if use_bio_duo else 0  # 1 ถุง (15 กก.) ต่อไร่
    biomax_liters = round((rai_area * 100.0) / 1000.0, 2) if use_bio_duo else 0.0 # 100 cc ต่อไร่
    biomax_bottles = math.ceil(biomax_liters) if biomax_liters > 0 else 0

    pest_bottles = math.ceil(rai_area * 0.2) if use_pest_repellent else 0 # สารไล่แมลง 1 ลิตร ต่อ 5 ไร่
    if use_pest_repellent and pest_bottles < 1:
        pest_bottles = 1

    return {
        "stage_name": s_data["name"],
        "water_management": s_data["water_advice"],
        "commercial_recommendation": s_data["commercial"],
        "chemical_kg": {
            "urea_46_0_0": round(urea_kg, 1),
            "dap_18_46_0": round(dap_kg, 1),
            "mop_0_0_60": round(mop_kg, 1)
        },
        "bio_products": {
            "resoil_bottles": resoil_bottles,
            "biosoil_bags_15kg": biosoil_bags,
            "biomax_bottles": biomax_bottles,
            "pest_repellent_bottles": pest_bottles
        }
    }

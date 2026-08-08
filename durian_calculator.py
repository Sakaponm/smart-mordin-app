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
    """
    ฟังก์ชันคำนวณปุ๋ยทุเรียนอัจฉริยะ รองรับการวัดค่า N (ppm) จากเครื่องตรวจดิน
    """
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
    
    # ตัวคูณปรับแก้ตามค่า N (ppm)
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

    # 1. คำนวณแม่ปุ๋ยเดี่ยว
    mop_g = (target_k / 60.0) * 100.0
    dap_g = (target_p / 46.0) * 100.0
    n_from_dap = dap_g * 0.18
    remaining_n = max(0.0, target_n - n_from_dap)
    urea_g = (remaining_n / 46.0) * 100.0

    # 2. คำนวณทางเลือกปุ๋ยสูตรสำเร็จ
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

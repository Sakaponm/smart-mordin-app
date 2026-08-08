def calculate_durian_fertilizer_api(
    canopy_diameter_m: float,
    tree_count: int,
    stage: str,
    soil_ph: float,
    soil_om: float,
    soil_p_ppm: float,
    soil_k_ppm: float,
    use_bio_duo: bool = True
) -> dict:
    """
    ฟังก์ชันคำนวณปุ๋ยทุเรียนอัจฉริยะ รองรับโหมดเคมีปกติ และโหมดลดปุ๋ยเคมี 50% ด้วย BioMax + BioSoil
    """
    # 1. ความต้องการธาตุอาหารพื้นฐาน (กรัม/ต้น) อ้างอิงทรงพุ่ม 5 เมตร
    BASE_REQUIREMENTS = {
        "stage_1": {"N": 300, "P": 100, "K": 150, "name": "ฟื้นฟูต้น/ทำใบ"},
        "stage_2": {"N": 100, "P": 300, "K": 300, "name": "สะสมอาหารทำดอก"},
        "stage_3": {"N": 200, "P": 100, "K": 300, "name": "ขยายขนาดผล"},
        "stage_4": {"N": 50,  "P": 50,  "K": 400, "name": "ทำหวานก่อนเก็บเกี่ยว"}
    }
    
    stage_data = BASE_REQUIREMENTS.get(stage, BASE_REQUIREMENTS["stage_1"])
    
    # 2. ตัวคูณขนาดทรงพุ่ม (Size Factor)
    size_factor = canopy_diameter_m / 5.0
    
    base_n = stage_data["N"] * size_factor
    base_p = stage_data["P"] * size_factor
    base_k = stage_data["K"] * size_factor
    
    # 3. ตัวคูณปรับแก้ตามค่าวิเคราะห์ดิน (Soil Correction Factors)
    f_n = 1.2 if soil_om < 1.5 else (0.8 if soil_om > 3.5 else 1.0)
    f_p = 1.2 if soil_p_ppm < 15 else (0.5 if soil_p_ppm > 45 else 1.0)
    f_k = 1.2 if soil_k_ppm < 60 else (0.75 if soil_k_ppm > 120 else 1.0)
    
    # ประสิทธิภาพปุ๋ยตามค่า pH
    eff_ph = 0.5 if (soil_ph < 5.0 or soil_ph > 7.5) else 1.0
    
    # 4. คำนวณธาตุอาหารบริสุทธิ์เป้าหมายต่อต้น (Grams/Tree)
    target_n = (base_n * f_n) / eff_ph
    target_p = (base_p * f_p) / eff_ph
    target_k = (base_k * f_k) / eff_ph
    
    # หากเลือกโหมด Bio-Duo ให้ลดเป้าหมายปุ๋ยเคมีลง 50%
    if use_bio_duo:
        target_n *= 0.5
        target_p *= 0.5
        target_k *= 0.5

    # 5. คำนวณถอดสูตรแม่ปุ๋ยเคมี (กรัม/ต้น)
    # MOP (0-0-60)
    mop_g = (target_k / 60.0) * 100.0
    
    # DAP (18-46-0)
    dap_g = (target_p / 46.0) * 100.0
    n_from_dap = dap_g * 0.18
    
    # Urea (46-0-0)
    remaining_n = max(0.0, target_n - n_from_dap)
    urea_g = (remaining_n / 46.0) * 100.0
    
    # 6. คำนวณชุดชีวภาพ BioMax + BioSoil (หากเปิดใช้งาน)
    bio_data = {}
    if use_bio_duo:
        biosoil_kg_per_tree = 0.5 * canopy_diameter_m
        total_biosoil_kg = biosoil_kg_per_tree * tree_count
        
        water_liters_total = 20.0 * tree_count
        biomax_liters_total = water_liters_total / 1000.0  # อัตราส่วน 1 ลิตร : 1,000 ลิตร[cite: 1, 2]
        
        bio_data = {
            "bio_soil": {
                "kg_per_tree": round(biosoil_kg_per_tree, 2),
                "total_kg": round(total_biosoil_kg, 2),
                "bags_50kg": round(total_biosoil_kg / 50.0, 1)
            },
            "bio_max": {
                "total_water_liters": round(water_liters_total, 1),
                "biomax_liters_required": round(biomax_liters_total, 2)
            }
        }

    # 7. ข้อความแจ้งเตือนสุขภาพดิน
    soil_alert = "สภาพดินปกติ"
    if soil_ph < 5.0:
        soil_alert = f"ดินกรดจัด (pH {soil_ph}) ทำให้ปุ๋ยละลายได้ไม่ดี แนะนำใส่โดโลไมต์ {round(0.5 * canopy_diameter_m, 1)} กก./ต้น ก่อนใส่ปุ๋ย 15 วัน"
    elif soil_ph > 7.5:
        soil_alert = f"ดินมีความเป็นด่างสูง (pH {soil_ph}) ระวังการขาดธาตุอาหารรอง"

    # 8. คำนวณรวมทั้งสวน (กิโลกรัม)
    return {
        "mode": "BIO_RECOVERY_50_PERCENT" if use_bio_duo else "100_PERCENT_CHEMICAL",
        "stage_name": stage_data["name"],
        "per_tree_chemical_g": {
            "urea_46_0_0": round(urea_g, 1),
            "dap_18_46_0": round(dap_g, 1),
            "mop_0_0_60": round(mop_g, 1),
            "total_mix_g": round(urea_g + dap_g + mop_g, 1)
        },
        "total_farm_chemical_kg": {
            "urea_46_0_0_kg": round((urea_g * tree_count) / 1000.0, 2),
            "dap_18_46_0_kg": round((dap_g * tree_count) / 1000.0, 2),
            "mop_0_0_60_kg": round((mop_g * tree_count) / 1000.0, 2)
        },
        "bio_products": bio_data,
        "soil_diagnostics": {
            "soil_ph": soil_ph,
            "alert_message": soil_alert
        }
    }

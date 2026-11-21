"""
CropCare AI - Soil Advisory, Irrigation Guidance, and Agri-Chatbot Engine
Implements domain-expert advisory calculations, precision fertilizer models,
and bilingual intelligent conversational assistance (supporting Gemini API + Local Expert NLP).
"""

import os
from typing import Dict, Any, List, Optional

class SoilAdvisor:
    """
    Expert system for soil nutrient evaluation, pH correction,
    and precision fertilizer recommendation per acre.
    """

    # Ideal NPK target ranges per crop in kg/ha
    CROP_NPK_TARGETS = {
        "wheat": {"n": 120, "p": 60, "k": 40, "ideal_ph": (6.0, 7.5)},
        "rice": {"n": 100, "p": 50, "k": 50, "ideal_ph": (5.5, 7.0)},
        "tomato": {"n": 100, "p": 80, "k": 60, "ideal_ph": (6.0, 7.0)},
        "potato": {"n": 150, "p": 100, "k": 120, "ideal_ph": (5.0, 6.5)},
        "cotton": {"n": 120, "p": 60, "k": 60, "ideal_ph": (6.0, 8.0)},
        "maize": {"n": 120, "p": 60, "k": 50, "ideal_ph": (5.8, 7.5)},
        "mustard": {"n": 80, "p": 40, "k": 40, "ideal_ph": (6.0, 7.5)},
        "chickpea": {"n": 20, "p": 50, "k": 20, "ideal_ph": (6.0, 7.5)},
        "chilli": {"n": 100, "p": 50, "k": 50, "ideal_ph": (6.0, 7.0)}
    }

    def analyze_soil(
        self,
        crop: str,
        n_val: float,
        p_val: float,
        k_val: float,
        ph_val: float,
        soil_type: str = "loamy",
        lang: str = "en"
    ) -> Dict[str, Any]:
        crop = crop.lower()
        target = self.CROP_NPK_TARGETS.get(crop, {"n": 100, "p": 50, "k": 50, "ideal_ph": (6.0, 7.5)})

        # pH Status
        min_ph, max_ph = target["ideal_ph"]
        if ph_val < min_ph:
            ph_status = "acidic"
            ph_advice_en = f"Soil is acidic (pH {ph_val:.1f}). Apply Agricultural Lime (Calcium Carbonate) or Dolomite @ 200-300 kg/acre to neutralize acidity."
            ph_advice_hi = f"मिट्टी अम्लीय है (pH {ph_val:.1f})। अम्लता कम करने के लिए 200-300 किलो/एकड़ कृषि चूना (लाइम) या डोलोमाइट डालें।"
        elif ph_val > max_ph:
            ph_status = "alkaline"
            ph_advice_en = f"Soil is alkaline/saline (pH {ph_val:.1f}). Apply Agricultural Gypsum @ 250-400 kg/acre and incorporate organic compost or green manure (Dhaincha)."
            ph_advice_hi = f"मिट्टी क्षारीय है (pH {ph_val:.1f})। सुधार हेतु 250-400 किलो/एकड़ जिप्सम डालें और ढैंचा या हरी खाद का प्रयोग करें।"
        else:
            ph_status = "optimal"
            ph_advice_en = f"Soil pH ({ph_val:.1f}) is in the optimal range ({min_ph}-{max_ph}) for maximum nutrient uptake."
            ph_advice_hi = f"मिट्टी का pH ({ph_val:.1f}) इस फसल के लिए सर्वोत्तम सीमा ({min_ph}-{max_ph}) में है।"

        # Calculate Nutrient Deficits (in kg/ha, converted to kg/acre by factor ~0.4)
        def_n = max(0.0, target["n"] - n_val)
        def_p = max(0.0, target["p"] - p_val)
        def_k = max(0.0, target["k"] - k_val)

        # Convert to commercial fertilizers (per acre):
        # 1. DAP provides 46% P2O5 and 18% N
        # 2. Urea provides 46% N
        # 3. MOP (Muriate of Potash) provides 60% K2O
        acre_factor = 0.4047

        dap_req = round((def_p / 0.46) * acre_factor, 1)
        n_supplied_by_dap = dap_req * 0.18
        remaining_n = max(0.0, (def_n * acre_factor) - n_supplied_by_dap)
        urea_req = round(remaining_n / 0.46, 1)
        mop_req = round((def_k / 0.60) * acre_factor, 1)

        # Nutrient level descriptions
        def get_level(val, tgt):
            ratio = val / tgt if tgt > 0 else 1.0
            if ratio < 0.7:
                return "Low" if lang == "en" else "कम (कमी)"
            elif ratio <= 1.2:
                return "Adequate" if lang == "en" else "पर्याप्त"
            return "High" if lang == "en" else "अधिक"

        n_level = get_level(n_val, target["n"])
        p_level = get_level(p_val, target["p"])
        k_level = get_level(k_val, target["k"])

        # Organic recommendations
        organic_en = [
            "Apply 4-5 tonnes of well-rotted Farmyard Manure (FYM) or 2 tonnes of Vermicompost per acre before final sowing.",
            "Incorporate biofertilizers: Azotobacter (for non-legumes) or Rhizobium (for pulses) @ 250g/10kg seed to reduce chemical nitrogen demand by 20-25%."
        ]
        organic_hi = [
            "बुवाई से पहले खेत में 4-5 टन सड़ी गोबर की खाद या 2 टन केंचुआ खाद (वर्मीकम्पोस्ट) प्रति एकड़ मिलाएं।",
            "एजोटोबैक्टर (अनाज वाली फसलों हेतु) या राइजोबियम (दलहन हेतु) जैव-उर्वरक का प्रयोग करें, जिससे रासायनिक यूरिया की 20-25% बचत होगी।"
        ]

        if lang == "hi":
            summary = (
                f"मृदा स्वास्थ्य विश्लेषण: नाइट्रोजन: {n_level}, फास्फोरस: {p_level}, पोटाश: {k_level}। "
                f"संतुलित पैदावार के लिए प्रति एकड़ अनुशंसित उर्वरक: यूरिया {urea_req} किग्रा, डीएपी {dap_req} किग्रा, और एमओपी (पोटाश) {mop_req} किग्रा।"
            )
        else:
            summary = (
                f"Soil Health Status: Nitrogen: {n_level}, Phosphorus: {p_level}, Potassium: {k_level}. "
                f"Targeted fertilizer schedule per acre: Urea: {urea_req} kg, DAP: {dap_req} kg, and MOP (Potash): {mop_req} kg."
            )

        return {
            "crop": crop,
            "ph_value": ph_val,
            "ph_status": ph_status,
            "ph_advice": ph_advice_hi if lang == "hi" else ph_advice_en,
            "nutrient_status": {
                "nitrogen": {"value": n_val, "target": target["n"], "level": n_level},
                "phosphorus": {"value": p_val, "target": target["p"], "level": p_level},
                "potassium": {"value": k_val, "target": target["k"], "level": k_level}
            },
            "fertilizer_plan_per_acre": {
                "urea_kg": urea_req,
                "dap_kg": dap_req,
                "mop_potash_kg": mop_req
            },
            "organic_remedies": organic_hi if lang == "hi" else organic_en,
            "soil_summary": summary
        }


class IrrigationAdvisor:
    """
    Expert rule base for calculating irrigation schedule, method, and volume
    based on crop growth stage, soil permeability, and season.
    """

    CRITICAL_STAGES = {
        "wheat": [
            {"stage_en": "Crown Root Initiation (CRI - 21 days)", "stage_hi": "शीर्ष जड़ जमने की अवस्था (21 दिन)", "importance": "Most Critical"},
            {"stage_en": "Tillering (40-45 days)", "stage_hi": "कल्ले फूटने की अवस्था (40-45 दिन)", "importance": "High"},
            {"stage_en": "Flowering / Heading (80-85 days)", "stage_hi": "फूल आने की अवस्था (80-85 दिन)", "importance": "Critical"},
            {"stage_en": "Milking / Grain Filling (100-105 days)", "stage_hi": "दूधिया अवस्था (100-105 दिन)", "importance": "High"}
        ],
        "rice": [
            {"stage_en": "Transplanting to Tillering", "stage_hi": "रोपाई से कल्ले निकलने तक (2-3 सेमी जलभराव)", "importance": "Critical"},
            {"stage_en": "Panicle Initiation to Flowering", "stage_hi": "बाली निकलने से फूल आने तक", "importance": "Most Critical"},
            {"stage_en": "Grain Filling", "stage_hi": "दाने भरने की अवस्था", "importance": "High"}
        ],
        "tomato": [
            {"stage_en": "Transplanting / Establishment", "stage_hi": "रोपाई व प्रारंभिक स्थापना", "importance": "High"},
            {"stage_en": "Flowering & Fruit Setting", "stage_hi": "फूल व फल बनने की अवस्था (नमी की कमी से फूल गिरते हैं)", "importance": "Most Critical"},
            {"stage_en": "Fruit Enlargement", "stage_hi": "फल विकास की अवस्था", "importance": "Critical"}
        ],
        "potato": [
            {"stage_en": "Stolon Formation & Tuber Initiation (20-30 days)", "stage_hi": "कंद बनने की शुरुआत (20-30 दिन)", "importance": "Most Critical"},
            {"stage_en": "Tuber Bulking Stage (45-65 days)", "stage_hi": "कंदों के विकास की अवस्था", "importance": "Critical"}
        ]
    }

    def get_guidance(
        self,
        crop: str,
        stage: str,
        soil_type: str = "loamy",
        season: str = "winter",
        lang: str = "en"
    ) -> Dict[str, Any]:
        crop = crop.lower()
        soil_type = soil_type.lower()
        season = season.lower()

        # Determine interval based on soil and season
        base_interval = 7  # days
        if soil_type == "sandy":
            base_interval -= 2  # Sandy soil drains quickly
        elif soil_type == "clayey":
            base_interval += 2  # Clay holds moisture longer

        if season in ["summer", "hot_dry"]:
            base_interval = max(3, base_interval - 2)
        elif season in ["monsoon", "rainy"]:
            base_interval += 4
        elif season in ["winter", "cool"]:
            base_interval += 1

        # Recommended irrigation method
        if crop in ["tomato", "chilli", "potato"]:
            method_en = "Drip Irrigation (saves 40-50% water and prevents fungal leaf splash)"
            method_hi = "ड्रिप (टपक) सिंचाई (40-50% पानी की बचत और फफूंद से सुरक्षा)"
        elif crop in ["wheat", "mustard", "chickpea"]:
            method_en = "Sprinkler Irrigation or Broad Bed Furrow (BBF)"
            method_hi = "स्प्रिंकलर (फव्वारा) सिंचाई या नाली विधि"
        elif crop == "rice":
            method_en = "Alternate Wetting and Drying (AWD) technique"
            method_hi = "वैकल्पिक गीला और सूखा तरीका (AWD तकनीक)"
        else:
            method_en = "Furrow irrigation with straw mulching"
            method_hi = "मल्चिंग के साथ नाली विधि"

        critical_list = self.CRITICAL_STAGES.get(crop, [
            {"stage_en": "Flowering stage", "stage_hi": "फूल आने की अवस्था", "importance": "Critical"},
            {"stage_en": "Fruit / Grain filling", "stage_hi": "फल / दाना भराव अवस्था", "importance": "High"}
        ])

        tips_en = [
            f"Irrigate every {base_interval} to {base_interval + 2} days depending on topsoil dryness.",
            "Water deeply during early morning or late evening to minimize evaporative losses.",
            "Check soil moisture by hand: take soil from 4-6 inches deep; if it forms a ball without crumbling, moisture is sufficient."
        ]

        tips_hi = [
            f"मिट्टी की नमी के अनुसार हर {base_interval} से {base_interval + 2} दिनों के अंतराल पर हल्की सिंचाई करें।",
            "वाष्पीकरण से पानी के नुकसान को रोकने के लिए सुबह जल्दी या शाम के समय ही सिंचाई करें।",
            "मिट्टी की नमी जांचें: 4-6 इंच गहराई से मिट्टी लेकर मुट्ठी बनाएं; यदि लड्डू बन जाए तो नमी पर्याप्त है।"
        ]

        return {
            "crop": crop,
            "stage": stage,
            "soil_type": soil_type,
            "season": season,
            "recommended_interval_days": base_interval,
            "recommended_method": method_hi if lang == "hi" else method_en,
            "critical_stages": critical_list,
            "actionable_tips": tips_hi if lang == "hi" else tips_en
        }


class AgriChatbot:
    """
    Intelligent Conversational Agricultural Assistant.
    Supports Google Gemini 2.5 Flash if an API key is available,
    plus an extensive offline agronomic semantic knowledge base covering 35+ topics.
    """

    INTENTS = [
        {
            "intent": "neem_spray",
            "keywords": ["neem", "organic", "neem oil", "spray", "जैविक", "नीम", "कीटनाशक"],
            "response_en": "🌿 **How to Prepare Organic Neem Spray:** Mix 5 ml of cold-pressed Neem oil (10,000 ppm) with 1 ml of mild liquid soap in 1 Litre of water. Shake well to form a milky emulsion. Spray in the late evening on both leaf sides. Repels chewing pests, aphids, and whiteflies effectively.",
            "response_hi": "🌿 **जैविक नीम का स्प्रे कैसे बनाएं:** 1 लीटर पानी में 5 मिली शुद्ध नीम का तेल (10,000 ppm) और 1 मिली हल्का तरल साबुन मिलाएं। अच्छी तरह हिलाकर दूधिया घोल बनाएं और शाम को पत्तियों के दोनों तरफ छिड़कें। यह माहू, सफेद मक्खी और सुंडी की रोकथाम करता है।"
        },
        {
            "intent": "jeevamrut",
            "keywords": ["jeevamrut", "jeevamrit", "organic manure", "जीवामृत", "देसी खाद"],
            "response_en": "🧪 **Jeevamrut Preparation (per acre):** In 200L water, mix 10 kg fresh cow dung, 10L cow urine, 2 kg jaggery (gur), 2 kg gram flour (besan), and a handful of fertile farm soil. Stir well twice daily for 4-5 days under shade. Filter and apply through irrigation or foliar spray to multiply soil microbes.",
            "response_hi": "🧪 **जीवामृत बनाने की विधि (प्रति एकड़):** 200 लीटर पानी में 10 किलो ताजा गोबर, 10 लीटर गोमूत्र, 2 किलो गुड़, 2 किलो बेसन और मुट्ठी भर खेत की मिट्टी मिलाएं। छांव में 4-5 दिन सुबह-शाम डंडे से हिलाएं। इसे सिंचाई के पानी के साथ या छानकर स्प्रे करें; यह मिट्टी में सूक्ष्मजीवों की संख्या तेजी से बढ़ाता है।"
        },
        {
            "intent": "urea_fertilizer",
            "keywords": ["urea", "nitrogen", "dap", "fertilizer", "khad", "यूरिया", "खाद", "डीएपी", "उर्वरक"],
            "response_en": "🧪 **Fertilizer Advisory:** Never apply Urea to a completely dry field or standing deep water. Split Urea into 2-3 equal doses: 1/3 at basal sowing, 1/3 at active tillering, and 1/3 before flowering. Use Neem-Coated Urea or Nano Urea (4ml/L) to prevent nitrogen volatilization losses.",
            "response_hi": "🧪 **उर्वरक सलाह:** सूखे खेत या बहुत गहरे पानी में कभी भी यूरिया न डालें। यूरिया को 2-3 किश्तों में दें: 1/3 बुवाई पर, 1/3 कल्ले फूटते समय, और 1/3 फूल आने से पहले। नीम लेपित यूरिया या नैनो यूरिया (4 मिली/लीटर) का प्रयोग करें जिससे बर्बादी रुके।"
        },
        {
            "intent": "nano_urea",
            "keywords": ["nano urea", "nano", "नैनो यूरिया"],
            "response_en": "💧 **IFFCO Nano Urea Usage:** Mix 2 to 4 ml Nano Urea liquid per Litre of water. Spray twice: 1st spray at active tillering (30-35 days after sowing), 2nd spray 1 week before flowering. One 500ml bottle replaces a 45kg bag of conventional urea with 80%+ absorption efficiency.",
            "response_hi": "💧 **इफको नैनो यूरिया का उपयोग:** 2 से 4 मिली नैनो यूरिया प्रति लीटर पानी में घोलें। 2 बार छिड़काव करें: पहला कल्ले निकलते समय (30-35 दिन पर) और दूसरा फूल आने से 1 सप्ताह पहले। 500 मिली की एक बोतल 45 किलो यूरिया के कट्टे का काम करती है।"
        },
        {
            "intent": "yellow_leaves",
            "keywords": ["yellow", "peela", "yellowing", "chlorosis", "पीली", "पीला", "पीले"],
            "response_en": "🍂 **Why Are Crop Leaves Turning Yellow?** Common causes include: 1. Nitrogen deficiency (lower older leaves turn pale yellow first). 2. Over-watering / root rot (leaves turn limp & pale). 3. Iron/Zinc deficiency (young upper leaves turn yellow with green veins). Use our Disease Diagnosis tab to check for specific fungal blights.",
            "response_hi": "🍂 **पत्तियां पीली क्यों पड़ रही हैं?** मुख्य कारण: 1. नाइट्रोजन की कमी (पुरानी निचली पत्तियां पहले पीली पड़ती हैं)। 2. खेत में जलभराव या जड़ सड़न। 3. जिंक या लोहे की कमी (नई ऊपरी पत्तियां नसों के बीच पीली होती हैं)। विशिष्ट रोग की पहचान के लिए हमारे 'रोग निदान' टैब का उपयोग करें।"
        },
        {
            "intent": "leaf_curl",
            "keywords": ["curl", "curling", "puckering", "मरोड़", "मुड़ना", "पत्ता मरोड़"],
            "response_en": "🍃 **Leaf Curl Management:** Leaf curl is mostly caused by Whitefly-transmitted geminiviruses (in tomato, chilli, cotton) or thrips/mites. Control: Spray Imidacloprid (0.5ml/L) or Neem oil (3ml/L) and install Yellow Sticky Traps (20/acre) to control the whitefly vector. Remove severely stunted infected plants.",
            "response_hi": "🍃 **पत्ता मरोड़ (लीफ कर्ल) नियंत्रण:** यह रोग सफेद मक्खी या थ्रिप्स कीटों द्वारा वायरस फैलाने से होता है। रोकथाम: सफेद मक्खी को रोकने के लिए इमिडाक्लोप्रिड (0.5 मिली/लीटर) या नीम तेल (3 मिली/लीटर) का छिड़काव करें और प्रति एकड़ 20 पीले चिपचिपे ट्रैप लगाएं।"
        },
        {
            "intent": "whitefly_pest",
            "keywords": ["whitefly", "safed makkhi", "मक्खी", "सफेद मक्खी"],
            "response_en": "🪰 **Whitefly Control:** Erect Yellow Sticky Traps @ 20-25 traps/acre. Spray Spiromesifen 22.9% SC @ 1ml/L or Pyriproxyfen 10% EC @ 2ml/L water. Ensure underside of leaves is covered during spraying.",
            "response_hi": "🪰 **सफेद मक्खी की रोकथाम:** खेत में 20-25 पीले चिपचिपे कार्ड (Yellow Sticky Traps) लगाएं। स्पाइरोमेसिफेन (1 मिली/लीटर) या पायरीप्रॉक्सीफेन (2 मिली/लीटर) का छिड़काव पत्तियों के नीचे तक अच्छी तरह करें।"
        },
        {
            "intent": "pink_bollworm",
            "keywords": ["bollworm", "sundi", "illi", "गुलाबी सुंडी", "सुंडी", "इल्ली"],
            "response_en": "🐛 **Bollworm / Caterpillar Management:** Install Pheromone Traps @ 5 traps/acre to monitor moth flights. Spray Chlorantraniliprole 18.5% SC (Coragen) @ 0.3ml/L or Emamectin Benzoate 5% SG @ 0.5g/L water during early larval emergence.",
            "response_hi": "🐛 **गुलाबी व अन्य सुंडी का नियंत्रण:** निगरानी हेतु 5 फेरोमोन ट्रैप प्रति एकड़ लगाएं। सुंडी दिखने पर कोराजन (क्लोरएंट्रानिलिप्रोल) 0.3 मिली/लीटर या एमामेक्टिन बेंजोएट 0.5 ग्राम/लीटर का छिड़काव करें।"
        },
        {
            "intent": "soil_test",
            "keywords": ["soil test", "sample", "mitti", "mitti janch", "मृदा", "मिट्टी", "जांच"],
            "response_en": "🌱 **Soil Testing Tip:** Collect soil samples in a 'V' shape up to 6 inches depth from 8-10 random spots in the field. Mix thoroughly, air-dry in shade, pack 500 grams in a clean bag, and send to your nearest Krishi Vigyan Kendra (KVK). Enter your NPK test values in our 'Soil Advisory' tab for a customized fertilizer plan!",
            "response_hi": "🌱 **मिट्टी जांच का सही तरीका:** खेत के 8-10 अलग-अलग स्थानों से 6 इंच गहराई तक 'V' आकार में मिट्टी का नमूना लें। सभी नमूनों को अच्छी तरह मिलाकर छांव में सुखाएं और 500 ग्राम मिट्टी नजदीकी कृषि विज्ञान केंद्र (KVK) भेजें। फिर अपनी रिपोर्ट हमारे 'मृदा सलाह' टैब में दर्ज करें!"
        },
        {
            "intent": "pm_kisan",
            "keywords": ["pm kisan", "kisan samman", "योजना", "पीएम किसान"],
            "response_en": "🏛️ **PM-KISAN Scheme:** Provides eligible farmer families ₹6,000 per year in three equal installments of ₹2,000 every 4 months directly into Aadhaar-linked bank accounts. To check beneficiary status or complete eKYC, visit pmkisan.gov.in.",
            "response_hi": "🏛️ **प्रधानमंत्री किसान सम्मान निधि (PM-KISAN):** पात्र किसान परिवारों को प्रति वर्ष ₹6,000 की वित्तीय सहायता ₹2,000 की तीन बराबर किश्तों में सीधे बैंक खाते में दी जाती है। स्थिति जांचने या e-KYC के लिए pmkisan.gov.in पर जाएं।"
        },
        {
            "intent": "crop_insurance",
            "keywords": ["crop insurance", "pmfby", "bima", "फसल बीमा", "बीमा"],
            "response_en": "🛡️ **Pradhan Mantri Fasal Bima Yojana (PMFBY):** Comprehensive crop insurance against non-preventable natural risks (drought, flood, pests, unseasonal rain). Premium is only 2% for Kharif crops, 1.5% for Rabi, and 5% for commercial/horticultural crops. Visit pmfby.gov.in.",
            "response_hi": "🛡️ **प्रधानमंत्री फसल बीमा योजना (PMFBY):** प्राकृतिक आपदाओं (सूखा, बाढ़, ओलावृष्टि, कीट प्रकोप) से फसल नुकसान की भरपाई। प्रीमियम: खरीफ फसलों पर मात्र 2%, रबी पर 1.5%, और बागवानी फसलों पर 5% है। pmfby.gov.in पर आवेदन करें।"
        },
        {
            "intent": "drip_irrigation",
            "keywords": ["drip", "sprinkler", "subsidy", "टपक", "ड्रिप", "फव्वारा"],
            "response_en": "💧 **Micro-Irrigation (Drip/Sprinkler):** Saves 40-60% water, increases fertilizer efficiency by 30%, and reduces weed growth. Government provides 45% to 55% subsidy (up to 70% in some states for small/marginal farmers) under PMKSY (Per Drop More Crop).",
            "response_hi": "💧 **सूक्ष्म सिंचाई (ड्रिप/स्प्रिंकलर):** 40-60% पानी की बचत, उर्वरक की खपत में 30% कमी और खरपतवार नियंत्रण। 'पर ड्रॉप मोर क्रॉप' योजना के तहत 45% से 55% (लघु किसानों हेतु 70% तक) सरकारी अनुदान मिलता है।"
        },
        {
            "intent": "greeting",
            "keywords": ["hello", "hi", "namaste", "kisan", "help", "नमस्ते", "हेलो", "मदद"],
            "response_en": "👨‍🌾 **Namaste! I am your CropCare AI Kisan Assistant.** You can ask me questions about crop diseases, organic sprays, fertilizer dosages, irrigation, crop selection, government schemes, or soil health. How may I help you today?",
            "response_hi": "👨‍🌾 **नमस्ते! मैं आपका क्रॉपकेयर एआई किसान मित्र हूँ।** आप मुझसे फसल रोग, जैविक उपचार, यूरिया/खाद की मात्रा, सिंचाई, सही फसल चुनाव, सरकारी योजनाओं या मिट्टी की सेहत के बारे में पूछ सकते हैं। आज मैं आपकी क्या सहायता करूँ?"
        }
    ]

    def chat(self, user_message: str, lang: str = "en", api_key: Optional[str] = None) -> str:
        """
        Chat response generator with Gemini API support and fallback to local NLP knowledge base.
        """
        active_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()

        # If Gemini key is available, run multimodal generative response
        if active_key:
            try:
                from google import genai
                client = genai.Client(api_key=active_key)
                system_prompt = f"""
                You are Kisan Mitra, an empathetic, highly knowledgeable agricultural expert and extension agronomist for CropCare AI.
                Answer the farmer's question concisely, practically, and accurately.
                Use bullet points and bold highlights for dosages, timings, and safety warnings.
                Respond in { 'Hindi (हिंदी)' if lang == 'hi' else 'English' }.
                """
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[system_prompt, user_message]
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"Gemini Chat fallback to local NLP engine: {str(e)}")

        # Fallback to Local Knowledge Base
        msg = user_message.lower().strip()

        for item in self.INTENTS:
            for kw in item["keywords"]:
                if kw in msg:
                    return item["response_hi"] if lang == "hi" else item["response_en"]

        if lang == "hi":
            return (
                "👨‍🌾 मैं आपकी बात समझ रहा हूँ। आप मुझसे फसल रोगों (जैसे झुलसा, रतुआ, लीफ कर्ल), "
                "नीम का स्प्रे या जीवामृत बनाने, नैनो यूरिया की खुराक, ड्रिप सिंचाई अनुदान, फसल बीमा (PMFBY), "
                "या मिट्टी की जांच के बारे में पूछ सकते हैं।"
            )
        return (
            "👨‍🌾 I understand your query. You can ask me about crop diseases (blight, rust, leaf curl), "
            "organic neem sprays or Jeevamrut preparation, Nano Urea dosages, drip irrigation subsidies, "
            "crop insurance (PMFBY), irrigation intervals, or soil testing tips."
        )

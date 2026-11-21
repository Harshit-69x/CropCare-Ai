/**
 * CropCare AI - Internationalization (i18n) Module
 * Provides seamless English and Hindi bilingual switching for UI elements.
 */

const translations = {
    en: {
        app_title: "CropCare AI",
        app_subtitle: "Smart Agriculture Expert System & Crop Advisory",
        nav_dashboard: "Dashboard",
        nav_diagnosis: "Disease Diagnosis",
        nav_crop_rec: "Crop Recommender",
        nav_soil: "Soil Advisory",
        nav_irrigation: "Irrigation Guide",
        nav_chat: "Kisan Mitra Bot",
        nav_history: "Records & History",
        lang_btn: "हिंदी",
        btn_api_settings: "AI Settings",

        // Hero
        hero_badge: "AI-Powered Vision & Agronomic Intelligence",
        hero_title: "Intelligent Crop Health & Precision Farming Advisory",
        hero_desc: "Computer vision plant pathology, ML crop recommendation, precision soil fertilizer planning, irrigation scheduling, and bilingual farming guidance.",
        btn_start_diag: "Diagnose Leaf Disease",
        btn_recommend_crop: "Recommend Optimal Crop",
        btn_soil_plan: "Plan Soil Fertilizer",

        // Stats
        stat_diagnoses: "Diagnoses Generated",
        stat_recommendations: "Crops Recommended",
        stat_confidence: "Avg Diagnosis Certainty",
        stat_soil_records: "Soil Tests Evaluated",
        stat_crops_supported: "Supported Major Crops",

        // Diagnosis Tab
        diag_title: "Crop Disease Diagnosis Engine",
        diag_desc: "Upload a diseased plant leaf photograph for AI computer vision inspection, or pick observed symptoms for expert rule evaluation.",
        step1_crop: "1. Select Crop (Optional if uploading leaf)",
        step2_weather: "2. Field Conditions & Weather",
        step3_symptoms: "3. Observable Plant Symptoms",
        step4_image: "4. Leaf Photo Upload (AI Vision)",
        label_crop: "Target Crop",
        label_growth_stage: "Growth Stage",
        label_weather: "Current Field Weather",
        stage_seedling: "Seedling (0-20 days)",
        stage_vegetative: "Vegetative Growth",
        stage_flowering: "Flowering & Fruit Setting",
        stage_maturity: "Maturity / Grain Filling",
        weather_normal: "Normal / Moderate",
        weather_warm_humid: "Warm & Humid (High Fungal Risk)",
        weather_cool_wet: "Cool & Wet / Foggy",
        weather_dry_hot: "Dry & Hot (High Whitefly / Pest Risk)",
        filter_all_parts: "All Symptoms",
        filter_leaf: "Leaf",
        filter_stem: "Stem",
        filter_fruit: "Fruit / Grain",
        filter_whole: "Whole Plant",
        selected_symptoms_count: "Selected Symptoms",
        btn_run_diag: "Run AI Vision & Diagnosis",
        btn_reset_diag: "Reset Form",
        drag_drop_text: "Drag & drop leaf photo here, or click to browse",
        drop_formats: "PNG, JPG, WEBP up to 16MB",
        upload_badge: "Computer Vision & Gemini Vision Ready",

        // Results
        diag_result_title: "AI Diagnosis & Rule Explanation",
        badge_confidence: "Confidence Score",
        multi_modal_title: "Multi-Modal Diagnostic Evidence Breakdown",
        indep_vision_title: "Independent Computer Vision",
        indep_rules_title: "Independent Expert Rules",
        fusion_reconciliation_title: "Multi-Modal Evidence Reconciliation",
        dual_candidate_title: "Diagnostic Tension: Competing Disease Candidates",
        field_test_title: "Field Discriminating Inspection Test",
        user_symptoms_header: "Farmer-Reported Field Observations",
        image_symptoms_header: "Computer Vision Extracted Foliar Lesions",
        section_explanation: "Expert System Explanation Facility",
        why_fired_title: "Why This Rule Fired (Reasoning Trace)",
        matched_symptoms_title: "Key Matched Symptoms",
        differential_title: "Differential Diagnosis (Other Diseases Considered)",
        treatment_title: "Comprehensive Treatment & Advisory",
        organic_tab: "Organic & Bio-Control",
        chemical_tab: "Chemical Fungicide / Pesticide",
        preventive_tab: "Preventive Practices",
        dosage_label: "Recommended Dosage",
        btn_save_pdf: "Print / Save Diagnosis",

        // Crop Recommender Tab
        rec_title: "Machine Learning Crop Recommendation",
        rec_desc: "Enter your soil nutrient profile (N-P-K), soil pH, and climate conditions (Temperature, Humidity, Rainfall) to identify the most suitable and profitable crop.",
        rec_preset_rice: "Monsoon Paddy (High Rain)",
        rec_preset_wheat: "Winter Wheat (Cool/Dry)",
        rec_preset_maize: "Summer Maize (Warm)",
        rec_preset_pulses: "Arid Chickpea (Low N, High P/K)",
        label_temp: "Temperature (°C)",
        label_humidity: "Relative Humidity (%)",
        label_rainfall: "Seasonal Rainfall (mm)",
        btn_predict_crop: "Predict Best Crop",
        rec_result_title: "Top Recommended Crop",
        rec_suitability: "Suitability Score",
        rec_duration: "Maturity Period",
        rec_season: "Sowing Season",
        rec_cultivation_tip: "Key Agronomic Tip",
        rec_alternatives_title: "Alternative Suitable Crops",

        // Soil Advisory
        soil_title: "Soil Health & Precision Fertilizer Advisory",
        soil_desc: "Enter your soil test values (N-P-K & pH) to calculate exact commercial fertilizer bags (Urea, DAP, MOP) and organic amendments per acre.",
        preset_label: "Quick Sample Presets",
        preset_low_n: "Low Nitrogen Soil",
        preset_acidic: "Acidic Soil (Low pH)",
        preset_alkaline: "Alkaline Soil (High pH)",
        preset_balanced: "Balanced Fertile Soil",
        label_n: "Available Nitrogen (N) kg/ha",
        label_p: "Available Phosphorus (P) kg/ha",
        label_k: "Available Potassium (K) kg/ha",
        label_ph: "Soil pH Level",
        label_soil_type: "Soil Texture",
        soil_sandy: "Sandy (Light, Drains Fast)",
        soil_loamy: "Loamy (Ideal Balanced)",
        soil_clayey: "Clayey (Heavy, Holds Water)",
        btn_calculate_fertilizer: "Calculate Fertilizer Plan",
        ph_meter_title: "Soil Reaction (pH Meter)",
        plan_per_acre: "Precision Fertilizer Plan Per Acre",
        urea_badge: "Urea (46% N)",
        dap_badge: "DAP (18% N, 46% P2O5)",
        mop_badge: "MOP / Potash (60% K2O)",
        organic_advisory_title: "Organic Soil Enrichment",

        // Irrigation
        irri_title: "Crop Water & Irrigation Guidance",
        irri_desc: "Calculate watering frequency, critical growth moisture stages, and the best irrigation method to maximize yield and conserve water.",
        label_season: "Season / Climate",
        season_winter: "Winter (Rabi)",
        season_summer: "Summer (Zaid)",
        season_monsoon: "Monsoon (Kharif)",
        btn_get_irrigation: "Get Irrigation Schedule",
        watering_interval_title: "Recommended Watering Interval",
        best_method_title: "Optimal Irrigation Method",
        critical_stages_title: "Critical Crop Moisture Stages",

        // Chatbot
        chat_title: "Kisan Mitra - AI Agricultural Assistant",
        chat_subtitle: "Instant answers for crop diseases, organic remedies, fertilizer rates, and farming tips.",
        chat_placeholder: "Ask a question (e.g., How to prepare organic neem spray?)...",
        chat_send: "Send",
        chip_neem: "🌿 Organic Neem Spray",
        chip_urea: "🧪 Urea Dosage Schedule",
        chip_yellow: "🍂 Yellow Leaves Remedy",
        chip_soil: "🌱 Soil Testing Guide",

        // History
        hist_title: "Saved Advisories & History",
        hist_desc: "Review past disease diagnoses, crop recommendations, and soil test recommendations stored in SQLite database.",
        btn_seed_sample: "Load Sample Data",
        btn_clear_history: "Refresh Records",
        col_date: "Date & Time",
        col_crop: "Crop",
        col_disease: "Diagnosis / Plan",
        col_confidence: "Certainty",
        col_action: "Actions",

        // API Modal
        modal_api_title: "AI Vision & Model Settings",
        modal_api_desc: "Configure an optional Google Gemini API key to enable Gemini 2.5 Flash Vision for multi-modal leaf pathology and AI Chat. If left empty, CropCare AI automatically uses the high-precision Local Computer Vision and Agronomic ML Models offline.",
        modal_api_label: "Google Gemini API Key (Optional)",
        modal_api_save: "Save Settings",
        modal_api_clear: "Use Local Offline Models"
    },
    hi: {
        app_title: "क्रॉपकेयर एआई",
        app_subtitle: "स्मार्ट कृषि विशेषज्ञ प्रणाली एवं फसल परामर्श",
        nav_dashboard: "डैशबोर्ड",
        nav_diagnosis: "रोग निदान",
        nav_crop_rec: "फसल चयन (AI)",
        nav_soil: "मृदा सलाह",
        nav_irrigation: "सिंचाई मार्गदर्शन",
        nav_chat: "किसान मित्र बॉट",
        nav_history: "इतिहास व रिकॉर्ड",
        lang_btn: "English",
        btn_api_settings: "AI सेटिंग्स",

        // Hero
        hero_badge: "एआई विज़न एवं आधुनिक कृषि बुद्धिमत्ता",
        hero_title: "बुद्धिमान फसल स्वास्थ्य एवं सटीक कृषि परामर्श",
        hero_desc: "कंप्यूटर विज़न रोग पहचान, मशीन लर्निंग फसल चयन, सटीक उर्वरक गणना, सिंचाई सारणी और किसान-अनुकूल द्विभाषी मार्गदर्शन।",
        btn_start_diag: "पत्ती रोग की पहचान करें",
        btn_recommend_crop: "सर्वोत्तम फसल जानें",
        btn_soil_plan: "खाद योजना बनाएं",

        // Stats
        stat_diagnoses: "कुल रोग निदान",
        stat_recommendations: "फसल अनुशंसाएं",
        stat_confidence: "औसत निश्चितता",
        stat_soil_records: "मृदा परीक्षण रिकॉर्ड",
        stat_crops_supported: "समर्थित प्रमुख फसलें",

        // Diagnosis Tab
        diag_title: "फसल रोग निदान प्रणाली",
        diag_desc: "एआई कंप्यूटर विज़न जांच हेतु रोगी पत्ती की तस्वीर अपलोड करें, या विशेषज्ञ नियमों के आधार पर लक्षण चुनें।",
        step1_crop: "1. फसल का चयन (फोटो अपलोड करने पर वैकल्पिक)",
        step2_weather: "2. खेत का मौसम व अवस्था",
        step3_symptoms: "3. पौधे में दिखाई देने वाले लक्षण",
        step4_image: "4. पत्ती की फोटो अपलोड (एआई विज़न)",
        label_crop: "लक्षित फसल",
        label_growth_stage: "विकास की अवस्था",
        label_weather: "वर्तमान खेत का मौसम",
        stage_seedling: "अंकुरण / पौध अवस्था (0-20 दिन)",
        stage_vegetative: "वानस्पतिक विकास (बढ़वार)",
        stage_flowering: "फूल व फल बनने की अवस्था",
        stage_maturity: "परिपक्वता / दाना भराव",
        weather_normal: "सामान्य / मध्यम",
        weather_warm_humid: "गर्म व उमस भरा (कवक का अधिक जोखिम)",
        weather_cool_wet: "ठंडा व गीला / कोहरा",
        weather_dry_hot: "सूखा व गर्म (कीट / सफेद मक्खी का प्रकोप)",
        filter_all_parts: "सभी लक्षण",
        filter_leaf: "पत्ती",
        filter_stem: "तना",
        filter_fruit: "फल / बाली",
        filter_whole: "पूरा पौधा",
        selected_symptoms_count: "चुने गए लक्षण",
        btn_run_diag: "एआई विज़न एवं रोग निदान शुरू करें",
        btn_reset_diag: "फॉर्म रीसेट करें",
        drag_drop_text: "पत्ती की तस्वीर यहाँ खींचें या चुनने के लिए क्लिक करें",
        drop_formats: "PNG, JPG, WEBP (अधिकतम 16MB)",
        upload_badge: "कंप्यूटर विज़न एवं जेमिनी विज़न तैयार",

        // Results
        diag_result_title: "एआई रोग निदान एवं नियम स्पष्टीकरण",
        badge_confidence: "निश्चितता गुणांक",
        multi_modal_title: "मल्टी-मॉडल साक्ष्य विश्लेषण (विज़न बनाम नियम)",
        indep_vision_title: "स्वतंत्र कंप्यूटर विज़न",
        indep_rules_title: "स्वतंत्र विशेषज्ञ नियम",
        fusion_reconciliation_title: "मल्टी-मॉडल साक्ष्य समन्वय",
        dual_candidate_title: "निदान विरोधाभास: प्रतिस्पर्धी संभावित रोग",
        field_test_title: "खेत पर विभेदक परीक्षण एवं पुष्टि",
        user_symptoms_header: "किसान द्वारा खेत में देखे गए लक्षण",
        image_symptoms_header: "कंप्यूटर विज़न द्वारा पहचाने गए दृश्य लक्षण",
        section_explanation: "विशेषज्ञ प्रणाली स्पष्टीकरण सुविधा (Explanation Facility)",
        why_fired_title: "यह नियम क्यों लागू हुआ (तार्किक व्याख्या)",
        matched_symptoms_title: "मेल खाने वाले मुख्य लक्षण",
        differential_title: "अन्य संभावित रोग (जिन्हें खारिज किया गया)",
        treatment_title: "विस्तृत उपचार एवं सुरक्षा परामर्श",
        organic_tab: "जैविक व देशी उपचार",
        chemical_tab: "रासायनिक कवकनाशी/कीटनाशी",
        preventive_tab: "निवारक उपाय",
        dosage_label: "अनुशंसित मात्रा व छिड़काव",
        btn_save_pdf: "निदान रिपोर्ट प्रिंट / सेव करें",

        // Crop Recommender Tab
        rec_title: "मशीन लर्निंग फसल चयन प्रणाली (Crop Recommendation)",
        rec_desc: "अपनी मिट्टी के पोषक तत्वों (N-P-K), pH और जलवायु (तापमान, आर्द्रता, वर्षा) को दर्ज करें और सर्वाधिक उपयुक्त एवं लाभकारी फसल जानें।",
        rec_preset_rice: "मानसून धान (अधिक वर्षा)",
        rec_preset_wheat: "सर्दियों का गेहूँ (ठंड/मध्यम)",
        rec_preset_maize: "मक्का (गर्म मौसम)",
        rec_preset_pulses: "चना / दलहन (कम N, अधिक P/K)",
        label_temp: "तापमान (°C)",
        label_humidity: "सापेक्ष आर्द्रता (%)",
        label_rainfall: "मौसमी वर्षा (मिमी)",
        btn_predict_crop: "सर्वोत्तम फसल की भविष्यवाणी करें",
        rec_result_title: "शीर्ष अनुशंसित फसल",
        rec_suitability: "अनुकूलता स्कोर",
        rec_duration: "पकने की अवधि",
        rec_season: "बुवाई का मौसम",
        rec_cultivation_tip: "महत्वपूर्ण कृषि सलाह",
        rec_alternatives_title: "अन्य उपयुक्त वैकल्पिक फसलें",

        // Soil Advisory
        soil_title: "मृदा स्वास्थ्य एवं सटीक उर्वरक सलाह",
        soil_desc: "अपनी मिट्टी की जांच रिपोर्ट (N-P-K और pH) दर्ज करें और प्रति एकड़ आवश्यक यूरिया, डीएपी, पोटाश व जैविक खाद की सटीक मात्रा प्राप्त करें।",
        preset_label: "त्वरित परीक्षण नमूने",
        preset_low_n: "कम नाइट्रोजन वाली मिट्टी",
        preset_acidic: "अम्लीय मिट्टी (कम pH)",
        preset_alkaline: "क्षारीय मिट्टी (अधिक pH)",
        preset_balanced: "संतुलित उपजाऊ मिट्टी",
        label_n: "नाइट्रोजन (N) किग्रा/हेक्टेयर",
        label_p: "फास्फोरस (P) किग्रा/हेक्टेयर",
        label_k: "पोटाश (K) किग्रा/हेक्टेयर",
        label_ph: "मृदा pH मान",
        label_soil_type: "मिट्टी का प्रकार",
        soil_sandy: "रेतीली / बलुई (हल्की)",
        soil_loamy: "दोमट (सर्वोत्तम संतुलित)",
        soil_clayey: "चिकनी मिट्टी (भारी, पानी रोकने वाली)",
        btn_calculate_fertilizer: "उर्वरक योजना तैयार करें",
        ph_meter_title: "मृदा प्रतिक्रिया (pH मीटर)",
        plan_per_acre: "प्रति एकड़ सटीक उर्वरक आवश्यकता",
        urea_badge: "यूरिया (46% N)",
        dap_badge: "डीएपी (18% N, 46% P2O5)",
        mop_badge: "एमओपी / पोटाश (60% K2O)",
        organic_advisory_title: "जैविक मृदा सुधार उपाय",

        // Irrigation
        irri_title: "फसल जल व सिंचाई मार्गदर्शन",
        irri_desc: "अधिकतम पैदावार और पानी की बचत के लिए सिंचाई का सही अंतराल, संवेदनशील अवस्थाएं और सर्वोत्तम विधि जानें।",
        label_season: "मौसम / जलवायु",
        season_winter: "सर्दी (रबी)",
        season_summer: "गर्मी (जायद)",
        season_monsoon: "वर्षा (खरीफ)",
        btn_get_irrigation: "सिंचाई सारणी प्राप्त करें",
        watering_interval_title: "अनुशंसित सिंचाई अंतराल",
        best_method_title: "सर्वोत्तम सिंचाई विधि",
        critical_stages_title: "सिंचाई के लिए सबसे संवेदनशील अवस्थाएं",

        // Chatbot
        chat_title: "किसान मित्र - एआई कृषि सहायक",
        chat_subtitle: "फसल रोग, जैविक उपचार, खाद की खुराक और खेती से जुड़े सवालों के तुरंत जवाब पाएं।",
        chat_placeholder: "अपना सवाल लिखें (जैसे: जैविक नीम का स्प्रे कैसे बनाएं?)...",
        chat_send: "पूछें",
        chip_neem: "🌿 जैविक नीम का स्प्रे",
        chip_urea: "🧪 यूरिया कब और कितना डालें",
        chip_yellow: "🍂 पत्तियां पीली पड़ने का कारण",
        chip_soil: "🌱 मिट्टी जांचने का तरीका",

        // History
        hist_title: "सुरक्षित किए गए रिकॉर्ड व इतिहास",
        hist_desc: "SQLite डेटाबेस में संग्रहीत पिछले सभी रोग निदान, फसल चयन और मृदा सलाह रिपोर्ट देखें।",
        btn_seed_sample: "नमूना डेटा लोड करें",
        btn_clear_history: "रिकॉर्ड ताज़ा करें",
        col_date: "दिनांक व समय",
        col_crop: "फसल",
        col_disease: "निदान / योजना",
        col_confidence: "निश्चितता",
        col_action: "कार्यवाही",

        // API Modal
        modal_api_title: "AI विज़न एवं मॉडल सेटिंग्स",
        modal_api_desc: "गूगल जेमिनी एपीआई की (API Key) दर्ज करके जेमिनी 2.5 फ्लैश विज़न मॉडल सक्रिय करें। यदि यह खाली छोड़ दिया जाता है, तो क्रॉपकेयर एआई पूरी तरह से ऑफलाइन स्थानीय कंप्यूटर विज़न एवं सांख्यिकीय मॉडलों का उपयोग करता है।",
        modal_api_label: "गूगल जेमिनी एपीआई की (वैकल्पिक)",
        modal_api_save: "सेटिंग्स सुरक्षित करें",
        modal_api_clear: "स्थानीय ऑफलाइन मॉडल उपयोग करें"
    }
};

let currentLang = localStorage.getItem("cropcare_lang") || "en";

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    localStorage.setItem("cropcare_lang", lang);

    // Update all elements with data-i18n attribute
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[lang][key]) {
            if (el.tagName === "INPUT" && el.getAttribute("placeholder")) {
                el.placeholder = translations[lang][key];
            } else {
                el.innerHTML = translations[lang][key];
            }
        }
    });

    // Update Language Toggle Button text
    const langBtn = document.getElementById("langToggleBtn");
    if (langBtn) {
        langBtn.textContent = translations[lang].lang_btn;
    }

    // Dispatch event for other modules
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { lang } }));
}

function t(key) {
    return (translations[currentLang] && translations[currentLang][key]) || key;
}

function getActiveLanguage() {
    return currentLang;
}

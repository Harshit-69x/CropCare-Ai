"""
CropCare AI - Production Rule Base
Knowledge base containing expert production rules for agricultural diagnosis.

Each rule represents formal expert knowledge in the structure:
IF (Crop == X AND PlantPart in Y AND Symptoms match Z AND Weather conditions)
THEN (Diagnose Disease D WITH Confidence C AND Provide Treatment T)
"""

CROPS = [
    {"id": "tomato", "name_en": "Tomato", "name_hi": "टमाटर", "icon": "🍅"},
    {"id": "potato", "name_en": "Potato", "name_hi": "आलू", "icon": "🥔"},
    {"id": "wheat", "name_en": "Wheat", "name_hi": "गेहूँ", "icon": "🌾"},
    {"id": "rice", "name_en": "Rice / Paddy", "name_hi": "धान / चावल", "icon": "🌾"},
    {"id": "cotton", "name_en": "Cotton", "name_hi": "कपास", "icon": "🌱"},
    {"id": "maize", "name_en": "Maize / Corn", "name_hi": "मक्का", "icon": "🌽"},
    {"id": "mustard", "name_en": "Mustard", "name_hi": "सरसों", "icon": "🌼"},
    {"id": "chickpea", "name_en": "Chickpea / Gram", "name_hi": "चना", "icon": "🫘"},
    {"id": "chilli", "name_en": "Chilli / Pepper", "name_hi": "मिर्च", "icon": "🌶️"}
]

# Vocabulary of observable symptoms grouped by affected plant part
SYMPTOMS_VOCABULARY = [
    # Leaf Symptoms
    {"id": "yellowing_leaves", "part": "leaf", "en": "Yellowing of leaves (Chlorosis)", "hi": "पत्तियों का पीला पड़ना (क्लोरोसिस)"},
    {"id": "brown_spots", "part": "leaf", "en": "Brown / Black necrotic spots", "hi": "भूरे / काले धब्बे"},
    {"id": "concentric_rings", "part": "leaf", "en": "Target-like concentric rings on spots", "hi": "धब्बों पर गोल चक्र (कंसेंट्रिक रिंग्स)"},
    {"id": "water_soaked_lesions", "part": "leaf", "en": "Dark water-soaked wet patches", "hi": "पानी जैसे भीगे हुए गहरे धब्बे"},
    {"id": "white_powdery_growth", "part": "leaf", "en": "White powdery talcum-like coating", "hi": "सफेद पाउडर जैसी फफूंद"},
    {"id": "yellow_halo", "part": "leaf", "en": "Yellow halo surrounding dark spots", "hi": "काले धब्बों के चारों ओर पीला घेरा"},
    {"id": "leaf_curling", "part": "leaf", "en": "Curling / Puckering of leaves", "hi": "पत्तियों का मुड़ना या सिकुड़ना"},
    {"id": "orange_yellow_pustules", "part": "leaf", "en": "Orange / Yellow rusty powdery stripes", "hi": "नारंगी/पीली रतुआ जैसी धारियाँ या फफोले"},
    {"id": "mosaic_pattern", "part": "leaf", "en": "Light & dark green mosaic mottling", "hi": "हल्के व गहरे हरे मोज़ेक जैसे चकत्ते"},
    {"id": "drying_leaf_margins", "part": "leaf", "en": "Scorched or burning leaf tips and margins", "hi": "पत्तियों के किनारों व सिरों का झुलसना/सूखना"},
    {"id": "silvery_streaks", "part": "leaf", "en": "Silvery or translucent streaks / Thrips injury", "hi": "चांदी जैसी धारियां या कीड़े के निशान"},

    # Stem and Branch Symptoms
    {"id": "stem_canker", "part": "stem", "en": "Dark sunken lesions / Cankers on stem", "hi": "तने पर गहरे धंसे हुए घाव या छाले"},
    {"id": "wilting_drooping", "part": "stem", "en": "Sudden drooping / Daytime wilting", "hi": "पौधे का अचानक मुरझाना या झुकना"},
    {"id": "vascular_browning", "part": "stem", "en": "Brown ring inside cut stem (vascular discolouration)", "hi": "कटे हुए तने के अंदर भूरापन"},
    {"id": "stem_rotting", "part": "stem", "en": "Soft rot or blackening at soil line", "hi": "जड़ के पास तने का काला पड़ना या सड़ना"},

    # Fruit and Grain Symptoms
    {"id": "fruit_rot", "part": "fruit", "en": "Sunken leathery black spot on fruit bottom", "hi": "फल के निचले हिस्से में काला धंसा हुआ धब्बा"},
    {"id": "fruit_lesions", "part": "fruit", "en": "Water-soaked dark lesions on fruits/pods", "hi": "फलों या फलियों पर पानी जैसे काले धब्बे"},
    {"id": "black_powdery_earhead", "part": "fruit", "en": "Grains replaced by black powdery mass", "hi": "दानों की जगह काला चूर्ण या कालिख"},
    {"id": "boll_drop_punctures", "part": "fruit", "en": "Bore holes / Premature drop of buds or bolls", "hi": "फलों/कलियों में छेद या समय से पहले गिरना"},

    # Whole Plant Symptoms
    {"id": "stunted_growth", "part": "whole_plant", "en": "Dwarfed / Stunted overall plant growth", "hi": "पौधे का बौना रह जाना या विकास रुकना"},
    {"id": "bushy_top", "part": "whole_plant", "en": "Clustered bushy foliage at top", "hi": "शीर्ष पर पत्तियों का गुच्छा बनना"}
]

# Knowledge Base with Production Rules
KNOWLEDGE_BASE = [
    # ------------------ TOMATO RULES ------------------
    {
        "rule_id": "RULE_TOMATO_01",
        "crop": "tomato",
        "disease_id": "tomato_early_blight",
        "name_en": "Early Blight (Alternaria solani)",
        "name_hi": "अगेती झुलसा (अल्टरनेरिया सोलेनाई)",
        "pathogen": "Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "Moderate to High",
        "severity_hi": "मध्यम से उच्च",
        "required_symptoms": ["concentric_rings", "brown_spots"],
        "supporting_symptoms": ["yellow_halo", "yellowing_leaves", "stem_canker"],
        "weather_triggers": ["warm_humid", "moderate_rain"],
        "explanation_en": "Rule R_TOM_01 triggered: The plant exhibits target-like concentric rings inside dark brown spots surrounded by a chlorotic yellow halo on older foliage, which is the pathognomonic diagnostic signature of Alternaria solani (Early Blight).",
        "explanation_hi": "नियम R_TOM_01 लागू हुआ: निचली पत्तियों पर काले-भूरे धब्बों के अंदर गोल चक्र (टारगेट बोर्ड जैसे छल्ले) और चारों तरफ पीला घेरा पाया गया, जो अगेती झुलसा (अल्टरनेरिया) का मुख्य लक्षण है।",
        "treatment": {
            "organic_en": "Apply Neem Seed Kernel Extract (NSKE 5%) or Trichoderma harzianum @ 5g/L. Prune and destroy infected lower leaves. Ensure 3-year crop rotation with non-solanaceous crops.",
            "organic_hi": "नीम बीज अर्क (5%) या ट्राइकोडर्मा हरजिएनम (5 ग्राम/लीटर) का छिड़काव करें। निचली संक्रमित पत्तियों को काटकर नष्ट कर दें। गैर-टमाटर फसलों के साथ फसल चक्र अपनाएं।",
            "chemical_en": "Foliar spray of Mancozeb 75% WP @ 2.5g/L water, or Chlorothalonil 75% WP @ 2g/L. In severe cases, alternate with Azoxystrobin 23% SC @ 1ml/L.",
            "chemical_hi": "मैंकोजेब 75% WP (2.5 ग्राम/लीटर) या क्लोरोथैलोनिल 75% WP (2 ग्राम/लीटर) का छिड़काव करें। गंभीर प्रकोप में एजोक्सीस्ट्रोबिन (1 मिली/लीटर) का उपयोग करें।",
            "dosage": "2 - 2.5 g/L (500g in 200 Litres water per acre)",
            "prevention_en": "Avoid sprinkler/overhead irrigation that wets foliage. Mulch the soil bed with straw or plastic film to prevent soil-splashing fungal spores.",
            "prevention_hi": "पत्तियों पर सीधे पानी डालने से बचें। मिट्टी से कवक के फैलाव को रोकने के लिए पुआल या प्लास्टिक मल्चिंग का उपयोग करें।"
        }
    },
    {
        "rule_id": "RULE_TOMATO_02",
        "crop": "tomato",
        "disease_id": "tomato_late_blight",
        "name_en": "Late Blight (Phytophthora infestans)",
        "name_hi": "पछैती झुलसा (फाइटोपथोरा इन्फेस्टन्स)",
        "pathogen": "Oomycete / Fungal",
        "pathogen_hi": "कवक/ऊमाइसीट",
        "severity": "Critical",
        "severity_hi": "अत्यधिक गंभीर (आपातकालीन)",
        "required_symptoms": ["water_soaked_lesions", "drying_leaf_margins"],
        "supporting_symptoms": ["fruit_lesions", "stem_canker", "wilting_drooping"],
        "weather_triggers": ["cool_wet", "high_humidity", "foggy"],
        "explanation_en": "Rule R_TOM_02 triggered: Water-soaked lesions expanding from leaf margins under cool, damp conditions indicate possible Late Blight (Phytophthora infestans). Note: Water-soaked lesions are supporting evidence (hydrosis), also seen in early bacterial infections; definitive confirmation requires observing white sporulation on lesion undersides.",
        "explanation_hi": "नियम R_TOM_02 लागू हुआ: ठंडे और नमी वाले मौसम में पत्तियों पर पानी से भीगे हुए घाव पछेती झुलसा (फाइटोपथोरा) की संभावना दर्शाते हैं। ध्यान दें: पानी जैसे घाव सहायक प्रमाण हैं (जो जीवाणु संक्रमण में भी दिख सकते हैं); अंतिम पुष्टि के लिए पत्ती के नीचे सफेद फफूंद देखना आवश्यक है।",
        "treatment": {
            "organic_en": "Spray Bordeaux Mixture (1%) or Copper Hydroxide @ 2.5g/L immediately upon first signs. Avoid water stagnation.",
            "organic_hi": "शुरुआती लक्षण दिखते ही बोर्डो मिश्रण (1%) या कॉपर हाइड्रोक्साइड (2.5 ग्राम/लीटर) का छिड़काव करें। खेत में जलभराव न होने दें।",
            "chemical_en": "Spray Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ) @ 2.5g/L water or Cymoxanil 8% + Mancozeb 64% WP @ 2g/L.",
            "chemical_hi": "मेटालेक्सिल + मैंकोजेब (रिडोमिल एमजेड) 2.5 ग्राम/लीटर या साइमोक्सानिल + मैंकोजेब 2 ग्राम/लीटर का तुरंत छिड़काव करें।",
            "dosage": "2.5 g/L water (Wait 7-10 days before harvest)",
            "prevention_en": "Destroy cull piles, use disease-free certified nursery seedlings, and maintain adequate plant-to-plant spacing for airflow.",
            "prevention_hi": "संक्रमित पौधों के अवशेष जला दें, प्रमाणित पौध का उपयोग करें और पौधों के बीच पर्याप्त दूरी रखें।"
        }
    },
    {
        "rule_id": "RULE_TOMATO_03",
        "crop": "tomato",
        "disease_id": "tomato_leaf_curl",
        "name_en": "Tomato Leaf Curl Virus (ToLCV)",
        "name_hi": "टमाटर पर्ण कुंचन विषाणु रोग (लीफ कर्ल)",
        "pathogen": "Viral (Vector: Whitefly)",
        "pathogen_hi": "विषाणु जनित (वाहक: सफेद मक्खी)",
        "severity": "High",
        "severity_hi": "उच्च",
        "required_symptoms": ["leaf_curling", "stunted_growth"],
        "supporting_symptoms": ["yellowing_leaves", "bushy_top"],
        "weather_triggers": ["dry_hot", "windy"],
        "explanation_en": "Rule R_TOM_03 triggered: Upward and inward curling of leaves coupled with severe plant stunting and bushy top growth, transmitted by the whitefly vector Bemisia tabaci.",
        "explanation_hi": "नियम R_TOM_03 लागू हुआ: पत्तियों का ऊपर और अंदर की ओर मुड़ना, विकास रुक जाना और ऊपरी भाग का झाड़ीनुमा होना; यह सफेद मक्खी द्वारा फैलाया जाने वाला वायरस है।",
        "treatment": {
            "organic_en": "Install Yellow Sticky Traps (15-20 traps/acre) to catch adult whiteflies. Spray Neem oil (10,000 ppm) @ 3ml/L water.",
            "organic_hi": "सफेद मक्खियों को पकड़ने के लिए पीले चिपचिपे ट्रैप (15-20 प्रति एकड़) लगाएं। नीम का तेल (10,000 ppm) 3 मिली/लीटर पानी में घोलकर छिड़कें।",
            "chemical_en": "Control the whitefly vector with Imidacloprid 17.8% SL @ 0.5ml/L or Diafenthiuron 50% WP @ 1g/L water.",
            "chemical_hi": "सफेद मक्खी की रोकथाम हेतु इमिडाक्लोप्रिड 17.8% SL (0.5 मिली/लीटर) या डायफेन्थियूरॉन (1 ग्राम/लीटर) का छिड़काव करें।",
            "dosage": "0.5 ml per Litre of water",
            "prevention_en": "Rogue out and bury severely infected plants immediately. Use nylon insect net (40-50 mesh) in nurseries.",
            "prevention_hi": "गंभीर रूप से ग्रसित पौधों को उखाड़कर जमीन में दबा दें। नर्सरी में 40-50 मेश वाली जाली का उपयोग करें।"
        }
    },
    {
        "rule_id": "RULE_TOMATO_04",
        "crop": "tomato",
        "disease_id": "tomato_blossom_end_rot",
        "name_en": "Blossom End Rot (Calcium Deficiency & Irregular Water)",
        "name_hi": "ब्लॉसम एंड रॉट (कैल्शियम की कमी व अनियमित सिंचाई)",
        "pathogen": "Physiological Disorder",
        "pathogen_hi": "पोषण व शारीरिक विकार",
        "severity": "Moderate",
        "severity_hi": "मध्यम",
        "required_symptoms": ["fruit_rot"],
        "supporting_symptoms": ["wilting_drooping"],
        "weather_triggers": ["dry_hot", "fluctuating_moisture"],
        "explanation_en": "Rule R_TOM_04 triggered: Water-soaked, sunken, leathery black decay specifically occurring at the blossom end of fruits caused by localized Calcium deficiency aggravated by uneven watering.",
        "explanation_hi": "नियम R_TOM_04 लागू हुआ: टमाटर के फल के निचले हिस्से में काला, सूखा और चमड़े जैसा धब्बा बनना; यह अनियमित सिंचाई और कैल्शियम की कमी का संकेत है।",
        "treatment": {
            "organic_en": "Apply well-decomposed farmyard manure enriched with agricultural gypsum or slaked lime (chuna) slurry around the root zone.",
            "organic_hi": "जड़ों के पास अच्छी तरह सड़ी हुई गोबर की खाद और हल्का बुझा हुआ चूना या जिप्सम डालें।",
            "chemical_en": "Foliar spray of Calcium Nitrate (100% water soluble) @ 5g/L water during the fruit development stage.",
            "chemical_hi": "फल बनने की अवस्था में कैल्शियम नाइट्रेट (5 ग्राम/लीटर) का पर्णीय छिड़काव करें।",
            "dosage": "5 g/L water (repeat after 10 days)",
            "prevention_en": "Maintain consistent soil moisture. Mulch to retain uniform soil water levels.",
            "prevention_hi": "मिट्टी में नमी का स्तर एक समान रखें। नमी बनाए रखने के लिए खेत में मल्चिंग करें।"
        }
    },

    # ------------------ POTATO RULES ------------------
    {
        "rule_id": "RULE_POTATO_01",
        "crop": "potato",
        "disease_id": "potato_late_blight",
        "name_en": "Potato Late Blight (Phytophthora infestans)",
        "name_hi": "आलू का पछैती झुलसा",
        "pathogen": "Oomycete / Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "Critical",
        "severity_hi": "अत्यधिक गंभीर",
        "required_symptoms": ["water_soaked_lesions", "drying_leaf_margins"],
        "supporting_symptoms": ["stem_rotting", "brown_spots"],
        "weather_triggers": ["cool_wet", "high_humidity", "foggy"],
        "explanation_en": "Rule R_POT_01 triggered: Water-soaked dark brownish-black margins on leaves with white fuzzy fungal growth on the underside during humid/foggy weather.",
        "explanation_hi": "नियम R_POT_01 लागू हुआ: पत्तियों के किनारों पर पानी से भीगे हुए काले-भूरे धब्बे और निचली सतह पर सफेद फफूंद दिखना पछैती झुलसे का संकेत है।",
        "treatment": {
            "organic_en": "Spray Copper Oxychloride 50 WP @ 3g/L or fermented butter-milk (chhaas) solution (5%) as a preventive wash.",
            "organic_hi": "कॉपर ऑक्सीक्लोराइड 50 WP (3 ग्राम/लीटर) या 5% खट्टी छाछ के घोल का निवारक छिड़काव करें।",
            "chemical_en": "Spray Metalaxyl + Mancozeb (2.5g/L) or Dimethomorph 50% WP (1g/L) mixed with Mancozeb (2g/L).",
            "chemical_hi": "मेटालेक्सिल + मैंकोजेब (2.5 ग्राम/लीटर) या डाईमेथोमोर्फ (1 ग्राम/लीटर) के साथ मैंकोजेब मिलाकर छिड़कें।",
            "dosage": "2.5 g/L (Spray thoroughly on both leaf sides)",
            "prevention_en": "Ensure proper earthing up to bury tubers deep so swimming spores cannot reach tubers. Cut and destroy haulms 10 days before digging.",
            "prevention_hi": "कंदों पर अच्छी तरह मिट्टी चढ़ाएं ताकि कवक कंद तक न पहुंचे। खुदाई से 10 दिन पहले बेलें काट दें।"
        }
    },
    {
        "rule_id": "RULE_POTATO_02",
        "crop": "potato",
        "disease_id": "potato_early_blight",
        "name_en": "Potato Early Blight (Alternaria solani)",
        "name_hi": "आलू का अगेती झुलसा",
        "pathogen": "Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "Moderate",
        "severity_hi": "मध्यम",
        "required_symptoms": ["concentric_rings", "brown_spots"],
        "supporting_symptoms": ["yellow_halo", "yellowing_leaves"],
        "weather_triggers": ["warm_humid"],
        "explanation_en": "Rule R_POT_02 triggered: Circular to angular brown spots with distinctive concentric rings (target spots) appearing first on lower mature foliage.",
        "explanation_hi": "नियम R_POT_02 लागू हुआ: निचली पत्तियों पर संकेंद्री छल्ले वाले भूरे धब्बे बनना अगेती झुलसे का लक्षण है।",
        "treatment": {
            "organic_en": "Spray Trichoderma viride @ 5g/L or Pseudomonas fluorescens @ 5ml/L at early infection stage.",
            "organic_hi": "ट्राइकोडर्मा विरिडी (5 ग्राम/लीटर) या स्यूडोमोनास फ्लोरेसेंस (5 मिली/लीटर) का छिड़काव करें।",
            "chemical_en": "Apply Propineb 70% WP @ 2.5g/L or Mancozeb 75% WP @ 2.5g/L water at 10-12 day intervals.",
            "chemical_hi": "प्रोपीनेब 70% WP (2.5 ग्राम/लीटर) या मैंकोजेब (2.5 ग्राम/लीटर) का 10-12 दिनों के अंतराल पर छिड़काव करें।",
            "dosage": "2.5 g per Litre of water",
            "prevention_en": "Balanced nitrogen fertilizer application; excess nitrogen makes foliage overly succulent and susceptible.",
            "prevention_hi": "संतुलित मात्रा में नाइट्रोजन खाद दें; अधिक नाइट्रोजन से पत्तियां कोमल होकर रोग के प्रति संवेदनशील हो जाती हैं।"
        }
    },

    # ------------------ WHEAT RULES ------------------
    {
        "rule_id": "RULE_WHEAT_01",
        "crop": "wheat",
        "disease_id": "wheat_yellow_rust",
        "name_en": "Yellow Rust / Stripe Rust (Puccinia striiformis)",
        "name_hi": "गेहूँ का पीला रतुआ / हल्दी रोग",
        "pathogen": "Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "Critical",
        "severity_hi": "अत्यंत गंभीर",
        "required_symptoms": ["orange_yellow_pustules"],
        "supporting_symptoms": ["yellowing_leaves", "drying_leaf_margins"],
        "weather_triggers": ["cool_wet", "cloudy"],
        "explanation_en": "Rule R_WHT_01 triggered: Parallel rows of bright yellow/orange powdery pustules resembling turmeric powder stripes along leaf veins, diagnostic for Stripe Rust in cool climates.",
        "explanation_hi": "नियम R_WHT_01 लागू हुआ: पत्तियों की नसों के समानांतर हल्दी के समान पीले-नारंगी पाउडर की धारियां और फफोले दिखना पीला रतुआ का निश्चित संकेत है।",
        "treatment": {
            "organic_en": "Spray cow urine solution (10% fermented) mixed with garlic extract for early organic suppression.",
            "organic_hi": "शुरुआती रोकथाम के लिए 10% गोमूत्र और लहसुन के अर्क का घोल बनाकर छिड़कें।",
            "chemical_en": "Spray Propiconazole 25% EC (Tilt) @ 1ml/L water or Tebuconazole 25.9% EC @ 1ml/L water immediately.",
            "chemical_hi": "प्रोपिकोनाज़ोल 25% EC (टिल्ट) 1 मिली/लीटर या टेबुकोनाज़ोल 1 मिली/लीटर पानी में घोलकर तुरंत छिड़काव करें।",
            "dosage": "1 ml/L (200 ml in 200 Litres water per acre)",
            "prevention_en": "Sow rust-resistant varieties (e.g., HD-2967, HD-3086, DBW-187, DBW-222). Avoid late sowing.",
            "prevention_hi": "रोग प्रतिरोधी किस्में (जैसे HD-3086, DBW-187) बोएं। समय पर बुवाई करें।"
        }
    },
    {
        "rule_id": "RULE_WHEAT_02",
        "crop": "wheat",
        "disease_id": "wheat_loose_smut",
        "name_en": "Loose Smut (Ustilago tritici)",
        "name_hi": "गेहूँ का अनावृत कंडुआ / काला दाना रोग",
        "pathogen": "Fungal (Seed-borne)",
        "pathogen_hi": "कवक जनित (बीजोढ़)",
        "severity": "High",
        "severity_hi": "उच्च",
        "required_symptoms": ["black_powdery_earhead"],
        "supporting_symptoms": ["stunted_growth"],
        "weather_triggers": ["moderate"],
        "explanation_en": "Rule R_WHT_02 triggered: Earheads completely transformed into a loose black sooty powdery mass of fungal spores, leaving only the bare central rachis.",
        "explanation_hi": "नियम R_WHT_02 लागू हुआ: बालियों के दानों का काले चूर्ण (कालिख) में बदल जाना और केवल डंठल शेष रह जाना अनावृत कंडुआ का स्पष्ट लक्षण है।",
        "treatment": {
            "organic_en": "Solar heat treatment: Soak seeds in water for 4-5 hours on a sunny May/June day, then spread thin on a tarpaulin to dry in strong sun before storing.",
            "organic_hi": "सौर ताप उपचार: मई-जून की तेज धूप में बीजों को 4 घंटे पानी में भिगोकर तिरपाल पर सुखाएं।",
            "chemical_en": "Treat seed before sowing with Carboxin 37.5% + Thiram 37.5% (Vitavax) @ 2.5g/kg seed or Tebuconazole @ 1.5g/kg seed.",
            "chemical_hi": "बुवाई से पहले बीज को विटावैक्स (कार्बोक्सिन + थीरम) 2.5 ग्राम प्रति किलो बीज की दर से उपचारित करें।",
            "dosage": "2 - 2.5 g per kg seed treatment (cannot cure once earhead is black; rogue out affected plants)",
            "prevention_en": "Carefully uproot affected earheads inside a plastic bag and bury them to prevent wind dispersal of spores.",
            "prevention_hi": "प्रभावित बालियों को प्लास्टिक थैली से ढककर उखाड़ें और जमीन में गाड़ दें ताकि हवा से न फैले।"
        }
    },
    {
        "rule_id": "RULE_WHEAT_03",
        "crop": "wheat",
        "disease_id": "wheat_powdery_mildew",
        "name_en": "Powdery Mildew (Blumeria graminis)",
        "name_hi": "गेहूँ का चूर्णिल आसिता (सफेद फफूंद)",
        "pathogen": "Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "Moderate",
        "severity_hi": "मध्यम",
        "required_symptoms": ["white_powdery_growth"],
        "supporting_symptoms": ["yellowing_leaves", "drying_leaf_margins"],
        "weather_triggers": ["cool_dry", "cloudy"],
        "explanation_en": "Rule R_WHT_03 triggered: White to grey superficial fluffy powdery patches on upper leaf surfaces and lower stem sheaths.",
        "explanation_hi": "नियम R_WHT_03 लागू हुआ: पत्तियों की ऊपरी सतह पर सफेद-धूसर आटे जैसा चूर्ण दिखना चूर्णिल आसिता का संकेत है।",
        "treatment": {
            "organic_en": "Spray Wettable Sulphur 80% WDG @ 2.5g/L water or 20% fresh cow milk spray.",
            "organic_hi": "घुलनशील सल्फर 80% WDG (2.5 ग्राम/लीटर) या 20% गाय के ताजे दूध के घोल का छिड़काव करें।",
            "chemical_en": "Foliar spray of Propiconazole 25% EC @ 1ml/L or Hexaconazole 5% EC @ 2ml/L.",
            "chemical_hi": "प्रोपिकोनाज़ोल (1 मिली/लीटर) या हेक्साकोनाज़ोल (2 मिली/लीटर) का छिड़काव करें।",
            "dosage": "1 - 2 ml/L water",
            "prevention_en": "Avoid excessive density of plants; improve field ventilation and sunlight exposure.",
            "prevention_hi": "बहुत घनी बुवाई न करें; खेत में धूप और हवा का संचार बनाए रखें।"
        }
    },

    # ------------------ RICE RULES ------------------
    {
        "rule_id": "RULE_RICE_01",
        "crop": "rice",
        "disease_id": "rice_bacterial_blight",
        "name_en": "Bacterial Leaf Blight (Xanthomonas oryzae)",
        "name_hi": "धान का जीवाणु झुलसा (बैक्टीरियल ब्लाइट)",
        "pathogen": "Bacterial",
        "pathogen_hi": "जीवाणु जनित",
        "severity": "High to Critical",
        "severity_hi": "उच्च से गंभीर",
        "required_symptoms": ["drying_leaf_margins", "water_soaked_lesions"],
        "supporting_symptoms": ["yellowing_leaves", "wilting_drooping"],
        "weather_triggers": ["warm_humid", "heavy_rain", "cyclonic_winds"],
        "explanation_en": "Rule R_RICE_01 triggered: Water-soaked translucent streaks turning into wavy, bleached yellowish-white margins that dry rapidly from the leaf tip downward.",
        "explanation_hi": "नियम R_RICE_01 लागू हुआ: पत्तियों के सिरे और किनारों से शुरू होकर लहरदार पीले-सफेद सूखे किनारे बनना, जो जीवाणु झुलसे का स्पष्ट संकेत है।",
        "treatment": {
            "organic_en": "Spray fresh cow dung supernatant solution (20%) or Neem oil spray (3ml/L). Drain excess water from the paddy field.",
            "organic_hi": "गोबर के साफ पानी (20%) या नीम के तेल (3 मिली/लीटर) का छिड़काव करें। खेत से अतिरिक्त पानी निकाल दें।",
            "chemical_en": "Spray Streptocycline (Sulfate) @ 0.15g/L (6g in 40 Litres) mixed with Copper Oxychloride 50 WP @ 2.5g/L water.",
            "chemical_hi": "स्ट्रेप्टोसाइक्लिन (6 ग्राम प्रति 40-50 लीटर पानी) के साथ कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) मिलाकर छिड़काव करें।",
            "dosage": "Streptocycline 150 ppm + Copper Oxychloride 2.5 g/L",
            "prevention_en": "Stop nitrogen top-dressing immediately when disease appears. Drain standing water and re-irrigate fresh water.",
            "prevention_hi": "रोग दिखते ही यूरिया का छिड़काव तुरंत बंद करें। खेत का पानी बदलकर ताजा पानी भरें।"
        }
    },
    {
        "rule_id": "RULE_RICE_02",
        "crop": "rice",
        "disease_id": "rice_blast",
        "name_en": "Rice Blast (Magnaporthe oryzae)",
        "name_hi": "धान का झोंका रोग (ब्लास्ट)",
        "pathogen": "Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "Critical",
        "severity_hi": "अत्यंत गंभीर",
        "required_symptoms": ["brown_spots"],
        "supporting_symptoms": ["drying_leaf_margins", "stunted_growth"],
        "weather_triggers": ["high_humidity", "dew", "cool_nights"],
        "explanation_en": "Rule R_RICE_02 triggered: Spindle/diamond-shaped eye spots with ash-grey centers and reddish-brown borders on leaves and black necrosis on node/neck of panicles.",
        "explanation_hi": "नियम R_RICE_02 लागू हुआ: पत्तियों पर नाव या आंख के आकार के धब्बे जिनका केंद्र राख जैसे धूसर रंग का और किनारे लाल-भूरे हैं; यह ब्लास्ट रोग है।",
        "treatment": {
            "organic_en": "Seed treatment and foliar spray of Pseudomonas fluorescens @ 10g/L or botanicals like Casuarina leaf extract.",
            "organic_hi": "स्यूडोमोनास फ्लोरेसेंस (10 ग्राम/लीटर) से बीज उपचार और पर्णीय छिड़काव करें।",
            "chemical_en": "Spray Tricyclazole 75% WP @ 0.6g/L water or Isoprothiolane 40% EC @ 1.5ml/L or Kasugamycin 3% SL @ 2ml/L.",
            "chemical_hi": "ट्राइसाइक्लाजोल 75% WP (0.6 ग्राम/लीटर) या आइसोप्रोपियोलेन (1.5 मिली/लीटर) का छिड़काव करें।",
            "dosage": "0.6 g/L (120g in 200 Litres water per acre)",
            "prevention_en": "Do not over-apply nitrogen. Split nitrogen doses into 3-4 applications.",
            "prevention_hi": "नाइट्रोजन की अधिक मात्रा न दें। यूरिया को 3-4 किश्तों में बांटकर दें।"
        }
    },

    # ------------------ COTTON RULES ------------------
    {
        "rule_id": "RULE_COTTON_01",
        "crop": "cotton",
        "disease_id": "cotton_leaf_curl",
        "name_en": "Cotton Leaf Curl Virus (CLCuV)",
        "name_hi": "कपास का पत्ता मरोड़ रोग (लीफ कर्ल)",
        "pathogen": "Viral (Vector: Whitefly)",
        "pathogen_hi": "विषाणु जनित",
        "severity": "Critical",
        "severity_hi": "गंभीर",
        "required_symptoms": ["leaf_curling"],
        "supporting_symptoms": ["vascular_browning", "stunted_growth", "bushy_top"],
        "weather_triggers": ["dry_hot"],
        "explanation_en": "Rule R_COT_01 triggered: Upward/downward cupping and curling of leaves, vein thickening (enation), and leaf-like small outgrowths beneath main veins.",
        "explanation_hi": "नियम R_COT_01 लागू हुआ: पत्तियों का ऊपर या नीचे की ओर मुड़ना, नसों का मोटा होना और उल्टी तरफ छोटे पत्तों जैसी संरचनाएं बनना लीफ कर्ल वायरस का लक्षण है।",
        "treatment": {
            "organic_en": "Spray Neem seed oil formulation (1500 ppm) @ 5ml/L. Erect yellow sticky traps (25/acre) to reduce whitefly vectors.",
            "organic_hi": "नीम का तेल (5 मिली/लीटर) का छिड़काव करें। सफेद मक्खी को रोकने के लिए प्रति एकड़ 25 पीले चिपचिपे ट्रैप लगाएं।",
            "chemical_en": "Spray Spiromesifen 22.9% SC @ 1ml/L or Pyriproxyfen 10% EC @ 2ml/L or Flonicamid 50% WG @ 0.4g/L.",
            "chemical_hi": "स्पाइरोमेसिफेन (1 मिली/लीटर) या पायरीप्रॉक्सीफेन (2 मिली/लीटर) या फ्लोनिकैमिड (0.4 ग्राम/लीटर) का छिड़काव करें।",
            "dosage": "1 ml per Litre of water",
            "prevention_en": "Eradicate alternate weed hosts (like Kanghi / Abutilon indicum) along field borders.",
            "prevention_hi": "खेत की मेड़ों से कंघी व अन्य खरपतवारों को नष्ट करें जो सफेद मक्खी के शरणस्थल हैं।"
        }
    },
    {
        "rule_id": "RULE_COTTON_02",
        "crop": "cotton",
        "disease_id": "cotton_bollworm",
        "name_en": "Bollworm Infestation (Helicoverpa / Pectinophora)",
        "name_hi": "कपास की सुंडी / इल्ली (गुलाबी व अमेरिकन सुंडी)",
        "pathogen": "Pest / Insect Larva",
        "pathogen_hi": "कीट / सुंडी",
        "severity": "High",
        "severity_hi": "उच्च",
        "required_symptoms": ["boll_drop_punctures"],
        "supporting_symptoms": ["drying_leaf_margins", "stunted_growth"],
        "weather_triggers": ["warm_humid"],
        "explanation_en": "Rule R_COT_02 triggered: Circular bore holes in squares and bolls, rosette flowers, and premature dropping of squares caused by bollworm larvae.",
        "explanation_hi": "नियम R_COT_02 लागू हुआ: कलियों और टिंडों में छेद होना, फूलों का बंद गुलाब जैसा दिखना और कलियों का गिरना सुंडी के प्रकोप का लक्षण है।",
        "treatment": {
            "organic_en": "Install Pheromone traps @ 5-8 traps/acre for monitoring. Release Trichogramma egg parasitoids @ 60,000/acre. Spray HaNPV @ 1ml/L.",
            "organic_hi": "फेरोमोन ट्रैप (5-8 प्रति एकड़) लगाएं। ट्राइकोग्रामा परजीवी (60,000 प्रति एकड़) छोड़ें। HaNPV 1 मिली/लीटर का छिड़काव करें।",
            "chemical_en": "Spray Chlorantraniliprole 18.5% SC (Coragen) @ 0.3ml/L water or Emamectin Benzoate 5% SG @ 0.5g/L.",
            "chemical_hi": "कोराजन (क्लोरएंट्रानिलिप्रोल) 0.3 मिली/लीटर या एमामेक्टिन बेंजोएट (0.5 ग्राम/लीटर) का छिड़काव करें।",
            "dosage": "0.3 - 0.5 ml/L",
            "prevention_en": "Deep summer plowing to expose pupae to predatory birds and heat. Timely harvest and crop residue disposal.",
            "prevention_hi": "गर्मियों में गहरी जुताई करें ताकि सुंडी के प्यूपा नष्ट हो जाएं। फसल अवशेषों को नष्ट करें।"
        }
    },

    # ------------------ MAIZE RULES ------------------
    {
        "rule_id": "RULE_MAIZE_01",
        "crop": "maize",
        "disease_id": "maize_fall_armyworm",
        "name_en": "Fall Armyworm (Spodoptera frugiperda)",
        "name_hi": "मक्का का फॉल आर्मीवर्म (सैनिक कीट)",
        "pathogen": "Insect Pest",
        "pathogen_hi": "कीट प्रकोप",
        "severity": "Critical",
        "severity_hi": "अत्यंत गंभीर",
        "required_symptoms": ["drying_leaf_margins", "stunted_growth"],
        "supporting_symptoms": ["yellowing_leaves"],
        "weather_triggers": ["warm_humid"],
        "explanation_en": "Rule R_MAZ_01 triggered: Ragged shot holes on leaf whorls, sawdust-like excreta (frass) inside the central whorl, and severe defoliation by Fall Armyworm caterpillars.",
        "explanation_hi": "नियम R_MAZ_01 लागू हुआ: मक्के की पत्तियों के बीच (गाभ) में छलनी जैसे छेद और बुरादे जैसा मल दिखना फॉल आर्मीवर्म का मुख्य संकेत है।",
        "treatment": {
            "organic_en": "Whorl application of dry sand mixed with ash (9:1 ratio) or neem cake powder. Spray Metarhizium anisopliae or Beauveria bassiana @ 5g/L.",
            "organic_hi": "पौधे के गोफ (गाभ) में सूखी रेत व राख (9:1) या नीम की खली डालें। ब्युवेरिया बासियाना (5 ग्राम/लीटर) का छिड़काव करें।",
            "chemical_en": "Direct whorl spray of Chlorantraniliprole 18.5% SC @ 0.4ml/L or Spinetoram 11.7% SC @ 0.5ml/L water.",
            "chemical_hi": "मक्के की गोफ में सीधे कोराजन (0.4 मिली/लीटर) या स्पिनेटोरम (0.5 मिली/लीटर) का छिड़काव करें।",
            "dosage": "0.4 ml/L targeted directly into the whorl",
            "prevention_en": "Intercrop with pulses (cowpea / pigeonpea). Scout whorls within 10-15 days after germination.",
            "prevention_hi": "दलहनी फसलों (लोबिया आदि) के साथ सह-फसल लें। अंकुरण के 10-15 दिनों के भीतर निगरानी शुरू करें।"
        }
    },

    # ------------------ MUSTARD RULES ------------------
    {
        "rule_id": "RULE_MUSTARD_01",
        "crop": "mustard",
        "disease_id": "mustard_white_rust",
        "name_en": "White Rust / Blister (Albugo candida)",
        "name_hi": "सरसों का सफेद रतुआ (सफेद रोली)",
        "pathogen": "Oomycete / Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "High",
        "severity_hi": "उच्च",
        "required_symptoms": ["white_powdery_growth"],
        "supporting_symptoms": ["drying_leaf_margins", "stunted_growth"],
        "weather_triggers": ["cool_wet", "dew"],
        "explanation_en": "Rule R_MUS_01 triggered: Raised white or creamy pustules/blisters on the lower side of leaves and staghead malformation of the floral stems.",
        "explanation_hi": "नियम R_MUS_01 लागू हुआ: पत्तियों की निचली सतह पर सफेद या हल्के पीले उभरे हुए फफोले दिखना सफेद रतुआ का लक्षण है।",
        "treatment": {
            "organic_en": "Spray Garlic extract (2%) or fermented butter-milk (chhaas) on foliage during early foggy spells.",
            "organic_hi": "लहसुन का अर्क (2%) या खट्टी छाछ का छिड़काव करें।",
            "chemical_en": "Spray Metalaxyl 35% WS as seed treatment (6g/kg) and foliar spray with Metalaxyl 8% + Mancozeb 64% WP (Ridomil) @ 2g/L.",
            "chemical_hi": "रिडोमिल (मेटालेक्सिल + मैंकोजेब) 2 ग्राम/लीटर या मैंकोजेब (2.5 ग्राम/लीटर) का छिड़काव करें।",
            "dosage": "2 g per Litre of water",
            "prevention_en": "Sow mustard early (before 20th October) to escape cool foggy periods favoring infection.",
            "prevention_hi": "सरसों की अगेती बुवाई (20 अक्टूबर से पहले) करें ताकि कोहरे वाले मौसम से बचा जा सके।"
        }
    },
    {
        "rule_id": "RULE_MUSTARD_02",
        "crop": "mustard",
        "disease_id": "mustard_aphids",
        "name_en": "Mustard Aphid Infestation (Lipaphis erysimi)",
        "name_hi": "सरसों का चेपा / माहू कीट",
        "pathogen": "Insect Pest",
        "pathogen_hi": "कीट प्रकोप",
        "severity": "High",
        "severity_hi": "उच्च",
        "required_symptoms": ["yellowing_leaves", "stunted_growth"],
        "supporting_symptoms": ["leaf_curling", "drying_leaf_margins"],
        "weather_triggers": ["cloudy", "humid"],
        "explanation_en": "Rule R_MUS_02 triggered: Dense colonies of tiny greenish-grey aphids sucking sap from inflorescence, tender pods, and leaves causing yellowing and stunted curl.",
        "explanation_hi": "नियम R_MUS_02 लागू हुआ: फूलों की टहनियों और फलियों पर हरे-धूसर रंग के छोटे कीटों (माहू) का झुंड रस चूसते हुए दिखना चेपा प्रकोप का संकेत है।",
        "treatment": {
            "organic_en": "Spray 5% Neem seed kernel extract (NSKE) or Fish oil rosin soap @ 20g/L. Conserve natural ladybird beetles.",
            "organic_hi": "नीम बीज अर्क (5%) या साबुन के घोल का छिड़काव करें। लेडीबर्ड बीटल (मित्र कीट) का संरक्षण करें।",
            "chemical_en": "Spray Dimethoate 30% EC (Rogor) @ 1.5ml/L or Imidacloprid 17.8% SL @ 0.3ml/L or Thiamethoxam 25% WG @ 0.3g/L.",
            "chemical_hi": "डाइमिथॉएट (रोगोर) 1.5 मिली/लीटर या थियामेथॉक्सम (0.3 ग्राम/लीटर) या इमिडाक्लोप्रिड का छिड़काव करें।",
            "dosage": "1 - 1.5 ml/L water (Spray in the evening to protect honeybees)",
            "prevention_en": "Early sowing helps escape peak aphid infestation. Spray only in late afternoon when honeybees are inactive.",
            "prevention_hi": "समय पर बुवाई करें। मधुमक्खियों को बचाने के लिए कीटनाशक का छिड़काव शाम के समय ही करें।"
        }
    },

    # ------------------ CHICKPEA RULES ------------------
    {
        "rule_id": "RULE_CHICKPEA_01",
        "crop": "chickpea",
        "disease_id": "chickpea_fusarium_wilt",
        "name_en": "Fusarium Wilt (Fusarium oxysporum f. sp. ciceris)",
        "name_hi": "चने का उकठा रोग (विल्ट)",
        "pathogen": "Soil-borne Fungal",
        "pathogen_hi": "मृदा जनित कवक",
        "severity": "Critical",
        "severity_hi": "अत्यंत गंभीर",
        "required_symptoms": ["wilting_drooping", "vascular_browning"],
        "supporting_symptoms": ["yellowing_leaves", "drying_leaf_margins"],
        "weather_triggers": ["warm", "dry_soil"],
        "explanation_en": "Rule R_CHK_01 triggered: Sudden drooping and drying of leaves without shedding, internal dark brown vascular discoloration when main root/stem is split open.",
        "explanation_hi": "नियम R_CHK_01 लागू हुआ: पत्तियों का बिना गिरे अचानक मुरझाकर सूख जाना और जड़ व तने को चीरने पर अंदर भूरी धारियां दिखना उकठा रोग का मुख्य संकेत है।",
        "treatment": {
            "organic_en": "Seed treatment with Trichoderma viride @ 10g/kg seed. Enrich soil with 2.5 kg Trichoderma mixed in 100 kg compost per acre.",
            "organic_hi": "ट्राइकोडर्मा विरिडी (10 ग्राम/किलो) से बीज उपचार करें। 2.5 किलो ट्राइकोडर्मा को 100 किलो गोबर की खाद में मिलाकर खेत में डालें।",
            "chemical_en": "Seed treatment with Carbendazim 50% WP @ 2g/kg seed or Carbendazim 25% + Mancozeb 50% (SAAF) @ 2.5g/kg seed.",
            "chemical_hi": "कार्बेंडाजिम (2 ग्राम/किलो बीज) या साफ (कार्बेंडाजिम + मैंकोजेब) 2.5 ग्राम प्रति किलो बीज से उपचारित करें।",
            "dosage": "2 - 2.5 g per kg seed treatment",
            "prevention_en": "Practice 3 to 4 year crop rotation. Avoid sowing in wilt-infested fields in warm early season; sow deep (8-10 cm).",
            "prevention_hi": "3-4 साल का फसल चक्र अपनाएं। उकठा प्रभावित खेत में गहरी बुवाई (8-10 सेमी) करें।"
        }
    },

    # ------------------ CHILLI RULES ------------------
    {
        "rule_id": "RULE_CHILLI_01",
        "crop": "chilli",
        "disease_id": "chilli_anthracnose",
        "name_en": "Anthracnose / Dieback / Fruit Rot (Colletotrichum capsici)",
        "name_hi": "मिर्च का डाईबैक / फल सड़न रोग (एंथ्रेक्नोज)",
        "pathogen": "Fungal",
        "pathogen_hi": "कवक जनित",
        "severity": "High",
        "severity_hi": "उच्च",
        "required_symptoms": ["fruit_lesions", "drying_leaf_margins"],
        "supporting_symptoms": ["concentric_rings", "stem_canker"],
        "weather_triggers": ["warm_humid", "heavy_dew"],
        "explanation_en": "Rule R_CHL_01 triggered: Circular sunken dark spots on ripe red chillies with concentric black specks and tip dieback of twigs drying from top downward.",
        "explanation_hi": "नियम R_CHL_01 लागू हुआ: लाल पकी मिर्च पर काले धंसे हुए धब्बे और टहनियों का ऊपर से नीचे की ओर सूखना (डाईबैक) एंथ्रेक्नोज का लक्षण है।",
        "treatment": {
            "organic_en": "Foliar spray of Panchagavya (3%) or Trichoderma harzianum @ 5g/L. Collect and destroy dropped infected fruits.",
            "organic_hi": "पंचगव्य (3%) या ट्राइकोडर्मा (5 ग्राम/लीटर) का छिड़काव करें। जमीन पर गिरे सड़े फलों को इकट्ठा कर नष्ट करें।",
            "chemical_en": "Spray Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L or Copper Oxychloride 50 WP @ 2.5g/L water.",
            "chemical_hi": "एजोक्सीस्ट्रोबिन + डाईफेनोकोनाज़ोल (1 मिली/लीटर) या कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) का 12 दिन के अंतराल पर छिड़काव करें।",
            "dosage": "1 ml per Litre of water",
            "prevention_en": "Use certified disease-free seeds. Treat seeds with Thiram @ 3g/kg seed before sowing.",
            "prevention_hi": "रोगमुक्त प्रमाणित बीज उपयोग करें। बुवाई से पहले थीरम 3 ग्राम प्रति किलो बीज से उपचारित करें।"
        }
    }
]

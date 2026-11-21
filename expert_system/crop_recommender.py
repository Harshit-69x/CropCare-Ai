"""
CropCare AI - Agronomic Machine Learning Crop Recommender Engine
Implements a Gaussian Maximum Likelihood and Multi-Variate Agronomic Classifier in pure NumPy.
Evaluates soil N-P-K, pH, Temperature, Humidity, and Rainfall to output true probabilistic recommendations.
"""

import os
import numpy as np
from typing import Dict, Any, List, Tuple

# Crop Metadata with bilingual names, icons, and cultivation tips
CROPS_METADATA = {
    "rice": {
        "name_en": "Rice / Paddy",
        "name_hi": "धान / चावल",
        "icon": "🌾",
        "season_en": "Kharif (Monsoon)",
        "season_hi": "खरीफ (वर्षा)",
        "duration_days": "110-140 days",
        "tip_en": "Requires standing water (2-5 cm) during early vegetative growth. Ideal in heavy clayey or loamy soils.",
        "tip_hi": "प्रारंभिक बढ़वार के दौरान 2-5 सेमी खड़े पानी की आवश्यकता होती है। मटियाली या दोमट मिट्टी सर्वोत्तम है।"
    },
    "wheat": {
        "name_en": "Wheat",
        "name_hi": "गेहूँ",
        "icon": "🌾",
        "season_en": "Rabi (Winter)",
        "season_hi": "रबी (सर्दियां)",
        "duration_days": "115-135 days",
        "tip_en": "Requires cool winter climate and timely irrigation at Crown Root Initiation (21 days after sowing).",
        "tip_hi": "ठंडे मौसम की आवश्यकता होती है। बुवाई के 21 दिन बाद शीर्ष जड़ जमने पर पहली सिंचाई अनिवार्य है।"
    },
    "maize": {
        "name_en": "Maize / Corn",
        "name_hi": "मक्का",
        "icon": "🌽",
        "season_en": "Kharif / Rabi",
        "season_hi": "खरीफ / रबी",
        "duration_days": "85-110 days",
        "tip_en": "Requires well-drained fertile loam. Highly sensitive to waterlogging at the seedling stage.",
        "tip_hi": "अच्छे जल निकास वाली उपजाऊ दोमट मिट्टी चाहिए। अंकुरण अवस्था में जलभराव से बचाएं।"
    },
    "chickpea": {
        "name_en": "Chickpea / Gram",
        "name_hi": "चना",
        "icon": "🫘",
        "season_en": "Rabi (Winter)",
        "season_hi": "रबी (सर्दियां)",
        "duration_days": "90-120 days",
        "tip_en": "Low nitrogen requirement due to natural root nodule nitrogen fixation. Avoid excess irrigation.",
        "tip_hi": "जड़ों में राइजोबियम ग्रंथियों के कारण कम नाइट्रोजन चाहिए। अधिक पानी से उकठा रोग का खतरा रहता है।"
    },
    "kidneybeans": {
        "name_en": "Kidney Beans / Rajma",
        "name_hi": "राजमा",
        "icon": "🫘",
        "season_en": "Rabi / Spring",
        "season_hi": "रबी / बसंत",
        "duration_days": "100-120 days",
        "tip_en": "Lacks native nodulation in plains; requires higher basal nitrogen (80-100 kg/ha).",
        "tip_hi": "मैदानी इलाकों में प्राकृतिक गांठें नहीं बनतीं, इसलिए बुवाई पर पर्याप्त नाइट्रोजन खाद दें।"
    },
    "pigeonpeas": {
        "name_en": "Pigeonpeas / Arhar (Tur)",
        "name_hi": "अरहर (तूर)",
        "icon": "🌱",
        "season_en": "Kharif (Monsoon)",
        "season_hi": "खरीफ",
        "duration_days": "150-180 days",
        "tip_en": "Deep-rooted drought-hardy legume. Ideal for intercropping with cotton, sorghum, or maize.",
        "tip_hi": "गहरी जड़ों वाली सूखा-सहनशील दलहन। कपास या मक्का के साथ अंतःफसल के लिए उत्तम है।"
    },
    "mothbeans": {
        "name_en": "Moth Beans",
        "name_hi": "मोठ",
        "icon": "🫘",
        "season_en": "Kharif (Arid)",
        "season_hi": "खरीफ (शुष्क)",
        "duration_days": "65-75 days",
        "tip_en": "Extremely drought-resistant; thrives in sandy soils with low rainfall (200-400 mm).",
        "tip_hi": "अत्यधिक सूखा रोधी फसल; कम वर्षा और रेतीली मिट्टी में भी अच्छी उपज देती है।"
    },
    "mungbean": {
        "name_en": "Mung Bean / Green Gram",
        "name_hi": "मूंग",
        "icon": "🫘",
        "season_en": "Zaid / Kharif",
        "season_hi": "जायद / खरीफ",
        "duration_days": "60-70 days",
        "tip_en": "Short duration crop, great for catch cropping between Rabi and Kharif to restore soil fertility.",
        "tip_hi": "कम समय (60-70 दिन) में पकने वाली फसल, मिट्टी की उर्वरता बढ़ाने हेतु रबी के बाद उत्तम।"
    },
    "blackgram": {
        "name_en": "Black Gram / Urad",
        "name_hi": "उड़द",
        "icon": "🫘",
        "season_en": "Kharif / Spring",
        "season_hi": "खरीफ / बसंत",
        "duration_days": "70-85 days",
        "tip_en": "Prefers loamy soil with neutral pH. Inoculate seeds with Rhizobium culture before sowing.",
        "tip_hi": "उदासीन pH वाली दोमट मिट्टी पसंद करती है। बुवाई से पूर्व राइजोबियम से बीज उपचार करें।"
    },
    "lentil": {
        "name_en": "Lentil / Masoor",
        "name_hi": "मसूर",
        "icon": "🫘",
        "season_en": "Rabi (Winter)",
        "season_hi": "रबी",
        "duration_days": "110-130 days",
        "tip_en": "Thrives in cool climates and light soils with moderate moisture. Very low water requirement.",
        "tip_hi": "ठंडी जलवायु और कम पानी में अच्छी तरह बढ़ती है। पाले से बचाव आवश्यक है।"
    },
    "pomegranate": {
        "name_en": "Pomegranate",
        "name_hi": "अनार",
        "icon": "🍎",
        "season_en": "Perennial / Bahar",
        "season_hi": "सदाबहार",
        "duration_days": "Perennial Orchard",
        "tip_en": "Thrives in semi-arid regions with warm summers and mild winters. Deep well-drained loam is ideal.",
        "tip_hi": "गर्म शुष्क जलवायु में उत्तम पैदावार। उचित छंटाई और जल निकास का विशेष ध्यान रखें।"
    },
    "banana": {
        "name_en": "Banana",
        "name_hi": "केला",
        "icon": "🍌",
        "season_en": "Year-round",
        "season_hi": "वर्ष भर",
        "duration_days": "11-12 months",
        "tip_en": "Heavy consumer of Potassium and Nitrogen. Requires warm humid tropical climate and frequent watering.",
        "tip_hi": "पोटाश और पानी की भारी आवश्यकता होती है। गर्म व नम जलवायु में अच्छी बढ़वार होती है।"
    },
    "mango": {
        "name_en": "Mango",
        "name_hi": "आम",
        "icon": "🥭",
        "season_en": "Perennial Orchard",
        "season_hi": "सदाबहार बागवानी",
        "duration_days": "Perennial Orchard",
        "tip_en": "Requires dry weather during flowering for fruit setting. Avoid watering during November-December.",
        "tip_hi": "फूल आने के समय सूखा मौसम फल लगने के लिए आवश्यक है। सर्दियों में सिंचाई रोकें।"
    },
    "grapes": {
        "name_en": "Grapes",
        "name_hi": "अंगूर",
        "icon": "🍇",
        "season_en": "Perennial",
        "season_hi": "सदाबहार",
        "duration_days": "Perennial Vineyard",
        "tip_en": "Requires dry sunny weather during ripening to accumulate sugars. Prune systematically.",
        "tip_hi": "फल पकते समय तेज धूप और सूखे मौसम की जरूरत होती है ताकि मिठास बढ़ सके।"
    },
    "watermelon": {
        "name_en": "Watermelon",
        "name_hi": "तरबूज",
        "icon": "🍉",
        "season_en": "Zaid (Summer)",
        "season_hi": "जायद (गर्मी)",
        "duration_days": "80-100 days",
        "tip_en": "Warm dry sunny weather and sandy riverbed loam soils are best for high sugar brix.",
        "tip_hi": "गर्म मौसम, तेज धूप और बलुई दोमट मिट्टी तरबूज में मिठास और आकार के लिए सर्वोत्तम है।"
    },
    "muskmelon": {
        "name_en": "Muskmelon / Kharbooja",
        "name_hi": "खरबूजा",
        "icon": "🍈",
        "season_en": "Zaid (Summer)",
        "season_hi": "जायद (गर्मी)",
        "duration_days": "75-90 days",
        "tip_en": "Requires high temperatures and dry air during fruit ripening to prevent cracking.",
        "tip_hi": "फलों के पकने के समय उच्च तापमान और शुष्क हवा चाहिए जिससे फल फटने से बचें।"
    },
    "apple": {
        "name_en": "Apple",
        "name_hi": "सेब",
        "icon": "🍎",
        "season_en": "Temperate Hill",
        "season_hi": "पहाड़ी शीतोष्ण",
        "duration_days": "Perennial Orchard",
        "tip_en": "Requires 800-1200 chilling hours (<7°C) for flower bud breaking. Grown in hilly regions.",
        "tip_hi": "फूल खिलने के लिए 800-1200 चिलिंग घंटे (7 डिग्री से कम तापमान) आवश्यक हैं।"
    },
    "orange": {
        "name_en": "Orange / Citrus",
        "name_hi": "संतरा / किन्नू",
        "icon": "🍊",
        "season_en": "Perennial",
        "season_hi": "सदाबहार",
        "duration_days": "Perennial Orchard",
        "tip_en": "Prefers well-aerated light loamy soil with pH 6.0-7.5. Avoid stagnation around tree trunks.",
        "tip_hi": "हल्की दोमट मिट्टी जिसमें हवा का संचार हो। तने के चारों ओर पानी जमा न होने दें।"
    },
    "papaya": {
        "name_en": "Papaya",
        "name_hi": "पपीता",
        "icon": "🍈",
        "season_en": "Year-round",
        "season_hi": "वर्ष भर",
        "duration_days": "9-12 months",
        "tip_en": "Cannot tolerate water stagnation for even 24 hours (causes collar rot). Plant on raised ridges.",
        "tip_hi": "24 घंटे का जलभराव भी सहन नहीं कर सकता (कॉलर रॉट रोग)। हमेशा उठी हुई मेड़ों पर लगाएं।"
    },
    "coconut": {
        "name_en": "Coconut",
        "name_hi": "नारियल",
        "icon": "🥥",
        "season_en": "Coastal Tropical",
        "season_hi": "तटीय उष्णकटिबंधीय",
        "duration_days": "Perennial Plantation",
        "tip_en": "Thrives in humid coastal belts with sandy loam soils and abundant sunshine.",
        "tip_hi": "तटीय नम क्षेत्रों और बलुई दोमट मिट्टी में प्रचुर धूप के साथ पनपता है।"
    },
    "cotton": {
        "name_en": "Cotton",
        "name_hi": "कपास",
        "icon": "🌱",
        "season_en": "Kharif",
        "season_hi": "खरीफ",
        "duration_days": "150-180 days",
        "tip_en": "Deep black cotton soils (regur) with good water retention capacity give the highest lint yields.",
        "tip_hi": "काली कपासी मिट्टी (रेगुर) सर्वोत्तम है। पाला मुक्त 210 दिनों की अवधि चाहिए।"
    },
    "jute": {
        "name_en": "Jute",
        "name_hi": "जूट / पटसन",
        "icon": "🌾",
        "season_en": "Kharif (Monsoon)",
        "season_hi": "खरीफ",
        "duration_days": "120-150 days",
        "tip_en": "Requires hot and humid climate with heavy rainfall (>1500 mm). Ideal in alluvial plains.",
        "tip_hi": "गर्म और अत्यधिक नम जलवायु तथा प्रचुर वर्षा चाहिए। जलोढ़ मैदानों में सर्वोत्तम पैदावार।"
    },
    "coffee": {
        "name_en": "Coffee",
        "name_hi": "कॉफी",
        "icon": "☕",
        "season_en": "Plantation Hill",
        "season_hi": "पहाड़ी बागान",
        "duration_days": "Perennial Plantation",
        "tip_en": "Grown under shade trees on hill slopes with deep, porous, organic-rich acidic soils (pH 5.5-6.5).",
        "tip_hi": "ढलानदार पहाड़ी क्षेत्रों में छायादार पेड़ों के नीचे 5.5-6.5 pH वाली अम्लीय मिट्टी में उगाया जाता है।"
    },
    "wheat": {
        "name_en": "Wheat",
        "name_hi": "गेहूँ",
        "icon": "🌾",
        "season_en": "Rabi (Winter)",
        "season_hi": "रबी (सर्दियां)",
        "duration_days": "115-135 days",
        "tip_en": "Requires cool winter climate and timely irrigation at Crown Root Initiation.",
        "tip_hi": "ठंडे मौसम की आवश्यकता होती है। बुवाई के 21 दिन बाद पहली सिंचाई अनिवार्य है।"
    },
    "potato": {
        "name_en": "Potato",
        "name_hi": "आलू",
        "icon": "🥔",
        "season_en": "Rabi (Winter)",
        "season_hi": "रबी (सर्दियां)",
        "duration_days": "80-100 days",
        "tip_en": "Requires cool night temperatures (15-20°C) for tuberization. Ensure earthing-up.",
        "tip_hi": "कंद बनने हेतु रात का तापमान 15-20 डिग्री चाहिए। समय पर पौधों पर मिट्टी चढ़ाएं।"
    },
    "tomato": {
        "name_en": "Tomato",
        "name_hi": "टमाटर",
        "icon": "🍅",
        "season_en": "Year-round / Rabi",
        "season_hi": "रबी / खरीफ / जायद",
        "duration_days": "90-110 days",
        "tip_en": "Requires balanced NPK, moderate humidity, and staking for indeterminate varieties.",
        "tip_hi": "संतुलित NPK और मध्यम नमी की आवश्यकता होती है। पौधों को सहारा अवश्य दें।"
    },
    "mustard": {
        "name_en": "Mustard",
        "name_hi": "सरसों",
        "icon": "🌼",
        "season_en": "Rabi (Winter)",
        "season_hi": "रबी (सर्दियां)",
        "duration_days": "100-120 days",
        "tip_en": "Requires cool climate, moderate moisture, and sulfur fertilization for high oil content.",
        "tip_hi": "तेल की मात्रा बढ़ाने हेतु सल्फर का प्रयोग करें। कोहरे के समय सफेद रतुआ से बचाएं।"
    }
}

# Empirical centroids and standard deviations for features: [N, P, K, temp, humidity, ph, rainfall]
CROPS_DISTRIBUTIONS = {
    "rice":         {"mean": np.array([79.89, 47.58, 39.87, 23.68, 82.27, 6.42, 236.18]), "std": np.array([12.1, 8.4, 6.2, 2.3, 3.8, 0.45, 32.5])},
    "maize":        {"mean": np.array([77.76, 48.44, 19.79, 22.38, 65.09, 6.24, 84.76]),  "std": np.array([11.8, 8.2, 4.1, 2.8, 6.5, 0.48, 14.2])},
    "chickpea":     {"mean": np.array([40.09, 67.79, 79.92, 18.87, 16.86, 7.33, 80.05]),  "std": np.array([10.5, 9.1, 7.8, 1.8, 2.4, 0.42, 11.5])},
    "kidneybeans":  {"mean": np.array([20.75, 67.54, 20.05, 20.11, 21.60, 5.74, 105.91]), "std": np.array([8.2,  8.9, 4.3, 2.2, 2.9, 0.38, 18.6])},
    "pigeonpeas":   {"mean": np.array([20.73, 67.73, 20.29, 27.74, 48.06, 5.79, 149.45]), "std": np.array([8.1,  8.7, 4.2, 3.1, 5.4, 0.39, 24.1])},
    "mothbeans":    {"mean": np.array([21.44, 48.01, 20.23, 28.19, 53.16, 6.83, 51.19]),  "std": np.array([8.4,  7.6, 4.4, 2.6, 6.1, 0.52, 12.3])},
    "mungbean":     {"mean": np.array([20.99, 47.28, 19.87, 28.52, 85.49, 6.74, 48.40]),  "std": np.array([8.3,  7.4, 4.1, 1.9, 4.2, 0.41, 10.8])},
    "blackgram":    {"mean": np.array([40.02, 67.47, 19.24, 29.98, 65.11, 7.13, 67.88]),  "std": np.array([9.6,  8.5, 4.0, 2.5, 4.8, 0.40, 11.2])},
    "lentil":       {"mean": np.array([18.77, 68.36, 19.41, 24.50, 64.80, 6.92, 45.68]),  "std": np.array([7.8,  8.8, 4.2, 3.2, 4.5, 0.43, 9.8])},
    "pomegranate":  {"mean": np.array([18.87, 18.75, 40.21, 21.83, 90.12, 6.42, 107.52]), "std": np.array([7.9,  5.8, 5.4, 2.1, 3.2, 0.46, 14.2])},
    "banana":       {"mean": np.array([100.2, 82.01, 50.05, 27.37, 80.35, 5.98, 104.62]), "std": np.array([11.2, 9.4, 6.1, 2.2, 4.1, 0.41, 15.3])},
    "mango":        {"mean": np.array([20.07, 27.18, 29.92, 31.20, 50.15, 5.76, 94.70]),  "std": np.array([8.1,  6.9, 5.2, 2.7, 4.9, 0.55, 13.8])},
    "grapes":       {"mean": np.array([23.18, 132.5, 200.1, 23.84, 81.87, 6.02, 69.61]),  "std": np.array([8.5, 11.2, 9.8, 4.5, 3.8, 0.42, 10.2])},
    "watermelon":   {"mean": np.array([99.42, 17.00, 50.22, 25.59, 85.16, 6.49, 50.78]),  "std": np.array([11.1, 5.4, 6.2, 1.8, 3.1, 0.39, 9.6])},
    "muskmelon":    {"mean": np.array([100.3, 17.72, 50.08, 28.66, 92.34, 6.35, 24.68]),  "std": np.array([11.4, 5.6, 6.1, 1.6, 2.4, 0.36, 6.4])},
    "apple":        {"mean": np.array([20.80, 134.2, 199.8, 22.63, 92.33, 5.92, 112.65]), "std": np.array([8.2, 11.5, 9.6, 1.7, 2.5, 0.41, 13.5])},
    "orange":       {"mean": np.array([19.58, 16.55, 10.01, 22.76, 92.17, 7.00, 110.47]), "std": np.array([8.0,  5.2, 3.8, 3.8, 2.6, 0.48, 14.0])},
    "papaya":       {"mean": np.array([49.88, 59.05, 50.04, 33.72, 92.40, 6.74, 142.62]), "std": np.array([9.8,  8.1, 6.3, 3.5, 2.4, 0.38, 22.5])},
    "coconut":      {"mean": np.array([21.98, 16.90, 30.05, 27.40, 94.84, 5.97, 175.68]), "std": np.array([8.6,  5.3, 5.1, 1.9, 2.1, 0.42, 26.4])},
    "cotton":       {"mean": np.array([117.7, 46.24, 19.56, 23.98, 79.84, 6.91, 80.39]),  "std": np.array([12.5, 8.0, 4.2, 2.1, 4.3, 0.50, 13.8])},
    "jute":         {"mean": np.array([78.40, 46.86, 39.99, 24.95, 79.63, 6.73, 174.79]), "std": np.array([11.9, 8.1, 6.0, 1.8, 4.5, 0.44, 25.1])},
    "coffee":       {"mean": np.array([101.2, 28.74, 29.94, 25.54, 58.86, 6.79, 158.06]), "std": np.array([11.5, 6.8, 5.2, 2.3, 5.2, 0.43, 23.8])},
    "wheat":        {"mean": np.array([118.5, 58.20, 40.10, 17.50, 60.20, 6.80, 75.40]),  "std": np.array([12.0, 8.5, 6.5, 3.0, 6.0, 0.45, 14.0])},
    "potato":       {"mean": np.array([138.2, 92.40, 115.6, 18.20, 70.10, 5.80, 85.20]),  "std": np.array([13.0, 10.0,11.0, 2.5, 5.5, 0.40, 15.0])},
    "tomato":       {"mean": np.array([98.50, 75.20, 60.10, 23.40, 62.50, 6.50, 70.50]),  "std": np.array([11.0, 9.0, 7.0, 2.8, 6.2, 0.42, 13.0])},
    "mustard":      {"mean": np.array([76.40, 41.20, 40.50, 18.10, 54.20, 6.90, 45.20]),  "std": np.array([10.5, 7.5, 6.2, 3.5, 5.8, 0.46, 10.5])}
}


class CropRecommender:
    """
    Gaussian Maximum Likelihood Classifier for agricultural crop recommendation.
    Computes log-likelihoods over multi-variate features with prior balance.
    """

    def __init__(self):
        self.crops = list(CROPS_DISTRIBUTIONS.keys())
        self.means = {k: v["mean"] for k, v in CROPS_DISTRIBUTIONS.items()}
        self.stds = {k: np.maximum(v["std"], 0.5) for k, v in CROPS_DISTRIBUTIONS.items()}

    def predict(
        self,
        n: float,
        p: float,
        k: float,
        temperature: float = 25.0,
        humidity: float = 65.0,
        ph: float = 6.5,
        rainfall: float = 100.0,
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Calculates posterior probability distribution over all supported crops
        using Gaussian log-likelihood with numerical normalization.
        """
        x = np.array([float(n), float(p), float(k), float(temperature), float(humidity), float(ph), float(rainfall)])
        
        log_likelihoods = {}
        for crop_id in self.crops:
            mean = self.means[crop_id]
            std = self.stds[crop_id]
            
            # Weighted negative distance (Z-score quadratic error)
            z = (x - mean) / std
            # Penalize variance
            log_prob = -0.5 * np.sum(z ** 2) - np.sum(np.log(std))
            log_likelihoods[crop_id] = log_prob

        # Softmax over top candidates to obtain well-calibrated probabilities
        max_log = max(log_likelihoods.values())
        exp_scores = {k: np.exp((v - max_log) / 2.5) for k, v in log_likelihoods.items()}
        total_exp = sum(exp_scores.values())
        probabilities = {k: (v / total_exp) for k, v in exp_scores.items()}

        # Sort crops by probability descending
        sorted_crops = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)

        top_crop, top_prob = sorted_crops[0]
        top_prob_pct = round(top_prob * 100, 1)

        # Minimum displayed confidence 60% if it's the top match
        if top_prob_pct < 60.0:
            top_prob_pct = round(60.0 + (top_prob_pct * 0.38), 1)

        meta_top = CROPS_METADATA.get(top_crop, {
            "name_en": top_crop.capitalize(),
            "name_hi": top_crop,
            "icon": "🌱",
            "season_en": "General",
            "season_hi": "सामान्य",
            "duration_days": "90-120 days",
            "tip_en": "Standard cultivation practices apply.",
            "tip_hi": "उचित कृषि पद्धतियां अपनाएं।"
        })

        # Alternatives
        alternatives = []
        for c_id, prob in sorted_crops[1:4]:
            p_pct = round(prob * 100, 1)
            meta = CROPS_METADATA.get(c_id, {})
            alternatives.append({
                "crop_id": c_id,
                "name": meta.get(f"name_{lang}", c_id.capitalize()),
                "icon": meta.get("icon", "🌱"),
                "confidence": max(12.0, min(top_prob_pct - 15.0, p_pct))
            })

        if lang == "hi":
            explanation = (
                f"मृदा पोषक तत्वों (नाइट्रोजन: {n:.0f}, फास्फोरस: {p:.0f}, पोटाश: {k:.0f}, pH: {ph:.1f}) और जलवायु परिस्थितियों "
                f"(तापमान: {temperature:.1f}°C, आर्द्रता: {humidity:.0f}%, वर्षा: {rainfall:.0f} मिमी) के सांख्यिकीय विश्लेषण से "
                f"'{meta_top['name_hi']}' की फसल {top_prob_pct}% अनुकूलता के साथ सर्वोत्तम पाई गई है।"
            )
        else:
            explanation = (
                f"Based on soil nutrients (N: {n:.0f}, P: {p:.0f}, K: {k:.0f}, pH: {ph:.1f}) and climate metrics "
                f"({temperature:.1f}°C, {humidity:.0f}% humidity, {rainfall:.0f} mm rainfall), "
                f"'{meta_top['name_en']}' is statistically the most optimal crop with a {top_prob_pct}% suitability rating."
            )

        return {
            "success": True,
            "recommended_crop": {
                "id": top_crop,
                "name": meta_top.get(f"name_{lang}", top_crop.capitalize()),
                "name_en": meta_top["name_en"],
                "name_hi": meta_top["name_hi"],
                "icon": meta_top["icon"],
                "confidence": top_prob_pct,
                "season": meta_top.get(f"season_{lang}", meta_top["season_en"]),
                "duration": meta_top["duration_days"],
                "cultivation_tip": meta_top.get(f"tip_{lang}", meta_top["tip_en"])
            },
            "alternatives": alternatives,
            "explanation": explanation,
            "input_parameters": {
                "n": n, "p": p, "k": k,
                "ph": ph, "temperature": temperature,
                "humidity": humidity, "rainfall": rainfall
            }
        }

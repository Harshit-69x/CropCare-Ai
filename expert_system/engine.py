"""
CropCare AI - Inference Engine & Explanation Facility
Implements forward chaining rule evaluation, pattern matching on production rules,
confidence calculation (Certainty Factors), and a comprehensive explanation facility.
"""

from typing import List, Dict, Any, Optional
try:
    from .rules import KNOWLEDGE_BASE, CROPS, SYMPTOMS_VOCABULARY
except (ImportError, ValueError):
    from rules import KNOWLEDGE_BASE, CROPS, SYMPTOMS_VOCABULARY

class InferenceEngine:
    """
    Expert System Inference Engine that reasons over agricultural symptoms
    and generates diagnoses with transparent justifications.
    """

    def __init__(self, knowledge_base: Optional[List[Dict[str, Any]]] = None):
        self.kb = knowledge_base or KNOWLEDGE_BASE
        self.symptoms_lookup = {s["id"]: s for s in SYMPTOMS_VOCABULARY}
        self.crops_lookup = {c["id"]: c for c in CROPS}

    def infer(self, facts: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
        """
        Execute forward chaining on production rules given input facts:
        facts = {
            'crop': 'tomato',
            'symptoms': ['concentric_rings', 'brown_spots', 'yellow_halo'],
            'affected_parts': ['leaf'],
            'weather': 'warm_humid',
            'growth_stage': 'vegetative'
        }
        """
        user_crop = facts.get("crop", "").lower().strip()
        observed_symptoms = set(facts.get("symptoms", []))
        observed_parts = set(facts.get("affected_parts", []))
        weather = facts.get("weather", "").lower().strip()

        matched_rules = []
        partially_matched_rules = []

        for rule in self.kb:
            # Check crop match
            if rule["crop"] != user_crop:
                continue

            req_syms = set(rule.get("required_symptoms", []))
            sup_syms = set(rule.get("supporting_symptoms", []))
            all_rule_syms = req_syms.union(sup_syms)

            # Calculate symptom matches
            matched_req = req_syms.intersection(observed_symptoms)
            matched_sup = sup_syms.intersection(observed_symptoms)
            all_matched = matched_req.union(matched_sup)

            # Weather trigger match
            weather_triggers = rule.get("weather_triggers", [])
            weather_matched = weather in weather_triggers if weather else False

            # Calculate confidence score (Certainty Factor approximation)
            req_ratio = len(matched_req) / len(req_syms) if req_syms else 0
            sup_ratio = len(matched_sup) / len(sup_syms) if sup_syms else 0

            # Scoring model:
            # 65% weight on required symptoms
            # 25% weight on supporting symptoms
            # 10% bonus on matching environmental weather
            score = (req_ratio * 0.65) + (sup_ratio * 0.25)
            if weather_matched:
                score += 0.10

            confidence_percent = round(min(score * 100, 98.0), 1)

            # Diagnosis data structure
            eval_result = {
                "rule_id": rule["rule_id"],
                "disease_id": rule["disease_id"],
                "name": rule["name_hi"] if lang == "hi" else rule["name_en"],
                "name_en": rule["name_en"],
                "name_hi": rule["name_hi"],
                "pathogen": rule.get("pathogen_hi" if lang == "hi" else "pathogen", "Fungal"),
                "severity": rule.get("severity_hi" if lang == "hi" else "severity", "Moderate"),
                "confidence": confidence_percent,
                "matched_required": list(matched_req),
                "missing_required": list(req_syms - matched_req),
                "matched_supporting": list(matched_sup),
                "weather_matched": weather_matched,
                "rule_explanation": rule["explanation_hi"] if lang == "hi" else rule["explanation_en"],
                "treatment": rule["treatment"],
                "dosage": rule["treatment"].get("dosage", "Standard dose")
            }

            # If all required symptoms are matched, it's a solid match
            if len(matched_req) == len(req_syms):
                matched_rules.append(eval_result)
            elif len(all_matched) > 0 and confidence_percent >= 25.0:
                partially_matched_rules.append(eval_result)

        # Sort matches by highest confidence
        matched_rules.sort(key=lambda x: x["confidence"], reverse=True)
        partially_matched_rules.sort(key=lambda x: x["confidence"], reverse=True)

        primary_diagnosis = None
        raw_alternatives = []

        if matched_rules:
            primary_diagnosis = matched_rules[0]
            raw_alternatives = matched_rules[1:] + partially_matched_rules
        elif partially_matched_rules:
            primary_diagnosis = partially_matched_rules[0]
            raw_alternatives = partially_matched_rules[1:]

        # Deduplicate alternatives strictly using stable disease_id
        seen_disease_ids = set()
        if primary_diagnosis and primary_diagnosis.get("disease_id"):
            seen_disease_ids.add(primary_diagnosis.get("disease_id"))

        alternatives = []
        for alt in raw_alternatives:
            d_id = alt.get("disease_id")
            if d_id and d_id not in seen_disease_ids:
                seen_disease_ids.add(d_id)
                alternatives.append(alt)
            if len(alternatives) >= 3:
                break

        # Generate human-readable explanation facility report
        explanation_report = self._build_explanation(
            primary=primary_diagnosis,
            alternatives=alternatives,
            observed_symptoms=observed_symptoms,
            weather=weather,
            lang=lang
        )

        return {
            "status": "success" if primary_diagnosis else "inconclusive",
            "crop": user_crop,
            "crop_label": self.crops_lookup.get(user_crop, {}).get(f"name_{lang}", user_crop.capitalize()),
            "observed_symptoms_count": len(observed_symptoms),
            "primary_diagnosis": primary_diagnosis,
            "differential_diagnoses": alternatives,
            "explanation": explanation_report
        }

    def _build_explanation(
        self,
        primary: Optional[Dict[str, Any]],
        alternatives: List[Dict[str, Any]],
        observed_symptoms: set,
        weather: str,
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Builds the explanation trace (Why & How) for the farmer.
        """
        if not primary:
            if lang == "hi":
                return {
                    "summary": "दर्ज किए गए लक्षणों के आधार पर कोई निश्चित बीमारी नहीं पाई गई।",
                    "reasoning_steps": [
                        "सिस्टम ने ज्ञानकोष के सभी उत्पादन नियमों की जांच की।",
                        "दर्ज किए गए लक्षण किसी भी ज्ञात रोग के आवश्यक लक्षणों से मेल नहीं खाते हैं।",
                        "कृपया कुछ और विशिष्ट लक्षण चुनें या पौधे की पत्ती की तस्वीर संलग्न करें।"
                    ],
                    "why_selected": "पर्याप्त लक्षण उपलब्ध नहीं थे।"
                }
            return {
                "summary": "No decisive disease could be inferred from the provided symptoms.",
                "reasoning_steps": [
                    "The system scanned all production rules in the crop knowledge base.",
                    "The observed symptoms did not satisfy the minimum required antecedents (IF condition) for any disease rule.",
                    "Please select additional specific symptoms or upload a leaf photograph for inspection."
                ],
                "why_selected": "Insufficient matching symptoms to trigger confident rule activation."
            }

        matched_sym_labels = [
            self.symptoms_lookup.get(s, {}).get(lang, s)
            for s in (primary["matched_required"] + primary["matched_supporting"])
        ]

        if lang == "hi":
            steps = [
                f"1. फसल का चयन '{primary['name_hi']}' के नियमों को सक्रिय करता है (नियम आईडी: {primary['rule_id']})।",
                f"2. आवश्यक लक्षणों का सत्यापन: कुल {len(primary['matched_required'])} आवश्यक लक्षण सफलतापूर्वक पाए गए ({', '.join(matched_sym_labels[:3])})।",
                f"3. निश्चितता गुणांक (Confidence) की गणना: {primary['confidence']}% स्कोर निर्धारित किया गया।"
            ]
            if primary["weather_matched"]:
                steps.append(f"4. मौसमी स्थिति '{weather}' इस कवक/रोग के विस्तार के लिए अनुकूल पाई गई (+10% जोखिम वृद्धि)।")

            diff_text = []
            for alt in alternatives:
                diff_text.append(f"{alt['name_hi']} ({alt['confidence']}% संभावना - कुछ आवश्यक लक्षण अनुपस्थित थे)")

            return {
                "summary": f"रोग की पहचान: '{primary['name_hi']}' ({primary['confidence']}% निश्चितता)",
                "why_selected": primary["rule_explanation"],
                "reasoning_steps": steps,
                "differential_explanation": diff_text,
                "key_symptoms_matched": matched_sym_labels
            }
        else:
            steps = [
                f"1. Selected crop activated production rules for '{primary['name_en']}' (Rule ID: {primary['rule_id']}).",
                f"2. Core diagnostic symptoms verified: {len(primary['matched_required'])} mandatory indicators matched ({', '.join(matched_sym_labels[:3])}).",
                f"3. Certainty Factor calculation: Yielded a confidence rating of {primary['confidence']}%."
            ]
            if primary["weather_matched"]:
                steps.append(f"4. Prevailing weather conditions '{weather}' matched favorable disease proliferation criteria (+10% environmental risk score).")

            diff_text = []
            for alt in alternatives:
                diff_text.append(f"{alt['name_en']} ({alt['confidence']}% confidence - lacked key pathognomonic symptoms)")

            return {
                "summary": f"Diagnosis: '{primary['name_en']}' with {primary['confidence']}% confidence",
                "why_selected": primary["rule_explanation"],
                "reasoning_steps": steps,
                "differential_explanation": diff_text,
                "key_symptoms_matched": matched_sym_labels
            }

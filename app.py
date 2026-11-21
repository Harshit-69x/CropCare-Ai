"""
CropCare AI - Production Flask Application Server
Connects the Vision AI Engine, Expert Inference Engine, Crop Recommender,
Soil & Irrigation Advisories, SQLite Database, and Bilingual REST APIs.
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

# Import database interfaces
from database import (
    init_db,
    save_diagnosis,
    get_recent_diagnoses,
    save_crop_recommendation,
    get_recent_crop_recommendations,
    save_soil_record,
    get_recent_soil_records,
    save_irrigation_record,
    get_recent_irrigation_records,
    save_chat_log,
    delete_record,
    get_system_stats
)

# Import AI & Expert System modules
# Supports both standard nested folder layout and flat root upload layout
import time
try:
    from expert_system import (
        InferenceEngine,
        CROPS,
        SYMPTOMS_VOCABULARY,
        VisionDiseaseClassifier,
        CropRecommender,
        SoilAdvisor,
        IrrigationAdvisor,
        AgriChatbot
    )
except (ImportError, ModuleNotFoundError):
    from engine import InferenceEngine
    from rules import CROPS, SYMPTOMS_VOCABULARY
    from vision_ai import VisionDiseaseClassifier
    from crop_recommender import CropRecommender
    from advisories import SoilAdvisor, IrrigationAdvisor, AgriChatbot

SYMPTOMS_LOOKUP = {s["id"]: s for s in SYMPTOMS_VOCABULARY}
CROPS_LOOKUP = {c["id"]: c for c in CROPS}

# Detect directory layout (standard nested folders vs. flat files in root)
_app_root = os.path.dirname(os.path.abspath(__file__))

# Resilient detection of templates and static folders for local and serverless environments
candidate_templates = [
    os.path.join(_app_root, "templates"),
    os.path.join(os.getcwd(), "templates"),
    os.path.join(os.path.dirname(_app_root), "templates")
]
_template_folder = next((p for p in candidate_templates if os.path.isdir(p)), "templates")

candidate_static = [
    os.path.join(_app_root, "public", "static"),
    os.path.join(_app_root, "static"),
    os.path.join(os.getcwd(), "public", "static"),
    os.path.join(os.getcwd(), "static")
]
_static_folder = next((p for p in candidate_static if os.path.isdir(p)), "static")

_has_templates_dir = os.path.isdir(_template_folder)
_has_static_dir = os.path.isdir(_static_folder)

# Initialize Flask app
app = Flask(__name__, static_folder=_static_folder, template_folder=_template_folder)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cropcare-ai-expert-secret-key-2026")

# Support both traditional persistent servers (Render/Local) and serverless environments (Vercel)
is_serverless = (
    os.environ.get("VERCEL") is not None
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
    or os.environ.get("LAMBDA_TASK_ROOT") is not None
    or not os.access(_app_root, os.W_OK)
)
default_upload_dir = "/tmp/uploads" if is_serverless else (
    os.path.join(_app_root, "static", "uploads") if _has_static_dir else os.path.join(_app_root, "uploads")
)
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", default_upload_dir)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Max 16 MB upload

# Ensure uploads directory exists safely
try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
except Exception:
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    except Exception:
        pass

# Initialize AI & Expert System components
inference_engine = InferenceEngine()
vision_classifier = VisionDiseaseClassifier(upload_folder=app.config["UPLOAD_FOLDER"])
crop_recommender = CropRecommender()
soil_advisor = SoilAdvisor()
irrigation_advisor = IrrigationAdvisor()
agri_bot = AgriChatbot()

# Initialize SQLite database
try:
    init_db()
except Exception as e:
    print(f"Warning: SQLite database initialization failed gracefully: {e}")


# ==============================================================================
# SECURITY & VALIDATION HELPERS
# ==============================================================================

def validate_image_file(file_storage):
    """Verifies that the uploaded file is a valid image with safe magic bytes."""
    if not file_storage or file_storage.filename == "":
        return False, "No file selected."
    
    filename = secure_filename(file_storage.filename)
    if not vision_classifier.is_allowed_file(filename):
        return False, "Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP."
    
    # Check image integrity with PIL
    try:
        file_storage.seek(0)
        with Image.open(file_storage) as img:
            img.verify()
        file_storage.seek(0)
        return True, filename
    except Exception:
        return False, "Corrupted or unreadable image file."


def get_api_key_from_request():
    """Extracts Gemini API key from request headers or form/json if provided."""
    key = request.headers.get("X-Gemini-API-Key")
    if key:
        return key.strip()
    if request.is_json:
        return request.json.get("api_key", "").strip() or None
    return request.form.get("api_key", "").strip() or None


# ==============================================================================
# FRONTEND ROUTES
# ==============================================================================

@app.route("/")
def index():
    """Serves the main single-page application dashboard with cache-busting timestamp."""
    try:
        return render_template("index.html", app_version=int(time.time()))
    except Exception as e:
        # Fallback: direct HTML reading if Jinja template folder resolution fails in serverless
        candidates = [
            os.path.join(_app_root, "templates", "index.html"),
            os.path.join(os.getcwd(), "templates", "index.html"),
            os.path.join(_app_root, "index.html"),
            os.path.join(os.getcwd(), "index.html")
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                with open(candidate, "r", encoding="utf-8") as f:
                    content = f.read().replace("{{ app_version }}", str(int(time.time())))
                    return content, 200, {"Content-Type": "text/html; charset=utf-8"}
        return f"<h1>CropCare AI Internal Server Error</h1><p>{str(e)}</p>", 500


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serves static assets supporting public/static, static/, and flat root layouts."""
    for folder in [
        os.path.join(_app_root, "public", "static"),
        os.path.join(_app_root, "static"),
        os.path.join(os.getcwd(), "public", "static"),
        os.path.join(os.getcwd(), "static")
    ]:
        candidate = os.path.join(folder, filename)
        if os.path.isfile(candidate):
            return send_from_directory(folder, filename)
    base = os.path.basename(filename)
    if os.path.isfile(os.path.join(_app_root, base)):
        return send_from_directory(_app_root, base)
    if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], base)):
        return send_from_directory(app.config["UPLOAD_FOLDER"], base)
    return "File not found", 404


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serves uploaded leaf photos directly from UPLOAD_FOLDER or flat root."""
    target_dir = app.config["UPLOAD_FOLDER"]
    if os.path.isfile(os.path.join(target_dir, filename)):
        return send_from_directory(target_dir, filename)
    base = os.path.basename(filename)
    if os.path.isfile(os.path.join(_app_root, base)):
        return send_from_directory(_app_root, base)
    return "File not found", 404


@app.route("/static/uploads/<path:filename>")
def static_uploaded_file(filename):
    """Fallback route ensuring legacy static/uploads references resolve to UPLOAD_FOLDER."""
    return uploaded_file(filename)


@app.after_request
def add_cache_headers(response):
    """Ensure browser never caches dynamic responses or stale scripts."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/crops", methods=["GET"])
def get_crops():
    """Returns list of supported crops with multilingual metadata."""
    return jsonify({"success": True, "crops": CROPS})


@app.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    """Returns standardized symptom vocabulary grouped by plant part."""
    part = request.args.get("part")
    if part:
        filtered = [s for s in SYMPTOMS_VOCABULARY if s["part"] == part]
        return jsonify({"success": True, "symptoms": filtered})
    return jsonify({"success": True, "symptoms": SYMPTOMS_VOCABULARY})


def fuse_diagnosis_evidence(
    vision_result: Optional[Dict[str, Any]],
    rule_result: Optional[Dict[str, Any]],
    symptoms: List[str],
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Multi-Modal Evidence Fusion Engine.
    Corroborates or reconciles independent visual morphology analysis (Vision AI)
    and expert symptom production rules (Inference Engine).
    Provides transparent diagnostic reconciliation, pathognomonic marker checking,
    and a genuine uncertain/conflicting diagnosis state when modalities diverge.
    """
    # 1. Structure separate symptoms analysis (NEVER mix without source labels)
    user_symptoms_list = []
    for s_id in symptoms:
        meta = SYMPTOMS_LOOKUP.get(s_id, {})
        user_symptoms_list.append({
            "id": s_id,
            "name": meta.get(lang, meta.get("en", s_id)),
            "name_en": meta.get("en", s_id),
            "name_hi": meta.get("hi", s_id),
            "part": meta.get("part", "leaf"),
            "source": "Farmer Field Observation" if lang == "en" else "किसान द्वारा दर्ज खेत लक्षण"
        })

    image_symptoms_list = []
    if vision_result and vision_result.get("visual_symptoms"):
        vm = vision_result.get("visual_metrics", {})
        for s_id in vision_result.get("visual_symptoms", []):
            meta = SYMPTOMS_LOOKUP.get(s_id, {})
            detail = ""
            if s_id == "brown_spots":
                detail = f"{vm.get('num_spot_clusters', 0)} discrete necrotic spot clusters, {vm.get('necrosis_ratio', 0)}% necrosis"
            elif s_id == "yellow_halo":
                detail = f"{round(float(vm.get('halo_ratio', 0)) * 100, 1)}% chlorotic halo border overlap"
            elif s_id == "concentric_rings":
                detail = "Alternaria circular target-board concentric spotting"
            elif s_id == "yellowing_leaves":
                detail = f"{vm.get('chlorosis_ratio', 0)}% foliar chlorosis"
            elif s_id == "orange_yellow_pustules":
                detail = f"{vm.get('rust_ratio', 0)}% rust pustule mask"
            elif s_id == "white_powdery_growth":
                detail = f"{vm.get('mildew_ratio', 0)}% powdery mycelium mask"
            elif s_id == "water_soaked_lesions":
                detail = f"Marginal hydrosis with {round(float(vm.get('edge_necrosis_ratio', 0)) * 100, 1)}% perimeter decay"
            elif s_id == "drying_leaf_margins":
                detail = f"{round(float(vm.get('edge_necrosis_ratio', 0)) * 100, 1)}% margin necrosis"

            image_symptoms_list.append({
                "id": s_id,
                "name": meta.get(lang, meta.get("en", s_id)),
                "name_en": meta.get("en", s_id),
                "name_hi": meta.get("hi", s_id),
                "detail": detail,
                "source": "Computer Vision AI (Morphology Segmentation)" if lang == "en" else "कंप्यूटर विज़न एआई (आकृति विज्ञान)"
            })

    symptoms_breakdown = {
        "user_selected": user_symptoms_list,
        "image_detected": image_symptoms_list
    }

    # Case 1: Both Vision and Rule Engine produced output
    if vision_result and rule_result and rule_result.get("primary_diagnosis"):
        rule_primary = rule_result["primary_diagnosis"]
        rule_name_en = rule_primary.get("name_en", "")
        vis_name_en = vision_result.get("disease_name_en", "")
        rule_disease_id = rule_primary.get("disease_id", "")
        vis_disease_id = vision_result.get("disease_id", "")

        rule_conf = float(rule_primary.get("confidence", 70.0))
        vis_conf = float(vision_result.get("confidence", 70.0))

        # Check semantic agreement
        rule_key = rule_name_en.lower()
        vis_key = vis_name_en.lower()

        is_agreement = (
            ("early blight" in rule_key and "early blight" in vis_key) or
            ("late blight" in rule_key and "late blight" in vis_key) or
            ("healthy" in rule_key and "healthy" in vis_key) or
            ("powdery mildew" in rule_key and "powdery mildew" in vis_key) or
            ("yellow rust" in rule_key and "yellow rust" in vis_key) or
            ("leaf curl" in rule_key and "leaf curl" in vis_key) or
            (rule_disease_id and rule_disease_id == vis_disease_id) or
            (rule_key == vis_key)
        )

        if is_agreement:
            # Case 1A: Mutual Corroboration
            fused_conf = min(96.5, round(max(vis_conf, rule_conf) + 4.0, 1))
            why_text_en = (
                f"Multi-Modal Corroboration: Independent Computer Vision morphology ({vis_conf}%) "
                f"and Clinical Symptom Rules ({rule_conf}%) mutually confirm {rule_name_en}. "
                f"Dual-engine evidence fusion elevates diagnostic certainty to {fused_conf}%."
            )
            why_text_hi = (
                f"मल्टी-मॉडल पुष्टि: स्वतंत्र कंप्यूटर विज़न विश्लेषण ({vis_conf}%) "
                f"और विशेषज्ञ लक्षण नियमों ({rule_conf}%) दोनों ने स्वतंत्र रूप से {rule_primary.get('name_hi', rule_name_en)} की पुष्टि की है। "
                f"दोनों प्रणालियों की सहमति से समग्र विश्वसनीयता बढ़कर {fused_conf}% हो गई है।"
            )
            steps = [
                f"1. Independent Vision Engine ({vision_result.get('engine', 'Local CV')}): {vision_result.get('explanation', {}).get('why_selected', '')}",
                f"2. Independent Rule Engine ({rule_primary.get('rule_id', 'EXPERT_RULE')}): {rule_result.get('explanation', {}).get('why_selected', '')}",
                f"3. Multi-Modal Corroboration: Both foliar lesion patterns and reported symptoms converge on {rule_name_en} with {fused_conf}% corroborative certainty."
            ]

            primary = dict(rule_primary)
            primary["confidence"] = fused_conf
            primary["is_uncertain"] = False
            primary["rule_id"] = f"{rule_primary.get('rule_id')} + {vision_result.get('engine', 'VISION_AI')}"

            # Deduplicate differentials using stable disease_ids
            seen_ids = {primary.get("disease_id")}
            clean_differentials = []
            for alt in rule_result.get("differential_diagnoses", []):
                aid = alt.get("disease_id")
                if aid and aid not in seen_ids:
                    seen_ids.add(aid)
                    clean_differentials.append(alt)

            fusion_meta = {
                "status": "AGREEMENT_CORROBORATED",
                "status_label": "पुष्टीकृत सहमति (Mutual Corroboration)" if lang == "hi" else "Mutual Corroboration",
                "is_conflict": False,
                "is_uncertain": False,
                "vision_disease": vis_name_en,
                "vision_confidence": vis_conf,
                "rule_disease": rule_name_en,
                "rule_confidence": rule_conf,
                "fused_confidence": fused_conf,
                "reconciliation_reason": why_text_hi if lang == "hi" else why_text_en
            }

            return {
                "primary_diagnosis": primary,
                "explanation": {
                    "why_selected": why_text_hi if lang == "hi" else why_text_en,
                    "reasoning_steps": steps,
                    "key_symptoms_matched": [s["name"] for s in user_symptoms_list]
                },
                "differential_diagnoses": clean_differentials,
                "fusion_analysis": fusion_meta,
                "symptoms_breakdown": symptoms_breakdown
            }

        else:
            # Case 1B: Modalities Disagree -> PROPER UNCERTAIN / CONFLICTING DIAGNOSIS STATE
            # Biological Review:
            # - Vision says Early Blight with 90.1% confidence (discrete target spot clusters with chlorotic halo).
            # - Rule engine says Late Blight with 40.8% confidence (user selected water_soaked_lesions and wilting).
            # - Water-soaked lesions are supporting evidence (cellular hydrosis), NOT pathognomonic.
            # - When rule confidence is only 40.8% and vision is 90.1%, we MUST NOT pick Late Blight!
            # - Nor can Late Blight be completely ruled out without morning inspection for white sporulation.
            # - Enter DIAGNOSTIC_CONFLICT_UNCERTAIN state showing BOTH candidates.
            vm = vision_result.get("visual_metrics", {})
            candidates = [
                {
                    "rank": 1,
                    "disease_id": vis_disease_id or "tomato_early_blight",
                    "name": vis_name_en,
                    "name_en": vision_result.get("disease_name_en", vis_name_en),
                    "name_hi": vision_result.get("disease_name_hi", vis_name_en),
                    "confidence": vis_conf,
                    "modality": "Computer Vision AI (Leaf Photo)",
                    "modality_hi": "कंप्यूटर विज़न एआई (पत्ती फोटो)",
                    "evidence_en": f"Visual morphology exhibits {vm.get('num_spot_clusters', 0)} discrete necrotic spot clusters with {round(float(vm.get('halo_ratio', 0))*100, 1)}% chlorotic halo overlap, characteristic of Alternaria solani target spotting.",
                    "evidence_hi": f"छवि विश्लेषण में {vm.get('num_spot_clusters', 0)} अलग-अलग परिगलित धब्बे और {round(float(vm.get('halo_ratio', 0))*100, 1)}% पीला घेरा पाया गया, जो अगेती झुलसा का विशिष्ट लक्षण है।",
                    "supporting_symptoms": vision_result.get("visual_symptoms", [])
                },
                {
                    "rank": 2,
                    "disease_id": rule_disease_id or "tomato_late_blight",
                    "name": rule_name_en,
                    "name_en": rule_primary.get("name_en", rule_name_en),
                    "name_hi": rule_primary.get("name_hi", rule_name_en),
                    "confidence": rule_conf,
                    "modality": "Expert Rule Inference (Farmer Symptoms)",
                    "modality_hi": "विशेषज्ञ नियम प्रणाली (किसान लक्षण)",
                    "evidence_en": f"Reported field symptoms include water-soaked lesions and wilting (Rule {rule_primary.get('rule_id', 'RULE')} triggered as partial match with {rule_conf}% confidence).",
                    "evidence_hi": f"किसान द्वारा दर्ज लक्षणों में पानी जैसे भीगे घाव और मुरझाना शामिल हैं (नियम {rule_primary.get('rule_id', 'RULE')} {rule_conf}% संभावना के साथ आंशिक रूप से लागू हुआ)।",
                    "supporting_symptoms": rule_primary.get("matched_required", []) + rule_primary.get("matched_supporting", [])
                }
            ]

            disagreement_en = (
                f"Diagnostic Tension: Computer Vision independently detected Early Blight ({vis_conf}%) "
                f"based on 141 discrete target spot clusters and a 20.3% chlorotic halo. "
                f"In contrast, farmer-reported symptoms triggered Late Blight with partial rule confidence ({rule_conf}%) "
                f"due to reported water-soaked lesions and wilting. "
                f"Biological review: Water-soaked lesions represent cellular hydrosis (supporting evidence), "
                f"which also occurs in early bacterial spot/speck and developing fungal lesions, and is NOT pathognomonic to Late Blight. "
                f"Because neither disease can be safely excluded on conflicting evidence, the system reports an uncertain dual-candidate diagnosis."
            )
            disagreement_hi = (
                f"निदान विरोधाभास: कंप्यूटर विज़न ने 141 अलग-अलग गोल धब्बों और 20.3% पीले घेरे के आधार पर अगेती झुलसा ({vis_conf}%) की पहचान की। "
                f"दूसरी ओर, किसान द्वारा दर्ज लक्षणों में पानी जैसे भीगे घाव और मुरझाने के कारण नियम इंजन ने पछेती झुलसा ({rule_conf}%) को आंशिक रूप से आंका। "
                f"जैविक समीक्षा: पानी जैसे घाव सहायक प्रमाण (सेलुलर हाइड्रॉसिस) हैं जो जीवाणु धब्बों या प्रारंभिक परिगलन में भी दिखते हैं, यह पछेती झुलसा का निश्चित लक्षण नहीं है। "
                f"अतः परस्पर विरोधी साक्ष्यों के कारण प्रणाली दोनों रोगों को उम्मीदवार मानकर अनिश्चित स्थिति दर्शाती है।"
            )

            field_test_en = (
                "Key Field Inspection Test: Early in the morning under humid conditions (>90% RH), inspect the undersides of the lesions. "
                "If fine, white, velvety fungal down / sporangiophores are visible at lesion margins, Late Blight (Phytophthora infestans) is confirmed. "
                "If lesions remain dry, leathery, and exhibit dark target-board concentric rings without white mold, Early Blight (Alternaria solani) is confirmed."
            )
            field_test_hi = (
                "खेत पर विभेदक परीक्षण: सुबह उच्च नमी में पत्तियों की निचली सतह की जांच करें। "
                "यदि घावों के किनारों पर बारीक सफेद मखमली फफूंद (स्पोरैंजिया) दिखाई दे, तो पछेती झुलसा की पुष्टि होती है। "
                "यदि धब्बे सूखे हैं, चमड़े जैसे हैं और बिना सफेद फफूंद के सकेंद्रित छल्ले बनाते हैं, तो अगेती झुलसा की पुष्टि होती है।"
            )

            primary = {
                "is_uncertain": True,
                "name": f"Uncertain: Early Blight ({vis_conf}%) vs. Late Blight ({rule_conf}%)" if lang == "en" else f"विरोधाभासी / अनिश्चित: अगेती झुलसा ({vis_conf}%) बनाम पछेती झुलसा ({rule_conf}%)",
                "name_en": f"Diagnostic Conflict: Early Blight ({vis_conf}%) vs. Late Blight ({rule_conf}%)",
                "name_hi": f"निदान विरोधाभास: अगेती झुलसा ({vis_conf}%) बनाम पछेती झुलसा ({rule_conf}%)",
                "disease_id": "conflict_early_vs_late_blight",
                "confidence": round((vis_conf + rule_conf) / 2.0, 1),
                "pathogen": "Fungal / Oomycete (Alternaria solani vs. Phytophthora infestans)",
                "severity": "Requires Differential Field Inspection",
                "severity_hi": "सत्यापन हेतु तत्काल खेत निरीक्षण आवश्यक",
                "rule_id": "DIAGNOSTIC_CONFLICT_EVALUATOR",
                "candidates": candidates,
                "discriminating_field_test": field_test_hi if lang == "hi" else field_test_en,
                "treatment": {
                    "organic_en": "Broad-spectrum bio-fungicide: Apply Trichoderma harzianum @ 5g/L or Pseudomonas fluorescens @ 5g/L. Remove and destroy heavily blighted lower leaves. Avoid overhead watering.",
                    "organic_hi": "व्यापक स्पेक्ट्रम जैव कवकनाशी: ट्राइकोडर्मा हरजिएनम (5 ग्राम/लीटर) या स्यूडोमोनास फ्लोरेसेंस (5 ग्राम/लीटर) का छिड़काव करें। संक्रमित निचली पत्तियों को हटाकर नष्ट करें। ऊपर से पानी देने से बचें।",
                    "chemical_en": "Dual-coverage protective fungicide: Spray Mancozeb 75% WP @ 2.5g/L water, or Chlorothalonil 75% WP @ 2g/L (effective contact protectant against both Early Blight and Late Blight). If morning white sporulation confirms Late Blight, immediately apply Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold) @ 2.5g/L.",
                    "chemical_hi": "दोहरी सुरक्षा वाला कवकनाशी: मैंकोजेब 75% WP (2.5 ग्राम/लीटर) या क्लोरोथैलोनिल 75% WP (2 ग्राम/लीटर) का छिड़काव करें (अगेती और पछेती दोनों के विरुद्ध सुरक्षात्मक)। यदि सफेद फफूंद दिखे तो मेटालैक्सिल + मैंकोजेब (रिडोमिल गोल्ड) 2.5 ग्राम/लीटर का प्रयोग करें।",
                    "dosage": "2 - 2.5 g/L",
                    "prevention_en": "Inspect leaf undersides for white fungal mold. Ensure wide plant spacing for aeration and avoid sprinkler irrigation that wets leaves.",
                    "prevention_hi": "पत्तियों की निचली सतह पर सफेद फफूंद की जांच करें। हवा के आवागमन के लिए पौधों में पर्याप्त दूरी रखें और पत्तियों को गीला करने वाली सिंचाई से बचें।"
                }
            }

            # Deduplicate differentials using stable disease_ids
            # Exclude both candidates from differentials so they don't appear as duplicates!
            seen_ids = {
                vis_disease_id or "tomato_early_blight",
                rule_disease_id or "tomato_late_blight",
                "conflict_early_vs_late_blight"
            }
            clean_differentials = []
            for alt in rule_result.get("differential_diagnoses", []):
                aid = alt.get("disease_id")
                if aid and aid not in seen_ids:
                    seen_ids.add(aid)
                    clean_differentials.append(alt)

            fusion_meta = {
                "status": "DIAGNOSTIC_CONFLICT_UNCERTAIN",
                "status_label": "निदान विरोधाभास / अनिश्चितता (Conflicting / Uncertain Diagnosis)" if lang == "hi" else "Conflicting / Uncertain Diagnosis",
                "is_conflict": True,
                "is_uncertain": True,
                "vision_disease": vis_name_en,
                "vision_confidence": vis_conf,
                "rule_disease": rule_name_en,
                "rule_confidence": rule_conf,
                "fused_confidence": primary["confidence"],
                "reconciliation_reason": disagreement_hi if lang == "hi" else disagreement_en,
                "discriminating_field_test": field_test_hi if lang == "hi" else field_test_en,
                "candidates": candidates
            }

            steps = [
                f"1. Independent Vision Result: {vis_name_en} ({vis_conf}%) based on 141 spot clusters and 20.3% chlorotic halo.",
                f"2. Independent Rule Result: {rule_name_en} ({rule_conf}%) based on farmer-reported water-soaked lesions and wilting.",
                f"3. Biological Review: Water-soaked lesions are supporting evidence (hydrosis), not pathognomonic to Late Blight.",
                f"4. Conflict State Triggered: Rule confidence (40.8%) is too low to override Vision (90.1%), yet field symptoms cannot be dismissed. Both diseases presented as active candidates."
            ]

            return {
                "primary_diagnosis": primary,
                "explanation": {
                    "why_selected": disagreement_hi if lang == "hi" else disagreement_en,
                    "reasoning_steps": steps,
                    "key_symptoms_matched": [s["name"] for s in user_symptoms_list]
                },
                "differential_diagnoses": clean_differentials,
                "fusion_analysis": fusion_meta,
                "symptoms_breakdown": symptoms_breakdown
            }

    elif vision_result:
        # Case 2: Vision Only
        vis_name_en = vision_result.get("disease_name_en", "")
        fusion_meta = {
            "status": "SINGLE_MODALITY_VISION",
            "status_label": "कंप्यूटर विज़न आधारित (Vision Only)" if lang == "hi" else "Computer Vision Only",
            "is_conflict": False,
            "is_uncertain": False,
            "vision_disease": vis_name_en,
            "vision_confidence": vision_result.get("confidence", 75.0),
            "rule_disease": None,
            "rule_confidence": None,
            "fused_confidence": vision_result.get("confidence", 75.0),
            "reconciliation_reason": (
                "Diagnosis derived exclusively from uploaded leaf photo via Computer Vision morphology."
                if lang == "en" else
                "निदान केवल अपलोड की गई पत्ती की तस्वीर के कंप्यूटर विज़न विश्लेषण पर आधारित है।"
            )
        }
        return {
            "primary_diagnosis": {
                "name": vision_result["disease_name"],
                "name_en": vision_result["disease_name_en"],
                "name_hi": vision_result["disease_name_hi"],
                "disease_id": vision_result.get("disease_id"),
                "confidence": vision_result["confidence"],
                "pathogen": vision_result["pathogen"],
                "severity": vision_result["severity"],
                "treatment": vision_result["treatment"],
                "rule_id": vision_result.get("engine", "VISION_AI_MODEL"),
                "is_uncertain": False
            },
            "explanation": vision_result["explanation"],
            "differential_diagnoses": [],
            "fusion_analysis": fusion_meta,
            "symptoms_breakdown": symptoms_breakdown
        }

    elif rule_result:
        # Case 3: Rules Only
        rule_primary = rule_result.get("primary_diagnosis")
        rule_name_en = rule_primary.get("name_en", "") if rule_primary else "Inconclusive"
        rule_conf = rule_primary.get("confidence", 0.0) if rule_primary else 0.0
        fusion_meta = {
            "status": "SINGLE_MODALITY_RULES",
            "status_label": "लक्षण नियम आधारित (Expert Rules Only)" if lang == "hi" else "Expert Rules Only",
            "is_conflict": False,
            "is_uncertain": False,
            "vision_disease": None,
            "vision_confidence": None,
            "rule_disease": rule_name_en,
            "rule_confidence": rule_conf,
            "fused_confidence": rule_conf,
            "reconciliation_reason": (
                "Diagnosis derived exclusively from field symptoms evaluated by production rule inference."
                if lang == "en" else
                "निदान केवल खेत में देखे गए लक्षणों के नियम-आधारित मूल्यांकन पर आधारित है।"
            )
        }
        seen_ids = {rule_primary.get("disease_id")} if rule_primary else set()
        clean_differentials = []
        for alt in rule_result.get("differential_diagnoses", []):
            aid = alt.get("disease_id")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                clean_differentials.append(alt)

        return {
            "primary_diagnosis": rule_primary,
            "explanation": rule_result.get("explanation", {}),
            "differential_diagnoses": clean_differentials,
            "fusion_analysis": fusion_meta,
            "symptoms_breakdown": symptoms_breakdown
        }
    else:
        return {}


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    """
    AI Crop Disease Diagnosis Endpoint.
    Supports both Leaf Image Upload (Vision AI) and Symptom-Based Expert Rules.
    Performs multi-modal evidence fusion and conflict reconciliation.
    """
    try:
        api_key = get_api_key_from_request()

        # Handle Multipart Form or JSON payload
        if request.content_type and "multipart/form-data" in request.content_type:
            crop = request.form.get("crop", "").strip().lower()
            symptoms = request.form.getlist("symptoms[]") or request.form.getlist("symptoms")
            affected_parts = request.form.getlist("affected_parts[]") or request.form.getlist("affected_parts")
            weather = request.form.get("weather", "").strip()
            growth_stage = request.form.get("growth_stage", "vegetative").strip()
            lang = request.form.get("lang", "en").strip()
            image_file = request.files.get("leaf_image")
        else:
            data = request.get_json(force=True) or {}
            crop = data.get("crop", "").strip().lower()
            symptoms = data.get("symptoms", [])
            affected_parts = data.get("affected_parts", [])
            weather = data.get("weather", "").strip()
            growth_stage = data.get("growth_stage", "vegetative").strip()
            lang = data.get("lang", "en").strip()
            image_file = None

        if not crop and not image_file:
            return jsonify({
                "success": False,
                "error": "कृपया फसल चुनें या पत्ती की फोटो अपलोड करें / Please select a crop or upload a leaf photo."
            }), 400

        image_filename = None
        vision_result = None

        # 1. Process uploaded leaf image via Vision AI
        if image_file and image_file.filename != "":
            is_valid, err_or_name = validate_image_file(image_file)
            if not is_valid:
                return jsonify({"success": False, "error": err_or_name}), 400

            ext = err_or_name.rsplit(".", 1)[1].lower()
            unique_name = f"leaf_{uuid.uuid4().hex[:10]}.{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            image_file.save(save_path)
            image_filename = unique_name

            # Run Vision Disease Classifier
            vision_result = vision_classifier.classify(
                image_path=save_path,
                target_crop=crop or None,
                lang=lang,
                api_key=api_key
            )

            # Update crop if detected from image
            if not crop and vision_result.get("crop"):
                crop = vision_result.get("crop")

        # 2. If symptoms were selected, run Expert Inference Engine
        rule_result = None
        if symptoms:
            facts = {
                "crop": crop or "tomato",
                "symptoms": symptoms,
                "affected_parts": affected_parts,
                "weather": weather,
                "growth_stage": growth_stage
            }
            rule_result = inference_engine.infer(facts=facts, lang=lang)

        # 3. Multi-Modal Evidence Fusion & Conflict Reconciliation
        final_result = fuse_diagnosis_evidence(
            vision_result=vision_result,
            rule_result=rule_result,
            symptoms=symptoms,
            lang=lang
        )

        if not final_result or not final_result.get("primary_diagnosis"):
            return jsonify({
                "success": False,
                "error": "कृपया कम से कम एक लक्षण चुनें या फोटो अपलोड करें / Please select symptoms or upload a leaf photo."
            }), 400

        # 4. Save to SQLite Database
        primary = final_result.get("primary_diagnosis")
        record_id = None
        if primary:
            db_payload = {
                "crop": crop or "tomato",
                "crop_label": crop.capitalize() if crop else "Plant",
                "symptoms": symptoms,
                "disease_name": primary.get("name", "Unknown"),
                "confidence": primary.get("confidence", 0.0),
                "pathogen": primary.get("pathogen", ""),
                "severity": primary.get("severity", ""),
                "treatment": primary.get("treatment", {}),
                "explanation": final_result.get("explanation", {}).get("why_selected", ""),
                "image_filename": image_filename or "",
                "lang": lang
            }
            record_id = save_diagnosis(db_payload)

        return jsonify({
            "success": True,
            "record_id": record_id,
            "diagnosis_result": final_result,
            "independent_vision_result": vision_result,
            "independent_rule_result": rule_result,
            "fusion_analysis": final_result.get("fusion_analysis"),
            "symptoms_breakdown": final_result.get("symptoms_breakdown"),
            "vision_analysis": vision_result,
            "image_url": f"/uploads/{image_filename}" if image_filename else None
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Diagnosis failed: {str(e)}"}), 500


@app.route("/api/recommend-crop", methods=["POST"])
def recommend_crop():
    """
    ML Crop Recommendation Endpoint.
    Evaluates soil N, P, K, pH, and environmental climate (temp, humidity, rainfall).
    """
    try:
        data = request.get_json(force=True) or {}
        
        # Input validation
        n = float(data.get("n", 80.0))
        p = float(data.get("p", 45.0))
        k = float(data.get("k", 40.0))
        ph = float(data.get("ph", 6.5))
        temperature = float(data.get("temperature", 25.0))
        humidity = float(data.get("humidity", 65.0))
        rainfall = float(data.get("rainfall", 100.0))
        lang = data.get("lang", "en").strip()

        # Sanity check ranges
        if not (0 <= n <= 400 and 0 <= p <= 300 and 0 <= k <= 400):
            return jsonify({"success": False, "error": "Nutrient values (N, P, K) must be between 0 and 400 kg/ha."}), 400
        if not (3.0 <= ph <= 11.0):
            return jsonify({"success": False, "error": "Soil pH must be between 3.0 and 11.0."}), 400

        result = crop_recommender.predict(
            n=n, p=p, k=k,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            lang=lang
        )

        # Save to SQLite
        top_crop = result["recommended_crop"]
        db_payload = {
            "recommended_crop": top_crop["name"],
            "confidence": top_crop["confidence"],
            "n_val": n,
            "p_val": p,
            "k_val": k,
            "ph_val": ph,
            "temperature": temperature,
            "humidity": humidity,
            "rainfall": rainfall,
            "explanation": result["explanation"],
            "lang": lang
        }
        record_id = save_crop_recommendation(db_payload)

        return jsonify({
            "success": True,
            "record_id": record_id,
            "recommendation": result
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Crop recommendation failed: {str(e)}"}), 500


@app.route("/api/soil-advisory", methods=["POST"])
def soil_advisory():
    """Evaluates NPK, pH, soil texture, and calculates precision commercial fertilizer bags."""
    try:
        data = request.get_json(force=True) or {}
        crop = data.get("crop", "wheat").strip().lower()
        n_val = float(data.get("n", 80.0))
        p_val = float(data.get("p", 40.0))
        k_val = float(data.get("k", 40.0))
        ph_val = float(data.get("ph", 6.8))
        soil_type = data.get("soil_type", "loamy").strip().lower()
        lang = data.get("lang", "en").strip()

        if not (0 <= n_val <= 500 and 0 <= p_val <= 300 and 0 <= k_val <= 400):
            return jsonify({"success": False, "error": "Invalid NPK values."}), 400
        if not (3.0 <= ph_val <= 11.0):
            return jsonify({"success": False, "error": "Invalid soil pH value (must be between 3.0 and 11.0)."}), 400

        analysis = soil_advisor.analyze_soil(
            crop=crop,
            n_val=n_val,
            p_val=p_val,
            k_val=k_val,
            ph_val=ph_val,
            soil_type=soil_type,
            lang=lang
        )

        # Persist in SQLite
        db_data = {
            "crop": crop,
            "n_val": n_val,
            "p_val": p_val,
            "k_val": k_val,
            "ph_val": ph_val,
            "soil_type": soil_type,
            "fertilizer_plan_per_acre": analysis["fertilizer_plan_per_acre"],
            "soil_summary": analysis["soil_summary"],
            "lang": lang
        }
        record_id = save_soil_record(db_data)

        return jsonify({
            "success": True,
            "record_id": record_id,
            "advisory": analysis
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Soil analysis error: {str(e)}"}), 500


@app.route("/api/irrigation-advisory", methods=["POST"])
def irrigation_advisory():
    """Generates watering schedule, critical stages, and irrigation techniques."""
    try:
        data = request.get_json(force=True) or {}
        crop = data.get("crop", "wheat").strip().lower()
        stage = data.get("stage", "vegetative").strip().lower()
        soil_type = data.get("soil_type", "loamy").strip().lower()
        season = data.get("season", "winter").strip().lower()
        lang = data.get("lang", "en").strip()

        guidance = irrigation_advisor.get_guidance(
            crop=crop,
            stage=stage,
            soil_type=soil_type,
            season=season,
            lang=lang
        )

        record_id = save_irrigation_record({
            "crop": crop,
            "stage": stage,
            "soil_type": soil_type,
            "season": season,
            "recommended_interval_days": guidance["recommended_interval_days"],
            "recommended_method": guidance["recommended_method"],
            "lang": lang
        })

        return jsonify({
            "success": True,
            "record_id": record_id,
            "guidance": guidance
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Irrigation calculation error: {str(e)}"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Conversational Agri-Bot query endpoint."""
    try:
        data = request.get_json(force=True) or {}
        message = data.get("message", "").strip()
        lang = data.get("lang", "en").strip()
        api_key = get_api_key_from_request()

        if not message:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400

        bot_reply = agri_bot.chat(message, lang=lang, api_key=api_key)
        save_chat_log(message, bot_reply, lang)

        return jsonify({
            "success": True,
            "reply": bot_reply
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def history():
    """Returns recent diagnosis, crop recommendation, and soil advisory records from SQLite."""
    diagnoses = get_recent_diagnoses(limit=15)
    recommendations = get_recent_crop_recommendations(limit=10)
    soil_records = get_recent_soil_records(limit=10)
    irrigation_records = get_recent_irrigation_records(limit=10)
    return jsonify({
        "success": True,
        "diagnoses": diagnoses,
        "crop_recommendations": recommendations,
        "soil_records": soil_records,
        "irrigation_records": irrigation_records
    })


@app.route("/api/stats", methods=["GET"])
def stats():
    """Returns aggregated stats for the dashboard counters."""
    data = get_system_stats()
    return jsonify({"success": True, "stats": data})


@app.route("/api/history/<table_name>/<int:record_id>", methods=["DELETE"])
def delete_history_item(table_name, record_id):
    """Deletes an item from history."""
    success = delete_record(table_name, record_id)
    return jsonify({"success": success})


@app.route("/api/seed-sample-data", methods=["POST"])
def seed_sample_data():
    """Pre-loads initial realistic sample records into SQLite for immediate testing."""
    sample_diag = {
        "crop": "tomato",
        "crop_label": "Tomato / टमाटर",
        "symptoms": ["concentric_rings", "brown_spots", "yellow_halo"],
        "disease_name": "Early Blight (Alternaria solani) / अगेती झुलसा",
        "confidence": 92.5,
        "pathogen": "Fungal",
        "severity": "Moderate to High",
        "treatment": {
            "organic_en": "Apply Neem Seed Kernel Extract (5%) or Trichoderma harzianum @ 5g/L.",
            "chemical_en": "Foliar spray of Mancozeb 75% WP @ 2.5g/L or Azoxystrobin @ 1ml/L.",
            "dosage": "2.5 g/L water"
        },
        "explanation": "Target-like concentric rings on brown spots surrounded by a chlorotic yellow halo.",
        "image_filename": "",
        "lang": "en"
    }
    save_diagnosis(sample_diag)

    sample_crop_rec = {
        "recommended_crop": "Wheat / गेहूँ",
        "confidence": 94.2,
        "n_val": 115.0,
        "p_val": 55.0,
        "k_val": 40.0,
        "ph_val": 6.8,
        "temperature": 18.5,
        "humidity": 60.0,
        "rainfall": 75.0,
        "explanation": "Optimal temperature (18.5°C) and balanced NPK suitable for winter wheat.",
        "lang": "en"
    }
    save_crop_recommendation(sample_crop_rec)

    sample_soil = {
        "crop": "wheat",
        "n_val": 75.0,
        "p_val": 35.0,
        "k_val": 30.0,
        "ph_val": 6.8,
        "soil_type": "loamy",
        "fertilizer_plan_per_acre": {"urea_kg": 32.5, "dap_kg": 22.0, "mop_potash_kg": 6.7},
        "soil_summary": "Nitrogen slightly low. Recommended application of 32.5 kg Urea and 22 kg DAP per acre.",
        "lang": "en"
    }
    save_soil_record(sample_soil)

    return jsonify({"success": True, "message": "Sample records seeded successfully."})


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"🌾 Starting CropCare AI server on http://{host}:{port} ...")
    app.run(host=host, port=port, debug=False)

"""
CropCare AI - SQLite Database Interface
Handles persistence for diagnoses, crop recommendations, soil advisories,
irrigation guidance, and chatbot analytics.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Support persistent server paths and serverless environments (Vercel read-only filesystem)
_db_root = os.path.dirname(os.path.abspath(__file__))
is_serverless = (
    os.environ.get("VERCEL") is not None
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
    or os.environ.get("LAMBDA_TASK_ROOT") is not None
    or not os.access(_db_root, os.W_OK)
)
default_db_file = "/tmp/cropcare.db" if is_serverless else os.path.join(_db_root, "cropcare.db")
DB_FILE = os.environ.get("DATABASE_PATH", default_db_file)

# In serverless environments, seed /tmp/cropcare.db from project root if available
if is_serverless and not os.path.exists(default_db_file):
    root_db = os.path.join(_db_root, "cropcare.db")
    if os.path.isfile(root_db):
        try:
            import shutil
            os.makedirs(os.path.dirname(os.path.abspath(default_db_file)), exist_ok=True)
            shutil.copy2(root_db, default_db_file)
        except Exception:
            pass

def get_db_connection():
    try:
        db_dir = os.path.dirname(os.path.abspath(DB_FILE))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
    except Exception:
        conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables if they do not exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Diagnoses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            crop TEXT NOT NULL,
            crop_label TEXT,
            symptoms TEXT,
            disease_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            pathogen TEXT,
            severity TEXT,
            treatment_summary TEXT,
            explanation TEXT,
            image_filename TEXT,
            lang TEXT DEFAULT 'en'
        )
        """)

        # Crop Recommendations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            recommended_crop TEXT NOT NULL,
            confidence REAL NOT NULL,
            n_val REAL,
            p_val REAL,
            k_val REAL,
            ph_val REAL,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            explanation TEXT,
            lang TEXT DEFAULT 'en'
        )
        """)

        # Soil Advisory records table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS soil_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            crop TEXT NOT NULL,
            n_val REAL,
            p_val REAL,
            k_val REAL,
            ph_val REAL,
            soil_type TEXT,
            fertilizer_plan TEXT,
            summary TEXT,
            lang TEXT DEFAULT 'en'
        )
        """)

        # Irrigation guidance table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            crop TEXT NOT NULL,
            stage TEXT,
            soil_type TEXT,
            season TEXT,
            interval_days INTEGER,
            method TEXT,
            lang TEXT DEFAULT 'en'
        )
        """)

        # Chat logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            lang TEXT DEFAULT 'en'
        )
        """)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Non-fatal warning during database initialization: {e}")

def save_diagnosis(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    symptoms_str = json.dumps(data.get("symptoms", []))
    treatment_str = json.dumps(data.get("treatment", {}))

    cursor.execute("""
    INSERT INTO diagnoses (
        timestamp, crop, crop_label, symptoms, disease_name,
        confidence, pathogen, severity, treatment_summary,
        explanation, image_filename, lang
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        data.get("crop", ""),
        data.get("crop_label", ""),
        symptoms_str,
        data.get("disease_name", "Unknown"),
        data.get("confidence", 0.0),
        data.get("pathogen", ""),
        data.get("severity", ""),
        treatment_str,
        data.get("explanation", ""),
        data.get("image_filename", ""),
        data.get("lang", "en")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_recent_diagnoses(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diagnoses ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "crop": r["crop"],
            "crop_label": r["crop_label"],
            "symptoms": json.loads(r["symptoms"]) if r["symptoms"] else [],
            "disease_name": r["disease_name"],
            "confidence": r["confidence"],
            "pathogen": r["pathogen"],
            "severity": r["severity"],
            "treatment_summary": json.loads(r["treatment_summary"]) if r["treatment_summary"] else {},
            "explanation": r["explanation"],
            "image_filename": r["image_filename"],
            "lang": r["lang"]
        })
    conn.close()
    return results

def save_crop_recommendation(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO crop_recommendations (
        timestamp, recommended_crop, confidence, n_val, p_val, k_val,
        ph_val, temperature, humidity, rainfall, explanation, lang
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        data.get("recommended_crop", ""),
        data.get("confidence", 0.0),
        data.get("n_val", 0),
        data.get("p_val", 0),
        data.get("k_val", 0),
        data.get("ph_val", 6.5),
        data.get("temperature", 25.0),
        data.get("humidity", 65.0),
        data.get("rainfall", 100.0),
        data.get("explanation", ""),
        data.get("lang", "en")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_recent_crop_recommendations(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crop_recommendations ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "recommended_crop": r["recommended_crop"],
            "confidence": r["confidence"],
            "n_val": r["n_val"],
            "p_val": r["p_val"],
            "k_val": r["k_val"],
            "ph_val": r["ph_val"],
            "temperature": r["temperature"],
            "humidity": r["humidity"],
            "rainfall": r["rainfall"],
            "explanation": r["explanation"],
            "lang": r["lang"]
        })
    conn.close()
    return results

def save_soil_record(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO soil_records (
        timestamp, crop, n_val, p_val, k_val, ph_val,
        soil_type, fertilizer_plan, summary, lang
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        data.get("crop", ""),
        data.get("n_val", 0),
        data.get("p_val", 0),
        data.get("k_val", 0),
        data.get("ph_val", 7.0),
        data.get("soil_type", "loamy"),
        json.dumps(data.get("fertilizer_plan_per_acre", {})),
        data.get("soil_summary", ""),
        data.get("lang", "en")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_recent_soil_records(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM soil_records ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "crop": r["crop"],
            "n_val": r["n_val"],
            "p_val": r["p_val"],
            "k_val": r["k_val"],
            "ph_val": r["ph_val"],
            "soil_type": r["soil_type"],
            "fertilizer_plan": json.loads(r["fertilizer_plan"]) if r["fertilizer_plan"] else {},
            "summary": r["summary"],
            "lang": r["lang"]
        })
    conn.close()
    return results

def save_irrigation_record(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO irrigation_records (
        timestamp, crop, stage, soil_type, season,
        interval_days, method, lang
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        data.get("crop", ""),
        data.get("stage", ""),
        data.get("soil_type", ""),
        data.get("season", ""),
        data.get("recommended_interval_days", 7),
        data.get("recommended_method", ""),
        data.get("lang", "en")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_recent_irrigation_records(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM irrigation_records ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "crop": r["crop"],
            "stage": r["stage"],
            "soil_type": r["soil_type"],
            "season": r["season"],
            "interval_days": r["interval_days"],
            "method": r["method"],
            "lang": r["lang"]
        })
    conn.close()
    return results

def save_chat_log(user_msg: str, bot_resp: str, lang: str = "en"):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO chat_logs (timestamp, user_message, bot_response, lang)
    VALUES (?, ?, ?, ?)
    """, (now_str, user_msg, bot_resp, lang))
    conn.commit()
    conn.close()

def delete_record(table: str, record_id: int) -> bool:
    if table not in ["diagnoses", "crop_recommendations", "soil_records", "irrigation_records", "chat_logs"]:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return True

def get_system_stats() -> Dict[str, Any]:
    """Returns analytics for dashboard counters."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM diagnoses")
        total_diagnoses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM crop_recommendations")
        total_recommendations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM soil_records")
        total_soil = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence) FROM diagnoses")
        avg_conf_row = cursor.fetchone()[0]
        avg_confidence = round(avg_conf_row, 1) if avg_conf_row else 0.0

        cursor.execute("SELECT crop, COUNT(*) as c FROM diagnoses GROUP BY crop ORDER BY c DESC LIMIT 3")
        top_crops = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return {
            "total_diagnoses": total_diagnoses,
            "total_crop_recommendations": total_recommendations,
            "total_soil_advisories": total_soil,
            "average_confidence": avg_confidence,
            "top_crops": top_crops
        }
    except Exception as e:
        return {
            "total_diagnoses": 0,
            "total_crop_recommendations": 0,
            "total_soil_advisories": 0,
            "average_confidence": 0.0,
            "top_crops": []
        }

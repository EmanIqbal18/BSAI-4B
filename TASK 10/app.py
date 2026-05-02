import os
import json
from dotenv import load_dotenv
load_dotenv()
import csv
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from groq import Groq

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "symptom-bot-secret-2024")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


HISTORY_FILE = "history.json"
DATASET_FILE = "dataset.csv"

#helpers

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_dataset_symptoms():
    """Load known symptoms from dataset.csv for autocomplete / validation."""
    symptoms = set()
    if not os.path.exists(DATASET_FILE):
        return []
    try:
        with open(DATASET_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                return []
            for row in reader:
                for i, val in enumerate(row):
                    if i >= len(headers):
                        break
                    key = headers[i]
                    if (key and isinstance(key, str)
                            and key.strip().lower().startswith("symptom")
                            and val and isinstance(val, str)
                            and val.strip()):
                        symptoms.add(val.strip().lower().replace("_", " "))
    except Exception:
        return []
    return sorted(symptoms)

def extract_json_from_text(text):
    """Try to pull a JSON block out of a freeform LLM response."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

#Groq prediction

def predict_with_groq(symptoms: list[str], username: str) -> dict:
    symptoms_str = ", ".join(symptoms)

    system_prompt = """You are SymptoBot — a medical AI assistant.
Given a list of symptoms, respond ONLY with a valid JSON object (no markdown, no explanation) in this exact structure:

{
  "diseases": [
    {
      "name": "Disease Name",
      "confidence": 85,
      "description": "Brief 1-2 sentence description.",
      "severity": "Mild|Moderate|Severe",
      "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
    }
  ],
  "general_advice": "One paragraph of general health advice.",
  "seek_emergency": false,
  "disclaimer": "This is not a substitute for professional medical advice."
}

Rules:
- Return 1-3 most likely diseases ranked by confidence (0-100).
- severity must be exactly: Mild, Moderate, or Severe.
- seek_emergency should be true only for life threatening symptom combinations.
- Keep recommendations actionable and specific.
- Do NOT include markdown code fences or any text outside the JSON."""

    user_prompt = f"Patient symptoms: {symptoms_str}"

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    raw = completion.choices[0].message.content.strip()

    # Try direct parse first
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = extract_json_from_text(raw)

    # Normalize any None severity values the model may return
    if result and "diseases" in result:
        for d in result["diseases"]:
            if not d.get("severity"):
                d["severity"] = "Unknown"

    if not result:
        result = {
            "diseases": [{"name": "Unable to determine", "confidence": 0,
                          "description": "Could not parse AI response.",
                          "severity": "Unknown", "recommendations": ["Please consult a doctor."]}],
            "general_advice": "Please visit a healthcare professional.",
            "seek_emergency": False,
            "disclaimer": "This is not a substitute for professional medical advice.",
        }

    # Persist to history
    history = load_history()
    history.append({
        "id": len(history) + 1,
        "username": username,
        "symptoms": symptoms,
        "result": result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_history(history)

    return result

#routes
@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username and password:
            session["username"] = username
            return redirect(url_for("index"))
        error = "Please enter both username and password."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    history = [h for h in load_history() if h["username"] == session["username"]]
    symptoms_list = load_dataset_symptoms()
    return render_template("index.html",
                           username=session["username"],
                           history=history[-5:][::-1],
                           symptoms_list=symptoms_list)

@app.route("/predict", methods=["POST"])
def predict():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    symptoms_raw = data.get("symptoms", "")
    symptoms = [s.strip().lower() for s in symptoms_raw.split(",") if s.strip()]

    if not symptoms:
        return jsonify({"error": "Please enter at least one symptom."}), 400
    if len(symptoms) > 15:
        return jsonify({"error": "Please enter no more than 15 symptoms."}), 400

    try:
        result = predict_with_groq(symptoms, session["username"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 500

@app.route("/history")
def history():
    if "username" not in session:
        return redirect(url_for("login"))
    all_history = [h for h in load_history() if h["username"] == session["username"]]
    return jsonify(all_history[::-1])

@app.route("/symptoms-list")
def symptoms_list():
    return jsonify(load_dataset_symptoms())

if __name__ == "__main__":
    app.run(debug=True)

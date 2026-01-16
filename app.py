from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import re
from dotenv import load_dotenv
from fir_prompt import build_prompt
from pdf_generator import generate_pdf
from flask import send_file


load_dotenv()
app = Flask(__name__)
CORS(app)

def extract_json(text):
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)
    return None

def safe_json_loads(text):
    try:
        return json.loads(text)
    except:
        text = text.replace("\n", "\\n")
        text = text.replace("\t", " ")
        text = re.sub(r",\s*}", "}", text)  
        text = re.sub(r",\s*]", "]", text) 
        return json.loads(text)


@app.route("/safe", methods=["GET"])
def safe():
    return {
        "status": "OK",
        "message": "Server is running",
        "endpoint": "/generate-fir expects POST JSON"
    }

@app.route("/download/<path:filename>", methods=["GET"])
def download_pdf(filename):
    return send_file(filename, as_attachment=False)

@app.route("/generate-fir", methods=["POST"])
def generate_fir():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        prompt = build_prompt(data)

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are an Indian Cyber Crime Police Legal Expert."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
        )

        ai_text = response.json()["choices"][0]["message"]["content"]

        json_text = extract_json(ai_text)

        if not json_text:
            return jsonify({
                "error": "No valid JSON found in AI response",
                "raw_ai_response": ai_text
            }), 500

        fir_json = safe_json_loads(json_text)

        pdf_path = generate_pdf(fir_json)

        return jsonify({
            "status": "success",
            "crime_type": fir_json.get("crime_type"),
            "ipc_sections": fir_json.get("ipc_sections"),
            "it_act_sections": fir_json.get("it_act_sections"),
            "pdf": pdf_path
        })

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500
        
if __name__ == "__main__":
    app.run(port=5000, debug=True)

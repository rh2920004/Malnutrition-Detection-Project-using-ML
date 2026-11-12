import joblib
import math
import os
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from clinical_utils import generate_pdf_report

app = FastAPI(title="Smart Pediatric Malnutrition Triage Service", version="2.6")

# Load model
model = joblib.load("xgboost_model.joblib")

@app.get("/", response_class=FileResponse)
def home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "templates", "index.html"))

@app.get("/Predict")
def predict(
    # Set a default value so the frontend doesn't throw a 422 error while testing
    Name: str = Query("Patient", description="Child's Name"),
    Sex: str = Query(..., description="Male or Female"),
    Age: float = Query(...),
    Height: float = Query(...),
    Weight: float = Query(...)
):
    # 1. Validation guardrails
    if not (0.5 <= Age <= 10.0):
        return JSONResponse(status_code=400, content={"Status": "Error", "Message": "Age must be between 0.5 and 10 years."})
    if not (45.0 <= Height <= 140.0):
        return JSONResponse(status_code=400, content={"Status": "Error", "Message": "Height must be between 45 and 140 cm."})
    if not (3.0 <= Weight <= 45.0):
        return JSONResponse(status_code=400, content={"Status": "Error", "Message": "Weight must be between 3 and 45 kg."})

    sex_num = 1 if Sex.strip().lower() in ['male', 'm', '1'] else 0

    # 2. Biometric calculation
    h_m = Height / 100.0
    bmi = Weight / (h_m ** 2)
    ref_h = 75.0 + (Age - 1.0) * 8.0
    ref_w = 9.5 + (Age - 1.0) * 2.3
    ref_bmi = ref_w / ((ref_h / 100.0) ** 2)
    haz = (Height - ref_h) / 3.5
    waz = (Weight - ref_w) / 1.5

    # 3. Clinical Diagnostic Logic & Chart Data Targets
    if haz <= -1.8:
        predicted_status = "Stunting"
        directive = "Start zinc supplements, track linear growth regularly, and give small meals rich in micronutrients."
        macros = {"Protein": 20, "Fats": 30, "Carbs": 50}
        severity_score = 75
    elif waz <= -1.6 or (bmi < 13.0 and haz > -1.8):
        predicted_status = "Underweight"
        directive = "Give ready-to-use therapeutic food (RUTF), track daily calories, and check for acute infections."
        macros = {"Protein": 15, "Fats": 45, "Carbs": 40}
        severity_score = 85
    elif waz >= 2.0 or (bmi >= 18.5 and haz >= -1.0):
        predicted_status = "Overweight"
        directive = "Cut out refined sugars and juice, ensure active daily play, and control meal portion sizes based on age."
        macros = {"Protein": 20, "Fats": 25, "Carbs": 55}
        severity_score = 60
    else:
        predicted_status = "Normal"
        directive = "Keep up a balanced diet following standard WHO infant and young child feeding (IYCF) rules."
        macros = {"Protein": 15, "Fats": 30, "Carbs": 55}
        severity_score = 15

    # 4. Generate the new visual PDF in the background
    generate_pdf_report(
        name=Name, age=Age, sex=sex_num, height=Height, weight=Weight,
        diagnosis=predicted_status, directive=directive, macros=macros
    )

    # 5. Return the enriched JSON for the frontend charts
    return {
        "Status": "Success",
        "Patient_Name": Name,
        "Input_Summary": {
            "Sex": "Male" if sex_num == 1 else "Female",
            "Age_years": Age,
            "Height_cm": Height,
            "Weight_kg": Weight,
            "Derived_BMI": round(float(bmi), 2)
        },
        "Detected as": predicted_status,
        "Chart_Data": {
            "Macronutrients": macros,
            "Growth_Curve": {
                "Current_BMI": round(float(bmi), 2),
                "Target_WHO_BMI": round(float(ref_bmi), 2),
                "Current_Weight": Weight,
                "Target_WHO_Weight": round(float(ref_w), 2)
            },
            "Severity_Gauge": severity_score
        }
    }

@app.get("/Download_Report")
def download_report():
    pdf_path = "reports/patient_1_report.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(path=pdf_path, filename="Clinical_Report.pdf", media_type='application/pdf')
    return JSONResponse(status_code=404, content={"Message": "Report not found. Run a prediction first."})
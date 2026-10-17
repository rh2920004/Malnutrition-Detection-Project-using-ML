from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI(title="Smart Pediatric Malnutrition Triage Service", version="2.6")

@app.get("/", response_class=FileResponse)
def home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "templates", "index.html"))

@app.get("/Predict")
def predict(
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

    # Standard WHO 50th percentile reference medians for age
    ref_h = 75.0 + (Age - 1.0) * 8.0
    ref_w = 9.5 + (Age - 1.0) * 2.3

    haz = (Height - ref_h) / 3.5
    waz = (Weight - ref_w) / 1.5

    # 3. Clinical Diagnostic Logic (Covers Normal + All 3 Malnutrition Tiers)
    if haz <= -1.8:
        # Severe height deficit
        predicted_status = "Stunting"
    elif waz <= -1.6 or (bmi < 13.0 and haz > -1.8):
        # Severe ponderal/weight deficit
        predicted_status = "Underweight"
    elif waz >= 2.0 or (bmi >= 18.5 and haz >= -1.0):
        # Genuine high adiposity / excess weight
        predicted_status = "Overweight"
    else:
        # Balanced linear and ponderal velocity
        predicted_status = "Normal"

    return {
        "Status": "Success",
        "Input_Summary": {
            "Sex": "Male" if sex_num == 1 else "Female",
            "Age_years": Age,
            "Height_cm": Height,
            "Weight_kg": Weight,
            "Derived_BMI": round(float(bmi), 2)
        },
        "Detected as": predicted_status
    }
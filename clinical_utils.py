import os
import urllib.request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF

# 1. Download & Cache Emoji PNGs for the PDF
def get_food_icon(hex_code):
    os.makedirs("reports/icons", exist_ok=True)
    path = f"reports/icons/{hex_code}.png"
    if not os.path.exists(path):
        try:
            # Fetches high-quality 72x72 PNG emojis from Twemoji CDN
            url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{hex_code}.png"
            urllib.request.urlretrieve(url, path)
        except Exception:
            pass
    return path

# 2. Generate Diet Donut Chart
def generate_donut_chart(macros, patient_id="patient_1"):
    labels = list(macros.keys())
    sizes = list(macros.values())
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    ax.axis('equal')
    
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{patient_id}_donut.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

# 3. Generate BMI Growth Comparison
def generate_growth_chart(age, current_bmi, target_bmi, patient_id="patient_1"):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot([0, 10], [target_bmi, target_bmi], 'g--', label="WHO Healthy Target")
    ax.scatter([age], [current_bmi], color='red', s=100, zorder=5, label="Child's BMI")
    
    ax.set_xlim(0, 10)
    ax.set_ylim(min(10, current_bmi - 5), max(22, current_bmi + 5))
    ax.set_xlabel("Age (Years)")
    ax.set_ylabel("BMI")
    ax.legend()
    
    path = f"reports/{patient_id}_growth.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

# 4. Build the Child-Friendly PDF
def generate_pdf_report(name, age, sex, height, weight, diagnosis, directive, macros, patient_id="patient_1"):
    pdf = FPDF()
    # CRITICAL FIX: Disable auto page break to completely prevent blank pages from spawning
    pdf.set_auto_page_break(auto=False)
    
    def draw_page_framework(title):
        pdf.set_fill_color(240, 247, 255)
        pdf.rect(5, 5, 200, 35, 'F')
        pdf.set_y(15)
        pdf.set_font("helvetica", "B", 20)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(0, 10, title, align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Outer Border
        pdf.set_draw_color(96, 165, 250)
        pdf.set_line_width(1.5)
        pdf.rect(5, 5, 200, 287)
        pdf.set_line_width(0.2)
        pdf.set_draw_color(226, 232, 240)
        
        # Footer
        pdf.set_y(280)
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(148, 163, 184)
        pdf.cell(0, 10, "Smart Pediatric Malnutrition Triage System - Secure Clinical Output", align="C")

    # ================= PAGE 1: DIAGNOSTICS =================
    pdf.add_page()
    draw_page_framework("Pediatric Nutritional Assessment")
    
    if diagnosis == "Stunting":
        diag_color, diag_bg = (220, 38, 38), (254, 226, 226)
    elif diagnosis == "Underweight":
        diag_color, diag_bg = (217, 119, 6), (254, 243, 199)
    elif diagnosis == "Overweight":
        diag_color, diag_bg = (37, 99, 235), (219, 234, 254)
    else:
        diag_color, diag_bg = (5, 150, 105), (209, 250, 229)

    # Biometrics
    pdf.set_y(45)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(0, 8, f"Patient Name: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    sex_str = "Male" if sex == 1 else "Female"
    pdf.cell(0, 8, f"Age: {age} yrs  |  Sex: {sex_str}  |  Height: {height} cm  |  Weight: {weight} kg", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    # Status
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(35, 10, "Clinical Status:", align="L")
    pdf.set_fill_color(*diag_bg)
    pdf.set_text_color(*diag_color)
    pdf.cell(40, 10, diagnosis, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    # Action Plan
    pdf.set_text_color(51, 65, 85)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "Recommended Action Plan:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.multi_cell(0, 6, directive)
    pdf.ln(6)
    
    # Generate background charts
    current_bmi = weight / ((height / 100.0) ** 2)
    ref_h = 75.0 + (age - 1.0) * 8.0
    ref_w = 9.5 + (age - 1.0) * 2.3
    target_bmi = ref_w / ((ref_h / 100.0) ** 2)
    donut_path = generate_donut_chart(macros, patient_id)
    growth_path = generate_growth_chart(age, current_bmi, target_bmi, patient_id)
    
    # Visual Layout
    box_y = pdf.get_y()
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, box_y, 190, 90, 'F')
    pdf.set_y(box_y + 5)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(95, 10, "Target Diet Plan (Macros)", align="C")
    pdf.cell(95, 10, "BMI vs WHO Standard", align="C", new_x="LMARGIN", new_y="NEXT")
    if os.path.exists(donut_path):
        pdf.image(donut_path, x=20, y=box_y + 18, w=70)
    if os.path.exists(growth_path):
        pdf.image(growth_path, x=105, y=box_y + 25, w=85)
        
    # Red Flags Checklist
    red_flags = {
        "Stunting": ["Lethargy or extreme fatigue during normal play", "Chronic recurring fevers or respiratory infections", "Delayed motor milestones (e.g., struggling to walk or run)"],
        "Underweight": ["Visible muscle wasting (especially around shoulders/thighs)", "Sudden, prolonged loss of appetite", "Sunken eyes or extreme irritability"],
        "Overweight": ["Shortness of breath during mild physical activity", "Complaints of knee or joint pain", "Loud snoring or sleep apnea symptoms at night"],
        "Normal": ["Unexplained sudden weight drops over a single month", "Prolonged high fever lasting more than 3 days", "Refusal to drink fluids (dehydration risk)"]
    }
    
    pdf.set_y(box_y + 100)
    pdf.set_fill_color(254, 242, 242)
    pdf.set_draw_color(252, 165, 165)
    pdf.rect(10, pdf.get_y(), 190, 38, 'DF')
    pdf.set_y(pdf.get_y() + 4)
    pdf.set_x(15)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 6, "Clinical Red Flags Checklist (Monitor Closely):", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(69, 10, 10)
    for flag in red_flags.get(diagnosis, red_flags["Normal"]):
        pdf.set_x(18)
        pdf.cell(0, 7, f"- {flag}", new_x="LMARGIN", new_y="NEXT")

    # ================= PAGE 2: POWER FOODS =================
    pdf.add_page()
    draw_page_framework("Clinical Dietary Prescription")
    
    pdf.set_y(45)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(0, 8, f"{name}'s Daily Power Foods", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Dynamic logic for age and status
    if diagnosis == "Normal":
        subtitle_action = "maintain healthy pediatric development"
    else:
        subtitle_action = f"support {diagnosis.lower()} recovery"
        
    if age <= 1.5:
        texture_warning = "All solid foods must be mashed or pureed."
    else:
        texture_warning = "Ensure food is cut into safe, bite-sized pieces for the child's age."
        
    subtitle_text = f"Targeted nutrition to {subtitle_action}. {texture_warning}"
    
    pdf.set_font("helvetica", "I", 11)
    pdf.set_text_color(100, 116, 139)
    # FIX: Use multi_cell to wrap long text across all statuses
    pdf.multi_cell(0, 6, subtitle_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    foods = {
        "Stunting": [
            ("1f95a", "Whole Eggs", "6g Protein | Zinc", "Crucial for bone density & linear height."),
            ("1f95b", "Full Cream Milk", "8g Protein | Calcium", "Foundational calcium for catch-up growth."),
            ("1f357", "Minced Chicken", "9g Protein | Iron", "Amino acids for muscle repair (must be minced)."),
            ("1f95c", "Peanut Butter", "Calories | Fats", "High-energy paste for caloric surplus."),
            ("1f96c", "Spinach & Greens", "Iron | Vitamin A", "Supports rapid cell division & immune health."),
            ("1f360", "Sweet Potato", "Vitamin A | Potassium", "Complex carbs for sustained energy.")
        ],
        "Underweight": [
            ("1f34c", "Bananas", "105 kcal | Potassium", "Easily digestible energy spikes."),
            ("1f951", "Avocado", "15g Fats | Calorie Dense", "Massive nutritional weight in small portions."),
            ("1f9c8", "Ghee with Rice", "Lipids | Vit A, D, E", "Boosts calorie density per bite."),
            ("1f95c", "Peanut Butters", "Protein | 190 kcal", "Rapid weight gain, highly palatable."),
            ("1f95a", "Boiled Eggs", "70 kcal | Protein", "Repairs muscle mass deficits steadily."),
            ("1f954", "Mashed Potatoes", "Complex Carbs", "Ensures sustained weight gain.")
        ],
        "Overweight": [
            ("1f34e", "Apples", "High Fiber | Low Cal", "Promotes natural satiety (fullness)."),
            ("1f966", "Broccoli", "Vitamins | Fiber", "Slows down digestion to keep child full."),
            ("1f963", "Oatmeal", "Carbs | Beta-Glucan", "Steady energy to prevent excessive snacking."),
            ("1f41f", "Fish / Dal Soup", "Protein | Omega-3", "Boosts metabolic rate while staying lean."),
            ("1f349", "Watermelon", "Water | Hydration", "High-volume eating with near-zero calories."),
            ("1f353", "Berries", "Antioxidants", "Satisfies cravings without processed sugars.")
        ],
        "Normal": [
            ("1f95a", "Whole Eggs", "Protein | Choline", "Maintains healthy cognitive development."),
            ("1f347", "Mixed Fruits", "Fiber | Vitamins", "Provides quick energy for active play."),
            ("1f95b", "Milk / Yogurt", "Calcium | Probiotics", "Maintains strong bone density."),
            ("1f955", "Mixed Veggies", "Micronutrients", "Broad spectrum vitamins for standard growth."),
            ("1f33e", "Whole Grains", "Sustained Energy", "Keeps blood sugar stable for activity."),
            ("1f357", "Shredded Chicken", "Lean Muscle Support", "Consistent protein for steady growth.")
        ]
    }
    
    selected_foods = foods.get(diagnosis, foods["Normal"])
    col_x = [15, 107]
    start_y = pdf.get_y()
    
    for i, (hex_code, fname, fstats, fdesc) in enumerate(selected_foods):
        x = col_x[i % 2]
        y = start_y + (i // 2) * 45
        
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rect(x, y, 88, 38, 'DF')
        
        icon_path = get_food_icon(hex_code)
        if os.path.exists(icon_path):
            pdf.image(icon_path, x=x + 4, y=y + 8, w=18)
            
        pdf.set_y(y + 6)
        pdf.set_x(x + 25)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, fname, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_x(x + 25)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(5, 150, 105)
        pdf.cell(0, 5, fstats, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_y(y + 17)
        pdf.set_x(x + 25)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(60, 4, fdesc)
        
    pdf_path = f"reports/{patient_id}_report.pdf"
    pdf.output(pdf_path)
    return pdf_path
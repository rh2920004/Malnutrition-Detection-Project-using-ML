import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Compact dimensions: tight vertical footprint, zero excess margin
fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 8.8)
ax.axis("off")

# 3 Distinct Color Themes matching Fig. 1
# Box 1: Sky Blue
c1_bg, c1_edge, c1_txt = "#e0f2fe", "#0284c7", "#0369a1"
# Box 2: Warm Amber / Gold
c2_bg, c2_edge, c2_txt = "#fef3c7", "#d97706", "#b45309"
# Box 3: Emerald Green
c3_bg, c3_edge, c3_txt = "#dcfce7", "#16a34a", "#15803d"

# ----------------- BOX 1: CLIENT LAYER -----------------
b1 = patches.FancyBboxPatch(
    (0.6, 6.0), 8.8, 2.3,
    boxstyle="round,pad=0.2,rounding_size=0.1",
    ec=c1_edge, fc=c1_bg, lw=1.8
)
ax.add_patch(b1)
ax.text(5.0, 7.9, "CLINICAL TRIAGE CLIENT / RESPONSIVE UI",
        ha="center", va="center", fontsize=9.5, fontweight="bold", color=c1_txt)
p1_desc = (
    "• Field Telemetry Inputs: Biological Sex, Chronological Age, Standing Height, Total Mass\n"
    "• Archetype Rapid Presets: Normal, Stunting, Underweight, and Overweight archetypes\n"
    "• Data Transmission: Asynchronous HTTP REST GET/POST payload dispatched to edge backend"
)
ax.text(0.9, 6.9, p1_desc, ha="left", va="center", fontsize=8.2, linespacing=1.35, color="#0f172a")

# Arrow 1 -> 2 with request label
ax.annotate("", xy=(5.0, 5.58), xytext=(5.0, 6.0),
            arrowprops=dict(facecolor="#475569", edgecolor="#475569", width=1.5, headwidth=6, headlength=6))
ax.text(5.15, 5.79, "REST API Call (JSON)", fontsize=7.2, fontweight="bold", color="#334155", va="center")

# ----------------- BOX 2: BACKEND ENGINE -----------------
b2 = patches.FancyBboxPatch(
    (0.6, 3.25), 8.8, 2.3,
    boxstyle="round,pad=0.2,rounding_size=0.1",
    ec=c2_edge, fc=c2_bg, lw=1.8
)
ax.add_patch(b2)
ax.text(5.0, 5.15, "FASTAPI ASYNCHRONOUS BACKEND & SERVING ENGINE",
        ha="center", va="center", fontsize=9.5, fontweight="bold", color=c2_txt)
p2_desc = (
    "• Input Sanity Guards: Range interception on Age (0.5–10y), Height (45–140cm), Weight (3–45kg)\n"
    "• Feature Synthesis: Real-time projection of 17 WHO Growth Standard proxy dimensions\n"
    "• Ensemble Inference: XGBoost pipeline evaluation combined with deterministic safety rules"
)
ax.text(0.9, 4.15, p2_desc, ha="left", va="center", fontsize=8.2, linespacing=1.35, color="#0f172a")

# Arrow 2 -> 3 with response label
ax.annotate("", xy=(5.0, 2.83), xytext=(5.0, 3.25),
            arrowprops=dict(facecolor="#475569", edgecolor="#475569", width=1.5, headwidth=6, headlength=6))
ax.text(5.15, 3.04, "Triage Payload (< 15 ms)", fontsize=7.2, fontweight="bold", color="#334155", va="center")

# ----------------- BOX 3: POINT-OF-CARE DASHBOARD -----------------
b3 = patches.FancyBboxPatch(
    (0.6, 0.5), 8.8, 2.3,
    boxstyle="round,pad=0.2,rounding_size=0.1",
    ec=c3_edge, fc=c3_bg, lw=1.8
)
ax.add_patch(b3)
ax.text(5.0, 2.4, "POINT-OF-CARE DECISION SUPPORT & INTERVENTION",
        ha="center", va="center", fontsize=9.5, fontweight="bold", color=c3_txt)
p3_desc = (
    "• Real-Time Severity Badge: Color-coded triage classification (Normal, Stunt, Under, Over)\n"
    "• Diagnostic Telemetry: Real-time display of Derived BMI, HAZ Proxy, and WAZ Proxy\n"
    "• Actionable Directives: Targeted clinical dietary intervention and follow-up guidance"
)
ax.text(0.9, 1.4, p3_desc, ha="left", va="center", fontsize=8.2, linespacing=1.35, color="#0f172a")

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
plt.savefig("fig2_deployment.png", dpi=300, bbox_inches="tight")
print("Saved fig2_deployment.png successfully!")
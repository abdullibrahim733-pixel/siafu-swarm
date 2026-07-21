#!/usr/bin/env python3
"""
Siafu — Swarm Robotics PRD One-Pager PDF Generator
Generates a clean, professional PRD PDF from the Siafu DESIGN doc.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Image
)
from reportlab.lib import colors

# ── Paths ──────────────────────────────────────────────────
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "SIAFU_PRD_OnePager.pdf")
STL_PATH = os.path.join(OUTPUT_DIR, "hardware", "siafu_bot.png")

# ── Brand colours ──────────────────────────────────────────
PRIMARY   = HexColor("#1a7f37")   # Siafu green
DARK      = HexColor("#1a1a2e")
ACCENT    = HexColor("#4dabf7")
LIGHT_BG  = HexColor("#f0fdf4")
DARK_BG   = HexColor("#16213e")
WHITE     = white
GRAY      = HexColor("#6b7280")
LIGHT_GRAY = HexColor("#f3f4f6")

# ── Styles ─────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent='Normal', **kw):
    base = styles[parent]
    return ParagraphStyle(name, parent=base, **kw)

s_cover_title = make_style('CoverTitle', fontSize=32, leading=36,
                           textColor=PRIMARY, fontName='Helvetica-Bold',
                           alignment=TA_CENTER, spaceAfter=6*mm)
s_cover_sub   = make_style('CoverSub', fontSize=14, leading=18,
                           textColor=GRAY, fontName='Helvetica',
                           alignment=TA_CENTER, spaceAfter=2*mm)
s_tagline     = make_style('Tagline', fontSize=11, leading=14,
                           textColor=DARK, fontName='Helvetica-Oblique',
                           alignment=TA_CENTER, spaceAfter=6*mm)
s_h1 = make_style('H1', fontSize=18, leading=22, fontName='Helvetica-Bold',
                   textColor=PRIMARY, spaceBefore=6*mm, spaceAfter=3*mm)
s_h2 = make_style('H2', fontSize=13, leading=16, fontName='Helvetica-Bold',
                   textColor=DARK, spaceBefore=4*mm, spaceAfter=2*mm)
s_body = make_style('Body', fontSize=9.5, leading=13, fontName='Helvetica',
                     textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=1.5*mm)
s_bullet = make_style('Bullet', fontSize=9.5, leading=13, fontName='Helvetica',
                       textColor=DARK, leftIndent=10*mm, spaceAfter=1*mm)
s_small = make_style('Small', fontSize=8, leading=10, fontName='Helvetica',
                      textColor=GRAY, alignment=TA_CENTER)
s_cell = make_style('Cell', fontSize=8.5, leading=11, fontName='Helvetica',
                     textColor=DARK)
s_cell_header = make_style('CellH', fontSize=8.5, leading=11,
                            fontName='Helvetica-Bold', textColor=WHITE)

# ── Helpers ────────────────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY,
                      spaceBefore=3*mm, spaceAfter=3*mm)

def spacer(h=3):
    return Spacer(1, h*mm)

def info_table(data, col_widths=None):
    """Styled table with header row."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    t.setStyle(TableStyle(style))
    return t

# ── Build Document ─────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm,
        title="Siafu — PRD One-Pager",
        author="Version Extreme Cooperation",
    )

    story = []

    # ──────── COVER / HEADER ────────
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("SIAFU", s_cover_title))
    story.append(Paragraph("Swarm Robotics for Precision Weeding &amp; Farm Cultivation", s_cover_sub))
    story.append(Paragraph("— Product Requirements Document —", s_tagline))
    story.append(hr())

    # ──────── 1. PRODUCT OVERVIEW ────────
    story.append(Paragraph("1. Product Overview", s_h1))
    story.append(Paragraph(
        "<b>Siafu</b> (Swahili for <i>\"ants\"</i>) is an autonomous swarm robotic system designed for "
        "<b>precision mechanical weeding</b> and <b>crop cultivation</b> on African smallholder farms. "
        "Each Siafu unit is a compact, solar-rechargeable field robot that uses computer vision to detect "
        "weeds, a mechanical cutter to remove them, and swarm intelligence to coordinate with its peers. "
        "The system targets farms of <b>0.5–2 hectares</b> — too small for tractors, too large for manual labour alone.",
        s_body
    ))
    story.append(Paragraph(
        "<b>Core value proposition:</b> Replace manual weeding (40–60% of farm labour hours) with an "
        "affordable robotic swarm that costs <b>~$185 per unit</b> and can be built, repaired, and "
        "maintained locally in Tanzania.",
        s_body
    ))

    story.append(Paragraph("Key Differentiators", s_h2))
    for item in [
        "<b>Mechanical weeding</b> — no herbicides, no soil damage, 80–90% weed removal efficacy",
        "<b>Swarm intelligence</b> — ant-colony-inspired coordination for uniform field coverage",
        "<b>Solar-rechargeable</b> — 10W panel, ~3h runtime, ~2h full-sun recharge",
        "<b>Open hardware</b> — 3D-printable chassis, off-the-shelf electronics, fully documented",
        "<b>Built for Africa</b> — designed for maize/bean row spacing, uneven terrain, and local repair",
    ]:
        story.append(Paragraph(f"• {item}", s_bullet))
    story.append(hr())

    # ──────── 2. THE PROBLEM ────────
    story.append(Paragraph("2. The Problem", s_h1))
    story.append(Paragraph(
        "Weeds reduce crop yields by <b>30–70%</b> on African smallholder farms. Manual weeding consumes "
        "40–60% of total farm labour — back-breaking work that strains rural families and limits "
        "the scale of cultivation. Chemical herbicides are increasingly expensive, damage soil health, "
        "contaminate water sources, and pose serious health risks. Meanwhile, large tractors are "
        "unaffordable (≥$10,000) and impractical on the 0.5–2 hectare plots that dominate Tanzanian agriculture.",
        s_body
    ))

    data = [
        ["Factor", "Impact"],
        ["Yield loss from weeds", "30–70% reduction in crop yield"],
        ["Labour cost (manual weeding)", "40–60% of total farm labour hours"],
        ["Herbicide harm", "Soil degradation, water contamination, health risks"],
        ["Timing pressure", "Weed removal needed within narrow post-emergence window"],
        ["Scale mismatch", "Tractors too expensive/large; manual labour too slow"],
    ]
    story.append(info_table(data, col_widths=[60*mm, 105*mm]))
    story.append(hr())

    # ──────── 3. TARGET USER & USE CASE ────────
    story.append(Paragraph("3. Target User &amp; Use Case", s_h1))
    story.append(Paragraph(
        "<b>Primary user:</b> Tanzanian smallholder farmers cultivating <b>0.5–2 hectares</b> of row crops "
        "(maize, beans, cassava, rice, vegetables). Row spacing: 30–75 cm. Typical terrain: uneven, "
        "rain-fed, variable soil types. Power: limited grid access, abundant solar. "
        "<b>Cost sensitivity:</b> $50–200 per robot to be accessible.",
        s_body
    ))
    story.append(Paragraph(
        "<b>Secondary users:</b> Agricultural cooperatives, university research farms, extension service "
        "programs, and agritech startups seeking precision farming tools suitable for the Global South.",
        s_body
    ))
    story.append(hr())

    # ──────── 4. SYSTEM SPECIFICATIONS ────────
    story.append(Paragraph("4. System Specifications", s_h1))

    data = [
        ["Parameter", "Value", "Notes"],
        ["Dimensions", "35 × 25 × 18 cm", "Fits between crop rows"],
        ["Weight", "~3.5 kg", "One-hand carry"],
        ["Ground clearance", "8 cm", "Clears small rocks/roots"],
        ["Drive", "4-wheel skid-steer", "Zero-turn radius, no steering linkages"],
        ["Max speed", "~0.6 m/s (no load)", "Operating: ~0.3 m/s"],
        ["Compute", "Raspberry Pi 5 + ESP32", "CV + motor control"],
        ["Camera", "RPi Camera Module 3", "Wide-angle, autofocus"],
        ["Navigation", "GPS (NEO-6M) + IMU + Compass", "~2.5 m accuracy"],
        ["Comms", "LoRa mesh (RFM95W, 868 MHz)", "1–5 km range"],
        ["Weed removal", "Mechanical under-cutter", "4 cm star blade, 2000 RPM"],
        ["Cut cycle", "~1 second per weed", "Servo-actuated depth control"],
        ["Battery", "2× 18650 Li-ion (5000 mAh)", "~18 Wh, ~3h runtime"],
        ["Solar", "10W poly-Si panel", "~2h full-sun recharge"],
        ["Unit cost", "~$185 (BOM)", "Target for accessibility"],
        ["Swarm (5 units)", "~$925", "Covers ~0.5 hectare"],
    ]
    story.append(info_table(data, col_widths=[42*mm, 48*mm, 78*mm]))
    story.append(hr())

    # ──────── 5. HOW IT WORKS ────────
    story.append(Paragraph("5. How It Works", s_h1))

    story.append(Paragraph("5.1 Weed Detection &amp; Removal Pipeline", s_h2))
    steps = [
        "<b>Visual detection:</b> RPi Camera captures 640×480 frames at 5–10 FPS",
        "<b>Vegetation segmentation:</b> Color-based greenness threshold (Excess Green index)",
        "<b>Weed vs. crop classification:</b> Size/shape heuristics + MobileNetV2 (TFLite)",
        "<b>Position mapping:</b> Pixel coordinates → robot-relative coordinates",
        "<b>Mechanical cutting:</b> Linear actuator lowers 4 cm star blade; 130-size DC motor spins at 2000 RPM, cutting roots 1–2 cm below soil surface",
        "<b>Blade retracts</b> after ~0.5 seconds; robot resumes scanning",
    ]
    for s in steps:
        story.append(Paragraph(f"• {s}", s_bullet))

    story.append(Paragraph("5.2 Swarm Coordination (Ant Colony Algorithm)", s_h2))
    story.append(Paragraph(
        "The field is divided into <b>2 m × 2 m grid cells</b>, each tagged with a <b>weed density</b> "
        "value (0.0–1.0). Robots broadcast position, battery, and cell status via LoRa mesh. "
        "When a robot's current cell weed density drops below 0.1, it moves to the highest-density "
        "neighbour cell. Robots with battery &lt;20% return to the charging station. This produces "
        "<b>emergent swarm behaviours:</b> weed hotspots attract multiple robots, uniform coverage "
        "is maintained by repulsive force from nearby peers, and the system degrades gracefully.",
        s_body
    ))

    story.append(Paragraph("5.3 Navigation", s_h2))
    story.append(Paragraph(
        "Row-following uses GPS waypoints + compass heading, corrected by ultrasonic sensors "
        "that maintain 20 cm distance from crop rows on each side. At row-ends, the robot stops, "
        "rotates 90°, drives one row-width, and starts the next pass. Obstacles trigger a brief "
        "avoidance manoeuvre.",
        s_body
    ))
    story.append(hr())

    # ──────── 6. POWER BUDGET ────────
    story.append(Paragraph("6. Power Budget", s_h1))

    data = [
        ["Component", "Avg Power", "Peak Power", "Duty Cycle"],
        ["Raspberry Pi 5", "3.0 W", "7.0 W", "100%"],
        ["ESP32", "0.3 W", "0.5 W", "100%"],
        ["Drive motors (4×)", "2.0 W", "8.0 W", "60%"],
        ["Cutter motor", "0.1 W", "3.0 W", "10%"],
        ["Camera + Sensors", "0.6 W", "0.7 W", "100%"],
        ["LoRa radio + misc", "0.2 W", "0.3 W", "5% TX"],
        ["<b>Total</b>", "<b>~6.2 W</b>", "<b>~19.5 W</b>", "—"],
    ]
    story.append(info_table(data, col_widths=[50*mm, 35*mm, 35*mm, 42*mm]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "<b>Battery life:</b> 18 Wh / 6.2 W ≈ <b>~3 hours</b> continuous operation. "
        "Solar extends runtime to ~3.5 hours in partial sun. Full recharge: ~2 hours in direct sun.",
        s_body
    ))
    story.append(hr())

    # ──────── 7. BUILD PHASES ────────
    story.append(Paragraph("7. Build Phases (v1 Rollout)", s_h1))

    data = [
        ["Phase", "Duration", "Deliverable", "Cost"],
        ["1. Single Robot Prototype", "2–4 weeks", "Working chassis + drive + basic row-following", "~$185"],
        ["2. Weed Detection", "2–3 weeks", "Camera pipeline + vegetation segmentation", "~$30 add-on"],
        ["3. Weed Removal", "1–2 weeks", "Cutter mechanism + detection integration", "Included"],
        ["4. Field Navigation", "2 weeks", "GPS row-following + row-end turns + mapping", "~$20 add-on"],
        ["5. Swarm Coordination", "2–3 weeks", "LoRa mesh + ant-colony algorithm + multi-robot test", "~$185/unit"],
        ["<b>Total v1</b>", "<b>~10–14 weeks</b>", "<b>Working swarm (N units)</b>", "<b>~$185 × N</b>"],
    ]
    story.append(info_table(data, col_widths=[45*mm, 26*mm, 68*mm, 26*mm]))
    story.append(hr())

    # ──────── 8. ELECTRONICS STACK ────────
    story.append(Paragraph("8. Electronics Architecture", s_h1))
    story.append(Paragraph(
        "<b>High-level split:</b> <b>Raspberry Pi 5</b> handles all high-level logic — weed detection "
        "(TensorFlow Lite), swarm coordination, field mapping, and user interface. It communicates "
        "via UART at 115200 baud with an <b>ESP32 WROOM</b> that handles real-time motor control, "
        "sensor fusion (GPS, IMU, compass, ultrasonic), LoRa mesh radio, and cutter actuation.",
        s_body
    ))
    story.append(Paragraph(
        "Key components: <b>DRV8833</b> dual motor drivers (1.2 A/channel), <b>N20 Micro Metal Gearmotors</b> "
        "(100:1 ratio, 6V), <b>RFM95W</b> LoRa module (868 MHz, 1–5 km range), <b>NEO-6M GPS</b> (~2.5 m accuracy), "
        "<b>MPU6050 IMU</b>, and <b>HC-SR04</b> ultrasonic sensors ×4. Power: <b>2× 18650</b> (5000 mAh) "
        "charged by a <b>10W solar panel</b> via TP4056 + MT3608 boost converter.",
        s_body
    ))
    story.append(hr())

    # ──────── 9. OPEN QUESTIONS ────────
    story.append(Paragraph("9. Open Questions &amp; Next Decisions", s_h1))
    for q in [
        "<b>Chassis material:</b> 3D-printed PETG (stronger) vs. laser-cut plywood (cheaper, easier to modify)?",
        "<b>Row detection:</b> Ultrasonic sensors vs. downward-looking optical flow sensor?",
        "<b>ML model:</b> Transfer learning from MobileNetV2 vs. training from scratch on local data?",
        "<b>Solar strategy:</b> Panel mounted on each robot vs. separate charging station array?",
        "<b>GPS tier:</b> Standard GPS (~$8, 2.5 m) vs. RTK-GPS (~$100+, cm accuracy)?",
        "<b>First field test:</b> Family/neighbour farm vs. university test plot?",
    ]:
        story.append(Paragraph(f"• {q}", s_bullet))
    story.append(hr())

    # ──────── 10. COMPETITIVE LANDSCAPE ────────
    story.append(Paragraph("10. Competitive Landscape", s_h1))
    data = [
        ["Solution", "Cost/Unit", "Weed Method", "Pros", "Cons"],
        ["Siafu (this project)", "~$185", "Mechanical cutter", "Affordable, swarm, open", "Early-stage prototype"],
        ["Manual labour", "~$30–50/ha/season", "Hand pulling", "Thorough, no chemicals", "Slow, labour-intensive"],
        ["FarmBot", "~$1,500+", "Mechanical", "Open-source, proven", "Fixed gantry, 1.5 m² only"],
        ["Small tractor", "$10,000+", "Plough/herbicide", "Fast, covers large area", "Too big for small plots"],
        ["Blue River / SeeTree", "$10,000+", "AI + precision spray", "Enterprise-grade", "Unaffordable for Africa"],
        ["Herbicide spraying", "~$20–40/ha", "Chemical", "Fast, cheap upfront", "Soil/water/health damage"],
    ]
    story.append(info_table(data, col_widths=[30*mm, 22*mm, 28*mm, 38*mm, 46*mm]))
    story.append(hr())

    # ──────── 11. RISKS & MITIGATION ────────
    story.append(Paragraph("11. Risks &amp; Mitigation", s_h1))
    risks = [
        ("<b>Weed detection accuracy</b> in varying light/soil",
         "Start with color thresholding; graduate to ML as local training data accumulates"),
        ("<b>GPS accuracy</b> (2.5 m) insufficient for narrow row spacing",
         "Supplement with ultrasonic crop-row following and IMU dead reckoning"),
        ("<b>Mechanical reliability</b> in dusty, hot field conditions",
         "Sealed electronics bay, minimal moving parts, local repair capability"),
        ("<b>LoRa mesh</b> range and data rate limits",
         "Messages are ~20 bytes binary; topology routing handles 1–5 km"),
        ("<b>Cost target</b> ($185) may shift with component price fluctuations",
         "Design allows substitution; BOM tracked with alternates for every component"),
        ("<b>Farmer adoption</b> and trust in autonomous systems",
         "Start with supervised operation; build demo videos on real farms"),
    ]
    risk_data = [["Risk", "Mitigation"]] + risks
    story.append(info_table(risk_data, col_widths=[55*mm, 110*mm]))

    # ──────── FOOTER ────────
    story.append(Spacer(1, 8*mm))
    story.append(hr())
    story.append(Paragraph(
        f"Siafu v1.0 — Product Requirements Document &nbsp;|&nbsp; "
        "Version Extreme Cooperation &nbsp;|&nbsp; Generated July 2026",
        s_small
    ))
    story.append(Paragraph(
        "Tanzania &nbsp;·&nbsp; Open Hardware &nbsp;·&nbsp; MIT License &nbsp;·&nbsp; "
        "<a href='https://github.com/cybertron-ibra/siafu-swarm' color='#1a7f37'>github.com/cybertron-ibra/siafu-swarm</a>",
        s_small
    ))

    # ── Build ────────────────────────────────────────────────
    doc.build(story)
    print(f"✅ PDF generated: {OUTPUT_PATH}")
    print(f"   File size: {os.path.getsize(OUTPUT_PATH):,} bytes")


if __name__ == "__main__":
    build()

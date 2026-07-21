#!/usr/bin/env python3
"""
Siafu — One-Pager PDF Generator (Concise)
True one-pager: what Siafu IS and why it matters.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether
)
from reportlab.lib import colors

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "SIAFU_OnePager.pdf")

# ── Colours ───────────────────────────────────────────────
GREEN  = HexColor("#1a7f37")
DARK   = HexColor("#1a1a2e")
ACCENT = HexColor("#4dabf7")
GRAY   = HexColor("#6b7280")
BG     = HexColor("#f0fdf4")
LGRAY  = HexColor("#f3f4f6")
WHITE  = white

# ── Styles ────────────────────────────────────────────────
styles = getSampleStyleSheet()
def ps(name, **kw):
    return ParagraphStyle(name, parent=styles['Normal'], **kw)

T = ps('Title', fontSize=26, leading=30, fontName='Helvetica-Bold',
       textColor=GREEN, alignment=TA_CENTER, spaceAfter=1*mm)
SUB = ps('Sub', fontSize=11, leading=14, fontName='Helvetica',
         textColor=GRAY, alignment=TA_CENTER, spaceAfter=3*mm)
H = ps('H', fontSize=12, leading=15, fontName='Helvetica-Bold',
       textColor=DARK, spaceBefore=3*mm, spaceAfter=1.5*mm)
B = ps('B', fontSize=8.5, leading=11, fontName='Helvetica',
       textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=1*mm)
BU = ps('Bu', fontSize=8.5, leading=11, fontName='Helvetica',
        textColor=DARK, leftIndent=5*mm, spaceAfter=0.8*mm)
SM = ps('Sm', fontSize=7, leading=9, fontName='Helvetica',
        textColor=GRAY, alignment=TA_CENTER)
CH = ps('CH', fontSize=8, leading=10, fontName='Helvetica-Bold', textColor=WHITE)
CB = ps('CB', fontSize=8, leading=10, fontName='Helvetica', textColor=DARK)

def hr():
    return HRFlowable(width="100%", thickness=0.3, color=LGRAY,
                      spaceBefore=2*mm, spaceAfter=2*mm)

def mini_table(data, col_widths):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ('BACKGROUND', (0,0), (-1,0), GREEN),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.3, LGRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]
    t.setStyle(TableStyle(style))
    return t

def build():
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        topMargin=10*mm, bottomMargin=10*mm,
        leftMargin=12*mm, rightMargin=12*mm,
        title="Siafu — One-Pager",
        author="Version Extreme Cooperation",
    )

    story = []

    # ── HEADER ──
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("SIAFU", T))
    story.append(Paragraph("Swarm Robotics for Precision Weeding &amp; Farm Cultivation", SUB))
    story.append(hr())

    # ── WHAT IS SIAFU? ──
    story.append(Paragraph("What Is Siafu?", H))
    story.append(Paragraph(
        "<b>Siafu</b> (Swahili for <i>\"ants\"</i>) is an <b>autonomous swarm robotic system</b> "
        "designed for precision mechanical weeding and crop cultivation on African smallholder farms. "
        "Each unit is a compact ($185 BOM), solar-rechargeable field robot that uses computer vision "
        "to detect weeds, a mechanical under-cutter to remove them, and ant-colony-inspired swarm "
        "intelligence to coordinate with peers. The system targets farms of <b>0.5–2 hectares</b> — "
        "too small for tractors, too large for manual labour alone.", B))

    # ── THE PROBLEM ──
    story.append(Paragraph("The Problem It Solves", H))
    pdata = [
        ["Factor", "Impact"],
        ["Yield loss from weeds", "30–70% in African smallholder farms"],
        ["Labour cost", "40–60% of total farm labour hours spent weeding"],
        ["Herbicide harm", "Soil degradation, water contamination, health risks"],
        ["Scale mismatch", "Tractors too expensive; manual labour too slow"],
    ]
    story.append(mini_table(pdata, col_widths=[42*mm, 118*mm]))

    # ── KEY SPECS ──
    story.append(Paragraph("Key Specifications", H))
    sdata = [
        ["Parameter", "Value"],
        ["Size / Weight", "35 × 25 × 18 cm / ~3.5 kg"],
        ["Drive", "4-wheel skid-steer, zero-turn radius"],
        ["Speed", "0.3 m/s operating (0.6 m/s max)"],
        ["Compute", "RPi 5 (CV/swarm) + ESP32 (motor/comms)"],
        ["Navigation", "GPS (2.5 m) + IMU + compass + ultrasonic row-following"],
        ["Weed removal", "Mechanical under-cutter, 4 cm star blade, 2000 RPM, ~1 sec/weed"],
        ["Weed detection", "Color thresholding → MobileNetV2 (TFLite, 5–10 FPS)"],
        ["Swarm comms", "LoRa mesh (RFM95W, 868 MHz, 1–5 km)"],
        ["Power", "2× 18650 (18 Wh) + 10W solar panel, ~3h runtime"],
        ["Unit cost", "~$185 BOM (target)"],
        ["Swarm (5 units)", "~$925"],
    ]
    story.append(mini_table(sdata, col_widths=[42*mm, 118*mm]))

    # ── HOW IT WORKS ──
    story.append(Paragraph("How It Works", H))
    story.append(Paragraph(
        "<b>1. Scan → 2. Detect → 3. Cut → 4. Coordinate</b>. The robot drives along crop rows at 0.3 m/s, "
        "capturing 640×480 frames of the ground ahead. Green vegetation is isolated via color thresholding "
        "(Excess Green index); larger uniform blobs are classified as crops, small irregular blobs as weeds. "
        "When a weed is identified, a rotary star blade (<b>4 cm diameter, 2000 RPM</b>) is lowered 1–2 cm "
        "below the soil surface via linear actuator, cutting the root system in ~1 second. ", B))
    story.append(Paragraph(
        "<b>Swarm coordination:</b> The field is divided into 2 m grid cells, each with a weed density score. "
        "Robots share position/battery/density data via LoRa mesh. Low-battery units return to charge; "
        "others converge on high-density cells — <b>ant colony optimisation</b> in action. The system "
        "gracefully handles individual robot failures by expanding neighbour coverage.", B))

    # ── BUILD PLAN ──
    story.append(Paragraph("Build Plan (v1 — 10–14 weeks)", H))
    bdata = [
        ["Phase", "Duration", "Deliverable"],
        ["1. Single Robot Prototype", "2–4 wk", "Chassis + drive + row-following (~$185)"],
        ["2. Weed Detection", "2–3 wk", "Camera pipeline + veg segmentation (~$30)"],
        ["3. Weed Removal", "1–2 wk", "Cutter mech + detection integration"],
        ["4. Field Navigation", "2 wk", "GPS row-following + row-end turns (~$20)"],
        ["5. Swarm Coordination", "2–3 wk", "LoRa mesh + ant-colony + multi-robot test"],
    ]
    story.append(mini_table(bdata, col_widths=[42*mm, 22*mm, 96*mm]))

    # ── WHY THIS MATTERS ──
    story.append(Paragraph("Why It Matters", H))
    story.append(Paragraph(
        "<b>60% of Tanzania's labour force</b> works in agriculture — mostly smallholder farms. "
        "Weeds are the single largest preventable cause of yield loss. Siafu offers <b>herbicide-free, "
        "affordable automation</b> that can increase food production without the environmental damage "
        "of chemicals or the capital cost of tractors. It's designed to be built and repaired locally: "
        "3D-printed chassis, off-the-shelf electronics, open-source everything. "
        "<b>Version Extreme Cooperation, Tanzania.</b>", B))

    # ── FOOTER ──
    story.append(hr())
    story.append(Paragraph(
        "Siafu v1.0 — Version Extreme Cooperation, Tanzania &nbsp;·&nbsp; Open Hardware &nbsp;·&nbsp; MIT License",
        SM))

    doc.build(story)
    print(f"✅ One-pager PDF: {OUTPUT_PATH}")
    print(f"   Size: {os.path.getsize(OUTPUT_PATH):,} bytes")

if __name__ == "__main__":
    build()

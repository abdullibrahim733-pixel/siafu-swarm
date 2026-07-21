#!/usr/bin/env python3
"""
Siafu Main Control Board — KiCad Project Generator
Generates a complete KiCad 7.0 project with schematic (S-expression format).

Board: SIAFU-MCB-v1 (Main Control Board)
MCU:   ESP32-S3-WROOM-1
Power: 2x 18650 (7.4V) → Buck 5V → LDO 3.3V
Motor: 3× DRV8833 (4 drive + 1 cutter)
Comms: RFM95W LoRa, CH340C USB-Serial
Sensors: MPU-6050 IMU, HMC5883L compass, GPS, 4× HC-SR04
"""

import os, sys, json, uuid, shutil, textwrap
from pathlib import Path

PROJECT_DIR = os.path.expanduser("~/Projects/siafu-swarm/hardware/SIAFU-MCB-v1")
PROJECT_NAME = "SIAFU-MCB-v1"

# UUIDs for the project (deterministic for reproducibility)
def make_uuid(seed: str) -> str:
    """Generate a deterministic UUID v5 from a seed string."""
    import hashlib
    h = hashlib.sha256(seed.encode()).hexdigest()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

# ─── KiCad S-expression helpers ───────────────────────────────

def sexp(*args, indent=1) -> str:
    """Build an S-expression string. Lists become sub-expressions."""
    parts = []
    for a in args:
        if isinstance(a, (list, tuple)):
            sub = " ".join(_sexp_val(x) for x in a)
            parts.append(f"({sub})")
        elif isinstance(a, dict):
            parts.append(_sexp_dict(a))
        else:
            parts.append(_sexp_val(a))
    return " ".join(parts)

def _sexp_val(v) -> str:
    if isinstance(v, str):
        if v.startswith("("):  # already an sexp
            return v
        return f'"{v}"'
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (int, float)):
        return str(v)
    return str(v)

def _sexp_dict(d: dict) -> str:
    items = []
    for k, v in d.items():
        if isinstance(v, dict):
            items.append(f"({k} {_sexp_dict(v)})")
        elif isinstance(v, (list, tuple)):
            sub = " ".join(_sexp_val(x) for x in v)
            items.append(f"({k} {sub})")
        elif v is not None:
            items.append(f"({k} {_sexp_val(v)})")
    return " ".join(items)

def indent(level: int) -> str:
    return "\t" * level

def wrap(level: int, *lines) -> str:
    """Return indented lines joined by newline."""
    return "\n".join(indent(level) + l for l in lines if l)

# ─── Symbol library access ────────────────────────────────────

KICAD_SYM_DIR = Path("/usr/share/kicad/symbols")

def read_symbol(library: str, symbol: str) -> str | None:
    """Read a symbol definition from KiCad library."""
    lib_path = KICAD_SYM_DIR / f"{library}.kicad_sym"
    if not lib_path.exists():
        print(f"  ⚠ Library not found: {library}.kicad_sym")
        return None
    content = lib_path.read_text(encoding="utf-8", errors="replace")

    # Find the symbol definition
    import re
    pattern = r'\(symbol\s+"' + re.escape(symbol) + r'"(?!\w)'
    match = re.search(pattern, content)
    if not match:
        print(f"  ⚠ Symbol not found: {library}:{symbol}")
        return None

    # Extract balanced parentheses
    start = match.start()
    depth = 0
    for i in range(start, len(content)):
        if content[i] == "(":
            depth += 1
        elif content[i] == ")":
            depth -= 1
            if depth == 0:
                return content[start:i+1]
    return None

def convert_to_embedded(symbol_block: str, library: str, symbol: str) -> str:
    """Convert a library symbol block to embedded lib_symbols format."""
    import re
    result = symbol_block
    # Prefix symbol name with library
    result = re.sub(
        r'\(symbol\s+"' + re.escape(symbol) + r'"',
        f'(symbol "{library}:{symbol}"',
        result, count=1
    )
    # Strip library-specific attributes
    for attr in ["show_name", "do_not_autoplace", "in_pos_files", "duplicate_pin_numbers_are_jumpers"]:
        result = re.sub(r"\n?\s*\(" + attr + r"\s+\w+\)", "", result)
    # Normalize indentation
    lines = result.split("\n")
    min_indent = float("inf")
    for line in lines:
        s = line.lstrip()
        if s:
            min_indent = min(min_indent, len(line) - len(s))
    if min_indent == float("inf"):
        min_indent = 0
    normalized = []
    for line in lines:
        s = line.strip()
        if not s:
            normalized.append("")
            continue
        depth = max(0, (len(line) - len(line.lstrip()) - min_indent)) // 2
        normalized.append("\t\t" + "\t" * int(depth) + s)
    return "\n".join(normalized)

# ─── Component definition ─────────────────────────────────────

class Component:
    """A component to place in the schematic."""
    def __init__(self, ref: str, library: str, symbol: str, value: str,
                 x: float, y: float, footprint: str = "", unit: int = 1):
        self.ref = ref
        self.library = library
        self.symbol = symbol
        self.value = value
        self.x = x
        self.y = y
        self.footprint = footprint
        self.unit = unit
        self.uuid = make_uuid(f"SIAFU-MCB-v1_{ref}")
        self._symbol_block = None

    def load_symbol(self) -> None:
        """Load symbol definition from library."""
        block = read_symbol(self.library, self.symbol)
        if block:
            self._symbol_block = convert_to_embedded(block, self.library, self.symbol)
        else:
            print(f"  ⚠ Could not load symbol: {self.library}:{self.symbol}")

    def to_sexp(self) -> str:
        """Generate the (symbol ...) instance entry."""
        lib_id = f"{self.library}:{self.symbol}"
        lines = [
            f'(symbol (lib_id "{lib_id}") (at {self.x} {self.y} 0) (unit {self.unit})',
            f'  (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'  (uuid {self.uuid})',
            f'  (property "Reference" "{self.ref}" (at {self.x} {self.y-3.81} 0)',
            f'    (effects (font (size 1.27 1.27)) (justify left)))',
            f'  (property "Value" "{self.value}" (at {self.x} {self.y+2.54} 0)',
            f'    (effects (font (size 1.27 1.27)) (justify left)))',
        ]
        if self.footprint:
            lines.append(
                f'  (property "Footprint" "{self.footprint}" (at {self.x} {self.y+5.08} 0)'
                f'\n    (effects (font (size 1.27 1.27)) hide))'
            )
        lines.append(')')
        return "\n".join(lines)

# ─── Project generator ────────────────────────────────────────

def create_project():
    """Generate the complete KiCad project."""
    proj_dir = Path(PROJECT_DIR)
    proj_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Project directory: {proj_dir}")

    # ── Define all components ──────────────────────────────────
    # Coordinate system: mm, origin at bottom-left of A4 sheet
    # Page: 297 x 210 mm
    # Component placement organized by functional blocks

    components = []

    # === POWER SUPPLY (x=25-95, y=170-200) ===
    components.append(Component("J1", "Connector", "Screw_Terminal_01x02", "Battery 7.4V",
                                25, 195, "Connector:Screw_Terminal_01x02_Pin"))
    components.append(Component("D1", "Device", "D_Schottky", "SS34",
                                45, 195, "Diode_SMD:D_SMA"))
    components.append(Component("U1", "Regulator_Switching", "LM22676MR-5", "Buck 7.4V→5V",
                                65, 195, "Package_SOIC:SOIC-8_3.9x4.9mm_P1.27mm"))
    components.append(Component("L1", "Device", "L", "10µH",
                                85, 195, "Inductor_SMD:L_7.3x7.3mm_H4mm"))
    components.append(Component("U2", "Regulator_Linear", "AMS1117-3.3", "LDO 3.3V",
                                25, 173, "Package_TO_SOT_SMD:SOT-223"))
    components.append(Component("J2", "Connector", "Screw_Terminal_01x02", "Solar 6V",
                                65, 173, "Connector:Screw_Terminal_01x02_Pin"))
    components.append(Component("LED1", "Device", "LED", "Power Green",
                                45, 173, "LED_SMD:LED_0805_2012Metric"))

    # === USB & PROGRAMMING (x=25-95, y=140-170) ===
    components.append(Component("J3", "Connector", "USB_C_Receptacle", "USB Type-C",
                                25, 150, "Connector_USB:USB_C_Receptacle_USB2.0_14P"))
    components.append(Component("U3", "Interface_USB", "CH340C", "USB-UART",
                                50, 150, "Package_SOIC:SOIC-16_3.9x9.9mm_P1.27mm"))
    components.append(Component("SW1", "Switch", "SW_Push", "Reset",
                                80, 143, "Button_Switch_SMD:SW_SPST_B3U-1000P"))
    components.append(Component("SW2", "Switch", "SW_Push", "Boot",
                                80, 155, "Button_Switch_SMD:SW_SPST_B3U-1000P"))
    components.append(Component("LED2", "Device", "LED", "Status Blue",
                                85, 170, "LED_SMD:LED_0805_2012Metric"))

    # === ESP32-S3 MCU (x=105-175, y=150-200) ===
    components.append(Component("U4", "RF_Module", "ESP32-S3-WROOM-1", "ESP32-S3 MCU",
                                130, 180, "RF_Module:ESP32-S3-WROOM-1"))
    components.append(Component("Y1", "Device", "Crystal", "32.768kHz",
                                105, 195, "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm"))
    components.append(Component("R1", "Device", "R", "10k",
                                130, 145, "Resistor_SMD:R_0805_2012Metric"))

    # === MOTOR DRIVERS (x=25-130, y=60-130) ===
    components.append(Component("U5", "Driver_Motor", "DRV8833PW", "Motor Driver A/B",
                                40, 100, "Package_SOIC:TSSOP-16_4.4x5mm_P0.65mm"))
    components.append(Component("U6", "Driver_Motor", "DRV8833PW", "Motor Driver C/D",
                                85, 100, "Package_SOIC:TSSOP-16_4.4x5mm_P0.65mm"))
    components.append(Component("U7", "Driver_Motor", "DRV8833PW", "Cutter Driver",
                                40, 60, "Package_SOIC:TSSOP-16_4.4x5mm_P0.65mm"))
    components.append(Component("M1", "Connector", "Screw_Terminal_01x02", "Motor FL",
                                130, 85, "Connector:Screw_Terminal_01x02_Pin"))
    components.append(Component("M2", "Connector", "Screw_Terminal_01x02", "Motor FR",
                                130, 100, "Connector:Screw_Terminal_01x02_Pin"))
    components.append(Component("M3", "Connector", "Screw_Terminal_01x02", "Motor RL",
                                130, 115, "Connector:Screw_Terminal_01x02_Pin"))
    components.append(Component("M4", "Connector", "Screw_Terminal_01x02", "Motor RR",
                                130, 130, "Connector:Screw_Terminal_01x02_Pin"))
    components.append(Component("M5", "Connector", "Screw_Terminal_01x02", "Cutter Motor",
                                85, 55, "Connector:Screw_Terminal_01x02_Pin"))

    # === SENSORS (x=180-270, y=150-200) ===
    components.append(Component("U8", "Sensor_Motion", "MPU-6050", "IMU",
                                210, 195, "Package_DFN_QFN:QFN-24_4x4mm_P0.5mm"))
    components.append(Component("U9", "Connector_Generic", "Conn_01x04", "I2C Compass Ext",
                                210, 175, "Connector:PinHeader_1x04_P2.54mm_Vertical"))
    components.append(Component("J4", "Connector_Generic", "Conn_01x04", "HC-SR04 #1",
                                250, 195, "Connector:PinHeader_1x04_P2.54mm_Vertical"))
    components.append(Component("J5", "Connector_Generic", "Conn_01x04", "HC-SR04 #2",
                                250, 180, "Connector:PinHeader_1x04_P2.54mm_Vertical"))
    components.append(Component("J6", "Connector_Generic", "Conn_01x04", "HC-SR04 #3",
                                250, 165, "Connector:PinHeader_1x04_P2.54mm_Vertical"))
    components.append(Component("J7", "Connector_Generic", "Conn_01x04", "HC-SR04 #4",
                                250, 150, "Connector:PinHeader_1x04_P2.54mm_Vertical"))
    components.append(Component("J8", "RF_GPS", "L70-R", "GPS Module",
                                180, 155, "RF_Module:GPS_Module"))

    # === LORA COMMUNICATION (x=180-270, y=60-130) ===
    components.append(Component("U10", "RF_Module", "RFM95W-868S2", "LoRa Module",
                                210, 105, "RF_Module:RFM95W-868S2"))
    components.append(Component("J9", "Connector_Generic", "Conn_01x06", "RPi UART/I2C",
                                210, 68, "Connector:PinHeader_1x06_P2.54mm_Vertical"))

    # === DECOUPLING CAPS (distributed near ICs) ===
    for i, (ref, x, y, val) in enumerate([
        ("C1", 25, 185, "0.1µF"), ("C2", 35, 185, "10µF"), ("C3", 25, 168, "0.1µF"),
        ("C4", 35, 168, "10µF"), ("C5", 105, 178, "0.1µF"), ("C6", 110, 190, "10µF"),
        ("C7", 115, 178, "0.1µF"), ("C8", 120, 190, "10µF"),
        ("C9", 29, 88, "0.1µF"), ("C10", 34, 78, "0.1µF"),
        ("C11", 74, 88, "0.1µF"), ("C12", 79, 78, "0.1µF"),
        ("C13", 200, 190, "0.1µF"), ("C14", 200, 178, "0.1µF"),
        ("C15", 200, 98, "0.1µF"), ("C16", 200, 85, "0.1µF"),
    ]):
        components.append(Component(ref, "Device", "C", val, x, y))

    # === PULL-UP / BIAS RESISTORS ===
    for i, (ref, x, y, val) in enumerate([
        ("R2", 105, 185, "4.7k"), ("R3", 200, 170, "4.7k"), ("R4", 200, 165, "4.7k"),
        ("R5", 105, 170, "10k"), ("R6", 105, 165, "10k"),
    ]):
        components.append(Component(ref, "Device", "R", val, x, y))

    # Load all symbol definitions
    print("📦 Loading symbols...")
    for c in components:
        c.load_symbol()

    # ── Build the schematic file ──────────────────────────────
    sch_file = proj_dir / f"{PROJECT_NAME}.kicad_sch"
    print(f"📄 Writing schematic: {sch_file}")

    # Collect unique lib_symbols blocks
    lib_symbols_entries = []
    seen_symbols = set()
    for c in components:
        if c._symbol_block and c.library + ":" + c.symbol not in seen_symbols:
            lib_symbols_entries.append(c._symbol_block)
            seen_symbols.add(c.library + ":" + c.symbol)

    # Build the schematic
    sch_lines = [
        f'(kicad_sch (version 20240101) (generator "hermes-agent")',
        f'  (uuid {make_uuid("SIAFU-MCB-v1_sch")})',
        f'  (title_block',
        f'    (title "Siafu Main Control Board v1.0")',
        f'    (date "2026-07-10")',
        f'    (company "Version Extreme Cooperation")',
        f'    (rev "1.0")',
        f'  )',
        f'  (lib_symbols',
    ]

    # Add lib_symbols
    for entry in lib_symbols_entries:
        sch_lines.append(entry)

    sch_lines.append('  )')  # close lib_symbols

    # Add component instances
    sch_lines.append('  (symbol_instances')
    for c in components:
        sch_lines.append(f'    (symbol_instance (path "/{c.ref}") (reference "{c.ref}") (uuid {c.uuid}))')
    sch_lines.append('  )')

    # Add components (symbol instances with properties)
    for c in components:
        sch_lines.append(c.to_sexp())

    # ── POWER & GROUND SYMBOLS ──
    power_entries = [
        # (ref, symbol, x, y, uuid_seed)
        ("GND1", "power:GND", 25, 198, "PWR_GND1"),
        ("GND2", "power:GND", 25, 176, "PWR_GND2"),
        ("GND3", "power:GND", 130, 200, "PWR_GND3"),
        ("GND4", "power:GND", 40, 108, "PWR_GND4"),
        ("GND5", "power:GND", 85, 108, "PWR_GND5"),
        ("GND6", "power:GND", 40, 68, "PWR_GND6"),
        ("GND7", "power:GND", 210, 202, "PWR_GND7"),
        ("GND8", "power:GND", 210, 112, "PWR_GND8"),
        ("+5V", "power:+5V", 65, 200, "PWR_5V1"),
        ("+5V2", "power:+5V", 40, 95, "PWR_5V2"),
        ("+5V3", "power:+5V", 85, 95, "PWR_5V3"),
        ("+5V4", "power:+5V", 40, 55, "PWR_5V4"),
        ("+3V3", "power:+3V3", 130, 140, "PWR_3V3"),
        ("+3V3_S", "power:+3V3", 210, 170, "PWR_3V3_S"),
    ]

    for ref, sym_name, x, y, uid in power_entries:
        sch_lines.append(
            f'(symbol (lib_id "{sym_name}") (at {x} {y} 0)'
            f'\n  (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)'
            f'\n  (uuid {make_uuid(uid)})'
            f'\n  (property "Reference" "{ref}" (at {x} {y-2.54} 0)'
            f'\n    (effects (font (size 1.27 1.27)) hide))'
            f'\n  (property "Value" "{ref}" (at {x} {y+2.54} 0)'
            f'\n    (effects (font (size 1.27 1.27)))))'
        )

    # ── GLOBAL LABELS for net connections ──
    # Format: (label "NAME" (at x y orientation) (uuid ...))
    labels = [
        # I2C bus
        ("I2C_SCL", 200, 195, 0, "LBL_I2C_SCL"),
        ("I2C_SDA", 200, 190, 0, "LBL_I2C_SDA"),
        # SPI (LoRa)
        ("SPI_MOSI", 200, 125, 0, "LBL_SPI_MOSI"),
        ("SPI_MISO", 200, 120, 0, "LBL_SPI_MISO"),
        ("SPI_SCK", 200, 115, 0, "LBL_SPI_SCK"),
        ("SPI_CS_LORA", 200, 110, 0, "LBL_SPI_CS"),
        # UART (RPi)
        ("UART_TX_RPi", 200, 78, 0, "LBL_UART_TX"),
        ("UART_RX_RPi", 200, 75, 0, "LBL_UART_RX"),
        # UART (GPS)
        ("GPS_TX", 180, 175, 0, "LBL_GPS_TX"),
        ("GPS_RX", 180, 170, 0, "LBL_GPS_RX"),
        # Motor control
        ("MOT_AIN1", 29, 105, 0, "LBL_MOT_A1"),
        ("MOT_AIN2", 29, 102, 0, "LBL_MOT_A2"),
        ("MOT_BIN1", 29, 99, 0, "LBL_MOT_B1"),
        ("MOT_BIN2", 29, 96, 0, "LBL_MOT_B2"),
        ("MOT_CIN1", 74, 105, 0, "LBL_MOT_C1"),
        ("MOT_CIN2", 74, 102, 0, "LBL_MOT_C2"),
        ("MOT_DIN1", 74, 99, 0, "LBL_MOT_D1"),
        ("MOT_DIN2", 74, 96, 0, "LBL_MOT_D2"),
        ("MOT_EIN1", 29, 65, 0, "LBL_MOT_E1"),
        ("MOT_EIN2", 29, 62, 0, "LBL_MOT_E2"),
        # Ultrasonic
        ("TRIG1", 250, 195, 0, "LBL_TRIG1"),
        ("ECHO1", 250, 192, 0, "LBL_ECHO1"),
        ("TRIG2", 250, 180, 0, "LBL_TRIG2"),
        ("ECHO2", 250, 177, 0, "LBL_ECHO2"),
        ("TRIG3", 250, 165, 0, "LBL_TRIG3"),
        ("ECHO3", 250, 162, 0, "LBL_ECHO3"),
        ("TRIG4", 250, 150, 0, "LBL_TRIG4"),
        ("ECHO4", 250, 147, 0, "LBL_ECHO4"),
        # USB
        ("USB_DP", 25, 147, 0, "LBL_USB_DP"),
        ("USB_DN", 25, 144, 0, "LBL_USB_DN"),
    ]

    for name, x, y, orient, uid in labels:
        sch_lines.append(
            f'(label "{name}" (at {x} {y} {orient})'
            f'\n  (effects (font (size 1.27 1.27)) (justify left))'
            f'\n  (uuid {make_uuid(uid)}))'
        )

    # ── POWER FLAG (for ERC) ──
    for i, (x, y, uid) in enumerate([(25, 200, "PWR_FLAG1"), (65, 202, "PWR_FLAG2"),
                                      (130, 138, "PWR_FLAG3"), (210, 168, "PWR_FLAG4")]):
        sch_lines.append(
            f'(symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0)'
            f'\n  (unlocked yes) (unit 1)'
            f'\n  (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)'
            f'\n  (uuid {make_uuid(uid)})'
            f'\n  (property "Reference" "#FLAG{i+1}" (at {x} {y-2.54} 0)'
            f'\n    (effects (font (size 1.27 1.27)) hide))'
            f'\n  (property "Value" "PWR_FLAG" (at {x} {y+2.54} 0)'
            f'\n    (effects (font (size 1.27 1.27)))))'
        )

    # ── WIRES (BUS) ──
    # Short bus connections for power distribution
    bus_wires = [
        # 5V rail
        [(75, 200), (65, 200)],   # Buck output to 5V label
        [(40, 95), (45, 95)],     # 5V to Motor driver A
        [(85, 95), (90, 95)],     # 5V to Motor driver B
        [(40, 55), (45, 55)],     # 5V to Cutter driver
        # 3.3V rail
        [(25, 170), (30, 170)],   # LDO output
        [(130, 140), (135, 140)], # 3.3V to ESP32
        # I2C to sensors
        [(205, 195), (210, 195)], # SCL to MPU6050
        [(205, 190), (210, 190)], # SDA to MPU6050
    ]

    for pts in bus_wires:
        pts_str = " ".join(f"(xy {x} {y})" for x, y in pts)
        sch_lines.append(f'  (wire (pts {pts_str})\n  )')

    # Close the schematic
    sch_lines.append(')')

    # Write the schematic
    sch_content = "\n".join(sch_lines) + "\n"
    sch_file.write_text(sch_content)
    print(f"  ✅ Schematic: {len(components)} components, {len(lib_symbols_entries)} unique symbols")

    # ── Create .kicad_pro file ─────────────────────────────────
    pro_content = {
        "meta": {
            "filename": f"{PROJECT_NAME}.kicad_pro",
            "version": 2
        },
        "project": {
            "files": [],
            "name": PROJECT_NAME
        },
        "sheets": [[make_uuid("SIAFU-MCB-root"), "Root"]],
        "board": {
            "thickness": 1.6,
            "design_settings": {
                "rules": {
                    "min_clearance": 0.2,
                    "min_track_width": 0.25,
                    "min_via_diameter": 0.6,
                    "min_via_drill": 0.3,
                    "min_microvia_diameter": 0.3,
                    "min_microvia_drill": 0.1,
                    "min_hole_to_hole": 0.25,
                    "min_silk_to_copper": 0.15,
                    "min_silk_to_silk": 0.15,
                    "min_copper_to_edge": 0.2,
                    "min_hole_size": 0.2,
                    "blind_buried_vias_allowed": False,
                    "microvias_allowed": False
                }
            }
        },
        "schematic": {
            "drawing": {
                "page_layout": {
                    "height": 11.69,
                    "width": 8.27
                }
            }
        },
        "pcbnew": {}
    }

    pro_file = proj_dir / f"{PROJECT_NAME}.kicad_pro"
    with open(pro_file, "w") as f:
        json.dump(pro_content, f, indent=2)
    print(f"  ✅ Project file: {PROJECT_NAME}.kicad_pro")

    # ── Create fp-lib-table ────────────────────────────────────
    fp_lib = proj_dir / "fp-lib-table"
    fp_content = """(fp_lib_table
  (lib (name "")(type "KiCad")(uri "${KICAD6_FOOTPRINT_DIR}")(options "")(descr ""))
)
"""
    fp_lib.write_text(fp_content)
    print(f"  ✅ Footprint table: fp-lib-table")

    # ── Create .kicad_pcb with board outline ──────────────────
    pcb_file = proj_dir / f"{PROJECT_NAME}.kicad_pcb"
    board_width = 80.0   # mm
    board_height = 60.0  # mm
    board_x = 0
    board_y = 0

    pcb_content = f"""(kicad_pcb (version 20231001) (generator "hermes-agent")
  (uuid {make_uuid("SIAFU-MCB-PCB")})
  (paper "User")
  (title_block
    (title "Siafu Main Control Board v1.0")
    (date "2026-07-10")
    (company "Version Extreme Cooperation")
    (rev "1.0")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user)
    (33 "F.Adhes" user)
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user)
    (41 "Cmts.User" user)
    (42 "Eco1.User" user)
    (43 "Eco2.User" user)
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (stackup
      (layer "F.Cu" (type copper))
      (layer "B.Cu" (type copper))
    )
    (solder_mask (min_width 0.1))
  )
  (board (thickness 1.6)
    (xy 0 0) (xy {board_width} 0)
    (xy {board_width} {board_height}) (xy 0 {board_height})
    (xy 0 0)
  )
  (footprint "SIAFU-MCB-v1" (layer "F.Cu")
    (descr "Siafu Main Control Board 80x60mm")
    (attr board)
    (fp_polygon (pts
      (xy 0 0) (xy {board_width} 0)
      (xy {board_width} {board_height}) (xy 0 {board_height})
    ) (layer "Edge.Cuts") (width 0.15))
    (fp_text reference "" (at 40 58) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))) hide)
    (fp_text value "SIAFU-MCB-v1" (at 40 2) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  )
)
"""
    pcb_file.write_text(pcb_content)
    print(f"  ✅ PCB file: {PROJECT_NAME}.kicad_pcb ({board_width}×{board_height}mm)")

    # ── Summary ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"🎯 Siafu Main Control Board — Project Created!")
    print(f"{'='*60}")
    print(f"\n📁 Location: {proj_dir}")
    print(f"\n📄 Files:")
    for f in sorted(proj_dir.iterdir()):
        size = f.stat().st_size
        print(f"   {f.name:30s} {size:>6,} bytes")
    print(f"\n🔧 Components: {len(components)}")
    print(f"\n📋 Open in KiCad:")
    print(f"   kicad {pro_file}")
    print(f"\n   Next steps:")
    print(f"   1. Open KiCad → File → Open Project → {PROJECT_NAME}.kicad_pro")
    print(f"   2. Open schematic editor → place & wire components")
    print(f"   3. Annotate schematic (Tools → Annotate Schematics)")
    print(f"   4. Assign footprints")
    print(f"   5. Run ERC (Electrical Rules Check)")
    print(f"   6. Update PCB from schematic")
    print(f"   7. Route traces")
    print(f"   8. Run DRC → Export Gerbers")

if __name__ == "__main__":
    create_project()

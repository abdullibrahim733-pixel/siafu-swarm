#!/usr/bin/env python3
"""
Siafu Main Control Board — KiCad Project Generator v2
Copies the KiCad template, then adds all components properly.
"""

import json
import re
import shutil
import uuid
import os
from pathlib import Path

PROJECT_DIR = Path("/home/cybertron/Projects/siafu-swarm/hardware/SIAFU-MCB-v2")
PROJECT_NAME = "SIAFU-MCB-v2"
TITLE = "Siafu Main Control Board v1.0"
COMPANY = "Version Extreme Cooperation"
TEMPLATE_PATH = Path("/usr/share/kicad/template/Arduino_Mega")

# KiCad 7.0 schematic version
SCH_VERSION = "20221206"
ROOT_UUID = str(uuid.uuid4())

# ── Component definitions ──────────────────────────────────
COMPONENTS = [
    # Power section
    ("J1", "Connector", "Screw_Terminal_01x02", [("1",""),("2","")],
     "Battery Input", 30, 190, 0),
    ("D1", "Device", "D_Schottky", [("1","K"),("2","A")],
     "SS34", 50, 190, 0),
    ("U1", "Regulator_Switching", "LM22676MR-5", [("1","FB"),("2","SW"),("3","VIN"),("4","EN"),("5","GND"),("6","VOUT"),("7","NC"),("8","COMP")],
     "Buck 7.4V→5V", 70, 190, 0),
    ("L1", "Device", "L", [("1",""),("2","")],
     "10µH", 95, 190, 0),
    ("U2", "Regulator_Linear", "AMS1117-3.3", [("1","GND"),("2","VOUT"),("3","VIN")],
     "LDO 5V→3.3V", 110, 170, 0),

    # USB & Programming
    ("J3", "Connector", "USB_C_Receptacle_USB2.0_14P", [("1","VBUS"),("2","D-"),("3","D+"),("4","CC1"),("5","CC2"),("6","SBU1"),("7","SBU2"),("8","GND"),("9","GND"),("10","GND"),("11","GND"),("12","GND"),("13","GND"),("14","GND")],
     "USB Type-C", 30, 150, 0),
    ("U3", "Interface_USB", "CH340C", [("1","TX"),("2","RX"),("3","RTS#"),("4","CTS#"),("5","DTR#"),("6","DSR#"),("7","DCD#"),("8","RI#"),("9","V3"),("10","UD+"),("11","UD-"),("12","XI"),("13","XO"),("14","GND"),("15","VCC"),("16","RSV")],
     "USB-UART", 55, 150, 0),

    # ESP32-S3
    ("U4", "RF_Module", "ESP32-S3-WROOM-1", [("1","GND"),("2","3V3"),("3","EN"),("4","IO0"),("5","IO1"),("6","IO2"),("7","IO3"),("8","IO4"),("9","IO5"),("10","IO6"),("11","IO7"),("12","IO8"),("13","IO9"),("14","IO10"),("15","IO11"),("16","IO12"),("17","IO13"),("18","IO14"),("19","IO15"),("20","IO16"),("21","IO17"),("22","IO18"),("23","IO19"),("24","IO20"),("25","IO21"),("26","SDA"),("27","SCL"),("28","TXD0"),("29","RXD0"),("30","TXD1"),("31","RXD1"),("32","ADC1_CH0"),("33","ADC1_CH1"),("34","ADC1_CH2"),("35","ADC1_CH3"),("36","ADC1_CH4"),("37","ADC1_CH5"),("38","USB_D-"),("39","USB_D+"),("40","SPI_MOSI"),("41","SPI_MISO"),("42","SPI_CLK"),("43","SPI_CS"),("44","TXD2"),("45","RXD2")],
     "ESP32-S3", 120, 170, 0),

    # Motor drivers
    ("U5", "Driver_Motor", "DRV8833PW", [("1","AOUT1"),("2","AOUT2"),("3","AIN2"),("4","AIN1"),("5","VMM"),("6","NSLEEP"),("7","nFAULT"),("8","GND"),("9","BOUT1"),("10","BOUT2"),("11","BIN2"),("12","BIN1")],
     "Motor Driver 1-2", 80, 100, 0),
    ("U6", "Driver_Motor", "DRV8833PW", [("1","AOUT1"),("2","AOUT2"),("3","AIN2"),("4","AIN1"),("5","VMM"),("6","NSLEEP"),("7","nFAULT"),("8","GND"),("9","BOUT1"),("10","BOUT2"),("11","BIN2"),("12","BIN1")],
     "Motor Driver 3-4", 80, 60, 0),
    ("U7", "Driver_Motor", "DRV8833PW", [("1","AOUT1"),("2","AOUT2"),("3","AIN2"),("4","AIN1"),("5","VMM"),("6","NSLEEP"),("7","nFAULT"),("8","GND"),("9","BOUT1"),("10","BOUT2"),("11","BIN2"),("12","BIN1")],
     "Motor Driver Cutter", 110, 100, 0),

    # Sensors
    ("U8", "Sensor_Motion", "MPU-6050", [("1","CLKIN"),("2","AUX_DA"),("3","AUX_CL"),("4","VLOGIC"),("5","AD0"),("6","REGOUT"),("7","nCS"),("8","SCLK"),("9","SDI"),("10","SDO"),("11","SDA"),("12","SCL"),("13","GND"),("14","VDD"),("15","INT"),("16","FSYNC")],
     "IMU", 175, 190, 0),

    # Headers
    ("U9", "Connector_Generic", "Conn_01x04", [("1","Pin_1"),("2","Pin_2"),("3","Pin_3"),("4","Pin_4")],
     "I2C Compass/GPS", 200, 170, 0),
    ("J4", "Connector_Generic", "Conn_01x04", [("1","Pin_1"),("2","Pin_2"),("3","Pin_3"),("4","Pin_4")],
     "HC-SR04 #1", 150, 60, 0),
    ("J5", "Connector_Generic", "Conn_01x04", [("1","Pin_1"),("2","Pin_2"),("3","Pin_3"),("4","Pin_4")],
     "HC-SR04 #2", 170, 60, 0),
    ("J6", "Connector_Generic", "Conn_01x04", [("1","Pin_1"),("2","Pin_2"),("3","Pin_3"),("4","Pin_4")],
     "HC-SR04 #3", 190, 60, 0),
    ("J7", "Connector_Generic", "Conn_01x04", [("1","Pin_1"),("2","Pin_2"),("3","Pin_3"),("4","Pin_4")],
     "HC-SR04 #4", 210, 60, 0),

    # LoRa
    ("U10", "RF_Module", "RFM95W-868S2", [("1","GND"),("2","DIO5"),("3","DIO4"),("4","DIO3"),("5","DIO2"),("6","DIO1"),("7","DIO0"),("8","RST"),("9","CS"),("10","SCK"),("11","MOSI"),("12","MISO"),("13","ANT"),("14","VIN")],
     "LoRa Module", 200, 90, 0),

    # Passive components
    ("R1", "Device", "R", [("1",""),("2","")], "10kΩ I2C PU", 195, 185, 90),
    ("R2", "Device", "R", [("1",""),("2","")], "10kΩ I2C PU", 195, 180, 90),
    ("LED1", "Device", "LED", [("1","K"),("2","A")], "Power LED", 30, 175, 0),
    ("LED2", "Device", "LED", [("1","K"),("2","A")], "Status LED", 85, 155, 0),
    ("C1", "Device", "C", [("1",""),("2","")], "0.1µF", 115, 185, 0),
    ("C2", "Device", "C", [("1",""),("2","")], "10µF", 105, 160, 0),
    ("C3", "Device", "C", [("1",""),("2","")], "0.1µF", 130, 160, 0),
    ("C4", "Device", "C", [("1",""),("2","")], "0.1µF", 175, 175, 0),
    ("C5", "Device", "C", [("1",""),("2","")], "10µF", 30, 180, 0),
    ("C6", "Device", "C", [("1",""),("2","")], "0.1µF", 30, 185, 0),

    # Motor connectors
    ("M1", "Connector_Generic", "Conn_01x02", [("1","Pin_1"),("2","Pin_2")], "Motor 1", 60, 110, 0),
    ("M2", "Connector_Generic", "Conn_01x02", [("1","Pin_1"),("2","Pin_2")], "Motor 2", 60, 115, 0),
    ("M3", "Connector_Generic", "Conn_01x02", [("1","Pin_1"),("2","Pin_2")], "Motor 3", 100, 110, 0),
    ("M4", "Connector_Generic", "Conn_01x02", [("1","Pin_1"),("2","Pin_2")], "Motor 4", 100, 115, 0),
    ("M5", "Connector_Generic", "Conn_01x02", [("1","Pin_1"),("2","Pin_2")], "Cutter", 130, 110, 0),
]

# ── Helper: Extract symbol from library ────────────────────
def extract_symbol_text(library, symbol_name):
    """Read a symbol from a KiCad .kicad_sym library file."""
    sym_dir = Path("/usr/share/kicad/symbols")
    lib_path = sym_dir / f"{library}.kicad_sym"
    if not lib_path.exists():
        return None
    content = lib_path.read_text(encoding="utf-8", errors="replace")
    pattern = r'\(symbol\s+"' + re.escape(symbol_name) + r'"(?!\w)'
    match = re.search(pattern, content)
    if not match:
        return None
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

def convert_symbol_to_embedded(symbol_text, library, symbol_name):
    """Convert a library symbol to embedded format."""
    lib_id = f"{library}:{symbol_name}"
    # Add library prefix to the symbol name
    symbol_text = symbol_text.replace(f'(symbol "{symbol_name}"', f'(symbol "{lib_id}"', 1)
    # Remove kicad_sym-specific attributes
    for attr in [" (show_name yes)", " (duplicate_pin_numbers_are_jumpers yes)"]:
        symbol_text = symbol_text.replace(attr, "")
    # Normalize indentation (use 2-space indent)
    lines = []
    for line in symbol_text.split('\n'):
        stripped = line.rstrip()
        if stripped:
            lines.append(stripped)
    return '\n'.join(lines)

def get_pin_names(symbol_text, library, symbol_name):
    """Extract pin numbers and names from a symbol definition."""
    pins = {}
    for m in re.finditer(r'\(pin\s+(\w+)\s+line\s+\(at\s+[^)]+\)\s+\(length\s+[^)]+\)\s*\(name\s+"([^"]*)"', symbol_text):
        pin_num = m.group(1)
        pin_name = m.group(2)
        pins[pin_num] = pin_name
    return pins

# ── Main generator ─────────────────────────────────────────
def generate():
    print("=" * 60)
    print("Siafu MCB — KiCad Project Generator v2")
    print("=" * 60)

    # Step 1: Clean and copy template
    if PROJECT_DIR.exists():
        shutil.rmtree(PROJECT_DIR)
        print(f"  🗑️  Removed existing directory")
    
    PROJECT_DIR.mkdir(parents=True)
    
    print(f"  📁 Copying template {TEMPLATE_PATH.name}...")
    for file in TEMPLATE_PATH.glob("*"):
        if file.is_file():
            dest = PROJECT_DIR / file.name.replace("Arduino_Mega", PROJECT_NAME)
            shutil.copy(file, dest)
    
    # Rename files
    for old_file in PROJECT_DIR.glob("*"):
        if "Arduino_Mega" in old_file.name:
            new_name = old_file.name.replace("Arduino_Mega", PROJECT_NAME)
            new_path = old_file.parent / new_name
            if old_file != new_path:
                old_file.rename(new_path)

    # Step 2: Modify .kicad_pro
    pro_path = PROJECT_DIR / f"{PROJECT_NAME}.kicad_pro"
    if pro_path.exists():
        pro_data = json.loads(pro_path.read_text())
        pro_data["meta"]["filename"] = f"{PROJECT_NAME}.kicad_pro"
        # Add company
        if "schematic" in pro_data:
            pro_data["schematic"]["page_layout_descr_file"] = ""
        # Update sheets UUID
        pro_data["sheets"] = [[ROOT_UUID, ""]]
        pro_path.write_text(json.dumps(pro_data, indent=2))
    print(f"  ✅ Project file: {PROJECT_NAME}.kicad_pro")

    # Step 3: Modify .kicad_pcb (just update name)
    old_pcb = PROJECT_DIR / f"{PROJECT_NAME}.kicad_pcb"
    if old_pcb.exists():
        # Keep as-is (empty board from template)
        pass

    # Step 4: Build new schematic from scratch
    sch_path = PROJECT_DIR / f"{PROJECT_NAME}.kicad_sch"
    
    print(f"  📦 Loading symbols from KiCad libraries...")
    
    # Collect all unique library:symbol pairs
    lib_symbols_needed = {}
    for ref, library, symbol, pins, value, x, y, orient in COMPONENTS:
        key = f"{library}:{symbol}"
        lib_symbols_needed[key] = (library, symbol)
    
    # Read and convert all symbols
    embedded_symbols = {}
    for key, (library, symbol) in lib_symbols_needed.items():
        sym_text = extract_symbol_text(library, symbol)
        if sym_text:
            embedded = convert_symbol_to_embedded(sym_text, library, symbol)
            embedded_symbols[key] = embedded
            print(f"    ✓ {key}")
        else:
            print(f"    ⚠  {key} — NOT FOUND in library, using generic")
    
    # Build schematic content
    lines = []
    
    def L(text="", indent=0):
        lines.append("  " * indent + text)
    
    L(f'(kicad_sch (version {SCH_VERSION}) (generator "hermes-agent")')
    L("")
    L(f'  (uuid {ROOT_UUID})')
    L("")
    L('  (paper "A4")')
    L("")
    L("  (title_block")
    L('    (date "2026-07-10")', 2)
    L(f'    (title "{TITLE}")', 2)
    L(f'    (company "{COMPANY}")', 2)
    L(f'    (rev "1.0")', 2)
    L("  )")
    L("")
    L("  (lib_symbols")
    
    # Write all embedded symbols
    for key, sym_text in embedded_symbols.items():
        for line in sym_text.split('\n'):
            L(f"    {line.strip()}")
    
    L("  )")
    L("")
    
    # Components (instances)
    for ref, library, symbol, pins, value, x, y, orient in COMPONENTS:
        lib_id = f"{library}:{symbol}"
        comp_uuid = str(uuid.uuid4())
        unit = 1
        
        L("  (symbol (lib_id \"%s\") (at %d %d %d) (unit %d)" % (lib_id, x, y, orient, unit))
        L("    (in_bom yes) (on_board yes) (dnp no)")
        L(f"    (uuid {comp_uuid})")
        
        # Properties
        L(f'    (property "Reference" "{ref}" (at {x} {y - 10} 0)')
        L('      (effects (font (size 1.27 1.27)))')
        L("    )")
        L(f'    (property "Value" "{value}" (at {x} {y + 10} 0)')
        L('      (effects (font (size 1.27 1.27)))')
        L("    )")
        L(f'    (property "Footprint" "" (at {x} {y} 0)')
        L('      (effects (font (size 1.27 1.27)) hide)')
        L("    )")
        L(f'    (property "Datasheet" "~" (at {x} {y} 0)')
        L('      (effects (font (size 1.27 1.27)) hide)')
        L("    )")
        
        # Pin entries with UUIDs
        for pin_num, pin_name in pins:
            L(f'    (pin "{pin_num}" (uuid {str(uuid.uuid4())}))')
        
        # Instances section
        L("    (instances")
        L(f'      (project "{PROJECT_NAME}"', 2)
        L(f'        (path "/{ROOT_UUID}"', 2)
        L(f'          (reference "{ref}") (unit {unit})', 2)
        L(f'        )', 2)
        L(f'      )', 2)
        L("    )")
        L("  )")
        L("")
    
    # Sheet instances
    L("  (sheet_instances")
    L('    (path "/" (page "1"))', 2)
    L("  )")
    
    L(")")
    
    content = '\n'.join(lines)
    sch_path.write_text(content)
    
    # Verify
    size = sch_path.stat().st_size
    comp_count = len(COMPONENTS)
    
    print(f"\n  ✅ Schematic: {comp_count} components, {size:,} bytes")
    print(f"  📁 Project at: {PROJECT_DIR}")
    print(f"\n  Open in KiCad:")
    print(f"    kicad {PROJECT_DIR / Path(PROJECT_NAME + '.kicad_pro')}")
    print(f"")
    print(f"  Then in Schematic Editor:")
    print(f"    1. Tools → Annotate Schematics (assign reference designators)")
    print(f"    2. Inspect → Electrical Rules Checker → Run ERC")
    print(f"    3. Wire components together with labels and net connections")
    print(f"    4. File → Export → Netlist")
    print(f"    5. Open PCB Editor → Update PCB from Schematic")
    print(f"    6. Route traces → Run DRC → Export Gerbers")
    print("=" * 60)

if __name__ == "__main__":
    generate()

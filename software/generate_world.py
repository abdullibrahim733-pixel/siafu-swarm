#!/usr/bin/env python3
"""Generate Siafu Webots world file with all plants expanded."""

import os

HEADER = """#VRML_SIM R2025a utf8
# Siafu Swarm - Agricultural Field Simulation (generated)
# License: MIT

WorldInfo {
  title "Siafu Swarm - Weed Removal Field"
  info ["Swarm robotics for precision agriculture"
    "Tanzania maize field simulation"]
  basicTimeStep 32
  coordinateSystem "NUE"
  gpsCoordinateSystem "local"
}

Viewpoint {
  orientation 0.3 0.3 1 0.8
  position 8 6 10
  near 0.1
}

TexturedBackground { texture "dry_soil" }
TexturedBackgroundLight {}

DirectionalLight {
  direction 0.3 -1 0.2
  intensity 0.9
  color 1 1 1
  castShadows TRUE
}

# ==========================================
# SHARED NODES (hidden container for DEF/USE)
# ==========================================

DEF SHARED Transform {
  children [
    DEF MAIZE_SHAPE Group {
      children [
        Shape { geometry Cylinder { height 0.15 radius 0.015 } }
        Transform { translation 0 0.1 0 rotation 0 0 1 0.3 children [ Shape { geometry Box { size 0.2 0.005 0.04 } } ] }
        Transform { translation 0 0.08 0 rotation 0 0 1 -0.25 children [ Shape { geometry Box { size 0.18 0.005 0.04 } } ] }
      ]
    }

    DEF CROP_GREEN PBRAppearance {
      baseColor 0.15 0.55 0.15
      roughness 0.7
      metalness 0
    }

    DEF WEED_SHAPE Group {
      children [
        Shape { geometry Cylinder { height 0.02 radius 0.005 } }
        Transform { translation 0 0.03 0 children [ Shape { geometry Box { size 0.06 0.003 0.04 } } ] }
        Transform { translation 0.02 0.02 0 rotation 0 0 1 0.5 children [ Shape { geometry Box { size 0.04 0.003 0.03 } } ] }
        Transform { translation -0.02 0.025 0 rotation 0 0 1 -0.4 children [ Shape { geometry Box { size 0.05 0.003 0.03 } } ] }
      ]
    }

    DEF WEED_GREEN PBRAppearance {
      baseColor 0.25 0.70 0.15
      roughness 0.6
      metalness 0
    }
  ]
}

"""

GROUND = """# ==========================================
# GROUND
# ==========================================
Solid {
  translation 0 -0.05 0
  children [
    Shape {
      appearance PBRAppearance {
        baseColorMap ImageTexture { url ["https://webots.cloud/files/textures/soil_dry.jpg"] }
        roughness 0.9 metalness 0
      }
      geometry DEF FIELD_GROUND Plane { size 20 20 }
    }
  ]
  boundingObject Plane { size 20 20 }
  locked TRUE
}

"""

CROP_SOLID = """  Solid {
    translation %s 0 %s
    children [ USE MAIZE_SHAPE ]
    appearance USE CROP_GREEN
    boundingObject USE MAIZE_SHAPE
  }
"""

WEED_SOLID = """  Solid {
    translation %s 0 %s
    children [ USE WEED_SHAPE ]
    appearance USE WEED_GREEN
    boundingObject USE WEED_SHAPE
  }
"""

INLINE_WEED = 'Solid { translation %s 0 %s children [ USE WEED_SHAPE ] appearance USE WEED_GREEN boundingObject USE WEED_SHAPE }'

INLINE_SENSOR = 'Solid { translation %s -0.02 %s children [ Shape { appearance PBRAppearance { baseColor 0.4 0.3 0.2 roughness 0.8 } geometry Cylinder { height 0.02 radius 0.02 } } ] }'

CHARGING = """# ==========================================
# CHARGING STATION
# ==========================================
DEF ChargingStation Solid {
  translation -6 0 0
  children [
    Shape { appearance PBRAppearance { baseColor 0.9 0.2 0.2 roughness 0.3 metalness 0.1 } geometry Box { size 0.5 0.05 1.0 } }
    Transform { translation 0 0.1 0.4 children [ Shape { geometry Cylinder { height 0.15 radius 0.02 } appearance PBRAppearance { baseColor 1 0 0 emissiveColor 1 0 0 } } ] }
    Transform { translation 0 0.1 -0.4 children [ Shape { geometry Cylinder { height 0.15 radius 0.02 } appearance PBRAppearance { baseColor 0 1 0 emissiveColor 0 1 0 } } ] }
  ]
  name "charging_station"
}

"""

ROBOT = """SiafuBot {
  translation %s
  rotation 0 1 0 0
  name "%s"
  robotID %d
  bodyColor %s
}

"""

REAL_WEEDS = [
    (-3, -2.2), (-1.5, -2.8), (0, -2.2), (1.5, -2.8), (3, -2.2),
    (-3, 0.5), (-1, -0.5), (1, 0.5), (3, -0.5),
    (-2, 2.2), (0, 2.8), (2, 2.2), (4, 2.8),
]

SENSORS = [(-4, -1), (-2, 1), (0, -1), (2, 1), (4, -1)]


def build_world():
    lines = [HEADER, GROUND]
    
    # Crop rows
    lines.append("# ==========================================\n# CROP ROWS\n# ==========================================\n\n")
    for i in range(9):
        lines.append(CROP_SOLID % (-4 + i * 1.0, -3))
    for i in range(9):
        lines.append(CROP_SOLID % (-4 + i * 1.0, 0))
    for i in range(9):
        lines.append(CROP_SOLID % (-4 + i * 1.0, 3))
    
    # Weeds
    lines.append("\n# ==========================================\n# WEEDS\n# ==========================================\n\n")
    for i in range(13):
        lines.append(WEED_SOLID % (-4.5 + i * 0.7, -1.5))
    for i in range(11):
        lines.append(WEED_SOLID % (-4.0 + i * 0.8, 1.5))
    for x, z in REAL_WEEDS:
        lines.append("  " + INLINE_WEED % (x, z) + "\n")
    
    # Sensors
    lines.append("\n# ==========================================\n# SOIL MOISTURE SENSORS\n# ==========================================\n\n")
    for x, z in SENSORS:
        lines.append(INLINE_SENSOR % (x, z) + "\n")
    
    # Charging
    lines.append(CHARGING)
    
    # Robots
    lines.append("# ==========================================\n# SIAFU ROBOTS\n# ==========================================\n\n")
    lines.append(ROBOT % ("-5.5 0.07 -1.5", "siafu_1", 1, "0.2 0.2 0.8"))
    lines.append(ROBOT % ("-5.5 0.07 1.5", "siafu_2", 2, "0.8 0.2 0.2"))
    
    return "".join(lines)


if __name__ == '__main__':
    world = build_world()
    out_path = os.path.join(os.path.dirname(__file__), '..', 'simulation', 'worlds', 'field.wbt')
    with open(out_path, 'w') as f:
        f.write(world)
    print(f"Generated: {out_path}")
    print(f"Size: {len(world)} bytes, {world.count(chr(10))} lines")
    print(f"  - 27 crop plants, {13 + 11 + len(REAL_WEEDS)} weeds")
    print(f"  - 2 Siafu robots")

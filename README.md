# Siafu Swarm Robotics

> **Bio-inspired swarm robotics platform** — Named after the Siafu (Dorylus), the Tanzanian safari ant known for coordinated collective behavior.

[![OpenSCAD](https://img.shields.io/badge/Hardware-OpenSCAD-8A2BE2)](https://openscad.org)
[![Python](https://img.shields.io/badge/Simulation-Python-3776AB?logo=python)](https://python.org)
[![Webots](https://img.shields.io/badge/Simulator-Webots-00A1E4)](https://cyberbotics.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Overview

Siafu is an open-source, low-cost swarm robotics platform designed for **research, education, and real-world deployment** in Africa. Each robot is a small differential-drive unit that coordinates with peers to achieve collective goals — no central controller needed.

The project spans:

- **Hardware** — 3D-printable robot body (OpenSCAD), PCB design, sensor suite
- **Simulation** — Webots world with configurable swarm sizes and environments
- **Control** — Python-based controllers with flocking, consensus, and task allocation algorithms

## Repository Structure

```
siafu-swarm/
├── hardware/           # OpenSCAD models, STL exports, PCB design
│   ├── siafu_bot.scad  # Main robot body model
│   └── ...
├── simulation/
│   ├── worlds/         # Webots world files
│   ├── controllers/    # Robot controller Python code
│   │   └── siafu_controller/
│   └── protos/         # PROTO robot definitions
├── software/           # World generation, analysis tools
│   ├── generate_world.py
│   └── ...
├── docs/               # Design docs, diagrams, one-pagers
└── run_simulation.sh   # One-click Webots launcher
```

## Hardware Design

| Component | Specification |
|-----------|---------------|
| **Chassis** | 3D-printed PLA (OpenSCAD parametric) |
| **Drive** | 2-wheel differential with castor |
| **MCU** | ESP32 / STM32 |
| **Sensors** | IR proximity (×3), IMU, camera (optional) |
| **Communication** | ESP-NOW / Wi-Fi mesh |
| **Power** | Li-Ion 18650, hot-swappable |
| **Cost** | ~$25–35 per unit (target) |

## Simulation

A full Webots environment is included:

- **Configurable swarm size** — 5 to 50+ robots
- **Terrain** — Rough outdoor terrain mimicking Tanzanian environments
- **Collective behaviors** — Flocking, area coverage, consensus, task allocation
- **Sensor noise modeling** — Realistic noise injection

Quick start:

```bash
./run_simulation.sh
```

## Current Status

| Component | Status |
|-----------|--------|
| Robot chassis design | ✅ Complete (OpenSCAD) |
| STL export | ✅ Done |
| Webots world | ✅ Complete |
| Controllers | 🚧 In progress |
| PCB design | 🚧 In progress |
| Physical prototype | 📅 Planned |

## Why Swarm Robotics for Africa?

- **Low cost per unit** — Sub-$35 makes multi-robot systems accessible
- **No infrastructure needed** — Decentralized, no base stations
- **Resilient** — No single point of failure
- **Scalable** — Add more robots, no software changes needed
- **Open source** — Anyone can build, modify, and improve

## License

MIT — Open source, forever.

---

<div align="center">
  <sub>A project by <strong>UMG Africa</strong> — Built from Tanzania, for Africa.</sub>
</div>

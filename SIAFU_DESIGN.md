# Siafu — Swarm Robotics for Precision Weeding & Farm Cultivation

> **Siafu** (Swahili for "ants") — small, coordinated, relentless.
> A swarm of affordable agricultural robots that remove weeds mechanically,
> tend crops, and help smallholder farmers cultivate more efficiently.

---

## 1. PROBLEM ANALYSIS

### The Weed Problem
| Factor | Impact |
|--------|--------|
| **Yield loss** | Weeds reduce crop yields by 30–70% in African smallholder farms |
| **Labor cost** | Manual weeding consumes 40–60% of total farm labor hours |
| **Herbicide harm** | Chemical herbicides damage soil health, water, and human safety |
| **Timing** | Weeds must be removed within a narrow window after emergence |
| **Scale mismatch** | Large tractors are unaffordable and impractical for small plots |

### Target Context — Tanzanian Smallholder Farms
- Average farm size: **0.5–2 hectares**
- Common crops: maize, beans, cassava, rice, vegetables
- Row spacing: typically **50–75 cm** (maize), **30–45 cm** (beans)
- Terrain: uneven, often rain-fed, variable soil types
- Power availability: limited grid access, solar is abundant
- Cost sensitivity: **$50–200 per robot** target to be accessible

---

## 2. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                   FARM LEVEL (cloud/edge)                │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Field Map   │  │ Weed Density │  │ Swarm Command  │  │
│  │ & History   │  │ Heatmap      │  │ & Control      │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ LoRa / WiFi Mesh
┌──────────────────────┴──────────────────────────────────┐
│                   SWARM LAYER (mesh)                     │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │ Siafu  │◄─►│ Siafu  │◄─►│ Siafu  │◄─►│ Siafu  │ ...  │
│  │  #01   │   │  #02   │   │  #03   │   │  #04   │        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │ Charger│  │ Charger│  │ Charger│  │ Charger│        │
│  │ Station│  │ Station│  │ Station│  │ Station│        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. MECHANICAL DESIGN

### 3.1 Siafu Unit — Overview

```
                    ┌──────────────────┐
                    │   ☀️ Solar Panel  │
                    │  (10W poly-Si)    │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │      Electronics Bay        │
              │  ┌──────┐  ┌────────────┐   │
              │  │ RPi 5│  │ ESP32 M/C  │   │
              │  │ Cam  │  │ GPS + IMU  │   │
              │  └──────┘  └────────────┘   │
              └──────────────┬──────────────┘
      ┌──────────┐          │          ┌──────────┐
      │  Motor   │◄──── chassis ──────►│  Motor   │
      │  Driver  │     frame           │  Driver  │
      └────┬─────┘          │          └────┬─────┘
           │               ││               │
      ┌────┴────┐    ┌────┴┴────┐    ┌────┴────┐
      │  Wheel  │    │ Weeding  │    │  Wheel  │
      │ Motor A │    │ Mech.    │    │ Motor B │
      └─────────┘    └─────────┘    └─────────┘
      
      ┌─────────┐                   ┌─────────┐
      │  Wheel  │                   │  Wheel  │
      │ Motor C │                   │ Motor D │
      └─────────┘                   └─────────┘
```

### 3.2 Dimensions & Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Length** | 35 cm | Fits between crop rows |
| **Width** | 25 cm | Narrow enough for row crops |
| **Height** | 18 cm (without solar panel) | Low center of gravity |
| **Ground clearance** | 8 cm | Clears small rocks/roots |
| **Weight** | ~3.5 kg | Light enough for one-hand carry |
| **Wheel diameter** | 12 cm | Knobby tire for soil traction |
| **Track width** | 20 cm | Adjustable for different row spacing |

### 3.3 Locomotion — 4-Wheel Skid-Steer Drive

**Why skid-steer (tank drive):**
- Simplest mechanical design — no steering linkages
- Zero turn radius — can rotate in place between rows
- Good traction on loose soil
- Fewer moving parts = higher reliability in dusty conditions
- Each side driven by one motor (left pair, right pair)

**Motor selection:**
- **Type:** N20 Micro Metal Gearmotor (100:1 ratio)
- **Stall torque:** ~4.5 kg·cm
- **No-load speed:** ~100 RPM → gives ~0.6 m/s at 12 cm wheels
- **Operating speed (loaded):** ~50 RPM → ~0.3 m/s (perfect for weeding)
- **Voltage:** 6V (compatible with 2S LiPo or 3.7V Li-ion with boost)

### 3.4 Weed Removal Mechanism

**Approach: Mechanical Under-Cutter with Precision Control**

```
                    Front View
           ┌──────────────────────┐
           │      Robot Body       │
           └──────────┬───────────┘
                      │
              ┌───────┴───────┐
              │  Linear Act.   │  (height adjustment)
              └───────┬───────┘
                      │
              ┌───────┴───────┐
              │   DC Motor    │
              └───────┬───────┘
                      │
              ┌───────┴───────┐
              │   Cutter      │
              │   Blade       │ ← 4cm star blade
              └───────────────┘
                   ═╤═
              Soil surface
```

**How it works:**
1. Robot identifies weed via camera
2. Linear actuator lowers cutter blade to 1-2 cm below soil surface
3. Blade spins at 2000 RPM, cutting weed roots
4. Blade retracts after 0.5 seconds
5. If weed is large, robot does a small back-and-forth motion

**Specs:**
| Component | Value |
|-----------|-------|
| **Cutter motor** | 130-size DC coreless (3.7-6V) |
| **Blade type** | 3-prong star blade, 4 cm diameter |
| **Blade material** | Stainless steel (corrosion resistant) |
| **Linear actuator** | Micro servo + leadscrew mechanism |
| **Depth control** | ±3 mm precision via encoder |
| **Cut cycle time** | ~1 second per weed |

**Why mechanical cutting over alternatives:**

| Method | Cost | Complexity | Effectiveness | Soil Health |
|--------|------|-----------|--------------|-------------|
| Mechanical cutter | ✅ Low | ✅ Low | ✅ 80-90% | ✅ Good |
| Laser weeding | ❌ High | ❌ High | ✅ 95% | ✅ Good |
| Precision herbicide | 💲 Medium | ✅ Medium | ✅ 90% | ❌ Bad |
| Flame weeding | 💲 Medium | ❌ Medium | ✅ 85% | ⚠️ Mixed |
| Manual pulling | ✅ Low | ✅ None | ✅ 95% | ✅ Good |

---

## 4. ELECTRONICS & CIRCUIT DESIGN

### 4.1 System Block Diagram

```
                    ┌──────────────────┐
                    │   Solar Panel     │
                    │   10W, 5V USB     │
                    └────────┬─────────┘
                             │
                    ┌────────┴────────┐
                    │  TP4056 + 1S    │
                    │  Li-ion Charger │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐        ┌──────────────────┐
                    │  3.7V Li-ion    │        │  5V Boost Conv.  │
                    │  Battery Pack   │──┬─────►│  MT3608 (for     │
                    │  2x 18650       │  │      │  motors & RPi)   │
                    │  (5000 mAh)     │  │      └──────────────────┘
                    └─────────────────┘  │
                                         │      ┌──────────────────┐
                                         ├─────►│  3.3V LDO (for   │
                                         │      │  ESP32, sensors) │
                                         │      └──────────────────┘
                                         │
                    ┌─────────────────┐  │
                    │  Raspberry Pi 5 │  │  (main compute)
                    │  (runs CV/ML)   │◄─┤
                    │  GPIO UART I2C  │  │
                    └────────┬────────┘  │
                             │USB        │
                    ┌────────┴────────┐  │
                    │  USB Camera     │  │
                    │  (wide angle)   │  │
                    └─────────────────┘  │
                                          │
                    ┌─────────────────┐  │
                    │  ESP32 WROOM    │◄─┤  (motor control & comms)
                    │  UART→RPi       │  │
                    │  (motor control)│  │
                    └────────┬────────┘  │
                             │           │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
   │  Motor      │   │  Motor      │   │  Motor      │
   │  Driver     │   │  Driver     │   │  Driver     │
   │  DRV8833    │   │  DRV8833    │   │  DRV8833    │
   │  (L motors) │   │  (R motors) │   │  (cutter)   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
   ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
   │  Left Wheel │   │ Right Wheel │   │ Cutter      │
   │  Motors (2) │   │ Motors (2)  │   │ Motor       │
   └─────────────┘   └─────────────┘   └─────────────┘
   
   ┌──────────────────┐   ┌──────────────────┐
   │  GPS (NEO-6M)    │   │  IMU (MPU6050)   │
   │  UART→ESP32      │   │  I2C→ESP32       │
   └──────────────────┘   └──────────────────┘

   ┌──────────────────┐   ┌──────────────────┐
   │  LoRa Module     │   │  Compass        │
   │  (RFM95W)        │   │  (HMC5883L)     │
   │  SPI→ESP32       │   │  I2C→ESP32      │
   └──────────────────┘   └──────────────────┘

   ┌──────────────────┐   ┌──────────────────┐
   │  Ultrasonic x4   │   │  Soil Moisture   │
   │  (HC-SR04)       │   │  Sensor (opt.)   │
   │  GPIO→ESP32      │   │  ADC→ESP32       │
   └──────────────────┘   └──────────────────┘
```

### 4.2 Component Selection & Justification

| Component | Model | Qty | Unit Cost | Total | Why |
|-----------|-------|-----|-----------|-------|-----|
| **Main Computer** | Raspberry Pi 5 (2GB) | 1 | $50 | $50 | Runs ML inference for weed detection, handles high-level logic |
| **Motor Controller** | ESP32 WROOM DevKit | 1 | $5 | $5 | Real-time motor control, sensor fusion, LoRa/WiFi comms |
| **Camera** | Raspberry Pi Camera Module 3 | 1 | $25 | $25 | Wide angle, autofocus, good for weed classification |
| **Left Motor Driver** | DRV8833 Dual Motor Driver | 1 | $3 | $3 | 1.2A/channel, low voltage drop, compact |
| **Right Motor Driver** | DRV8833 Dual Motor Driver | 1 | $3 | $3 | Same, second channel for cutter |
| **Drive Motors** | N20 Micro Metal 100:1 (6V) | 4 | $4 | $16 | Proven, cheap, reliable for small robots |
| **Cutter Motor** | 130 Coreless DC (5V) | 1 | $1 | $1 | High RPM, tiny, cheap |
| **GPS** | NEO-6M / GY-GPS6MV2 | 1 | $8 | $8 | ~2.5m accuracy, sufficient for row navigation |
| **IMU** | MPU6050 (6-axis) | 1 | $2 | $2 | Accelerometer + gyro for dead reckoning |
| **Compass** | HMC5883L | 1 | $2 | $2 | Heading reference between GPS fixes |
| **LoRa Radio** | RFM95W (868 MHz) | 1 | $8 | $8 | Long-range mesh comms (1-5 km) |
| **Battery** | 18650 Li-ion (2500 mAh) | 2 | $4 | $8 | 5000 mAh @ 3.7V (~18 Wh) |
| **Solar Charge** | TP4056 + MT3608 boost | 1 | $3 | $3 | Solar charging module |
| **Solar Panel** | 10W Poly-Si (foldable) | 1 | $15 | $15 | Charges battery in ~3h full sun |
| **Ultrasonic** | HC-SR04 | 4 | $1 | $4 | Obstacle detection, crop row following |
| **Soil Moisture** | Capacitive (not resistive) | 1 | $3 | $3 | Optional: soil data collection |
| **Linear Actuator** | Micro servo + lead screw | 1 | $5 | $5 | For cutter height adjustment |
| **Chassis** | 3D printed PETG / laser-cut plywood | 1 | $10 | $10 | Durable, repairable locally |
| **Wheels** | 12 cm knobby rubber | 4 | $3 | $12 | Traction on loose soil |
| | | | **Total** | **~$185** | |
| **Swarm (5 units)** | | 5 | $185 | **~$925** | Covers ~0.5 hectare |

### 4.3 Power Budget

| Component | Load (avg) | Load (peak) | Duty Cycle | Avg Power |
|-----------|-----------|-------------|------------|-----------|
| Raspberry Pi 5 | 3W (0.6A @ 5V) | 7W (ML infer.) | 100% | 3.5W |
| ESP32 | 0.3W | 0.5W (radio TX) | 100% | 0.3W |
| Drive Motors (4) | 2W (0.5A each) | 8W (stall) | 60% | 1.2W |
| Cutter Motor | 1W | 3W (stall) | 10% | 0.1W |
| Camera | 0.5W | 0.5W | 100% | 0.5W |
| LoRa (idle/TX) | 0.01W / 0.1W | 0.1W | 5% TX | 0.01W |
| Sensors (total) | 0.1W | 0.15W | 100% | 0.1W |
| **Total** | | | | **~5.7W** |

**Battery life:** 18 Wh / 5.7 W = **~3 hours continuous operation**
**With solar (500 mW avg in partial sun):** extends to **~3.5 hours**
**Charge time:** 18 Wh / 10W solar = **~2 hours full sun**

### 4.4 Circuit Schematic (High-Level)

```
                      ┌─────────────────────────────┐
                      │         RASPBERRY PI 5       │
                      │                              │
                      │  CSI ─► Camera               │
                      │  USB ─► (optional: LTE dongle)│
                      │  GPIO UART TX/RX ───► ESP32  │
                      │  I2C (optional sensors)       │
                      │  5V Power In ─► from battery │
                      └──────────────┬───────────────┘
                                     │ UART @ 115200
                                     │ (command protocol)
                      ┌──────────────┴───────────────┐
                      │          ESP32 WROOM          │
                      │                              │
                      │  UART RX/TX ◄─► RPi          │
                      │  I2C SDA/SCL ── MPU6050      │
                      │                  HMC5883L     │
                      │  SPI CS/MOSI/MISO ── RFM95W  │
                      │  GPIO ── DRV8833 (left)      │
                      │         DRV8833 (right)      │
                      │         DRV8833 (cutter)     │
                      │         Servo (linear act.)  │
                      │  UART ── NEO-6M GPS          │
                      │  GPIO ── HC-SR04 x4          │
                      │  ADC ── Soil moisture        │
                      │  GPIO ── Status LEDs         │
                      │  GPIO ── Button (start/stop) │
                      └─────────────────────────────┘
```

**Pin Mapping (ESP32 → peripherals):**

```
ESP32 Pin   │ Peripheral       │ Notes
────────────┼──────────────────┼─────────────────────────
GPIO 16,17  │ UART2 → RPi TX/RX│ Control protocol
GPIO 21,22  │ I2C SDA/SCL     │ MPU6050, HMC5883L
GPIO 5,18,19│ SPI (LoRa)      │ RFM95W CS=5, MOSI=18, MISO=19
GPIO 23     │ LoRa SCK        │ SPI clock
GPIO 25     │ LoRa RST        │ Reset
GPIO 26     │ LoRa DIO0       │ Interrupt
GPIO 13,12  │ DRV8833 L_IN1/2 │ Left motors PWM
GPIO 14,27  │ DRV8833 R_IN1/2 │ Right motors PWM
GPIO 32,33  │ DRV8833 C_IN1/2 │ Cutter motor PWM
GPIO 15     │ Servo signal    │ Linear actuator
GPIO 34     │ UART2 RX        │ GPS NEO-6M
GPIO 35     │ (option)        │ 
GPIO 36     │ ADC             │ Soil moisture sensor
GPIO 4,2    │ Trig/Echo       │ HC-SR04 front
GPIO 0,15   │ Trig/Echo       │ HC-SR04 rear (if needed)
```

---

## 5. SOFTWARE ARCHITECTURE

### 5.1 High-Level Logic Stack

```
┌───────────────────────────────────────────────────────┐
│                   SWARM COORDINATOR                    │
│  (Python on RPi 5 — primary node or base station)     │
│                                                       │
│  ┌─────────┐ ┌───────────┐ ┌───────────────────┐     │
│  │ Swarm   │ │ Field Map │ │ Task Allocation   │     │
│  │ Manager │ │ & History │ │ (ant colony opt.) │     │
│  └────┬────┘ └─────┬─────┘ └────────┬──────────┘     │
│       │            │                │                 │
│  ┌────┴────────────┴────────────────┴──────────┐     │
│  │            ROBOT CONTROLLER                  │     │
│  │  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │     │
│  │  │ Weed CV  │ │ Navigator│ │ Communicator│  │     │
│  │  │ (TFLite) │ │(GPS+IMU) │ │ (LoRaMesh)  │  │     │
│  │  └────┬─────┘ └────┬─────┘ └──────┬──────┘  │     │
│  └───────┼─────────────┼──────────────┼────────┘     │
└──────────┼─────────────┼──────────────┼──────────────┘
           │ (serial)    │              │
┌──────────┴─────────────┴──────────────┴──────────────┐
│              FIRMWARE (ESP32 - Arduino)                │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐    │
│  │ Motor    │ │ Sensor   │ │ LoRa   │ │ PID    │    │
│  │ Control  │ │ Fusion   │ │ Radio  │ │ Nav    │    │
│  └──────────┘ └──────────┘ └────────┘ └────────┘    │
└───────────────────────────────────────────────────────┘
```

### 5.2 Weed Detection — Computer Vision

**Approach: Lightweight CNN (MobileNetV2) on Raspberry Pi 5**

The RPi 5 can run ~5-10 FPS inference with TensorFlow Lite on MobileNetV2, which is sufficient for a robot moving at 0.3 m/s.

```
Input frame (640x480)
    │
    ▼
┌──────────────────────┐
│   Crop Region        │
│   (bottom 60% of     │
│    frame — ground)   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Segmentation       │  → Simple: green mask + position
│   (color threshold)  │  → Advanced: MobileNetV2 per patch
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Weed vs Crop       │
│   Classification     │  → Each green blob classified
│                      │  → Reject known crop patterns
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Weed Position      │  → Pixel coords → robot-relative coords
│   Mapping            │  → Queue cutting order
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   Cutting Command    │  → Send ESP32: (x, y, depth)
└──────────────────────┘
```

**Training data strategy:**
1. Start with labeled open-source weed datasets (DeepWeed, WeedNet, Crop/Weed Field Image Dataset)
2. Collect local Tanzanian crop/weed images for fine-tuning
3. Use transfer learning — MobileNetV2 pre-trained on ImageNet

**Initial deployment strategy:**
- **Phase 1:** Simple color thresholding (green = vegetation) + row-following (avoid crops based on known row positions)
- **Phase 2:** Add ML classification once enough local data is collected

### 5.3 Navigation Logic

```
GPS fix + Compass heading
    │
    ▼
┌───────────────────────────┐
│   Row Navigation          │
│   (follow crop row)       │
│                           │
│   Input: GPS waypoints    │
│          Row endpoints    │
│                           │
│   Control:                │
│    • Follow compass       │
│    • Correct with GPS     │
│    • Ultrasonic: keep 20cm│
│      from crop on each side│
└──────────┬────────────────┘
           ▼
┌───────────────────────────┐
│   Row-End Turn            │
│   (at end of row)         │
│                           │
│   • Stop                  │
│   • Rotate 90°            │
│   • Drive forward 1 row   │
│   • Rotate -90°           │
│   • Start next row        │
└───────────────────────────┘
```

### 5.4 Swarm Coordination Algorithm

Inspired by **ant colony optimization** — each robot leaves "digital pheromone trails":

```
Algorithm: SwarmWeedCoverage
────────────────────────────

Initialize:
  - Field divided into grid cells (2m x 2m cells)
  - Each cell has a "weed density" value (0.0 - 1.0)
  - All robots start at charging station

Loop:
  1. Each robot broadcasts: {id, position, battery%, cell_status}
  2. Each robot maintains local copy of field heatmap
  3. If battery < 20%: return to charger
  4. If current cell weed_density < 0.1: 
     a. Check neighboring cells' density
     b. Move to highest-density neighbor cell
  5. If weed_density > threshold:
     a. Scan rows in cell systematically
     b. Detect and cut weeds
     c. Decrement local weed_density after cutting
  6. Broadcast updated cell info every 30 seconds

Swarm benefits:
  - Robot A finds weed hotspot → shares → robots B,C move to help
  - Grid coverage ensures no area is missed
  - Graceful degradation if one robot fails
```

### 5.5 Communication Protocol

**LoRa Mesh (ESP32 + RFM95W):**
- Frequency: 868 MHz (license-free in Tanzania)
- Range: 1-5 km line of sight
- Data rate: ~1 kbps (enough for position/status messages)
- Protocol: Custom lightweight binary protocol

**Message format (binary, ~20 bytes):**

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ ID │Seq │Type│Bat │Lat │Lon │Cell│WDen│Stat│CRC │                   │
│ 2B │ 1B │ 1B │ 1B │ 4B │ 4B │ 2B │ 1B │ 1B │ 2B │                   │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴───────────────────┘

Types:
  0x01 = STATUS (position, battery, cell)
  0x02 = WEED_REPORT (cell x, cell y, density)
  0x03 = HELP_REQUEST (robot stuck, needs assistance)
  0x04 = CHARGING (heading to base)
```

---

## 6. ANT COLONY INTELLIGENCE — EMERGENT BEHAVIOR

The swarm exhibits these emergent behaviors:

| Behavior | Mechanism | Benefit |
|----------|-----------|---------|
| **Weed hotspot concentration** | Robots move toward cells with high reported weed density | Fast response to weed outbreaks |
| **Uniform coverage** | Repulsive force from nearby robots prevents clustering | No area missed |
| **Graceful degradation** | If a robot fails, others expand coverage | System still works |
| **Automatic load balancing** | Low-battery robots return; charged ones take over | Continuous operation |
| **Path optimization** | Shortest-path routing via mesh reduces overlap | Energy efficiency |
| **Adaptive patrol** | Clean cells checked less often | More time on problem areas |

---

## 7. BUILD PHASES

### Phase 1: Single Robot Prototype (2-4 weeks)
- [ ] Build chassis (3D print or laser-cut plywood)
- [ ] Wire electronics (RPi + ESP32 + motors + sensors)
- [ ] Basic motor control (ESP32 drives motors via serial commands)
- [ ] Simple line/crop-row following
- [ ] Test: can it drive across a field?

### Phase 2: Weed Detection (2-3 weeks)
- [ ] Mount camera, get live feed
- [ ] Implement color-based vegetation detection
- [ ] Train MobileNetV2 on weed/crop dataset
- [ ] Test: can it identify weeds in real time?

### Phase 3: Weed Removal (1-2 weeks)
- [ ] Build and test cutter mechanism
- [ ] Integrate with detection pipeline
- [ ] Test: can it cut identified weeds?
- [ ] Validate: does the weed actually die?

### Phase 4: Navigation (2 weeks)
- [ ] GPS + compass row-following
- [ ] Row-end turn logic
- [ ] Field mapping
- [ ] Obstacle avoidance

### Phase 5: Swarm (2-3 weeks)
- [ ] LoRa mesh communication
- [ ] Swarm coordination algorithm
- [ ] Multi-robot field test
- [ ] Charging station behavior

**Total estimated time: ~10-14 weeks for v1**

---

## 8. COST BREAKDOWN

| Phase | Cost | What You Get |
|-------|------|-------------|
| Phase 1 (single prototype) | **~$185** | One working Siafu robot |
| Phase 2-3 upgrades | ~$30 | Camera + cutter parts |
| Phase 4 (extra sensors) | ~$20 | Better GPS, sensors |
| Phase 5 (swarm expansion) | ~$185 x N | N additional robots |
| **5-robot swarm total** | **~$1,020** | Full swarm system |

---

## 9. OPEN QUESTIONS & NEXT DECISIONS

Before building, we need to decide:

1. **Chassis material:** 3D printed PETG (stronger) or laser-cut plywood (cheaper, easier to modify)?
2. **Row detection:** Ultrasonic sensors or downward-looking optical flow sensor?
3. **Weed ML model:** Train from scratch on local data or use transfer learning?
4. **Solar panel:** Mounted on robot permanently, or a separate charging station array?
5. **GPS vs RTK:** Standard GPS ($8) with ~2.5m accuracy, or RTK-GPS ($100+) with cm accuracy?
6. **First field test:** Your family/neighbor's farm or a university test plot?

---

## 10. RECOMMENDED NEXT STEPS

1. **Order components** — I can generate a full AliExpress/Tindie parts list with links
2. **Design the chassis** — I can create 3D model files (OpenSCAD) for printing
3. **Write the firmware** — I can code the ESP32 motor control + LoRa comms
4. **Write the CV pipeline** — I can set up the weed detection TensorFlow Lite model
5. **Simulation first** — I can build a Webots/Gazebo simulation to test the swarm algorithm before hardware

**Where do you want to start?**

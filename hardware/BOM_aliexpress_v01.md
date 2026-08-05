# Siafu v0.1 — AliExpress BOM ("First Drive")
Target: drive 3 m straight → stop → turn 180° → return → stop (video'd).
Budget: **~$18–25 + shipping**. Order via search terms (AliExpress links rot; terms don't).

## Must-buy
| # | Item | Search term | Est. $ |
|---|------|-------------|--------|
| 1 | 4WD smart car chassis kit — 2 acrylic plates, 4× TT motors, 4× wheels, screws | `4WD smart car chassis TT motor acrylic` | 9–13 |
| 2 | L298N motor driver module | `L298N motor driver module` | 2–3 |
| 3 | 4× AA battery holder with switch + leads | `4 AA battery holder box with switch` | 1–2 |
| 4 | Breadboard MB-102 + jumper wires (MM + MF) | `MB-102 breadboard jumper wire kit` | 3–4 |

> **Key insight:** the kit's own acrylic chassis doubles as the v0.1 test chassis —
> the 3D printer becomes **optional**. Print the real Siafu body (`hardware/siafu_bot.stl`)
> as milestone 2, not the critical path.
> AA batteries themselves: buy locally (alkaline is fine for drive tests).

## Optional / later
| Item | Search term | Est. $ |
|------|-------------|--------|
| ESP32-S3 DevKitC-1 (if not reusing existing devkit) | `ESP32-S3 DevKitC-1 N8R8` | 6–8 |
| TB6612FNG driver (cleaner than L298N; needs 2×) | `TB6612FNG motor driver` | 2 ea |
| 2S LiPo 7.4V 1500 mAh + charger (later upgrade) | `2S LiPo 7.4V 1500mAh XT60` | 12–15 |
| LM2596 buck converter (stable 5 V rail) | `LM2596 buck converter` | 1.5 |

## Sourcing rules
- Sellers ≥ 4.5★, prefer **"Choice" shipping** (10–15 days, tracked).
- Order **this week** so parts land before mid-term.
- Skip anything without tracking.

## Wiring (v0.1)
```
AA holder (6V) ──► L298N VCC          AA holder ──► ESP32-S3 5V/VIN (via breadboard)
L298N GND ── common
L298N IN1..IN4 ── ESP32-S3 GPIOs
L298N ENA/ENB ── PWM-capable GPIOs (or tie high = full speed)
Channel A ── left 2 motors (parallel)      Channel B ── right 2 motors (parallel)
```

## Test script
1. Flash differential-drive firmware (PlatformIO, espressif32, ESP32-S3).
2. Floor test: forward 3 m → stop → 180° → return → stop.
3. Video it → portfolio card flips to "🔧 Prototype — first controlled drive".

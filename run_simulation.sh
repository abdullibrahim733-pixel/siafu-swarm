#!/bin/bash
# Siafu — Launch the Webots Swarm Simulation
# Usage: ./run_simulation.sh [world_name]
# Default: field.wbt

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SIM_DIR="$SCRIPT_DIR/simulation"
WORLD="${1:-field.wbt}"
WORLD_PATH="$SIM_DIR/worlds/$WORLD"

if [ ! -f "$WORLD_PATH" ]; then
    echo "Error: World file not found at $WORLD_PATH"
    echo "Available worlds:"
    ls "$SIM_DIR/worlds/" 2>/dev/null
    exit 1
fi

echo "========================================="
echo "  Siafu Swarm — Webots Simulation"
echo "========================================="
echo "  World:    $WORLD"
echo "  Path:     $WORLD_PATH"
echo "  Webots:   $(which webots)"
echo ""
echo "Launching Webots..."
echo "  Tip: Press Ctrl+Z to pause simulation"
echo "  Tip: Press Ctrl+T to toggle time display"
echo "========================================="
echo ""

cd "$SIM_DIR"
webots "$WORLD_PATH"

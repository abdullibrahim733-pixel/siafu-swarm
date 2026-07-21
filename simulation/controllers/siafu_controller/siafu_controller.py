"""
Siafu — Webots Robot Controller v2
Fixed: coordinate system handling, row following
"""
import sys, math, struct, random, time

WEBOTS_PYTHON = '/usr/local/webots/lib/controller/python'
if WEBOTS_PYTHON not in sys.path:
    sys.path.insert(0, WEBOTS_PYTHON)
from controller import Robot, Camera, GPS, Compass, Gyro, DistanceSensor, Emitter, Receiver, PositionSensor, Motor

TIME_STEP = 32
SPEED_FORWARD = 3.0
SPEED_TURN = 2.0
SPEED_SLOW = 1.0

# Color thresholds for weed detection (RGB)
GREEN_THRESHOLD = 50      # Min green pixels to trigger weed
WEED_PIXEL_MIN = 30

MSG_WEED_FOUND = 1
MSG_WEED_CLEARED = 2

# Field: robot starts at x=-5.5, z=-1.5 (field is 20x20m, centered at origin)
FIELD_MIN_X = -7.0
FIELD_MAX_X = 7.0
FIELD_MIN_Z = -7.0
FIELD_MAX_Z = 7.0


class SiafuController:
    def __init__(self):
        self.robot = Robot()
        self.name = self.robot.getName()
        self.timestep = int(self.robot.getBasicTimeStep())

        # Extract robot ID
        try:
            self.robot_id = int(self.name.split('_')[-1])
        except:
            self.robot_id = 1

        print(f"[{self.name}] Initializing...")

        # Sensors
        self.camera = self.robot.getDevice('camera')
        if self.camera:
            self.camera.enable(self.timestep)
            self.cam_width = self.camera.getWidth()
            self.cam_height = self.camera.getHeight()
        else:
            self.cam_width = 0
            self.cam_height = 0

        self.gps = self.robot.getDevice('gps')
        if self.gps:
            self.gps.enable(self.timestep)

        self.compass_dev = self.robot.getDevice('compass')
        if self.compass_dev:
            self.compass_dev.enable(self.timestep)

        # Ultrasonic sensors
        self.us = {}
        for name in ['us_front', 'us_left', 'us_right']:
            s = self.robot.getDevice(name)
            if s:
                s.enable(self.timestep)
                self.us[name] = s

        # Communication
        self.emitter = self.robot.getDevice('lora_tx')
        self.receiver = self.robot.getDevice('lora_rx')
        if self.receiver:
            self.receiver.enable(self.timestep)

        # Motors
        self.left_motor = self.robot.getDevice('left_motor')
        self.right_motor = self.robot.getDevice('right_motor')
        if self.left_motor:
            self.left_motor.setPosition(float('inf'))
            self.left_motor.setVelocity(0.0)
        if self.right_motor:
            self.right_motor.setPosition(float('inf'))
            self.right_motor.setVelocity(0.0)

        # State
        self.state = 'DRIVE'
        self.weed_count = 0
        self.step_count = 0
        self.start_time = self.robot.getTime()
        self.direction = 1  # 1 = forward in current heading
        
        # Obstacle avoidance
        self.avoid_counter = 0
        
        print(f"[{self.name}] Ready. Steps at {self.timestep}ms")

    def get_position(self):
        """Returns (x, z) in meters."""
        if self.gps:
            v = self.gps.getValues()
            return (v[0], v[2])
        return None

    def get_heading_deg(self):
        """Compass heading in degrees. 0 = +X axis."""
        if not self.compass_dev:
            return 0.0
        n = self.compass_dev.getValues()
        # n = (north_x, north_y, north_z)
        # With NUE: +X = North, so heading = atan2(north_z, north_x)
        heading = math.degrees(math.atan2(n[2], n[0]))
        return heading

    def set_speed(self, left, right):
        if self.left_motor:
            self.left_motor.setVelocity(left)
        if self.right_motor:
            self.right_motor.setVelocity(-right)  # Right side inverted for skid-steer

    def stop(self):
        self.set_speed(0, 0)

    def drive_forward(self, speed=SPEED_FORWARD):
        self.set_speed(speed, speed)

    def drive_backward(self, speed=SPEED_SLOW):
        self.set_speed(-speed, -speed)

    def turn_left(self, speed=SPEED_TURN):
        self.set_speed(-speed, speed)

    def turn_right(self, speed=SPEED_TURN):
        self.set_speed(speed, -speed)

    def detect_weeds(self):
        """Color-based weed detection from camera image."""
        if not self.camera:
            return 0, []

        img = self.camera.getImage()
        if not img:
            return 0, []

        w, h = self.cam_width, self.cam_height

        green_count = 0
        # Scan lower half of image (ground)
        start_row = h // 3
        for y in range(start_row, h):
            for x in range(0, w, 2):  # Sub-sample for speed
                idx = (y * w + x) * 4
                if idx + 3 >= len(img):
                    continue
                b, g, r = img[idx], img[idx + 1], img[idx + 2]
                if g > r * 1.15 and g > b * 1.15 and g > 40:
                    green_count += 1

        has_weed = green_count > WEED_PIXEL_MIN
        if has_weed:
            return green_count, [0.1]  # Approx 10cm ahead
        return 0, []

    def run(self):
        print(f"[{self.name}] Control loop started.")
        while self.robot.step(self.timestep) != -1:
            self.step_count += 1
            pos = self.get_position()
            heading = self.get_heading_deg()
            
            # Obstacle detection
            obstacle = min(
                (self.us.get(n, type('', (), {'getValue': lambda: float('inf')})()).getValue()
                 for n in ['us_front', 'us_left', 'us_right']),
                default=float('inf')
            )

            # Weed detection
            weeds_found, _ = self.detect_weeds()

            # --- State machine ---
            if self.avoid_counter > 0:
                self.avoid_counter -= 1
                self.turn_right(SPEED_TURN)
                continue

            if obstacle < 0.2:
                self.stop()
                self.avoid_counter = 20
                continue

            if weeds_found > WEED_PIXEL_MIN:
                self.stop()
                self.weed_count += 1
                if pos:
                    print(f"[{self.name}] Weed #{self.weed_count} at ({pos[0]:.2f}, {pos[1]:.2f})")
                # Simulate cutting
                for _ in range(5):
                    self.robot.step(self.timestep)
                continue

            # Drive forward - follow along x-axis (North in NUE)
            self.drive_forward(SPEED_FORWARD)

            # Check field boundaries
            if pos:
                if pos[0] > FIELD_MAX_X:
                    # Hit North boundary - turn around
                    self.stop()
                    self.turn_left(SPEED_TURN)
                    for _ in range(30):
                        self.robot.step(self.timestep)
                    self.direction *= -1
                elif pos[0] < FIELD_MIN_X:
                    # Hit South boundary - turn around
                    self.stop()
                    self.turn_left(SPEED_TURN)
                    for _ in range(30):
                        self.robot.step(self.timestep)
                    self.direction *= -1

            # Print status every 4 seconds
            if self.step_count % 125 == 0:
                if pos:
                    print(f"[{self.name}] State={self.state} pos=({pos[0]:.2f},{pos[1]:.2f}) "
                          f"heading={heading:.0f}° weeds={self.weed_count}")
                else:
                    print(f"[{self.name}] Step={self.step_count} weeds={self.weed_count}")


def main():
    SiafuController().run()

if __name__ == '__main__':
    main()

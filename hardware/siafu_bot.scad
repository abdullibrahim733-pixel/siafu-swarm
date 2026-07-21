/**
 * Siafu — Swarm Agriculture Robot
 * OpenSCAD 3D Model
 * 
 * Dimensions (mm):
 *   Body: 120 × 100 × 40
 *   Wheels: Ø40 × 20
 *   Wheelbase: 100 × 70
 *   Ground clearance: 8
 */

// =============================
// PARAMETERS
// =============================
$fn = 32;

// Body
body_lx = 120;
body_ly = 100;
body_lz = 40;
body_round = 6;

// Chassis plate
chassis_z = 4;

// Wheels
wheel_r = 20;
wheel_w = 16;
wheel_tread = 3;
hub_r = 6;
axle_d = 4;

// Wheel positions (centers)
wb_x = 85;   // longitudinal wheelbase
wb_y = 72;   // lateral wheelbase

// Solar panel
solar_lx = 80;
solar_ly = 55;
solar_lz = 2;

// Camera housing
cam_lx = 16;
cam_ly = 10;
cam_lz = 12;
cam_angle = 30;  // downward tilt (degrees)

// Cutter
cutter_lx = 30;
cutter_ly = 8;
cutter_lz = 4;
blade_w = 40;

// Ultrasonic sensor
us_r = 5;
us_lz = 8;

// Antenna
ant_r = 2;
ant_h = 50;

// LED
led_r = 4;
led_h = 3;

// =============================
// MODULES
// =============================

// ----- Main Body -----
module body() {
  color("#4dabf7") {
    difference() {
      minkowski() {
        cube([body_lx - body_round, body_ly - body_round, body_lz - 4], center=true);
        sphere(r = body_round/2, $fn=16);
      }
      // Bottom cutout for electronics bay
      translate([0, 0, -body_lz/2 + chassis_z]) {
        cube([body_lx - 20, body_ly - 16, body_lz], center=true);
      }
    }
  }
}

// ----- Chassis base plate -----
module chassis() {
  color("#495057") {
    translate([0, 0, -body_lz/2 + chassis_z/2]) {
      cube([body_lx - 8, body_ly - 8, chassis_z], center=true);
    }
  }
}

// ----- Solar Panel -----
module solar_panel() {
  color("#212529") {
    translate([0, body_ly/2 - solar_ly/2 - 12, body_lz/2 + solar_lz/2]) {
      cube([solar_lx, solar_ly, solar_lz], center=true);
    }
  }
}

// ----- Wheel -----
module wheel() {
  // Tire
  color("#343a40") {
    difference() {
      cylinder(r=wheel_r, h=wheel_w, center=true);
      translate([0, 0, 0])
        cylinder(r=wheel_r - wheel_tread, h=wheel_w + 1, center=true);
    }
  }
  // Tread pattern
  color("#495057") {
    for (i = [0:15]) {
      rotate([0, 0, i * 360/16])
        translate([wheel_r - 2, 0, 0])
          cube([3, 2, wheel_w], center=true);
    }
  }
  // Hub
  color("#868e96") {
    cylinder(r=hub_r, h=wheel_w + 2, center=true);
  }
  // Axle hole
  color("#212529") {
    cylinder(r=axle_d/2, h=wheel_w + 4, center=true);
  }
}

// ----- All 4 Wheels -----
module wheels() {
  xf = wb_x/2;
  xr = -wb_x/2;
  yl = -wb_y/2;
  yr = wb_y/2;
  
  for (x = [xf, xr]) {
    for (y = [yl, yr]) {
      translate([x, y, -body_lz/2 - wheel_r + chassis_z]) {
        rotate([90, 0, 0]) wheel();
      }
    }
  }
}

// ----- Camera (front, downward angle) -----
module camera() {
  color("#868e96") {
    translate([body_lx/2 + 4, body_ly/6, body_lz/4]) {
      rotate([cam_angle, 0, 0]) {
        // Camera body
        cube([cam_lx, cam_ly, cam_lz], center=true);
        // Lens
        color("#212529") {
          translate([0, 0, cam_lz/2 + 1])
            cylinder(r=cam_lx/3, h=2, center=true);
        }
      }
    }
  }
}

// ----- Cutter Mechanism -----
module cutter() {
  color("#dee2e6") {
    // Mount
    translate([body_lx/2 + cutter_lx/2 - 4, -body_ly/4, 0]) {
      cube([cutter_lx, cutter_ly, cutter_lz], center=true);
    }
  }
  // Blade
  color("#adb5bd") {
    translate([body_lx/2 + cutter_lx + 6, -body_ly/4, 0]) {
      rotate([90, 0, 0]) {
        linear_extrude(height=cutter_ly, center=true, convexity=4)
          polygon(points=[
            [-blade_w/2, 0],
            [-blade_w/3, 8],
            [blade_w/3, 8],
            [blade_w/2, 0],
            [blade_w/3, -2],
            [-blade_w/3, -2]
          ]);
      }
    }
  }
}

// ----- Ultrasonic Sensors -----
module ultrasonic() {
  color("#ffd43b") {
    cylinder(r=us_r, h=us_lz, center=true);
  }
  color("#212529") {
    translate([0, 0, us_lz/2 + 1]) {
      cylinder(r=2, h=1.5, center=true);
    }
  }
}

module ultrasonics() {
  // Front (center)
  translate([body_lx/2 + 2, 0, body_lz/4]) {
    rotate([90, 0, 0]) ultrasonic();
  }
  // Left
  translate([body_lx/4, -body_ly/2 - 2, body_lz/4]) {
    rotate([0, 90, 0]) ultrasonic();
  }
  // Right
  translate([body_lx/4, body_ly/2 + 2, body_lz/4]) {
    rotate([0, -90, 0]) ultrasonic();
  }
}

// ----- LoRa Antenna -----
module antenna() {
  color("#adb5bd") {
    translate([-body_lx/2 + 15, body_ly/2 - 10, body_lz/2]) {
      cylinder(r=ant_r, h=ant_h);
    }
  }
  color("#868e96") {
    translate([-body_lx/2 + 15, body_ly/2 - 10, body_lz/2 + ant_h]) {
      sphere(r=3);
    }
  }
}

// ----- Status LED -----
module status_led() {
  color("#40c057") {
    translate([body_lx/2 - 18, body_ly/2 - 12, body_lz/2 + led_h/2]) {
      cylinder(r=led_r, h=led_h, center=true);
    }
  }
}

// ----- Electronics Bay (bottom) -----
module electronics_bay() {
  color("#212529") {
    translate([-15, 0, -body_lz/2 - 2]) {
      cube([50, 60, 4], center=true);
    }
  }
  // Raspberry Pi 5 indicator
  color("#1e7e34") {
    translate([-10, 5, -body_lz/2 - 3]) {
      cube([30, 20, 1], center=true);
    }
  }
  // ESP32 indicator
  color("#2b8a3e") {
    translate([-10, -15, -body_lz/2 - 3]) {
      cube([20, 12, 1], center=true);
    }
  }
}

// ----- Decal / Branding -----
module branding() {
  color("#ffffff") {
    translate([-10, 0, body_lz/2 + solar_lz + 1]) {
      linear_extrude(height=0.5)
        text("SIAFU", size=12, halign="center", valign="center", font="Liberation Sans:style=Bold");
    }
  }
}

// =============================
// ASSEMBLY
// =============================

module siafu() {
  // Layered from bottom to top
  wheels();
  electronics_bay();
  chassis();
  body();
  ultrasonics();
  camera();
  cutter();
  antenna();
  status_led();
  solar_panel();
  branding();
}

// Render
siafu();

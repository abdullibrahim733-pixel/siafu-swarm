// Siafu — Swarm Agriculture Robot Chassis
// Parametric 3D-printable design
// Units: millimeters

// ==========================================
// PARAMETERS (adjustable for your needs)
// ==========================================

// Chassis dimensions
chassis_length   = 150;  // mm
chassis_width    = 120;  // mm
chassis_height   = 8;    // mm (base plate thickness)
wall_thickness   = 3;    // mm for vertical walls

// Wheel parameters
wheel_diameter   = 60;   // mm (~12cm scaled down for printing)
wheel_width      = 20;   // mm
n20_mount_spacing = 12;  // mm (N20 screw hole spacing)
n20_mount_diameter = 2.5; // mm (M2.5 screw)

// Electronics bay
bay_length       = 80;   // mm
bay_width        = 60;   // mm
bay_height       = 40;   // mm (lid height)

// Cutter mechanism
cutter_arm_length = 40;  // mm
cutter_blade_diameter = 20; // mm (scaled for print)

// Solar panel mount
solar_width      = 100;  // mm
solar_length     = 70;   // mm

// General
screw_diameter   = 3;    // mm (M3 screw)
corner_radius    = 8;    // mm (fillet radius)
layer_height     = 0.2;  // mm (print layer height - for tolerances)
clearance        = 0.3;  // mm (clearance for moving parts)

// ==========================================
// MODULES
// ==========================================

// Utility: Rounded rectangle
module rounded_rect(w, d, h, r) {
    linear_extrude(height = h)
        offset(r = r)
            square([w - 2*r, d - 2*r], center = true);
}

// Utility: Screw hole
module screw_hole(diameter = screw_diameter, height = 10) {
    cylinder(d = diameter, h = height, $fn = 16, center = true);
}

// Utility: N20 motor mount hole pattern
module n20_mount_holes() {
    // N20 has 4 screw holes in a rectangular pattern
    for (x = [-n20_mount_spacing/2, n20_mount_spacing/2]) {
        for (y = [-n20_mount_spacing/2, n20_mount_spacing/2]) {
            translate([x, y, 0])
                cylinder(d = n20_mount_diameter, h = 20, $fn = 12, center = true);
        }
    }
    // Center shaft hole
    cylinder(d = 6, h = 20, $fn = 16, center = true);
}

// ==========================================
// CHASSIS BASE PLATE
// ==========================================

module chassis_base() {
    difference() {
        // Main plate with rounded corners
        rounded_rect(chassis_length, chassis_width, chassis_height, corner_radius);
        
        // Weight reduction cutouts
        for (x = [-30, 30]) {
            for (y = [-25]) {
                translate([x, y, chassis_height/2])
                    rounded_rect(30, 15, chassis_height + 1, 3);
            }
        }
        
        // Mounting screw holes (4 corners)
        for (x = [-chassis_length/2 + 15, chassis_length/2 - 15]) {
            for (y = [-chassis_width/2 + 12, chassis_width/2 - 12]) {
                translate([x, y, chassis_height/2])
                    screw_hole();
            }
        }
        
        // Cable routing holes
        translate([-chassis_length/4, 0, chassis_height/2])
            cylinder(d = 8, h = chassis_height + 1, $fn = 16, center = true);
        translate([chassis_length/4, 0, chassis_height/2])
            cylinder(d = 8, h = chassis_height + 1, $fn = 16, center = true);
    }
}

// ==========================================
// WHEEL MOUNT ARMS
// ==========================================

module wheel_mount_arm() {
    // Vertical arm extending from chassis
    difference() {
        union() {
            // Arm bracket
            hull() {
                translate([0, 0, -chassis_height/2])
                    cube([20, 8, chassis_height], center = true);
                translate([0, 0, -15])
                    cube([20, 8, 6], center = true);
            }
            // Motor mount plate
            translate([0, 0, -20])
                cube([24, 10, 8], center = true);
        }
        
        // N20 motor mounting holes
        translate([0, 0, -20])
            n20_mount_holes();
        
        // Screw holes to attach to chassis
        translate([0, 0, 0])
            cylinder(d = screw_diameter, h = 20, $fn = 12, center = true);
    }
}

// ==========================================
// ELECTRONICS BAY (waterproof lid)
// ==========================================

module electronics_bay() {
    difference() {
        union() {
            // Bay walls
            difference() {
                // Outer box
                rounded_rect(bay_length + 2*wall_thickness, 
                            bay_width + 2*wall_thickness, 
                            bay_height + chassis_height, 
                            corner_radius);
                
                // Inner hollow
                translate([0, 0, chassis_height])
                    rounded_rect(bay_length - clearance, 
                                bay_width - clearance, 
                                bay_height + 1, 
                                corner_radius - 2);
                
                // Ventilation slots on sides
                for (i = [0:4]) {
                    translate([-bay_length/2 - 1, -15 + i*8, chassis_height + 15])
                        cube([wall_thickness + 2, 4, 15], center = true);
                    translate([bay_length/2 + 1, -15 + i*8, chassis_height + 15])
                        cube([wall_thickness + 2, 4, 15], center = true);
                }
            }
            
            // Raspberry Pi mounting posts (inside bay)
            for (x = [-25, 25]) {
                for (y = [-15, 15]) {
                    translate([x, y, chassis_height])
                        cylinder(d = 5, h = 8, $fn = 12);
                }
            }
            
            // ESP32 mounting posts
            translate([0, -bay_width/4 + 8, chassis_height])
                cylinder(d = 4, h = 6, $fn = 12);
        }
        
        // Threaded insert holes for lid
        for (x = [-bay_length/2 + 8, bay_length/2 - 8]) {
            for (y = [-bay_width/2 + 8, bay_width/2 - 8]) {
                translate([x, y, bay_height + chassis_height - 3])
                    cylinder(d = screw_diameter, h = 6, $fn = 12);
            }
        }
        
        // RPi mounting post screw holes
        for (x = [-25, 25]) {
            for (y = [-15, 15]) {
                translate([x, y, chassis_height + 6])
                    cylinder(d = 2.5, h = 8, $fn = 12);
            }
        }
    }
}

// ==========================================
// ELECTRONICS BAY LID
// ==========================================

module bay_lid() {
    difference() {
        union() {
            rounded_rect(bay_length + 2*wall_thickness + 1,
                        bay_width + 2*wall_thickness + 1,
                        3, corner_radius);
            // Rubber seal lip
            translate([0, 0, -1])
                rounded_rect(bay_length + 0.5,
                            bay_width + 0.5,
                            2, corner_radius - 1);
        }
        
        // Screw holes aligned with bay
        for (x = [-bay_length/2 + 8, bay_length/2 - 8]) {
            for (y = [-bay_width/2 + 8, bay_width/2 - 8]) {
                translate([x, y, 0])
                    cylinder(d = screw_diameter, h = 10, $fn = 12, center = true);
            }
        }
        
        // Antenna passthrough
        translate([bay_length/2 - 5, bay_width/2 - 5, 0])
            cylinder(d = 6, h = 10, $fn = 12, center = true);
    }
}

// ==========================================
// CUTTER MECHANISM MOUNT
// ==========================================

module cutter_assembly() {
    // Arm extending from front of chassis
    translate([chassis_length/2, 0, 0]) {
        difference() {
            union() {
                // Main arm
                hull() {
                    translate([-10, 0, -chassis_height/2])
                        cube([10, 30, chassis_height], center = true);
                    translate([cutter_arm_length/2, 0, -10])
                        cube([cutter_arm_length, 20, 6], center = true);
                }
                
                // Servo mount
                translate([cutter_arm_length + 5, 0, -5])
                    cube([15, 24, 12], center = true);
                
                // Blade guard
                translate([cutter_arm_length + 10, 0, -8])
                    cylinder(d = cutter_blade_diameter + 10, h = 4, $fn = 24, center = true);
            }
            
            // Servo screw holes
            translate([cutter_arm_length + 5, -8, -5])
                cylinder(d = 2, h = 20, $fn = 12, center = true);
            translate([cutter_arm_length + 5, 8, -5])
                cylinder(d = 2, h = 20, $fn = 12, center = true);
            
            // Weight reduction
            translate([cutter_arm_length/2, 0, -10])
                cube([cutter_arm_length - 10, 10, 8], center = true);
        }
    }
}

// ==========================================
// SOLAR PANEL MOUNT
// ==========================================

module solar_mount() {
    difference() {
        translate([0, 0, bay_height + chassis_height])
            rounded_rect(solar_length, solar_width, 4, 5);
        
        // Screw holes
        for (x = [-solar_length/2 + 8, solar_length/2 - 8]) {
            for (y = [-solar_width/2 + 8, solar_width/2 - 8]) {
                translate([x, y, bay_height + chassis_height + 2])
                    cylinder(d = 3, h = 10, $fn = 12, center = true);
            }
        }
        
        // Cable passthrough
        translate([0, 0, bay_height + chassis_height + 2])
            cylinder(d = 10, h = 10, $fn = 16, center = true);
    }
    
    // Support pillars connecting to chassis
    for (x = [-solar_length/2 + 8, solar_length/2 - 8]) {
        for (y = [-solar_width/2 + 8, solar_width/2 - 8]) {
            translate([x, y, chassis_height]) {
                difference() {
                    cylinder(d = 8, h = bay_height, $fn = 12);
                    translate([0, 0, bay_height - 5])
                        cylinder(d = screw_diameter, h = 10, $fn = 12);
                }
            }
        }
    }
}

// ==========================================
// WHEEL (printable)
// ==========================================

module wheel() {
    difference() {
        // Rim
        cylinder(d = wheel_diameter, h = wheel_width, $fn = 48);
        
        // Center hub cutout
        cylinder(d = 20, h = wheel_width + 1, $fn = 24, center = true);
        
        // Spoke pattern
        for (a = [0:60:300]) {
            rotate([0, 0, a])
                translate([7, 0, 0])
                    cube([wheel_diameter/2 - 10, 4, wheel_width + 1], center = true);
        }
        
        // Axle hole
        cylinder(d = 4, h = wheel_width + 1, $fn = 16, center = true);
        
        // D-cut for N20 shaft
        translate([0, 1.5, 0])
            cube([4, 3, wheel_width + 1], center = true);
    }
    
    // Tire tread
    for (a = [0:30:330]) {
        rotate([0, 0, a])
            translate([wheel_diameter/2 - 2, 0, 0])
                cube([3, 4, wheel_width - 4], center = true);
    }
}

// ==========================================
// CAMERA MOUNT (front)
// ==========================================

module camera_mount() {
    translate([chassis_length/2 - 5, chassis_width/2 - 12, 0]) {
        difference() {
            union() {
                translate([0, 0, 5])
                    cube([15, 10, 10], center = true);
                // Angled face
                translate([0, 5, 5])
                    rotate([-15, 0, 0])
                        cube([15, 5, 8], center = true);
            }
            
            // Camera module slot (Pi Camera)
            translate([0, 7, 6]) {
                rotate([-15, 0, 0]) {
                    cube([24, 7, 2], center = true);
                    // Lens hole
                    translate([0, 0, 2])
                        cylinder(d = 8, h = 4, $fn = 16, center = true);
                }
            }
        }
    }
}

// ==========================================
// MAIN ASSEMBLY
// ==========================================

module siafu_assembly() {
    // Chassis base
    chassis_base();
    
    // Electronics bay
    electronics_bay();
    
    // Cutter assembly (front)
    cutter_assembly();
    
    // Camera mount
    camera_mount();
    
    // Wheel mounts (4 corners)
    // Front left
    translate([-chassis_length/2 + 5, -chassis_width/2 + 5, 0])
        wheel_mount_arm();
    // Front right
    translate([-chassis_length/2 + 5, chassis_width/2 - 5, 0])
        wheel_mount_arm();
    // Rear left
    translate([chassis_length/2 - 5, -chassis_width/2 + 5, 0])
        wheel_mount_arm();
    // Rear right
    translate([chassis_length/2 - 5, chassis_width/2 - 5, 0])
        wheel_mount_arm();
}

// ==========================================
// RENDER SELECTION
// ==========================================

// Uncomment one of these to render:

// Full robot assembly
siafu_assembly();

// Individual parts for STL export:
// !chassis_base();
// !electronics_bay();
// !bay_lid();
// !wheel();
// !cutter_assembly();
// !solar_mount();
// !camera_mount();

// Print layout (single plate view)
// translate([0, -120, 0]) wheel();
// translate([60, -120, 0]) wheel();
// translate([-60, -120, 0]) wheel();
// translate([0, 120, 0]) bay_lid();

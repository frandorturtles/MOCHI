// MOCHI - carcasa paramétrica (OpenSCAD >= 2021.01).
// Exportar:  3d-models/source/build_stl.sh      Vista:  openscad -D 'part="assembly"' mochi.scad
include <params.scad>;
part = "assembly";   // "base" | "lid" | "button" | "plate" | "assembly"
$fn = 64;

// ---------- Forma base: ovalo con bordes redondeados (perfil por rebanadas) ----------
function prof(h, r) = concat(
  [for (t = [0:15:90]) [r - r*cos(t), r - r*sin(t)]],      // filete inferior: [z, retranqueo]
  [for (t = [0:15:90]) [h - r + r*sin(t), r - r*cos(t)]]); // filete superior

module slice(w, l, z, ins) {
  translate([0, 0, z]) scale([w/2 - ins, l/2 - ins, 1]) cylinder(r = 1, h = 0.01, $fn = 96);
}
module blob(w, l, h, r) {
  p = prof(h, r);
  for (k = [0:len(p)-2]) hull() { slice(w, l, p[k][0], p[k][1]); slice(w, l, p[k+1][0], p[k+1][1]); }
}
module outer()  { blob(body_w, body_l, body_h, fillet); }
module cavity() { translate([0, 0, wall]) blob(body_w - 2*wall, body_l - 2*wall, body_h - 2*wall, fillet - wall); }
module shell()  { difference() { outer(); cavity(); } }
module lower_half() { translate([-100, -100, -1]) cube([200, 200, split_z + 1]); }
module upper_half() { translate([-100, -100, split_z]) cube([200, 200, 100]); }

module star2d(R, r) {
  offset(r = 0.7) offset(delta = -0.7)
    polygon([for (i = [0:9]) let(a = 90 + i*36, rad = (i % 2 == 0) ? R : r) [rad*cos(a), rad*sin(a)]]);
}

// ---------- BASE ----------
module base() {
  difference() {
    union() {
      intersection() { shell(); lower_half(); }
      for (p = screw_pts) translate([p[0], p[1], wall - 0.01]) cylinder(d = col_od, h = split_z - wall + 0.01);       // columnas de tornillo
      for (sx = [-1, 1], sy = [-1, 1]) translate([sx*post_x, sy*post_y, wall - 0.01]) {                             // postes de PCB
        cylinder(d = post_od, h = pcb_z0 - wall + 0.01);
        cylinder(d = pin_d, h = pcb_z0 - wall + pcb_t + 0.01);                                                      // pin de ubicacion
      }
      for (sx = [-1, 1]) translate([sx*(batt_w/2 + batt_clear + 0.6) - 0.6, -batt_l/2, wall - 0.01]) cube([1.2, batt_l, 2.2]);  // topes de bateria
      intersection() { outer(); translate([-body_w/2, mcu_y - mcu_dy/2, wall - 0.01]) cube([body_w/2 - 21, mcu_dy, plate_top - wall + 0.01]); }  // repisa del SuperMini
      translate([bz_x, bz_y, wall - 0.01]) difference() { cylinder(d = bz_d + 2.4, h = 2.0); translate([0, 0, -1]) cylinder(d = bz_d + 0.3, h = 4); }  // nido del buzzer
    }
    for (p = screw_pts) {
      translate([p[0], p[1], -1]) cylinder(d = clear_d, h = split_z + 2);
      translate([p[0], p[1], -1]) cylinder(d = head_d, h = head_h + 1);                                              // alojamiento de cabeza
    }
    translate([-body_w/2 - 1, mcu_y - usb_w/2, usb_z - usb_h/2]) cube([wall + 4, usb_w, usb_h]);                    // USB-C del SuperMini (pared -X)
    for (i = [-2:2]) translate([bz_x, bz_y + i*2.2, -1]) cylinder(d = 1.2, h = wall + 2);                           // salida de sonido (buzzer)
  }
}

// ---------- TAPA ----------
module wing2d() {
  union() {
    hull() { circle(r = 3.4); translate([8, 2.2]) circle(r = 2.6); }
    hull() { translate([1.5, -3]) circle(r = 2.8); translate([9.5, -1.2]) circle(r = 2.2); }
    translate([10.2, 1.2]) circle(r = 1.6);
  }
}
module decor() {
  translate([top_star_pos[0], top_star_pos[1], body_h - 2.2]) linear_extrude(3.8) star2d(6.2, 2.9);
  translate([loop_pos[0], loop_pos[1], split_z + 1]) difference() { cylinder(d = 9, h = 2.4); translate([0, 0, -1]) cylinder(d = 4.8, h = 5); }
  for (m = [0, 1]) mirror([m, 0, 0]) translate([body_w/2 - 3.2, 7, split_z + 1.5]) rotate([0, 0, 12]) linear_extrude(3) wing2d();
}
module lid() {
  difference() {
    union() {
      intersection() { shell(); upper_half(); }
      translate([0, disp_cy, body_h - 0.01]) difference() { cylinder(d = bezel_od, h = bezel_h + 0.01); translate([0, 0, -1]) cylinder(d = window_d, h = bezel_h + 3); }
      for (a = [0, 180, 270]) translate([0, disp_cy, ceiling_z - cage_h])                                             // lengüetas de la pantalla
        rotate([0, 0, a - 15]) rotate_extrude(angle = 30) translate([disp_d/2 + disp_clear, 0]) square([cage_w, cage_h + 0.01]);
      for (p = screw_pts) translate([p[0], p[1], split_z - 0.01]) cylinder(d = col_od, h = ceiling_z - split_z + 0.02);
      if (decor_fuse) decor();
    }
    translate([0, disp_cy, ceiling_z - 1]) cylinder(d = window_d, h = wall + bezel_h + 2);                            // ventana
    for (p = screw_pts) translate([p[0], p[1], split_z - 0.5]) cylinder(d = pilot_d, h = pilot_depth);                        // piloto del tornillo
    for (p = btn_pos) translate([p[0], p[1], ceiling_z - 1]) linear_extrude(wall + 4) offset(delta = btn_clear) star2d(star_R, star_r);
  }
}

// ---------- CAP DE BOTON (estrella). Origen = cara inferior de la brida ----------
module button_cap() {
  linear_extrude(flange_t) star2d(star_R + 1.2, star_r + 0.6);                                   // brida de retencion
  linear_extrude(flange_t + wall + cap_proud) star2d(star_R, star_r);                           // cabeza que sale por el techo
  translate([0, 0, -stem_len]) cylinder(d = stem_d, h = stem_len + 0.01);                         // vastago que pulsa el switch
}

module plate() {   // placa soporte (para imprimir como plantilla o recortar de perfboard)
  difference() {
    linear_extrude(pcb_t) offset(r = pcb_r) offset(delta = -pcb_r) square([pcb_w, pcb_l], center = true);
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx*post_x, sy*post_y, -1]) cylinder(d = pin_d + 0.3, h = pcb_t + 2);
    for (p = screw_pts) translate([p[0], p[1], -1]) cylinder(d = col_od + 1.2, h = pcb_t + 2);
  }
}

module assembly() {
  color("#8fe3d0") base();
  color("#8fe3d0") lid();
  for (p = btn_pos) color("#ffe98a") translate([p[0], p[1], ceiling_z - flange_t]) button_cap();
  color("#222") translate([-batt_w/2, -batt_l/2, batt_z0]) cube([batt_w, batt_l, batt_t]);                         // bateria
  color("#2a7") translate([0, 0, pcb_z0]) plate();                                                               // placa soporte
  color("#c33") translate([mcu_x0, mcu_y - mcu_dy/2, mcu_z0]) cube([mcu_dx, mcu_dy, mcu_h]);                        // SuperMini
  color("#39c") translate([tp_x0, tp_y0, plate_top]) cube([tp_dx, tp_dy, tp_h]);                                     // TP4056
  color("#555") translate([bz_x, bz_y, wall]) cylinder(d = bz_d, h = bz_h);                                           // buzzer
  color("#444") translate([0, disp_cy, plate_top + disp_gap]) cylinder(d = disp_d, h = disp_t);               // pantalla (volumen)
}

if (part == "base") base();
else if (part == "lid") lid();
else if (part == "button") button_cap();
else if (part == "plate") plate();
else assembly();

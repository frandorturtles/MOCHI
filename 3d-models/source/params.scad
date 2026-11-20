// ============================================================================
// MOCHI rev B - parametros de la carcasa (UNICA fuente de verdad: la leen mochi.scad, gen_stl.py y tests/test_fit.py)
// Circuito hecho con MODULOS YA HECHOS (sin PCB): ESP32-C3 SuperMini + TP4056 + pantalla GC9A01 + bateria + buzzer.
// TODAS las medidas de componentes son PROVISIONALES: confirmar con calibre (docs/manufacturing/measure_checklist.md).
// Unidades: mm. Solo asignaciones simples (numeros, listas y operaciones aritmeticas).
// ============================================================================

// ---- Cuerpo (ovalo) ----
body_w   = 62;
body_l   = 70;
body_h   = 20.2;
wall     = 2.2;
fillet   = 5;
split_z  = 14;      // plano de union base/tapa

// ---- Pantalla redonda GC9A01 1.28" (PROVISIONAL) ----
disp_d        = 37.5;
disp_t        = 3.5;
disp_active_d = 32.5;
disp_clear    = 0.3;
disp_cy       = 7;
disp_gap      = 4.8;    // entre la cara superior de la placa soporte y la cara inferior de la pantalla
window_d      = 33.5;
bezel_od      = 40;
bezel_h       = 2.0;
cage_h        = 4.4;
cage_w        = 1.2;

// ---- Placa soporte (perfboard recortada o impresa) donde van los modulos (PROVISIONAL) ----
pcb_w   = 44;
pcb_l   = 50;
pcb_t   = 1.6;
pcb_r   = 8;
pcb_z0  = 7.6;      // cara inferior; deja 0.8 mm para patas soldadas recortadas sobre la bateria
post_x  = 14;
post_y  = 23.5;
post_od = 3.6;
pin_d   = 1.4;

// ---- Modulos sobre la placa (PROVISIONAL; cajas envolventes) ----
mcu_x0 = -27;       // ESP32-C3 SuperMini: 22.5 x 18 mm, USB-C hacia la pared -X
mcu_dx = 22.5;
mcu_y  = -2;        // centro en Y (tambien centra la abertura USB)
mcu_dy = 18;
mcu_h  = 3.6;       // altura total sobre la placa (PCB 1.2 + conector USB-C)
mcu_board_t = 1.2;
usbc_h = 3.2;       // altura del conector USB-C sobre la placa del modulo
tp_x0  = -3;        // modulo TP4056 con proteccion: 26 x 17 mm
tp_dx  = 26;
tp_y0  = -11;
tp_dy  = 17;
tp_h   = 4.2;       // incluye su conector USB (sin usar)
sw_h   = 5.0;       // pulsador tact 6x6 mm de patas (hasta la punta del actuador)
sw_w   = 6.0;

// ---- Bateria LiPo ~402540 (PROVISIONAL), en el suelo ----
batt_t     = 4.0;
batt_w     = 25;
batt_l     = 40;
batt_clear = 0.6;

// ---- Buzzer pasivo redondo en el suelo, sobre los orificios de sonido (PROVISIONAL) ----
bz_x = 19;
bz_y = 0;
bz_d = 8.5;
bz_h = 5.0;

// ---- Tornillos M2 autorroscantes (3 puntos) ----
screw_pts   = [[-10, -24.5], [10, -24.5], [0, 30.5]];
col_od      = 4.4;
pilot_d     = 1.7;
clear_d     = 2.4;
head_d      = 3.8;
head_h      = 1.4;
screw_len   = 16;
pilot_depth = 5.0;

// ---- Botones: las 3 estrellas inferiores son los pulsadores A/B/C ----
btn_pos     = [[-13, -18], [0, -22], [13, -18]];
star_R      = 5.0;
star_r      = 2.3;
btn_clear   = 0.3;
flange_t    = 1.2;
cap_proud   = 1.2;
stem_d      = 3.0;

// ---- USB-C del SuperMini: abertura en la pared -X ----
usb_w = 9.4;
usb_h = 3.6;

// ---- Derivados ----
ceiling_z = body_h - wall;
plate_top = pcb_z0 + pcb_t;
mcu_z0    = plate_top;
usb_z     = mcu_z0 + mcu_board_t + usbc_h / 2;
batt_z0   = wall;
sw_top_z  = plate_top + sw_h;
stem_len  = ceiling_z - flange_t - sw_top_z;

// ---- Decoracion (como la referencia) ----
decor_fuse = true;
top_star_pos = [21, 27.5];
loop_pos     = [-23, 27];

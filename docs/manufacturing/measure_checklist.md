# Medidas a confirmar ANTES de imprimir

Todo esto esta como **provisional** en `3d-models/source/params.scad`. Mide con calibre, edita el archivo y ejecuta:
`make fit` (debe decir TODO OK) y luego `python3 3d-models/source/gen_stl.py` (o `build_stl.sh`) y `make renders`.

| Parametro | Provisional | Donde medirlo |
|---|---|---|
| `disp_d`, `disp_t`, `disp_active_d` | 37.5 / 3.5 / 32.5 mm | pantalla GC9A01 comprada |
| `mcu_dx`, `mcu_dy`, `mcu_h`, `usbc_h` | 22.5 x 18 mm, 3.6 y 3.2 mm | ESP32-C3 SuperMini (el conector USB-C debe quedar centrado en `mcu_y`) |
| `tp_dx`, `tp_dy`, `tp_h` | 26 x 17 x 4.2 mm | modulo TP4056 comprado |
| `batt_t`, `batt_w`, `batt_l` | 4.0 x 25 x 40 mm | bateria LiPo (+ cable) |
| `bz_d`, `bz_h` | 8.5 / 5 mm | buzzer comprado |
| `sw_w`, `sw_h` | 6.0 / 5.0 mm | pulsador tact (hasta la punta del actuador) |
| `pcb_*`, `post_*` | 44 x 50 mm | perfboard cortada |

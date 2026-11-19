# Medidas a confirmar ANTES de imprimir o fabricar la PCB

Todo lo de esta lista esta como **provisional** en `3d-models/source/params.scad`. Mide con calibre, edita el archivo y ejecuta:
`python3 tests/test_fit.py` (debe decir TODO OK) y luego `3d-models/source/build_stl.sh`.

| Parametro | Provisional | Donde medirlo |
|---|---|---|
| `disp_d`, `disp_t`, `disp_active_d` | 37.5 / 3.5 / 32.5 mm | modulo GC9A01 comprado |
| orden y paso de pines J3, altura del header | 8 pines 2.54 | modulo GC9A01 |
| `batt_t`, `batt_w`, `batt_l` | 5.0 x 30 x 35 mm | bateria LiPo comprada (+ cable y su polaridad) |
| `esp_h` | 2.4 mm | hoja de datos ESP32-C3-MINI-1 |
| `usbc_h`, `usbc_w` | 3.2 / 8.94 mm | receptaculo USB-C elegido |
| `sw_h`, `sw_w` | 2.0 / 4.5 mm | pulsador elegido (altura hasta el actuador) |
| buzzer: tamano, posicion de los orificios | ~8.5 x 8.5 x 3 mm | buzzer elegido |
| `pcb_w/pcb_l/pcb_r`, `post_*` | 40 x 50 mm, r 6 | PCB real de KiCad |

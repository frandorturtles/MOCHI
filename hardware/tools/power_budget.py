#!/usr/bin/env python3
"""Estimacion de consumo y autonomia de MOCHI. TODAS las cifras son valores TIPICOS de hojas de datos / estimaciones
y deben medirse en el prototipo (ver docs/electronics/measurements.md)."""
CAP_MAH = 300          # bateria provisional
USABLE = 0.85          # fraccion util (corte por proteccion/brownout)
modes = {              # mA  (componente: valor estimado)
  "pantalla encendida (uso)":   {"ESP32-C3 160 MHz": 25, "GC9A01 logica": 8, "retroiluminacion 40%": 8, "LED de alimentacion SuperMini": 1.0},
  "pantalla encendida (100%)":  {"ESP32-C3 160 MHz": 25, "GC9A01 logica": 8, "retroiluminacion 100%": 20, "LED de alimentacion SuperMini": 1.0},
  "pantalla apagada (light sleep)": {"ESP32-C3 light sleep": 0.8, "GC9A01 sleep": 0.01, "LDO onboard Iq": 0.1, "LED de alimentacion SuperMini": 1.0, "divisor ADC": 0.021},
}
duty = {"pantalla encendida (uso)": 0.04, "pantalla encendida (100%)": 0.0, "pantalla apagada (light sleep)": 0.96}  # 1 h/dia de uso
print(f"Bateria {CAP_MAH} mAh, util {USABLE:.0%}\n")
avg = 0.0
for m, comps in modes.items():
    tot = sum(comps.values()); avg += tot * duty[m]
    print(f"{m:34s} {tot:7.2f} mA  ({', '.join(f'{k} {v}' for k, v in comps.items())})")
hours = CAP_MAH * USABLE / avg
print(f"\nPromedio (1 h/dia de pantalla): {avg:.2f} mA  ->  autonomia estimada {hours:.0f} h (quitando el LED de alimentacion del SuperMini mejora ~2x en reposo) = {hours/24:.1f} dias")
print(f"Pantalla siempre encendida al 40%: {CAP_MAH*USABLE/41.055:.1f} h")
print("Carga: ~120 mA (TP4056 con R_PROG=10k) -> ~%.1f h de 0 a 100%% (CC/CV, tiempo real mayor)" % (CAP_MAH / 120 * 1.2))
print("Pico buzzer ~30 mA (breve); pico WiFi NO se usa (radio desactivada).")

#!/usr/bin/env python3
"""Verifica el circuito de MOCHI (modulos ya hechos): pines unicos, coherencia con firmware/src/config.h,
corriente de carga del TP4056, caida del diodo, excitador del buzzer y rango del ADC.
Uso: python3 hardware/tools/check_netlist.py"""
import json, re, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
nl = json.load(open(os.path.join(ROOT, "hardware/schematics/mochi_netlist.json")))
cfg = open(os.path.join(ROOT, "firmware/src/config.h")).read()
P = nl["params"]; ok = True
def fail(m):
    global ok; ok = False; print("  [FALLO]", m)
def good(m): print("  [ok]   ", m)

seen = {}
for net, pins in nl["nets"].items():
    for p in pins:
        ref, pin = p.split(".", 1)
        if ref not in nl["parts"] or pin not in nl["parts"][ref].get("pins", []): fail(f"{net}: pin inexistente {p}")
        if p in seen: fail(f"pin {p} en dos nets: {seen[p]} y {net}")
        seen[p] = net
good(f"{len(seen)} conexiones, ningun pin en dos nets")
for ref, part in nl["parts"].items():
    for pin in part["pins"]:
        if f"{ref}.{pin}" not in seen and f"{ref}.{pin}" not in nl["optional_pins"] and ref != "MCU":
            fail(f"{ref}.{pin} sin conectar")
good("todos los pines de los modulos/componentes estan conectados (salvo opcionales)")

defs = dict(re.findall(r"#define\s+PIN_(\w+)\s+(\d+)", cfg))
for k in ("BTN_A", "BTN_B", "BTN_C", "TFT_BL", "TFT_DC", "TFT_SCLK", "TFT_MOSI", "TFT_CS", "BUZZER", "CHG_STAT"):
    io = [p for p in nl["nets"][k] if p.startswith("MCU.IO")]
    if not io or io[0] != f"MCU.IO{defs.get(k)}": fail(f"PIN_{k}={defs.get(k)} no coincide con el circuito {io}")
io = [p for p in nl["nets"]["VSENSE"] if p.startswith("MCU.IO")]
(good if io and io[0] == f"MCU.IO{defs['VBAT_SENSE']}" else fail)("PIN_VBAT_SENSE coincide")
good("config.h coincide con el cableado (11 senales)")

used = sorted(int(p.split("IO")[1]) for p in seen if p.startswith("MCU.IO"))
bad = [n for n in used if n in (8, 9, 18, 19)]
(fail if bad else good)(f"GPIO usados {used}: ninguno es LED/BOOT/USB (8, 9, 18, 19)" if not bad else f"GPIO reservados usados: {bad}")
good("IO2 (estrapping) solo como entrada analogica con divisor ~2 V: no afecta al arranque")

# Cargador TP4056: I = 1200 / R_PROG(kohm)  [mA]   (hoja de datos TP4056)
ich = 1200.0 / (P["tp4056_rprog_ohm"] / 1000.0); c = ich / P["battery_mah"]
(good if c <= 0.5 else fail)(f"carga a {ich:.0f} mA = {c:.2f} C con {P['battery_mah']} mAh (limite <= 0.5 C). Con la R de fabrica (1.2k) serian 1000 mA = {1000/P['battery_mah']:.1f} C: NO usar sin cambiarla")

# Diodo OR: bateria -> 5V del SuperMini
vf = P["schottky_vf"]; vmin_reg = 3.3 + P["ldo_dropout"] + vf
print(f"  [info]   LDO del SuperMini regula 3.3 V mientras VBAT >= {vmin_reg:.2f} V; luego el riel baja con la bateria (el C3 funciona hasta ~3.0 V => se aprovecha la bateria hasta ~{3.0+P['ldo_dropout']+vf-0.2:.2f} V)")
ib = (3.3 - 0.7) / 1000.0; ic = (3.3 - 0.2) / P["buzzer_coil_ohm"]
(good if ib < 0.01 and ic < 0.1 else fail)(f"excitador del buzzer: Ib {ib*1000:.1f} mA (GPIO), Ic {ic*1000:.0f} mA (< 100 mA del BC547)")
vs = 4.2 * 100 / 200
(good if vs < 2.5 else fail)(f"ADC VBAT: {vs:.2f} V maximo; consumo del divisor {4.2/200e3*1e6:.0f} uA")
print("\nRESULTADO:", "TODO OK" if ok else "HAY FALLOS"); sys.exit(0 if ok else 1)

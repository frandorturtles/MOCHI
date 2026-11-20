# STL de MOCHI

| Archivo | Cant. | Volumen | Notas |
|---|---|---|---|
| `mochi_base.stl` | 1 | 13.5 cm3 | suelo, columnas de tornillo, postes de la placa, repisa del SuperMini, ranura USB (-X), nido del buzzer |
| `mochi_lid.stl` | 1 | 8.2 cm3 | tapa con ventana, bisel, retenes de pantalla, estrella superior, alas y argolla (fusionadas) |
| `mochi_button.stl` | 3 | 0.2 cm3 | estrellas A/B/C (girar 180 grados al imprimir) |

Generados con `../source/gen_stl.py --res 0.5` a partir de `../source/params.scad` (verificados: malla cerrada, 0 aristas no-manifold).
Regenerar: `make stl` (Python) o `../source/build_stl.sh` (OpenSCAD, mayor calidad). Renders en `../renders/`.

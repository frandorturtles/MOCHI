# Impresion 3D de MOCHI

| Pieza | Cant. | Orientacion | Soportes |
|---|---|---|---|
| `mochi_base.stl` | 1 | piso hacia la cama | no (ranura USB lateral = puente corto) |
| `mochi_lid.stl` | 1 | **plano de union hacia la cama** (ventana hacia arriba) | si, solo bajo las alas y la argolla (arbol, contacto ligero) |
| `mochi_button.stl` | 3 | **girar 180 grados en el laminador**: estrella contra la cama, vastago hacia arriba | no (la brida sobresale 1.2 mm) |
| placa soporte (opcional) | - | se puede recortar de perfboard; plantilla con `-D 'part="plate"'` o `gen_stl.py --parts plate` | - |

- **Material**: PETG o PLA+. Para el aspecto mate de la referencia: PLA mate + lijado + pintura acrilica suave. Botones en amarillo, alas en blanco (pintar o pausa de color).
- **Parametros (boquilla 0.4)**: capa 0.16-0.2 mm, 4-5 perimetros (pared 2.2 mm), relleno 15% giroide, techo/suelo 5 capas; PETG 235-245 C cama 70-80 C; PLA 205-215 C cama 55-60 C. Sin brim salvo mala adherencia.
- **Calidad de los STL incluidos**: generados con `3d-models/source/gen_stl.py` (campos de distancia + marching tetrahedra, malla de 0.5 mm, 0 aristas no-manifold, volumenes positivos). Las superficies tienen un leve facetado de ~0.1 mm: lijar. Para la mejor calidad compila `mochi.scad` con OpenSCAD (`build_stl.sh`).
- **Ajustes tras una prueba**: `btn_clear` (0.3 mm), `disp_clear` (0.3 mm), `pilot_d` (1.7 mm para M2 autorroscante). Imprime primero la tapa; si las estrellas no entran/se atoran, ajusta y regenera.

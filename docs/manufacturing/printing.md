# Impresion 3D de MOCHI

| Pieza | Cant. | Orientacion | Soportes |
|---|---|---|---|
| `mochi_base.stl` | 1 | piso hacia la cama | no (la ranura USB es un puente corto) |
| `mochi_lid.stl` | 1 | **plano de union hacia la cama** (ventana hacia arriba) | si, solo bajo las alas y el llavero (arbol, contacto ligero) |
| `mochi_button.stl` | 3 | **girar 180 grados en el laminador**: cabeza (estrella) contra la cama, vastago hacia arriba | no (la brida sobresale 1.2 mm: puente corto) |

- **Material**: PETG (resistente a golpes y al calor del bolsillo/coche) o PLA+ (mas facil, mas rigido). El efecto "arcilla mate" de la
  referencia se logra con PLA mate y lijado + pintura acrilica en spray suave. Botones en un color diferente (amarillo).
- **Parametros (boquilla 0.4)**: capa 0.16-0.2 mm, 4 perimetros (pared 2.2 mm = 5 de 0.44), relleno 15% giroide, techo/suelo 5 capas,
  PETG 235-245 C / cama 70-80 C; PLA 205-215 C / cama 55-60 C. Ventilador 100% en PLA, 30-50% en PETG. Sin brim salvo adherencia pobre.
- **Tolerancias a ajustar tras una prueba**: holgura del hueco de las estrellas (`btn_clear`, 0.3), holgura de la pantalla (`disp_clear`, 0.3),
  piloto del tornillo (`pilot_d` 1.7 para M2 autorroscante en PETG/PLA). Imprimir primero solo la tapa o una **prueba de ajuste** (anillo de pantalla + 1 boton).
- **Herramientas**: calibre digital, cutter/lima fina, destornillador PH0, soldador (T ~ 330 C), flux, pinzas, multimetro, lupa.

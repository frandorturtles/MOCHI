# Animaciones

Las animaciones pixel-art de MOCHI son **procedurales**: `firmware/tools/gen_sprites.py` dibuja 48 sprites de mascota
(6 etapas/formas x 8 emociones), 2 cuadros de huevo y 10 iconos, y los escribe en `firmware/src/sprites.h` (paleta de 16 colores RGB565).
El movimiento (rebote, balanceo del huevo, destellos de evolución, estrellas que caen) se genera en `firmware/src/ui.cpp`.
Para añadir una emoción o forma: edita `draw_pet()` en el script y ejecuta `make sprites`.

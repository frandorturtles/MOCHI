# Ensamblaje de MOCHI

> Antes de empezar: ejecutar `make check` y confirmar las medidas de `docs/manufacturing/measure_checklist.md`.

1. **Imprimir** base, tapa y 3 botones (ver `docs/manufacturing/printing.md`). Quitar soportes, lijar bordes, pintar si se desea.
2. **Prueba en seco**: colocar cada estrella en la tapa; debe moverse libre sin atascarse (ajustar `btn_clear` si no).
3. **Soldar la PCB** (flux + estano fino): primero los SMD pequenos (resistencias/condensadores), luego U2/U3/U4 (SOT-23), USB-C, el modulo ESP32 y los pulsadores. Revisar cortocircuitos entre VBUS/GND/3V3 con el multimetro **antes** de energizar.
4. **Primera energizacion sin bateria y sin pantalla**: conectar USB y medir 3V3 (3.2-3.4 V) en el modulo. Si falta, no seguir.
5. **Cargar el firmware** (ver README): `pio run -t upload` con USB. Si no entra, mantener BOOT y pulsar RESET.
6. **Conectar la pantalla** (J3). Cables cortos o header de poca altura. Probar el firmware.
7. **Bateria**: VERIFICAR la polaridad del conector contra los pads (+/-) con multimetro; muchos cables LiPo vienen invertidos. Conectar y comprobar carga por USB (STAT en bajo mientras carga).
8. **Montaje**: bateria en el suelo de la base (tope lateral + cinta doble cara), PCB sobre los 4 postes con sus pines, pantalla sobre el header con cinta de espuma, estrellas en sus huecos con la brida por dentro, cerrar la tapa y atornillar 3 tornillos M2x14 desde abajo (sin apretar de mas).
9. **Pruebas finales**: ver README "Lista de pruebas".

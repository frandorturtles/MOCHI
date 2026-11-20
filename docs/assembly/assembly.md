# Armado de MOCHI con modulos ya hechos (sin PCB)

> Antes: `make check` en el PC y confirmar medidas (`docs/manufacturing/measure_checklist.md`). Diagramas: `hardware/schematics/wiring_signals.png` y `wiring_power.png`.
> Herramientas: soldador, estano, flux, cable 28-30 AWG, pelacables, multimetro, cinta Kapton, pistola de silicona (poca), destornillador PH0.

## 0. Modificar el TP4056 (OBLIGATORIO)
Los modulos TP4056 vienen a **1 A** (R_PROG = 1.2 kOhm). Una bateria de 300 mAh debe cargarse a <= 0.5 C (150 mA).
Cambia esa resistencia (marcada "122" o "1K2", junto al chip de 8 patas) por **10 kOhm (marca "103")** => ~120 mA.
No conectes el USB propio del TP4056: se carga por el USB-C del SuperMini.

## 1. Pruebas en protoboard (antes de soldar nada definitivo)
1. SuperMini + pantalla (SCL=IO6, SDA=IO7, DC=IO5, CS=IO10, VCC=3V3, RST=3V3, GND, BL=IO4 via 100 ohm si existe).
2. Subir el firmware (`cd firmware && pio run -t upload`; si no entra: mantener BOOT y pulsar RESET). Debe verse el huevo.
3. Anadir los 3 pulsadores (IO0, IO1, IO3 a GND). Probar menu y minijuegos.
4. Anadir buzzer: IO20 -> 1k -> base de BC547; emisor a GND; buzzer (+) a 3V3, buzzer (-) al colector; 1N4148 (anodo al colector, catodo a 3V3).
5. Anadir el divisor 100k/100k de VBAT a IO2 (con bateria conectada, *Status* debe mostrar un % creible).

## 2. Potencia (con multimetro, sin pantalla conectada la primera vez)
1. Bateria -> B+ / B- del TP4056. **Verifica polaridad del conector con el multimetro antes de conectar.**
2. OUT- a GND comun. OUT+ al anodo del 1N5819; **catodo (franja) al pin 5V del SuperMini**.
3. IN+ del TP4056 al pin 5V del SuperMini, IN- a GND.
4. Conectar USB-C al SuperMini: el TP4056 debe cargar (LED rojo/CHRG). Medir 3.3 V en el pin 3V3.
5. Desconectar USB: el SuperMini sigue encendido con la bateria (3V3 presente). Si no, revisar el diodo.
6. (Opcional) cable del pin CHRG del TP4056 a IO21 para ver "charging" en *Status*.

## 3. Montaje en la carcasa
1. Imprimir y lijar base, tapa y 3 botones (`docs/manufacturing/printing.md`). Probar en seco que las estrellas se mueven libres.
2. Bateria en el suelo (cinta doble cara, entre los topes). Buzzer en su nido sobre los orificios de sonido.
3. Placa soporte (perfboard 44x50 mm con esquinas redondeadas) sobre los 4 postes (agujeros de 1.7 mm): soldar el TP4056, los 3 pulsadores (6x6) y los componentes pequenos; **recortar las patas al ras** por debajo (queda 0.8 mm sobre la bateria; cubrir la bateria con Kapton).
4. SuperMini con su conector USB-C asomando por la ranura de la pared izquierda (-X), apoyado en la repisa de la base.
5. Pantalla encima, separada 4.8 mm de la placa con espuma/cinta, cables cortos de 8 hilos. Que el vidrio no toque el techo (0.4 mm de holgura).
6. Estrellas en sus huecos con la brida hacia dentro; cerrar la tapa y poner 3 tornillos M2x16 desde abajo (sin apretar de mas).
7. Probar carga y botones con la tapa cerrada.

## Lista de pruebas
- [ ] 3V3 estable (3.2-3.4 V) con USB y con bateria
- [ ] Carga ~120 mA medida en serie con el multimetro (no mas de 150 mA)
- [ ] Pantalla, botones A/B/C, buzzer y menus
- [ ] *Status* muestra bateria y "charging"; apagar y encender conserva el progreso
- [ ] Temperatura: tras 10 min cargando, ningun modulo quema al tacto

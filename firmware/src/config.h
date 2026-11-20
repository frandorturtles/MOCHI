// MOCHI - mapa de pines (ESP32-C3 SuperMini). Debe coincidir con hardware/schematics/mochi_netlist.json
// (hardware/tools/check_netlist.py lo verifica automaticamente). IO8 (LED) e IO9 (BOOT) quedan libres.
#pragma once
#define PIN_BTN_A      0   // estrella izquierda  (RTC/wake)
#define PIN_BTN_B      1   // estrella central    (RTC/wake)
#define PIN_VBAT_SENSE 2   // divisor 100k/100k, ADC1_CH2
#define PIN_BTN_C      3   // estrella derecha    (RTC/wake)
#define PIN_TFT_BL     4   // PWM retroiluminacion (via MOSFET N)
#define PIN_TFT_DC     5
#define PIN_TFT_SCLK   6
#define PIN_TFT_MOSI   7
#define PIN_TFT_CS     10
#define PIN_BUZZER     20  // buzzer pasivo via transistor
#define PIN_CHG_STAT   21  // STAT del MCP73831 (opcional: CHRG del TP4056; sin cablear se lee como 'no cargando')

#define SCREEN_W 240
#define SCREEN_H 240
#define LONG_PRESS_MS   800
#define SCREEN_OFF_MS   20000
#define AUTOSAVE_SEC    300
#define VBAT_DIVIDER    2   // 100k/100k

// Stub minimo de Arduino para compilar el firmware en el PC (solo pruebas; NO se usa en el dispositivo).
#pragma once
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define PROGMEM
#define pgm_read_byte(p) (*(const uint8_t*)(p))
#define pgm_read_word(p) (*(const uint16_t*)(p))
#define INPUT_PULLUP 2
#define LOW 0
#define HIGH 1
extern uint32_t g_ms;
inline uint32_t millis() { return g_ms; }
inline uint32_t micros() { return g_ms * 1000u; }
inline void delay(uint32_t) {}
inline void pinMode(int, int) {}
inline int digitalRead(int) { return HIGH; }
inline void ledcSetup(int, int, int) {}
inline void ledcAttachPin(int, int) {}
inline void ledcWrite(int, int) {}
inline void ledcWriteTone(int, int) {}
inline void analogReadResolution(int) {}
inline uint32_t analogReadMilliVolts(int) { return 1900; }
inline uint32_t esp_random() { return 12345; }
struct SerialStub { void begin(int) {} void println(const char*) {} } inline Serial;

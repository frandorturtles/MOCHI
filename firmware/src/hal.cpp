#include "hal.h"
#include "config.h"
#include <Arduino.h>
#include <Preferences.h>
#include <sys/time.h>
#include <time.h>
#include "esp_sleep.h"
#include "driver/gpio.h"

namespace hal {

TFT_eSPI tft;
TFT_eSprite spr(&tft);
static Preferences prefs;
static bool dispOn = true;

// ---------- Pantalla ----------
void begin() {
  pinMode(PIN_BTN_A, INPUT_PULLUP); pinMode(PIN_BTN_B, INPUT_PULLUP); pinMode(PIN_BTN_C, INPUT_PULLUP);
  pinMode(PIN_CHG_STAT, INPUT_PULLUP);
  ledcSetup(0, 5000, 8); ledcAttachPin(PIN_TFT_BL, 0); ledcWrite(0, 0);
  ledcSetup(1, 2000, 8); ledcAttachPin(PIN_BUZZER, 1); ledcWrite(1, 0);
  analogReadResolution(12);
  tft.init(); tft.setRotation(0); tft.fillScreen(TFT_BLACK);
  spr.setColorDepth(16);
  if (!spr.createSprite(SCREEN_W, SCREEN_H)) {      // 115 KB; si falla, se reporta por USB
    Serial.println("ERROR: sin memoria para el framebuffer"); 
  }
  prefs.begin("mochi", false);
}

void setBacklight(uint8_t level) { ledcWrite(0, level); }

void displayOn(bool on) {
  if (on == dispOn) return;
  dispOn = on;
  if (on) { tft.writecommand(0x11); delay(120); tft.writecommand(0x29); }   // SLPOUT, DISPON
  else    { ledcWrite(0, 0); tft.writecommand(0x28); tft.writecommand(0x10); }  // DISPOFF, SLPIN
}

void present() { if (dispOn) spr.pushSprite(0, 0); }

// ---------- Botones (antirrebote 25 ms, pulsacion larga) ----------
struct Btn { uint8_t pin; bool down; bool raw; uint32_t tEdge, tDown; bool longFired; };
static Btn btns[3] = {{PIN_BTN_A, false, false, 0, 0, false}, {PIN_BTN_B, false, false, 0, 0, false}, {PIN_BTN_C, false, false, 0, 0, false}};

BtnEvt pollButtons() {
  uint32_t now = millis();
  for (int i = 0; i < 3; i++) {
    Btn& b = btns[i];
    bool r = digitalRead(b.pin) == LOW;
    if (r != b.raw) { b.raw = r; b.tEdge = now; }
    if (now - b.tEdge >= 25 && r != b.down) {
      b.down = r;
      if (r) { b.tDown = now; b.longFired = false; }
      else if (!b.longFired) return static_cast<BtnEvt>(A_SHORT + i);
    }
    if (b.down && !b.longFired && now - b.tDown >= LONG_PRESS_MS) { b.longFired = true; return static_cast<BtnEvt>(A_LONG + i); }
  }
  return BTN_NONE;
}
bool anyButtonDown() { return btns[0].down || btns[1].down || btns[2].down; }

// ---------- Audio (buzzer pasivo, sin bloqueo) ----------
static const Note* melody = nullptr; static uint8_t mLen = 0, mIdx = 0; static uint32_t mT = 0; static bool mOn = false;
void playNotes(const Note* n, uint8_t count, bool enabled) {
  if (!enabled) return;
  melody = n; mLen = count; mIdx = 0; mT = millis(); mOn = true;
  if (n[0].freq) ledcWriteTone(1, n[0].freq); else ledcWrite(1, 0);
}
void updateAudio() {
  if (!mOn) return;
  if (millis() - mT < melody[mIdx].ms) return;
  mIdx++; mT = millis();
  if (mIdx >= mLen) { mOn = false; ledcWriteTone(1, 0); ledcWrite(1, 0); return; }
  if (melody[mIdx].freq) ledcWriteTone(1, melody[mIdx].freq); else ledcWriteTone(1, 0);
}

// ---------- Guardado (NVS) ----------
bool saveState(const mochi::PetState& st) { return prefs.putBytes("pet", &st, sizeof(st)) == sizeof(st); }
bool loadState(mochi::PetState& st) {
  if (prefs.getBytesLength("pet") != sizeof(st)) return false;
  prefs.getBytes("pet", &st, sizeof(st));
  return mochi::verify(st);
}

// ---------- Reloj ----------
uint32_t nowEpoch() { return static_cast<uint32_t>(time(nullptr)); }
void setEpoch(uint32_t e) { struct timeval tv = {static_cast<time_t>(e), 0}; settimeofday(&tv, nullptr); }

// ---------- Bateria ----------
uint16_t batteryMv() { return static_cast<uint16_t>(analogReadMilliVolts(PIN_VBAT_SENSE) * VBAT_DIVIDER); }
bool charging() { return digitalRead(PIN_CHG_STAT) == LOW; }

// ---------- Ahorro de energia ----------
void lightSleepMs(uint32_t ms) {
  const int pins[3] = {PIN_BTN_A, PIN_BTN_B, PIN_BTN_C};
  for (int p : pins) gpio_wakeup_enable(static_cast<gpio_num_t>(p), GPIO_INTR_LOW_LEVEL);
  esp_sleep_enable_gpio_wakeup();
  esp_sleep_enable_timer_wakeup(static_cast<uint64_t>(ms) * 1000ULL);
  esp_light_sleep_start();
}

}  // namespace hal

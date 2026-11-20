// MOCHI - firmware principal (ESP32-C3 + GC9A01).
#include <Arduino.h>
#include "config.h"
#include "hal.h"
#include "pet.h"
#include "ui.h"

static mochi::Pet pet;
static UI ui(pet);
static uint32_t lastTick = 0, lastSave = 0, lastFrame = 0;
static bool screenOn = true;

static void save() { mochi::PetState st = pet.s; mochi::seal(st); hal::saveState(st); }

void setup() {
  Serial.begin(115200);
  hal::begin();
  mochi::PetState loaded;
  if (hal::loadState(loaded) && pet.adopt(loaded)) {
    Serial.println("Estado cargado");
    if (pet.s.clockValid) {                       // el reloj arranca desde el ultimo instante guardado
      hal::setEpoch(pet.s.lastEpoch);
      lastTick = pet.s.lastEpoch;
    }
  } else {
    Serial.println("Huevo nuevo");
    pet.reset(esp_random());
    pet.s.tzMinutes = -300;                        // UTC-5 (Colombia) por defecto; editable en Settings
  }
  ui.begin();
  if (lastTick == 0) lastTick = hal::nowEpoch();
  // Modo depuracion de envejecimiento rapido: pio run -e mochi -DMOCHI_FAST_AGING=60
#ifdef MOCHI_FAST_AGING
  pet.timeScale = MOCHI_FAST_AGING;
#endif
  ui.wake(millis());
}

void loop() {
  uint32_t ms = millis();
  hal::updateAudio();

  hal::BtnEvt e = hal::pollButtons();
  if (e != hal::BTN_NONE) {
    if (!screenOn) { screenOn = true; hal::displayOn(true); ui.begin(); ui.wake(ms); }   // el primer toque solo despierta
    else ui.onButton(e);
    ui.wake(ms);
  }

  // Tiempo de la mascota (basado en reloj de pared; sigue contando durante el light sleep)
  uint32_t now = hal::nowEpoch();
  if (now > lastTick) { ui.onEvents(pet.advance(now - lastTick, now)); lastTick = now; }
  else if (now < lastTick) lastTick = now;       // reloj atrasado manualmente

  if (ui.needsSave() || (now - lastSave) >= AUTOSAVE_SEC) { save(); lastSave = now; }

  if (screenOn && ms - lastFrame >= 50) {
    lastFrame = ms;
    ui.render(ms);
    hal::present();
  }

  if (screenOn && ui.screenShouldSleep(ms) && !hal::anyButtonDown()) { screenOn = false; hal::displayOn(false); }
  if (!screenOn && !hal::anyButtonDown()) hal::lightSleepMs(1000);   // despierta cada 1 s o con un boton
  else delay(2);
}

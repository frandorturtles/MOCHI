#pragma once
#include <stdint.h>
#include "pet.h"
#include <TFT_eSPI.h>

namespace hal {
enum BtnEvt : uint8_t { BTN_NONE = 0, A_SHORT, B_SHORT, C_SHORT, A_LONG, B_LONG, C_LONG };
struct Note { uint16_t freq; uint16_t ms; };   // freq 0 = silencio

extern TFT_eSprite spr;                 // framebuffer 240x240 RGB565

void begin();
void setBacklight(uint8_t level);
void displayOn(bool on);
void present();                         // empuja el framebuffer a la pantalla

BtnEvt pollButtons();
bool anyButtonDown();

void playNotes(const Note* n, uint8_t count, bool enabled);
void updateAudio();

bool saveState(const mochi::PetState& st);
bool loadState(mochi::PetState& st);

uint32_t nowEpoch();
void setEpoch(uint32_t epoch);
uint16_t batteryMv();
bool charging();
void lightSleepMs(uint32_t ms);         // duerme con espera por botones
}  // namespace hal

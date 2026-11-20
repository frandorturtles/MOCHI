#pragma once
#include <stdint.h>
#include "hal.h"
#include "pet.h"
#include "minigame.h"

class UI {
 public:
  explicit UI(mochi::Pet& p) : pet(p) {}
  void begin();
  void onButton(hal::BtnEvt e);
  void onEvents(uint16_t ev);
  void render(uint32_t ms);          // dibuja un cuadro en el framebuffer
  bool needsSave();                  // true una vez tras acciones importantes
  bool screenShouldSleep(uint32_t ms) const;
  void wake(uint32_t ms) { lastInput = ms; }
 private:
  enum class Scr : uint8_t { Home, Menu, Feed, PlayPick, StarCatch, Says, Status, Settings, Themes, SetTime, ConfirmReset };
  mochi::Pet& pet;
  Scr scr = Scr::Home;
  int8_t cur = 0;
  uint32_t lastInput = 0, toastUntil = 0, eatUntil = 0, flashUntil = 0, gameT = 0, saysT = 0;
  char toast[40] = "";
  bool dirty = false;
  // minijuegos
  mochi::StarCatch sc; mochi::MochiSays says;
  enum class SaysPhase : uint8_t { Show, Input, Over } phase = SaysPhase::Show;
  int8_t saysIdx = 0; int8_t lit = -1; uint32_t litUntil = 0; uint32_t resultUntil = 0;
  // ajustes
  int8_t hh = 12, mm = 0, tField = 0;

  void go(Scr s) { scr = s; cur = 0; }
  void say(const char* msg, uint32_t ms = 1600);
  void result(mochi::Result r, const char* okMsg);
  void startStarCatch(); void startSays();
  void finishGame(int score);
  void drawBackground();
  void drawSprite(const uint8_t* d, int w, int h, int x, int y, int scale);
  void drawIcon(int id, int cx, int cy, int scale);
  void drawText(const char* s, int x, int y, int font, uint16_t col, uint8_t datum = 4);
  void drawBar(int x, int y, int w, int v, uint16_t col);
  void renderHome(uint32_t ms); void renderMenu(); void renderFeed(); void renderPlayPick();
  void renderStarCatch(uint32_t ms); void renderSays(uint32_t ms); void renderStatus(); void renderSettings();
  void renderThemes(); void renderSetTime(); void renderConfirm();
  void toastOverlay(uint32_t ms);
};

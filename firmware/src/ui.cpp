#include "ui.h"
#include "config.h"
#include "sprites.h"
#include <Arduino.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

using namespace mochi;
using hal::spr;

// ---------------- Temas ----------------
struct Theme { uint8_t r1, g1, b1, r2, g2, b2; const char* name; };
static const Theme kThemes[4] = {
  {0x3a, 0x1c, 0x71, 0xd7, 0x6d, 0x77, "Sunset"},
  {0xb9, 0xf0, 0xe6, 0x5f, 0xc9, 0xc0, "Mint"},
  {0x0b, 0x10, 0x3a, 0x5c, 0x3d, 0xa8, "Night"},
  {0xff, 0xe3, 0xc8, 0xff, 0x9f, 0x8a, "Peach"},
};
static const uint16_t kMenuIcons[6] = {ICON_FOOD, ICON_GAME, ICON_MOON, ICON_PILL, ICON_HEART, ICON_GEAR};
static const char* kMenuNames[6] = {"Feed", "Play", "Sleep", "Medicine", "Status", "Settings"};
static const char* kStageNames[5] = {"Egg", "Baby", "Child", "Teen", "Adult"};
static const uint16_t kBrightness[3] = {40, 120, 255};

// ---------------- Sonidos ----------------
static const hal::Note sBeep[]  = {{1800, 25}};
static const hal::Note sOk[]    = {{1047, 70}, {1319, 90}};
static const hal::Note sNo[]    = {{300, 120}};
static const hal::Note sHappy[] = {{1047, 80}, {1319, 80}, {1568, 80}, {2093, 160}};
static const hal::Note sSad[]   = {{784, 150}, {659, 150}, {523, 300}};
static const hal::Note sAlert[] = {{880, 120}, {0, 80}, {880, 120}};
static const hal::Note sEvolve[]= {{523, 90}, {587, 90}, {659, 90}, {698, 90}, {784, 90}, {880, 90}, {988, 90}, {1047, 250}};
static const hal::Note sGift[]  = {{1568, 70}, {2093, 70}, {2637, 160}};
static const hal::Note sSaysN[3][1] = {{{523, 220}}, {{659, 220}}, {{784, 220}}};
#define PLAY(n) hal::playNotes(n, sizeof(n) / sizeof(n[0]), pet.s.soundOn)

static uint16_t rgb565(uint8_t r, uint8_t g, uint8_t b) { return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3); }
static uint16_t themeBottom(int i) { return rgb565(kThemes[i].r2, kThemes[i].g2, kThemes[i].b2); }

// ---------------- Utilidades de dibujo ----------------
void UI::drawBackground() {
  const Theme& t = kThemes[pet.s.themeIdx & 3];
  for (int y = 0; y < SCREEN_H; y += 4) {
    int k = y * 255 / (SCREEN_H - 1);
    spr.fillRect(0, y, SCREEN_W, 4, rgb565(t.r1 + (t.r2 - t.r1) * k / 255, t.g1 + (t.g2 - t.g1) * k / 255, t.b1 + (t.b2 - t.b1) * k / 255));
  }
}
void UI::drawSprite(const uint8_t* d, int w, int h, int x, int y, int scale) {
  for (int j = 0; j < h; j++) {
    int run = -1;
    for (int i = 0; i <= w; i++) {
      uint8_t idx = (i < w) ? pgm_read_byte(&d[j * w + i]) : 0;
      if (run >= 0 && (idx == 0 || i == w || idx != pgm_read_byte(&d[j * w + run]))) {   // cierra tramo de color
        uint8_t c0 = pgm_read_byte(&d[j * w + run]);
        spr.fillRect(x + run * scale, y + j * scale, (i - run) * scale, scale, pgm_read_word(&kPalette[c0]));
        run = -1;
      }
      if (run < 0 && idx != 0 && i < w) run = i;
    }
  }
}
void UI::drawIcon(int id, int cx, int cy, int scale) { drawSprite(kIcons[id], kIconW, kIconH, cx - kIconW * scale / 2, cy - kIconH * scale / 2, scale); }
void UI::drawText(const char* s, int x, int y, int font, uint16_t col, uint8_t datum) {
  spr.setTextDatum(datum); spr.setTextColor(col); spr.drawString(s, x, y, font);
}
void UI::drawBar(int x, int y, int w, int v, uint16_t col) {
  spr.fillRoundRect(x, y, w, 7, 3, rgb565(40, 30, 80));
  int f = w * v / 100; if (f > 0) spr.fillRoundRect(x, y, f < 6 ? 6 : f, 7, 3, col);
}
void UI::say(const char* msg, uint32_t ms) { strncpy(toast, msg, sizeof(toast) - 1); toast[sizeof(toast) - 1] = 0; toastUntil = millis() + ms; }
void UI::toastOverlay(uint32_t ms) {
  if (ms >= toastUntil) return;
  spr.fillRoundRect(50, 196, 140, 28, 12, rgb565(30, 20, 70));
  spr.drawRoundRect(50, 196, 140, 28, 12, rgb565(255, 233, 138));
  drawText(toast, 120, 210, 2, TFT_WHITE, MC_DATUM);
}
bool UI::needsSave() { bool d = dirty; dirty = false; return d; }
bool UI::screenShouldSleep(uint32_t ms) const {
  return scr == Scr::Home && ms - lastInput > SCREEN_OFF_MS && ms > toastUntil;
}

// ---------------- Logica ----------------
void UI::begin() {
  hal::setBacklight(kBrightness[pet.s.brightness % 3 == 0 ? 2 : pet.s.brightness % 3]);
  if (!pet.s.clockValid) { hh = 12; mm = 0; go(Scr::SetTime); }
}

void UI::result(Result r, const char* okMsg) {
  switch (r) {
    case Result::Ok: say(okMsg); PLAY(sOk); dirty = true; break;
    case Result::Full: say("Not hungry!"); PLAY(sNo); break;
    case Result::Asleep: say("Shh... sleeping"); PLAY(sNo); break;
    case Result::Sick: say("Needs medicine"); PLAY(sNo); break;
    case Result::Tired: say("Too tired"); PLAY(sNo); break;
    case Result::NotReady: say("Not now"); PLAY(sNo); break;
  }
}

void UI::onEvents(uint16_t ev) {
  if (!ev) return;
  dirty = true;
  if (ev & EV_HATCHED)  { say("Mochi hatched!", 2500); flashUntil = millis() + 1200; PLAY(sHappy); }
  if (ev & EV_EVOLVED)  { say("Mochi grew up!", 2500); flashUntil = millis() + 1500; PLAY(sEvolve); }
  if (ev & EV_BIRTHDAY) { say("Happy birthday! +5", 2500); PLAY(sHappy); }
  if (ev & EV_GIFT)     { say("A gift star!", 2000); PLAY(sGift); }
  if (ev & EV_HUNGRY)   { say("I'm hungry...", 2000); PLAY(sAlert); }
  if (ev & EV_TIRED)    { say("So sleepy...", 2000); PLAY(sSad); }
  if (ev & EV_SICK)     { say("Not feeling well", 2500); PLAY(sSad); }
  if (ev & EV_WOKE)     { say("Good morning!", 1800); PLAY(sOk); }
  if (ev & EV_ASLEEP)   { say("Zzz...", 1800); }
}

void UI::startStarCatch() { sc.reset(millis() | 1); gameT = millis(); go(Scr::StarCatch); }
void UI::startSays() { says.reset(millis() | 1); phase = SaysPhase::Show; saysIdx = 0; lit = -1; saysT = millis() + 700; go(Scr::Says); }
void UI::finishGame(int score) {
  Result r = pet.play(score > 255 ? 255 : score);
  go(Scr::Home);
  char b[32]; snprintf(b, sizeof(b), "Score %d!", score);
  result(r, b); if (r == Result::Ok) PLAY(sHappy);
}

void UI::onButton(hal::BtnEvt e) {
  lastInput = millis();
  if (e == hal::A_SHORT || e == hal::B_SHORT || e == hal::C_SHORT) { if (pet.s.soundOn && scr != Scr::StarCatch && scr != Scr::Says) PLAY(sBeep); }
  if (e == hal::B_LONG && scr != Scr::SetTime) { go(Scr::Home); return; }      // B larga = inicio
  int dir = (e == hal::A_SHORT) ? -1 : (e == hal::C_SHORT ? 1 : 0);
  bool ok = (e == hal::B_SHORT);

  switch (scr) {
    case Scr::Home:
      if (e == hal::A_SHORT) go(Scr::Menu);
      else if (ok) { result(pet.pat(), "<3"); }
      else if (e == hal::C_SHORT) { result(pet.toggleSleep(), pet.s.asleep ? "Good night" : "Good morning"); }
      break;
    case Scr::Menu:
      if (dir) cur = (cur + dir + 6) % 6;
      else if (ok) {
        switch (cur) {
          case 0: go(Scr::Feed); break;
          case 1: go(Scr::PlayPick); break;
          case 2: result(pet.toggleSleep(), pet.s.asleep ? "Good night" : "Good morning"); go(Scr::Home); break;
          case 3: result(pet.medicine(), "Feeling better"); go(Scr::Home); break;
          case 4: go(Scr::Status); break;
          case 5: go(Scr::Settings); break;
        }
      }
      break;
    case Scr::Feed:
      if (dir) cur = (cur + dir + 3) % 3;
      else if (ok) {
        Result r = pet.feed(static_cast<Food>(cur));
        if (r == Result::Ok) eatUntil = millis() + 1500;
        result(r, "Yum!"); go(Scr::Home);
      }
      break;
    case Scr::PlayPick:
      if (dir) cur = (cur + dir + 2) % 2;
      else if (ok) { if (pet.s.asleep || pet.s.energy < 10 || pet.stage() == Stage::Egg) { result(pet.play(0), ""); go(Scr::Home); }
                     else if (cur == 0) startStarCatch(); else startSays(); }
      break;
    case Scr::StarCatch:
      if (dir) { sc.step(dir); }
      break;
    case Scr::Says:
      if (phase == SaysPhase::Input) {
        int b = (e == hal::A_SHORT) ? 0 : (e == hal::B_SHORT ? 1 : (e == hal::C_SHORT ? 2 : -1));
        if (b >= 0) {
          lit = b; litUntil = millis() + 250; hal::playNotes(sSaysN[b], 1, pet.s.soundOn);
          if (!says.input(b)) { phase = SaysPhase::Over; resultUntil = millis() + 1500; PLAY(sNo); }
          else if (says.roundComplete) { if (says.len >= MochiSays::kMax) { says.nextRound(); phase = SaysPhase::Over; resultUntil = millis() + 1500; }
                                         else { says.nextRound(); phase = SaysPhase::Show; saysIdx = 0; lit = -1; saysT = millis() + 900; } }
        }
      }
      break;
    case Scr::Status: if (ok) go(Scr::Menu); break;
    case Scr::Settings:
      if (dir) cur = (cur + dir + 6) % 6;
      else if (ok) {
        switch (cur) {
          case 0: go(Scr::Themes); cur = pet.s.themeIdx & 3; break;
          case 1: pet.s.soundOn = !pet.s.soundOn; dirty = true; break;
          case 2: { uint8_t b = pet.s.brightness % 3; b = (b + 1) % 3; pet.s.brightness = b ? b : 3; hal::setBacklight(kBrightness[pet.s.brightness % 3]); dirty = true; break; }
          case 3: { uint32_t l = hal::nowEpoch() + pet.s.tzMinutes * 60; hh = (l / 3600) % 24; mm = (l / 60) % 60; tField = 0; go(Scr::SetTime); break; }
          case 4: pet.s.tzMinutes += 60; if (pet.s.tzMinutes > 840) pet.s.tzMinutes = -720; dirty = true; break;
          case 5: go(Scr::ConfirmReset); break;
        }
      }
      break;
    case Scr::Themes:
      if (dir) cur = (cur + dir + 4) % 4;
      else if (ok) { pet.s.themeIdx = cur; dirty = true; }
      break;
    case Scr::SetTime:
      if (dir) { if (tField == 0) hh = (hh + dir + 24) % 24; else mm = (mm + dir + 60) % 60; }
      else if (ok) {
        if (tField == 0) tField = 1;
        else {
          int32_t tz = pet.s.tzMinutes;
          int64_t local = static_cast<int64_t>(hal::nowEpoch()) + tz * 60;
          int64_t base = local - (((local % 86400) + 86400) % 86400);
          uint32_t utc = static_cast<uint32_t>(base + hh * 3600 + mm * 60 - tz * 60);
          if (!pet.s.clockValid) pet.setClock(utc, pet.s.tzMinutes); else pet.catchUp(utc);
          hal::setEpoch(utc); dirty = true; say("Clock set"); go(Scr::Home);
        }
      }
      break;
    case Scr::ConfirmReset:
      if (e == hal::A_SHORT) go(Scr::Settings);
      else if (e == hal::C_SHORT) { uint8_t th = pet.s.themeIdx, snd = pet.s.soundOn, br = pet.s.brightness; int16_t tz = pet.s.tzMinutes; uint32_t now = hal::nowEpoch();
                                    pet.reset(micros() | 1); pet.s.themeIdx = th; pet.s.soundOn = snd; pet.s.brightness = br; pet.setClock(now, tz); dirty = true; go(Scr::Home); say("New egg!"); }
      break;
  }
}

// ---------------- Render ----------------
void UI::render(uint32_t ms) {
  // minijuegos con reloj propio
  if (scr == Scr::StarCatch) {
    if (ms - gameT >= 100) { gameT += 100; sc.step(0); if (sc.over) { finishGame(sc.score); } }
  }
  if (scr == Scr::Says) {
    if (phase == SaysPhase::Show && ms >= saysT) {
      if (lit >= 0) { lit = -1; saysT = ms + 200; saysIdx++; if (saysIdx >= says.len) { phase = SaysPhase::Input; } }
      else if (saysIdx < says.len) { lit = says.seq[saysIdx]; hal::playNotes(sSaysN[lit], 1, pet.s.soundOn); saysT = ms + 450; }
    }
    if (lit >= 0 && phase == SaysPhase::Input && ms > litUntil) lit = -1;
    if (phase == SaysPhase::Over && ms > resultUntil) finishGame(says.score());
  }
  if (scr == Scr::Says || scr == Scr::StarCatch) drawBackground(); else drawBackground();
  switch (scr) {
    case Scr::Home: renderHome(ms); break;
    case Scr::Menu: renderMenu(); break;
    case Scr::Feed: renderFeed(); break;
    case Scr::PlayPick: renderPlayPick(); break;
    case Scr::StarCatch: renderStarCatch(ms); break;
    case Scr::Says: renderSays(ms); break;
    case Scr::Status: renderStatus(); break;
    case Scr::Settings: renderSettings(); break;
    case Scr::Themes: renderThemes(); break;
    case Scr::SetTime: renderSetTime(); break;
    case Scr::ConfirmReset: renderConfirm(); break;
  }
  toastOverlay(ms);
  if (ms < flashUntil) {   // destello de evolucion: bandas blancas que se desvanecen
    int a = (flashUntil - ms) * 100 / 1500;
    for (int y = 0; y < SCREEN_H; y += 6) if ((y / 6 + ms / 60) % 3 == 0) spr.drawFastHLine(0, y, SCREEN_W, rgb565(255, 255, 255 - a));
  }
}

void UI::renderHome(uint32_t ms) {
  uint32_t t = hal::nowEpoch() + pet.s.tzMinutes * 60;
  char tb[8]; snprintf(tb, sizeof(tb), "%02u:%02u", static_cast<unsigned>((t / 3600) % 24), static_cast<unsigned>((t / 60) % 60));
  drawText(tb, 120, 30, 4, TFT_WHITE, MC_DATUM);
  int bob = ((ms / (pet.s.asleep ? 900 : 380)) % 2) ? 0 : 4;
  if (pet.stage() == Stage::Egg) {
    drawSprite(kEggSprites[(ms / 350) % 2], kSpriteW, kSpriteH, 56 + ((ms / 350) % 2 ? 3 : -3), 50, 4);
    int pct = 100 * pet.s.ageSec / kEggSec; if (pct > 100) pct = 100;
    drawBar(70, 190, 100, pct, rgb565(255, 233, 138));
    return;
  }
  int si = (pet.stage() == Stage::Adult) ? 2 + static_cast<int>(pet.form()) : static_cast<int>(pet.stage()) - 1;   // 0..5
  Mood m = pet.mood();
  if (ms < eatUntil) m = Mood::Eating;
  // sombra y mascota
  spr.fillEllipse(120, 182, 34, 6, rgb565(30, 20, 70));
  drawSprite(kPetSprites[si][static_cast<int>(m)], kSpriteW, kSpriteH, 56, 46 + bob, 4);
  // fila de estadisticas
  const int ics[4] = {ICON_FOOD, ICON_HEART, ICON_BOLT, ICON_STAR};
  int vals[4] = {100 - pet.s.hunger, pet.s.happiness, pet.s.energy, pet.s.health};
  uint16_t cols[4] = {rgb565(255, 178, 107), rgb565(255, 107, 150), rgb565(255, 233, 138), rgb565(143, 227, 208)};
  for (int i = 0; i < 4; i++) {
    int x = 48 + i * 36;                       // 4 columnas dentro de la cuerda del circulo (y=200..217)
    drawIcon(ics[i], x + 12, 197, 1);
    drawBar(x, 209, 24, vals[i], cols[i]);
  }
}

void UI::renderMenu() {
  drawText("MOCHI", 120, 32, 4, TFT_WHITE, MC_DATUM);
  drawIcon(kMenuIcons[cur], 120, 112, 5);
  drawText(kMenuNames[cur], 120, 168, 4, TFT_WHITE, MC_DATUM);
  for (int i = 0; i < 6; i++) spr.fillCircle(84 + i * 14, 200, i == cur ? 4 : 2, i == cur ? TFT_WHITE : rgb565(200, 190, 230));
  drawText("<", 28, 112, 4, TFT_WHITE, MC_DATUM); drawText(">", 212, 112, 4, TFT_WHITE, MC_DATUM);
}

void UI::renderFeed() {
  drawText("Feed", 120, 32, 4, TFT_WHITE, MC_DATUM);
  if (cur == 0) { drawIcon(ICON_FOOD, 120, 112, 5); drawText("Onigiri", 120, 168, 4, TFT_WHITE, MC_DATUM); }
  if (cur == 1) { for (int i = 0; i < 3; i++) spr.fillCircle(120, 80 + i * 30, 18, i == 0 ? rgb565(255, 159, 181) : (i == 1 ? TFT_WHITE : rgb565(143, 227, 150)));
                  spr.drawFastVLine(120, 60, 100, rgb565(160, 110, 70)); drawText("Dango", 120, 178, 4, TFT_WHITE, MC_DATUM); }
  if (cur == 2) { spr.fillCircle(120, 112, 34, rgb565(224, 60, 90)); spr.fillTriangle(120, 72, 106, 62, 134, 62, rgb565(100, 200, 110)); drawText("Berry", 120, 168, 4, TFT_WHITE, MC_DATUM); }
  drawText("<", 28, 112, 4, TFT_WHITE, MC_DATUM); drawText(">", 212, 112, 4, TFT_WHITE, MC_DATUM);
}

void UI::renderPlayPick() {
  drawText("Play", 120, 32, 4, TFT_WHITE, MC_DATUM);
  if (cur == 0) { drawIcon(ICON_STAR, 120, 108, 5); drawText("Star Catch", 120, 168, 4, TFT_WHITE, MC_DATUM); drawText("A/C move", 120, 196, 2, TFT_WHITE, MC_DATUM); }
  else          { drawIcon(ICON_GAME, 120, 108, 5); drawText("Mochi Says", 120, 168, 4, TFT_WHITE, MC_DATUM); drawText("Repeat the stars", 120, 196, 2, TFT_WHITE, MC_DATUM); }
}

void UI::renderStarCatch(uint32_t) {
  const int x0 = 40, lw = 32, y0 = 44, rh = 22;
  char b[24]; snprintf(b, sizeof(b), "%d/%d", sc.score, StarCatch::kWinScore);
  drawText(b, 120, 28, 4, TFT_WHITE, MC_DATUM);
  for (int i = 0; i < sc.lives; i++) drawIcon(ICON_HEART, 96 + i * 24, 188 + 34, 1);
  for (auto& s : sc.stars) if (s.alive) drawIcon(ICON_STAR, x0 + s.lane * lw + lw / 2, y0 + s.row * rh + 8, 2);
  int si = pet.stage() == Stage::Egg ? 0 : (pet.stage() == Stage::Adult ? 2 + static_cast<int>(pet.form()) : static_cast<int>(pet.stage()) - 1);
  drawSprite(kPetSprites[si][static_cast<int>(Mood::Happy)], kSpriteW, kSpriteH, x0 + sc.lane * lw, y0 + (StarCatch::kRows - 1) * rh - 6, 1);
}

void UI::renderSays(uint32_t) {
  const int xs[3] = {50, 120, 190};
  drawText(phase == SaysPhase::Show ? "Watch..." : (phase == SaysPhase::Input ? "Your turn!" : "Done"), 120, 34, 4, TFT_WHITE, MC_DATUM);
  char b[16]; snprintf(b, sizeof(b), "Round %d", says.len); drawText(b, 120, 62, 2, TFT_WHITE, MC_DATUM);
  for (int i = 0; i < 3; i++) {
    spr.fillCircle(xs[i], 130, lit == i ? 34 : 28, lit == i ? rgb565(255, 255, 255) : rgb565(60, 40, 110));
    drawIcon(ICON_STAR, xs[i], 130, lit == i ? 3 : 2);
    drawText(i == 0 ? "A" : (i == 1 ? "B" : "C"), xs[i], 178, 2, TFT_WHITE, MC_DATUM);
  }
}

void UI::renderStatus() {
  static const char* names[4] = {"Hunger", "Happy", "Energy", "Health"};
  int vals[4] = {pet.s.hunger, pet.s.happiness, pet.s.energy, pet.s.health};
  uint16_t cols[4] = {rgb565(255, 178, 107), rgb565(255, 107, 150), rgb565(255, 233, 138), rgb565(143, 227, 208)};
  char b[40]; snprintf(b, sizeof(b), "%s  %lud", kStageNames[pet.s.stage], static_cast<unsigned long>(pet.s.ageSec / 86400u));
  drawText(b, 120, 30, 4, TFT_WHITE, MC_DATUM);
  for (int i = 0; i < 4; i++) { drawText(names[i], 40, 66 + i * 26, 2, TFT_WHITE, ML_DATUM); drawBar(100, 62 + i * 26, 90, vals[i], cols[i]); }
  snprintf(b, sizeof(b), "Stars %lu   Care %u", static_cast<unsigned long>(pet.s.stars), pet.s.care); drawText(b, 120, 176, 2, TFT_WHITE, MC_DATUM);
  uint16_t mv = hal::batteryMv(); int pct = (mv - 3300) * 100 / (4150 - 3300); if (pct < 0) pct = 0; if (pct > 100) pct = 100;
  snprintf(b, sizeof(b), "Batt %d%% %s", pct, hal::charging() ? "(charging)" : ""); drawText(b, 120, 200, 2, TFT_WHITE, MC_DATUM);
}

void UI::renderSettings() {
  char b[28]; static const char* names[6] = {"Theme", "Sound", "Brightness", "Set time", "UTC offset", "Reset pet"};
  drawText("Settings", 120, 32, 4, TFT_WHITE, MC_DATUM);
  drawText(names[cur], 120, 100, 4, TFT_WHITE, MC_DATUM);
  b[0] = 0;
  if (cur == 0) snprintf(b, sizeof(b), "%s", kThemes[pet.s.themeIdx & 3].name);
  if (cur == 1) snprintf(b, sizeof(b), "%s", pet.s.soundOn ? "ON" : "OFF");
  if (cur == 2) snprintf(b, sizeof(b), "Level %d/3", (pet.s.brightness % 3 == 0 ? 3 : pet.s.brightness % 3));
  if (cur == 4) snprintf(b, sizeof(b), "UTC%+d", pet.s.tzMinutes / 60);
  drawText(b, 120, 140, 4, rgb565(255, 233, 138), MC_DATUM);
  drawText("<", 28, 112, 4, TFT_WHITE, MC_DATUM); drawText(">", 212, 112, 4, TFT_WHITE, MC_DATUM);
  drawText("B: change", 120, 196, 2, TFT_WHITE, MC_DATUM);
}

// Pantalla de temas: 4 circulos de color con marca de verificacion (como la referencia de diseno).
void UI::renderThemes() {
  drawText("Themes", 120, 34, 4, rgb565(255, 120, 200), MC_DATUM);
  for (int i = 0; i < 4; i++) {
    int cx = 84 + (i % 2) * 72, cy = 100 + (i / 2) * 64;
    spr.fillCircle(cx, cy, 26, themeBottom(i));
    if (i == cur) spr.drawCircle(cx, cy, 30, TFT_WHITE);
    if (i == (pet.s.themeIdx & 3)) drawIcon(ICON_CHECK, cx, cy, 2);
  }
}

void UI::renderSetTime() {
  char b[16]; snprintf(b, sizeof(b), "%02d:%02d", hh, mm);
  drawText("Set time", 120, 40, 4, TFT_WHITE, MC_DATUM);
  drawText(b, 120, 118, 4, TFT_WHITE, MC_DATUM);
  spr.fillRect(tField == 0 ? 78 : 126, 140, 36, 4, rgb565(255, 233, 138));
  drawText("A -   C +   B next", 120, 190, 2, TFT_WHITE, MC_DATUM);
}

void UI::renderConfirm() {
  drawText("Reset pet?", 120, 80, 4, TFT_WHITE, MC_DATUM);
  drawText("All progress is lost", 120, 116, 2, TFT_WHITE, MC_DATUM);
  drawText("A: cancel     C: yes", 120, 170, 2, rgb565(255, 233, 138), MC_DATUM);
}

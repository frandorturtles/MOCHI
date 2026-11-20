// Renderiza las pantallas del firmware en el PC y guarda capturas (PPM + textos) para tools/snap2png.py.
// Sirve como prueba de humo de TODO el codigo de UI y para generar las imagenes del README.
#include "../firmware/src/ui.h"
#include "../firmware/src/config.h"
#include <stdio.h>
#include <stdlib.h>
uint32_t g_ms = 100000;
namespace hal {
TFT_eSprite spr(nullptr);
void setBacklight(uint8_t) {} void playNotes(const Note*, uint8_t, bool) {}
uint32_t nowEpoch() { return 1790000000u + 12 * 3600 + 34 * 60; }  // 12:34 UTC
void setEpoch(uint32_t) {} uint16_t batteryMv() { return 3900; } bool charging() { return true; }
}
using namespace mochi; using hal::BtnEvt;

static void snap(UI& ui, const char* name) {
  hal::spr.texts.clear(); ui.render(g_ms);
  char p[96]; snprintf(p, sizeof p, "%s/%s.ppm", getenv("SNAP_DIR") ? getenv("SNAP_DIR") : ".", name);
  FILE* f = fopen(p, "wb"); fprintf(f, "P6\n240 240\n255\n");
  for (uint16_t c : hal::spr.buf) { uint8_t rgb[3] = {uint8_t((c >> 8) & 0xF8), uint8_t((c >> 3) & 0xFC), uint8_t((c << 3) & 0xF8)}; fwrite(rgb, 1, 3, f); }
  fclose(f);
  snprintf(p, sizeof p, "%s/%s.txt", getenv("SNAP_DIR") ? getenv("SNAP_DIR") : ".", name);
  f = fopen(p, "w"); for (auto& t : hal::spr.texts) fprintf(f, "%d|%d|%d|%d|%d|%s\n", t.x, t.y, t.font, t.datum, t.col, t.s.c_str()); fclose(f);
}
static void press(UI& ui, BtnEvt e, int n = 1) { while (n--) { ui.onButton(e); g_ms += 60; } }

int main() {
  hal::spr.createSprite(SCREEN_W, SCREEN_H);
  Pet pet; pet.reset(1); pet.setClock(1790000000u, -300);
  UI ui(pet); ui.begin();
  snap(ui, "01_egg");
  pet.advance(200, 1790000200u); pet.s.themeIdx = 0;
  snap(ui, "02_home_baby");
  pet.s.stage = 4; pet.s.form = 1; pet.s.hunger = 80; pet.s.happiness = 60; snap(ui, "03_home_angel_hungry");
  pet.s.hunger = 30; pet.s.happiness = 90; pet.s.form = 2; pet.s.themeIdx = 2; snap(ui, "04_home_star_night"); pet.s.themeIdx = 0;
  press(ui, hal::A_SHORT); snap(ui, "05_menu_feed");
  press(ui, hal::C_SHORT); snap(ui, "06_menu_play");
  press(ui, hal::B_SHORT); snap(ui, "07_play_pick");
  press(ui, hal::B_SHORT);
  for (int i = 0; i < 60; i++) { g_ms += 100; ui.render(g_ms); }
  snap(ui, "08_star_catch"); press(ui, hal::B_LONG);
  press(ui, hal::A_SHORT); press(ui, hal::C_SHORT); press(ui, hal::B_SHORT); press(ui, hal::C_SHORT); press(ui, hal::B_SHORT);
  g_ms += 1500; for (int i = 0; i < 4; i++) { g_ms += 100; ui.render(g_ms); } snap(ui, "09_mochi_says"); press(ui, hal::B_LONG);
  press(ui, hal::A_SHORT); press(ui, hal::C_SHORT, 4); snap(ui, "10_menu_status"); press(ui, hal::B_SHORT); snap(ui, "11_status"); press(ui, hal::B_LONG);
  press(ui, hal::A_SHORT); press(ui, hal::C_SHORT, 5); press(ui, hal::B_SHORT); snap(ui, "12_settings"); press(ui, hal::B_SHORT); snap(ui, "13_themes"); press(ui, hal::B_LONG);
  press(ui, hal::A_SHORT); press(ui, hal::C_SHORT, 5); press(ui, hal::B_SHORT); press(ui, hal::C_SHORT, 3); press(ui, hal::B_SHORT); snap(ui, "14_set_time");
  printf("capturas OK\n"); return 0;
}

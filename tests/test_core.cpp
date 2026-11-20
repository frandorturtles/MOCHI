// Pruebas del nucleo de MOCHI (PC, sin hardware):  make -C tests
#include "../firmware/src/pet.h"
#include "../firmware/src/minigame.h"
#include <stdio.h>
#include <string.h>

using namespace mochi;
static int fails = 0, checks = 0;
#define CHECK(c) do { checks++; if (!(c)) { fails++; printf("FALLO %s:%d  %s\n", __FILE__, __LINE__, #c); } } while (0)

static const uint32_t T0 = 1790000000u;  // epoch arbitrario

static void test_hatch_and_growth() {
  Pet p; p.reset(1); p.setClock(T0, -300);
  CHECK(p.stage() == Stage::Egg);
  uint16_t ev = 0; for (int i = 0; i < 119; i++) ev |= p.advance(1, T0 + i);
  CHECK(p.stage() == Stage::Egg && !(ev & EV_HATCHED));
  ev = p.advance(1, T0 + 120);
  CHECK(p.stage() == Stage::Baby && (ev & EV_HATCHED));
  uint8_t h0 = p.s.hunger;
  p.advance(1800, T0 + 1920);                 // 1800 s / 180 s = +10
  CHECK(p.s.hunger == h0 + 10);
}

static void test_feed_rules() {
  Pet p; p.reset(2); p.advance(121, T0);
  p.s.hunger = 5;
  CHECK(p.feed(Food::Onigiri) == Result::Full);
  p.s.hunger = 60;
  CHECK(p.feed(Food::Onigiri) == Result::Ok && p.s.hunger == 30);
  p.s.asleep = 1;
  CHECK(p.feed(Food::Dango) == Result::Asleep);
  p.s.asleep = 0; p.s.health = 10;
  CHECK(p.feed(Food::Dango) == Result::Sick);
  CHECK(p.medicine() == Result::Ok && p.s.health == 40);
}

static void test_sleep_cycle() {
  Pet p; p.reset(3); p.advance(121, T0);
  p.s.energy = 30;
  CHECK(p.toggleSleep() == Result::Ok && p.mood() == Mood::Sleeping);
  uint16_t ev = p.advance(45u * 70u, T0 + 5000);   // 70 pts * 45 s
  CHECK(p.s.energy == 100 && !p.s.asleep && (ev & EV_WOKE));
  CHECK(p.toggleSleep() == Result::NotReady);     // no tiene sueno
}

static void test_neglect_makes_sick() {
  Pet p; p.reset(4); p.advance(121, T0);
  p.s.hunger = 100;
  uint16_t ev = p.advance(120u * 80u, T0 + 20000);
  CHECK(p.s.health < 30 && (ev & EV_SICK) && p.mood() == Mood::Sick);
}

// Simula 3 dias con cuidador diligente o negligente y revisa la forma adulta.
static Form simulate(bool diligent) {
  Pet p; p.reset(99); p.setClock(T0, 0);
  uint32_t now = T0;
  for (uint32_t t = 0; t < kTeenEnd + 600; t++) {
    now++; p.advance(1, now);
    if (!diligent) continue;
    if (t % 60 == 0 && p.s.asleep == 0 && p.s.hunger >= 50) p.feed(Food::Dango);
    if (t % 900 == 0) p.play(6);
    if (t % 600 == 0 && p.s.energy < 40) p.toggleSleep();
    if (t % 1200 == 0 && p.s.health < 60) p.medicine();
  }
  return p.form();
}
static void test_evolution_forms() {
  Pet p; p.reset(5); p.advance(kTeenEnd + 200, T0);
  CHECK(p.stage() == Stage::Adult);
  CHECK(simulate(true) == Form::Angel || simulate(true) == Form::Star);
  CHECK(simulate(false) == Form::Dreamer);
}

static void test_offline_catchup_cap() {
  Pet p; p.reset(6); p.setClock(T0, 0); p.advance(121, T0 + 121);
  uint32_t age0 = p.s.ageSec;
  p.catchUp(T0 + 121 + 30u * 86400u);              // 30 dias apagado
  CHECK(p.s.ageSec - age0 == kMaxOfflineSec / 2);  // tope: 6 h reales = 3 h de vida
  Pet q; q.reset(7); q.setClock(T0, 0);
  CHECK(q.catchUp(T0 - 100) == 0 && q.s.lastEpoch == T0 - 100);  // reloj hacia atras: no revienta
}

static void test_clock_tz() {
  Pet p; p.reset(8); p.setClock(0, -300);          // Colombia UTC-5
  CHECK(p.localHour(0) == 19);                     // 00:00 UTC = 19:00 local
  CHECK(p.localHour(5u * 3600u) == 0);
  p.s.tzMinutes = 330; CHECK(p.localHour(0) == 5); // UTC+5:30
}

static void test_save_crc() {
  Pet p; p.reset(9); p.advance(500, T0); p.s.stars = 42;
  seal(p.s);
  PetState copy; memcpy(&copy, &p.s, sizeof copy);
  Pet q; CHECK(q.adopt(copy) && q.s.stars == 42);
  copy.hunger ^= 0x10; CHECK(!verify(copy));       // un bit alterado se detecta
  PetState bad = p.s; bad.stage = 9; seal(bad);
  CHECK(!q.adopt(bad));                            // CRC valido pero valores fuera de rango
  CHECK(crc32(reinterpret_cast<const uint8_t*>("123456789"), 9) == 0xCBF43926u);  // vector estandar
}

static void test_star_catch() {
  StarCatch a, b; a.reset(1234); b.reset(1234);
  int moves[7] = {-1, 0, 1, 1, 0, -1, 0};
  for (int i = 0; i < 600 && !(a.over); i++) { a.step(moves[i % 7]); b.step(moves[i % 7]); }
  CHECK(a.score == b.score && a.lives == b.lives);  // determinista
  CHECK(a.over);                                    // sin jugar bien termina
  CHECK(a.lane >= 0 && a.lane < StarCatch::kLanes);
  // Un bot que sigue la estrella mas baja deberia ganar.
  StarCatch g; g.reset(77);
  for (int i = 0; i < 4000 && !g.over; i++) {
    int best = -1, row = -1;
    for (auto& s : g.stars) if (s.alive && s.row > row) { row = s.row; best = s.lane; }
    int mv = best < 0 ? 0 : (best > g.lane ? 1 : (best < g.lane ? -1 : 0));
    g.step(mv);
  }
  CHECK(g.over && g.won);
}

static void test_mochi_says() {
  MochiSays m; m.reset(5);
  for (int r = 0; r < MochiSays::kMax; r++) {
    for (int i = 0; i < m.len; i++) CHECK(m.input(m.seq[i]));
    CHECK(m.roundComplete);
    m.nextRound();
  }
  CHECK(m.over && m.won && m.score() == MochiSays::kMax);
  MochiSays e; e.reset(5); CHECK(!e.input((e.seq[0] + 1) % 3) && e.over && !e.won && e.score() == 0);
}

int main() {
  test_hatch_and_growth(); test_feed_rules(); test_sleep_cycle(); test_neglect_makes_sick();
  test_evolution_forms(); test_offline_catchup_cap(); test_clock_tz(); test_save_crc();
  test_star_catch(); test_mochi_says();
  printf("%d comprobaciones, %d fallos\n", checks, fails);
  return fails ? 1 : 0;
}

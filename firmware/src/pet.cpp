#include "pet.h"
#include <string.h>

namespace mochi {

static inline uint8_t clampU(int v) { return v < 0 ? 0 : (v > 100 ? 100 : static_cast<uint8_t>(v)); }
static uint32_t drain(uint32_t& acc, uint32_t dt, uint32_t period) {
  acc += dt;
  uint32_t n = acc / period;
  acc -= n * period;
  return n;
}
static const uint16_t kHungerPeriod[5] = {0, 180, 240, 300, 360};  // s por punto de hambre (despierto)

Stage stageForAge(uint32_t a) {
  if (a < kEggSec)   return Stage::Egg;
  if (a < kBabyEnd)  return Stage::Baby;
  if (a < kChildEnd) return Stage::Child;
  if (a < kTeenEnd)  return Stage::Teen;
  return Stage::Adult;
}

uint32_t Pet::rnd() {
  uint32_t x = s.rng ? s.rng : 0xA341316Cu;
  x ^= x << 13; x ^= x >> 17; x ^= x << 5;
  s.rng = x;
  return x;
}

void Pet::reset(uint32_t seed) {
  memset(&s, 0, sizeof(s));
  s.magic = kMagic; s.version = kVersion;
  s.rng = seed ? seed : 0xA341316Cu;
  s.stage = static_cast<uint8_t>(Stage::Egg);
  s.hunger = 0; s.happiness = 80; s.energy = 100; s.health = 100;
  s.soundOn = 1; s.brightness = 200;
}

bool Pet::adopt(const PetState& l) {
  if (!verify(l)) return false;
  if (l.stage > static_cast<uint8_t>(Stage::Adult) || l.form > static_cast<uint8_t>(Form::Dreamer)) return false;
  if (l.hunger > 100 || l.happiness > 100 || l.energy > 100 || l.health > 100) return false;
  s = l;
  return true;
}

void Pet::setClock(uint32_t epochUtc, int16_t tzMin) {
  s.clockValid = 1; s.tzMinutes = tzMin;
  s.lastEpoch = epochUtc; s.lastHourIdx = epochUtc / 3600;
}

int Pet::localHour(uint32_t epochUtc) const {
  int64_t t = static_cast<int64_t>(epochUtc) + static_cast<int64_t>(s.tzMinutes) * 60;
  int64_t h = (t / 3600) % 24;
  return static_cast<int>(h < 0 ? h + 24 : h);
}

Mood Pet::mood() const {
  if (s.asleep) return Mood::Sleeping;
  if (s.health < 30) return Mood::Sick;
  if (s.hunger >= 70) return Mood::Hungry;
  if (s.energy <= 20) return Mood::Tired;
  if (s.happiness <= 30) return Mood::Sad;
  if (s.happiness >= 75) return Mood::Happy;
  return Mood::Neutral;
}

uint16_t Pet::step(uint32_t dt, uint32_t now) {
  uint16_t ev = 0;
  const uint32_t prevAge = s.ageSec;
  s.ageSec += dt;
  const Stage target = stageForAge(s.ageSec);

  if (stage() == Stage::Egg) {
    if (target != Stage::Egg) {
      s.stage = static_cast<uint8_t>(Stage::Baby);
      s.hunger = 20; s.happiness = 80; s.energy = 100; s.health = 100;
      ev |= EV_HATCHED;
    }
    return ev;
  }

  const bool asleep = s.asleep != 0;
  const uint8_t pHunger = s.hunger, pEnergy = s.energy, pHealth = s.health;

  // Hambre
  uint32_t per = kHungerPeriod[s.stage] * (asleep ? 3u : 1u);
  s.hunger = clampU(s.hunger + static_cast<int>(drain(s.accHunger, dt, per)));

  // Felicidad (solo despierto; baja el doble de rapido con hambre o cansancio)
  if (!asleep) {
    uint32_t p = (s.hunger >= 70 || s.energy <= 20) ? 150 : 300;
    s.happiness = clampU(s.happiness - static_cast<int>(drain(s.accHappy, dt, p)));
  }

  // Energia / sueno
  if (asleep) s.energy = clampU(s.energy + static_cast<int>(drain(s.accEnergy, dt, 45)));
  else        s.energy = clampU(s.energy - static_cast<int>(drain(s.accEnergy, dt, 360)));

  // Salud
  const bool neglect = s.hunger >= 95 || (s.happiness == 0 && !asleep);
  if (neglect) {
    uint32_t n = drain(s.accHealth, dt, 120);
    s.health = clampU(s.health - static_cast<int>(n));
    s.care = (s.care > n) ? static_cast<uint16_t>(s.care - n) : 0;
  } else if (s.hunger < 60 && s.happiness >= 30) {
    s.health = clampU(s.health + static_cast<int>(drain(s.accHealth, dt, 300)));
  }

  if (pHunger < 70 && s.hunger >= 70) ev |= EV_HUNGRY;
  if (pEnergy > 20 && s.energy <= 20) ev |= EV_TIRED;
  if (pHealth >= 30 && s.health < 30) ev |= EV_SICK;

  // Dormir y despertar automaticos
  if (!s.asleep && s.energy == 0)   { s.asleep = 1; ev |= EV_ASLEEP; }
  if (s.asleep && s.energy >= 100)  { s.asleep = 0; ev |= EV_WOKE; }

  // Evolucion
  if (target > stage()) {
    s.stage = static_cast<uint8_t>(target);
    ev |= EV_EVOLVED;
    if (target == Stage::Adult)
      s.form = static_cast<uint8_t>(s.care >= kCareAngel ? Form::Angel : (s.care >= kCareStar ? Form::Star : Form::Dreamer));
  }

  // Cumpleanos
  if (prevAge / 86400u != s.ageSec / 86400u) {
    ev |= EV_BIRTHDAY; s.stars += 5; s.happiness = clampU(s.happiness + 10);
  }

  // Eventos por hora (requieren reloj valido)
  if (s.clockValid) {
    uint32_t h = now / 3600u;
    if (h != s.lastHourIdx) {
      s.lastHourIdx = h;
      uint32_t r = rnd() % 100u;
      if (r < 8) { s.stars += 1 + rnd() % 3u; ev |= EV_GIFT; }
      else if (r < 12 && s.hunger > 70) {          // dolor de barriga
        uint8_t before = s.health;
        s.health = clampU(s.health - 8);
        if (before >= 30 && s.health < 30) ev |= EV_SICK;
      }
    }
  }
  return ev;
}

uint16_t Pet::advanceRaw(uint32_t dt, uint32_t nowEpoch) {
  uint16_t ev = 0;
  uint32_t done = 0;
  while (done < dt) {
    uint32_t c = (dt - done > 60) ? 60 : (dt - done);
    done += c;
    ev |= step(c, nowEpoch - (dt - done));
  }
  return ev;
}

uint16_t Pet::advance(uint32_t dt, uint32_t nowEpoch) {
  uint16_t ev = advanceRaw(dt * timeScale, nowEpoch);
  s.lastEpoch = nowEpoch;
  return ev;
}

uint16_t Pet::catchUp(uint32_t nowEpoch) {
  if (!s.clockValid || nowEpoch <= s.lastEpoch) { s.lastEpoch = nowEpoch; return 0; }
  uint32_t gap = nowEpoch - s.lastEpoch;
  if (gap > kMaxOfflineSec) gap = kMaxOfflineSec;
  uint16_t ev = advanceRaw(gap / 2u, nowEpoch);   // apagado = envejece a mitad de ritmo
  s.lastEpoch = nowEpoch;
  return ev;
}

// ---------------- Acciones ----------------
Result Pet::feed(Food f) {
  if (stage() == Stage::Egg) return Result::NotReady;
  if (s.asleep) return Result::Asleep;
  if (s.health < 30) return Result::Sick;
  if (s.hunger < 10) { s.happiness = clampU(s.happiness - 2); return Result::Full; }
  const int hungryBefore = s.hunger;
  switch (f) {
    case Food::Onigiri: s.hunger = clampU(s.hunger - 30); s.happiness = clampU(s.happiness + 2); break;
    case Food::Dango:   s.hunger = clampU(s.hunger - 15); s.happiness = clampU(s.happiness + 10); break;
    case Food::Berry:   s.hunger = clampU(s.hunger - 20); s.energy = clampU(s.energy + 5); s.happiness = clampU(s.happiness + 4); break;
    default: break;
  }
  uint16_t gain = hungryBefore >= 50 ? 3 : 1;
  s.care = (s.care + gain > 1000) ? 1000 : static_cast<uint16_t>(s.care + gain);
  return Result::Ok;
}

Result Pet::medicine() {
  if (stage() == Stage::Egg) return Result::NotReady;
  if (s.health >= 100) return Result::Full;
  s.health = clampU(s.health + 30);
  s.happiness = clampU(s.happiness - 5);
  s.care = (s.care + 2 > 1000) ? 1000 : static_cast<uint16_t>(s.care + 2);
  return Result::Ok;
}

Result Pet::play(uint8_t score) {
  if (stage() == Stage::Egg) return Result::NotReady;
  if (s.asleep) return Result::Asleep;
  if (s.health < 30) return Result::Sick;
  if (s.energy < 10) return Result::Tired;
  int gain = 8 + score * 4; if (gain > 35) gain = 35;
  s.happiness = clampU(s.happiness + gain);
  s.energy = clampU(s.energy - 8);
  s.hunger = clampU(s.hunger + 6);
  s.stars += score / 3u;
  uint16_t c = score >= 3 ? 2 : 1;
  s.care = (s.care + c > 1000) ? 1000 : static_cast<uint16_t>(s.care + c);
  return Result::Ok;
}

Result Pet::pat() {
  if (stage() == Stage::Egg) return Result::NotReady;
  if (s.asleep) return Result::Asleep;
  if (s.happiness < 60) s.happiness = clampU(s.happiness + 2);
  return Result::Ok;
}

Result Pet::toggleSleep() {
  if (stage() == Stage::Egg) return Result::NotReady;
  if (s.asleep) { s.asleep = 0; return Result::Ok; }
  if (s.energy >= 95) return Result::NotReady;
  s.asleep = 1;
  return Result::Ok;
}

// ---------------- CRC / sellado ----------------
uint32_t crc32(const uint8_t* d, size_t n) {
  uint32_t c = 0xFFFFFFFFu;
  for (size_t i = 0; i < n; i++) {
    c ^= d[i];
    for (int k = 0; k < 8; k++) c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
  }
  return ~c;
}

void seal(PetState& st) {
  st.magic = kMagic; st.version = kVersion;
  st.crc = crc32(reinterpret_cast<const uint8_t*>(&st), sizeof(PetState) - sizeof(uint32_t));
}

bool verify(const PetState& st) {
  if (st.magic != kMagic || st.version != kVersion) return false;
  return st.crc == crc32(reinterpret_cast<const uint8_t*>(&st), sizeof(PetState) - sizeof(uint32_t));
}

}  // namespace mochi

// MOCHI - nucleo de la mascota (logica pura, sin dependencias de Arduino).
// Se compila igual en el ESP32-C3 y en el PC (ver tests/).
#pragma once
#include <stdint.h>
#include <stddef.h>

namespace mochi {

// ---------- Constantes de juego (segundos de vida del dispositivo) ----------
constexpr uint32_t kMagic        = 0x4D4F4348;   // MOCH
constexpr uint16_t kVersion      = 1;
constexpr uint32_t kEggSec       = 120;          // huevo -> bebe
constexpr uint32_t kBabyEnd      = 6u * 3600u;   // bebe -> nino
constexpr uint32_t kChildEnd     = 24u * 3600u;  // nino -> adolescente
constexpr uint32_t kTeenEnd      = 72u * 3600u;  // adolescente -> adulto
constexpr uint32_t kMaxOfflineSec = 6u * 3600u;  // maximo a recuperar tras apagado
constexpr uint16_t kCareAngel    = 150;          // cuidado >= -> forma Angel
constexpr uint16_t kCareStar     = 70;           // cuidado >= -> forma Star, si no Dreamer

enum class Stage : uint8_t { Egg = 0, Baby, Child, Teen, Adult };
enum class Form  : uint8_t { None = 0, Angel, Star, Dreamer };
enum class Mood  : uint8_t { Neutral = 0, Happy, Hungry, Sad, Tired, Sleeping, Eating, Sick, kCount };
enum class Food  : uint8_t { Onigiri = 0, Dango, Berry, kCount };
enum class Result : uint8_t { Ok = 0, Full, Asleep, Sick, Tired, NotReady };

// Eventos devueltos por advance() como mascara de bits (para sonidos/animaciones).
enum Event : uint16_t {
  EV_NONE = 0,
  EV_HATCHED  = 1 << 0,
  EV_EVOLVED  = 1 << 1,
  EV_GIFT     = 1 << 2,
  EV_HUNGRY   = 1 << 3,
  EV_TIRED    = 1 << 4,
  EV_SICK     = 1 << 5,
  EV_BIRTHDAY = 1 << 6,
  EV_WOKE     = 1 << 7,
  EV_ASLEEP   = 1 << 8,
};

// Estado persistente: 64 bytes exactos, sin padding, con CRC32 al final.
struct PetState {
  uint32_t magic;
  uint16_t version;
  uint16_t reserved0;
  uint32_t ageSec;        // segundos de vida (incluye huevo)
  uint32_t lastEpoch;     // ultimo instante UTC procesado
  uint32_t rng;           // estado xorshift32
  uint32_t stars;         // moneda: estrellas ganadas
  uint32_t accHunger, accHappy, accEnergy, accHealth;  // acumuladores (s)
  uint32_t lastHourIdx;   // epoch/3600 de la ultima tirada de eventos
  int16_t  tzMinutes;     // zona horaria respecto a UTC
  uint16_t care;          // puntaje de cuidado 0..1000
  uint8_t  stage, form;
  uint8_t  hunger, happiness, energy, health;  // 0..100 (hunger: 100 = hambriento)
  uint8_t  asleep, clockValid;
  uint8_t  themeIdx, soundOn, brightness, reserved1;
  uint32_t crc;
};
static_assert(sizeof(PetState) == 64, "PetState debe medir 64 bytes");

class Pet {
 public:
  PetState s;
  uint16_t timeScale = 1;  // >1 solo para depuracion (envejecimiento rapido)

  void reset(uint32_t seed);                       // huevo nuevo
  bool adopt(const PetState& loaded);              // valida y carga estado guardado
  uint16_t advance(uint32_t dtSec, uint32_t nowEpoch);   // avanza el tiempo en vivo
  uint16_t catchUp(uint32_t nowEpoch);             // tras arrancar: recupera tiempo apagado
  void setClock(uint32_t epochUtc, int16_t tzMin);

  Stage stage() const { return static_cast<Stage>(s.stage); }
  Form  form()  const { return static_cast<Form>(s.form); }
  Mood  mood()  const;
  int   localHour(uint32_t epochUtc) const;

  Result feed(Food f);
  Result medicine();
  Result play(uint8_t score);   // score 0..15 desde un minijuego
  Result pat();
  Result toggleSleep();

 private:
  uint16_t step(uint32_t dt, uint32_t nowEpoch);   // dt <= 60 s
  uint16_t advanceRaw(uint32_t dt, uint32_t nowEpoch);
  uint32_t rnd();
};

Stage stageForAge(uint32_t ageSec);

// Guardado: CRC32 (IEEE) y sellado/verificacion del bloque.
uint32_t crc32(const uint8_t* data, size_t n);
void seal(PetState& st);
bool verify(const PetState& st);

}  // namespace mochi

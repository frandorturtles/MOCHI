// Minijuegos de MOCHI (logica pura). Los 3 botones fisicos son A, B, C (las 3 estrellas).
#pragma once
#include <stdint.h>

namespace mochi {

// "Atrapa estrellas": A = izquierda, C = derecha. Llama step() cada ~100 ms.
class StarCatch {
 public:
  static constexpr int kLanes = 5, kRows = 6, kMaxStars = 3, kWinScore = 15;
  struct Star { int8_t lane, row; bool alive; };
  Star stars[kMaxStars];
  int lane = 2, score = 0, lives = 3;
  bool over = false, won = false;

  void reset(uint32_t seed);
  void step(int move);          // move: -1 izquierda, 0 nada, +1 derecha
 private:
  uint32_t rng_ = 1, tick_ = 0;
  uint32_t rnd();
};

// "Mochi dice": repite la secuencia con A/B/C (memoria, secuencias hasta 12).
class MochiSays {
 public:
  static constexpr int kMax = 12;
  uint8_t seq[kMax];
  int len = 0, pos = 0;
  bool roundComplete = false, over = false, won = false;

  void reset(uint32_t seed);    // empieza con 1 elemento
  bool input(uint8_t button);   // 0..2; false = error (game over)
  void nextRound();             // tras roundComplete: agrega un elemento
  int  score() const { return over && !won ? len - 1 : len; }   // rondas completadas
 private:
  uint32_t rng_ = 1;
  uint32_t rnd();
};

}  // namespace mochi

#include "minigame.h"

namespace mochi {

uint32_t StarCatch::rnd() { rng_ ^= rng_ << 13; rng_ ^= rng_ >> 17; rng_ ^= rng_ << 5; return rng_; }

void StarCatch::reset(uint32_t seed) {
  rng_ = seed ? seed : 7; tick_ = 0;
  lane = kLanes / 2; score = 0; lives = 3; over = won = false;
  for (auto& s : stars) s = {0, 0, false};
}

void StarCatch::step(int move) {
  if (over) return;
  lane += move;
  if (lane < 0) lane = 0;
  if (lane > kLanes - 1) lane = kLanes - 1;
  tick_++;

  int fallEvery = 6 - score / 4; if (fallEvery < 2) fallEvery = 2;
  int spawnEvery = 14 - score / 3; if (spawnEvery < 6) spawnEvery = 6;

  if (tick_ % fallEvery == 0) {
    for (auto& s : stars) {
      if (!s.alive) continue;
      s.row++;
      if (s.row >= kRows - 1) {              // llega al piso
        s.alive = false;
        if (s.lane == lane) score++; else lives--;
      }
    }
  }
  if (tick_ % spawnEvery == 0) {
    for (auto& s : stars) if (!s.alive) { s = {static_cast<int8_t>(rnd() % kLanes), 0, true}; break; }
  }
  if (score >= kWinScore) { over = true; won = true; }
  else if (lives <= 0)    { over = true; }
}

uint32_t MochiSays::rnd() { rng_ ^= rng_ << 13; rng_ ^= rng_ >> 17; rng_ ^= rng_ << 5; return rng_; }

void MochiSays::reset(uint32_t seed) {
  rng_ = seed ? seed : 7;
  len = 0; pos = 0; roundComplete = over = won = false;
  seq[len++] = static_cast<uint8_t>(rnd() % 3);
}

bool MochiSays::input(uint8_t b) {
  if (over || roundComplete) return !over;
  if (b != seq[pos]) { over = true; return false; }
  if (++pos == len) roundComplete = true;
  return true;
}

void MochiSays::nextRound() {
  if (!roundComplete) return;
  if (len >= kMax) { over = true; won = true; return; }
  seq[len++] = static_cast<uint8_t>(rnd() % 3);
  pos = 0; roundComplete = false;
}

}  // namespace mochi

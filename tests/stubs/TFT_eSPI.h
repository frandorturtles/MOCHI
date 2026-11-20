// Framebuffer por software que imita la parte usada de TFT_eSprite (para capturas de pantalla en el PC).
#pragma once
#include <stdint.h>
#include <string.h>
#include <string>
#include <vector>
#include <stdio.h>
#define TFT_WHITE 0xFFFF
#define TFT_BLACK 0x0000
enum { TL_DATUM = 0, TC_DATUM = 1, ML_DATUM = 3, MC_DATUM = 4 };
struct TextOp { std::string s; int x, y, font, datum; uint16_t col; };
class TFT_eSPI { public: void init() {} void setRotation(int) {} void fillScreen(uint16_t) {} void writecommand(uint8_t) {} };
class TFT_eSprite {
 public:
  explicit TFT_eSprite(TFT_eSPI*) {}
  std::vector<uint16_t> buf; std::vector<TextOp> texts; int W = 0, H = 0; int datum = 0; uint16_t col = 0xFFFF;
  void setColorDepth(int) {}
  bool createSprite(int w, int h) { W = w; H = h; buf.assign(w * h, 0); return true; }
  void px(int x, int y, uint16_t c) { if (x >= 0 && y >= 0 && x < W && y < H) buf[y * W + x] = c; }
  void fillRect(int x, int y, int w, int h, uint16_t c) { for (int j = 0; j < h; j++) for (int i = 0; i < w; i++) px(x + i, y + j, c); }
  void drawFastHLine(int x, int y, int w, uint16_t c) { fillRect(x, y, w, 1, c); }
  void drawFastVLine(int x, int y, int h, uint16_t c) { fillRect(x, y, 1, h, c); }
  void fillCircle(int cx, int cy, int r, uint16_t c) { for (int y = -r; y <= r; y++) for (int x = -r; x <= r; x++) if (x * x + y * y <= r * r) px(cx + x, cy + y, c); }
  void drawCircle(int cx, int cy, int r, uint16_t c) { for (int y = -r - 1; y <= r + 1; y++) for (int x = -r - 1; x <= r + 1; x++) { int d = x * x + y * y; if (d <= r * r + r && d >= r * r - r) px(cx + x, cy + y, c); } }
  void fillEllipse(int cx, int cy, int rx, int ry, uint16_t c) { for (int y = -ry; y <= ry; y++) for (int x = -rx; x <= rx; x++) if (x * x * ry * ry + y * y * rx * rx <= rx * rx * ry * ry) px(cx + x, cy + y, c); }
  void fillRoundRect(int x, int y, int w, int h, int r, uint16_t c) { fillRect(x + r, y, w - 2 * r, h, c); fillRect(x, y + r, w, h - 2 * r, c); fillCircle(x + r, y + r, r, c); fillCircle(x + w - r - 1, y + r, r, c); fillCircle(x + r, y + h - r - 1, r, c); fillCircle(x + w - r - 1, y + h - r - 1, r, c); }
  void drawRoundRect(int x, int y, int w, int h, int, uint16_t c) { drawFastHLine(x, y, w, c); drawFastHLine(x, y + h - 1, w, c); drawFastVLine(x, y, h, c); drawFastVLine(x + w - 1, y, h, c); }
  void fillTriangle(int x0, int y0, int x1, int y1, int x2, int y2, uint16_t c) {
    auto e = [](int ax, int ay, int bx, int by, int x, int y) { return (x - ax) * (by - ay) - (y - ay) * (bx - ax); };
    for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) { int a = e(x0, y0, x1, y1, x, y), b = e(x1, y1, x2, y2, x, y), d = e(x2, y2, x0, y0, x, y); if ((a >= 0 && b >= 0 && d >= 0) || (a <= 0 && b <= 0 && d <= 0)) px(x, y, c); } }
  void setTextDatum(int d) { datum = d; }
  void setTextColor(uint16_t c) { col = c; }
  int drawString(const char* s, int x, int y, int font) { texts.push_back({s, x, y, font, datum, col}); return 0; }
  void pushSprite(int, int) {}
};

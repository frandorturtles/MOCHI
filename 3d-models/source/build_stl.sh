#!/usr/bin/env bash
# Genera los STL de MOCHI. Requiere OpenSCAD >= 2021.01 (https://openscad.org). Uso: ./build_stl.sh
set -euo pipefail
cd "$(dirname "$0")"; OUT=../STL; mkdir -p "$OUT"
for p in base lid button plate; do
  echo "Exportando $p..."; openscad -o "$OUT/mochi_$p.stl" -D "part=\"$p\"" mochi.scad
done
echo "Renders (opcional):"
for v in "iso:55,0,35" "front:90,0,0" "top:0,0,0" "back:140,0,200"; do
  n=${v%%:*}; rot=${v#*:}
  openscad -o "../renders/mochi_$n.png" --imgsize=1200,1000 --camera=0,0,10,$rot,220 --colorscheme=Tomorrow -D 'part="assembly"' mochi.scad || true
done
ls -la "$OUT"

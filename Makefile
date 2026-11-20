# Verificaciones que corren sin hardware ni herramientas CAD:  make check
.PHONY: check test fit netlist power sprites snapshots stl stl-openscad renders wiring
check: test fit netlist
test:         ; $(MAKE) -C tests test syntax
fit:          ; python3 tests/test_fit.py
netlist:      ; python3 hardware/tools/check_netlist.py
power:        ; python3 hardware/tools/power_budget.py
sprites:      ; python3 firmware/tools/gen_sprites.py
snapshots:    ; $(MAKE) -C tests snapshots
wiring:       ; python3 hardware/tools/draw_wiring.py
stl:          ; python3 3d-models/source/gen_stl.py --res 0.5 --parts base lid button
stl-openscad: ; 3d-models/source/build_stl.sh
renders:      ; python3 3d-models/source/render_png.py

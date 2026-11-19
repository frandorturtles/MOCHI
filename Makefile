# Verificaciones que corren sin hardware ni herramientas CAD:  make check
.PHONY: check test fit netlist power sprites snapshots stl
check: test fit netlist
test:        ; $(MAKE) -C tests test syntax
fit:         ; python3 tests/test_fit.py
netlist:     ; python3 hardware/tools/check_netlist.py
power:       ; python3 hardware/tools/power_budget.py
sprites:     ; python3 firmware/tools/gen_sprites.py
snapshots:   ; $(MAKE) -C tests snapshots
stl:         ; 3d-models/source/build_stl.sh

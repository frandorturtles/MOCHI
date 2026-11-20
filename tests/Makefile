CXX ?= g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O1 -fsanitize=address,undefined
SRC = ../firmware/src
test: test_core
	./test_core
test_core: test_core.cpp $(SRC)/pet.cpp $(SRC)/minigame.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^
# Comprueba que TODO el firmware (hal, ui, main) compila contra stubs de Arduino (detecta errores de sintaxis/tipos)
syntax:
	for f in hal ui main; do $(CXX) -std=c++17 -fsyntax-only -Wall -Wextra -Istubs -I$(SRC) $(SRC)/$$f.cpp || exit 1; done; echo "firmware: sintaxis OK"
snapshots: ui_snapshot snap2png.py
	mkdir -p snap_raw && SNAP_DIR=snap_raw ./ui_snapshot && python3 snap2png.py snap_raw ../docs/screens
ui_snapshot: ui_snapshot.cpp $(SRC)/ui.cpp $(SRC)/pet.cpp $(SRC)/minigame.cpp
	$(CXX) -std=c++17 -Wall -Wextra -O1 -Istubs -I$(SRC) -o $@ $^
clean:
	rm -rf test_core ui_snapshot snap_raw

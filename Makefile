
ICARUS_SRC=./src/hdl/uartprobe.v \
           ./src/test/tb.v
ICARUS_SIM=./work/uartprobe.ivsim

WAVE_FILE=./work/waves.vcd

all: $(ICARUS_SIM)
run: $(WAVE_FILE)

$(ICARUS_SIM) : $(ICARUS_SRC)
	iverilog -o $(ICARUS_SIM) -Wall -t vvp $(ICARUS_SRC)

$(WAVE_FILE) : $(ICARUS_SIM)
	vvp $(ICARUS_SIM)

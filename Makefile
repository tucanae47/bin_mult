# COCOTB variables
export COCOTB_REDUCED_LOG_FMT=1
export PYTHONPATH := test:$(PYTHONPATH)
export LIBPYTHON_LOC=$(shell cocotb-config --libpython)

all: test_bin_mult_wb

test_bin_mult_wb:
	rm -rf sim_build/ results.xml
	mkdir sim_build/
	iverilog -o sim_build/sim.vvp -s wb_top_bin_mult -s dump src/bin_mult.v src/xnor7.v src/top_bin_mult.v src/wb_top_bin_mult.v test/dump_bin_mult.v
	PYTHONOPTIMIZE=${NOASSERT} MODULE=test_bin_mult_wb vvp -M $$(cocotb-config --prefix)/cocotb/libs -m libcocotbvpi_icarus sim_build/sim.vvp
	! grep failure results.xml

show_%: %.vcd %.gtkw
	gtkwave $^

lint:
	verible-verilog-lint src/*v --rules_config verible.rules

clean:
	rm -rf *vcd sim_build test/__pycache__ results.xml

.PHONY: clean

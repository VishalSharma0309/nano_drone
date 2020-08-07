ifdef gui
override CONFIG_OPT += **/vsim/gui=true
endif

ifdef simchecker
override CONFIG_OPT += **/vsim/simchecker=true
endif

ifdef vsim/script
override CONFIG_OPT += **/vsim/script=$(vsim/script)
endif

ifdef vsim/recordwlf
override CONFIG_OPT += **/vsim/recordwlf=true
endif

ifdef vsim/dofile
override CONFIG_OPT += **/vsim/dofile="$(vsim/dofile)"
endif

ifdef vsim/model
override CONFIG_OPT += **/vsim/model=$(vsim/model)
endif

ifdef vsim/enablecov
override CONFIG_OPT += **/vsim/enablecov=true
endif

ifdef vsim/enableJtagTargetSync
override CONFIG_OPT += **/vsim/enableJtagTargetSync=true
endif



BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD=\033[1m
STD=\033[0m

help_opt_vsim:
	@echo
	@echo "Available make options for vsim platform:"
	@echo "  gui=1                   	Launch simulation from vsim GUI"
	@echo "  simchecker=1            	Activate RISCV simchecker (ISA comparison against golden model)"
	@echo "  vsim/script=<path       	Specify path to a script used to launch the platform>"
	@echo "  vsim/recordwlf=1        	Activate Questasim WLF waveform trace recording in gap.wlf file"
	@echo "  vsim/dofile=<filename>  	Specify one do file located in \$VSIM_PATH/waves to record specific traces during a simulation"
	@echo "  vsim/enablecov=1        	Enable code coverage feature in Questasim"
	@echo "  vsim/enableJtagTargetSync=1    Enable JTAG target synchronization with tb to authorize EOC checks via JTAG"
	@echo ""
	@echo "Available make target for vsim platform:"
	@echo "  clean_rtl               Clean compiled RTL platform"
	@echo "  build_rtl               Compile RTL platform"
	@echo "  build_tb                Compile testbench only of RTL platform"
	@echo "  vsim_debug              Questasim debug mode using only msimviewer licence."
	@echo "  vsim_cov_report         Generate code coverage report"
	@echo "  vsim_cov_gui            Open Questasim viewer in coverage mode"
	@echo "  vsim_cov_html           Open firefox to view code coverage report in html format"



VEGA_TOP_PATH=$(VSIM_PATH)/../..

build_rtl:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile build_rtl

build_tb:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile build_tb

clean_rtl:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile clean_rtl


#########################################################################
### Questasim debug mode using only msimviewer licence
#########################################################################
vsim_debug:
	@vsim -view $(CONFIG_BUILD_DIR)/vega.wlf -do "$(CONFIG_BUILD_DIR)/waves/$(vsim/dofile)"


#########################################################################
### Questasim Coverage report generation
#########################################################################
vsim_cov_report:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile  vsim_cov_report

vsim_cov_gui:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile  vsim_cov_gui

vsim_cov_html:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile  vsim_cov_html

vsim_cov_clean:
	@cd $(VEGA_TOP_PATH) && make -f $(VEGA_TOP_PATH)/Makefile  vsim_cov_clean


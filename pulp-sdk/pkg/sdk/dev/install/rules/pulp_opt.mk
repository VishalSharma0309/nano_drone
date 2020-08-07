override PLT_OPT += --config-file=$(PULP_CURRENT_CONFIG)
ifdef PULP_CURRENT_CONFIG_ARGS
override PLT_OPT += $(foreach var,$(PULP_CURRENT_CONFIG_ARGS), --config-opt=$(var))
endif

ifdef USER_CONFIG
USER_CONFIG_OPT = --config-user=$(USER_CONFIG)
override PLT_OPT += --config-user=$(USER_CONFIG)
endif

ifdef cluster
override CONFIG_OPT += **/rt/cluster-start=true
endif

ifdef periphs
override CONFIG_OPT += **/runner/use_tb_comps=true **/runner/active_tb_comps=$(periphs)
endif

ifdef fc
override CONFIG_OPT += **/rt/fc-start=true
endif

ifdef platform
override CONFIG_OPT += platform=$(platform)
override PLT_OPT += --config-opt=platform=$(platform)
endif

ifdef system
override PULP_CURRENT_CONFIG = $(system)@config_file=$(PULP_CONFIGS_PATH)/systems/$(system).json
endif

ifdef io
override CONFIG_OPT += **/rt/iodev=$(io)
endif

ifdef no-werror
override CONFIG_OPT += **/rt/werror=false gvsoc/werror=false
endif

ifdef libgomp
override CONFIG_OPT += **/rt/openmp-rt=libgomp
endif

ifdef boot
override CONFIG_OPT += **/runner/boot-mode=$(boot)
endif

ifdef bridge-commands
override CONFIG_OPT += **/debug_bridge/commands=$(bridge-commands)
endif

ifdef gdb
override PULP_TEMPLATE_ARGS += gdb($(gdb))
export PULP_TEMPLATE_ARGS
override CONFIG_OPT += **/gdb/active=true
endif

ifdef bridge
override CONFIG_OPT += **/debug_bridge/active=true
endif

ifdef simulator
override CONFIG_OPT += **/runner/simulator=$(simulator)
endif

ifdef bridge-autorun
override CONFIG_OPT += **/debug_bridge/autorun=true
endif

ifdef VERBOSE
override CONFIG_OPT += **/runner/verbose=true
override CONFIG_OPT += **/runner/py-stack=true
endif

help_generic:
	@echo "Generic options:"
	@echo "  platform=<name>      Specify the platform on which to launch the application."
	@echo "  io=<name>            Specify the device used for debug IOs (default, uart)."
	@echo "  no-werror=1          Deactivate errors on warnings for all modules"
	@echo "  boot=<boot>          Specify the boot mode (rom, jtag, rom_spi, rom_hyper)"
	@echo "  gdb=1                Activate GDB support"
	@echo "  bridge=<mode>        Activate debug bridge support with the specified mode (jtag)"
	@echo "  simulator=<name>     Specify simulator to be used." 

help_opt: help_generic help_opt_vsim help_opt_vp help_opt_rt

-include $(PULP_SDK_INSTALL)/rules/pulp_opt_vsim.mk
-include $(PULP_SDK_INSTALL)/rules/pulp_opt_vp.mk
-include $(PULP_SDK_INSTALL)/rules/pulp_opt_rt.mk
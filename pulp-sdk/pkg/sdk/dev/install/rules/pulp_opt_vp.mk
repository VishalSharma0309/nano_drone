ifdef vp/no-werror
override CONFIG_OPT += **/gvsoc/werror=false
endif

ifdef vp/trace
override CONFIG_OPT += **/gvsoc/trace=$(vp/trace)
endif

help_opt_vp:
	@echo
	@echo "Available make options for vp platform:"
	@echo "  vp/no-werror=1         Deactivate errors on warnings"
	
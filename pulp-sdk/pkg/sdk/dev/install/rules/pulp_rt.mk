#
# This is the top makefile which can be included by a module or application in 
# order to bring everything.
# A script is used to generate the hierarchy of makefiles for the specified
# architecture and is then included.
#

ifndef PULP_CURRENT_CONFIG
$(error PULP_CURRENT_CONFIG must contain the current configuration)
endif

ifndef PULP_SDK_HOME
ifndef INSTALL_DIR
$(error The SDK is not configured, PULP_SDK_HOME is undefined)
else
export PULP_SDK_INSTALL=$(TARGET_INSTALL_DIR)
export PULP_SDK_WS_INSTALL=$(INSTALL_DIR)
endif
endif

# This file is a dummy one and is included just to trigger module recompilation
# in case the tools are updated
include $(PULP_SDK_INSTALL)/rules/tools.mk
include $(PULP_SDK_INSTALL)/rules/pulp_defs.mk
include $(PULP_SDK_INSTALL)/rules/pulp_help.mk
include $(PULP_SDK_INSTALL)/rules/pulp_opt.mk

# Work-around to don't break old applications using PULP_OMP_APP which is now deprecated
ifdef PULP_OMP_APP
PULP_APP = $(PULP_OMP_APP)
endif

properties = $(foreach prop,$(PULP_PROPERTIES), --property=$(prop))
libs       = $(foreach lib,$(PULP_LIBS), --lib=$(lib))
apps       = $(foreach app,$(PULP_APP), --app=$(app))

override CONFIG_OPT += **/rt/type=pulp-rt

ifdef CONFIG_OPT
export PULP_CURRENT_CONFIG_ARGS += $(CONFIG_OPT)
override PLT_OPT += $(foreach opt,$(CONFIG_OPT), --config-opt=$(opt))
endif

ifdef PLT_OPT
pulpRunOpt += $(PLT_OPT)
endif

ifdef runner_args
pulpRunOpt += $(runner_args)
endif

configs_opt = $(foreach prop,$(PULP_CURRENT_CONFIG_ARGS), --config=$(prop))

genconf:
	plpflags gen --input=$(PULP_CURRENT_CONFIG) $(configs_opt)$(FLAGS_OPT) --output-dir=$(CONFIG_BUILD_DIR) --makefile=$(CONFIG_BUILD_DIR)/config.mk $(properties) $(libs) $(apps) $(USER_CONFIG_OPT)
	plpconf --input=$(PULP_CURRENT_CONFIG) $(configs_opt) --output=$(CONFIG_BUILD_DIR)/config.json $(USER_CONFIG_OPT)


$(CONFIG_BUILD_DIR)/config.json: $(PULP_SDK_INSTALL)/rules/tools.mk
	plpflags gen --input=$(PULP_CURRENT_CONFIG) $(configs_opt)$(FLAGS_OPT) --output-dir=$(CONFIG_BUILD_DIR) --makefile=$(CONFIG_BUILD_DIR)/config.mk $(properties) $(libs) $(apps) $(USER_CONFIG_OPT)
	plpconf --input=$(PULP_CURRENT_CONFIG) $(configs_opt) --output=$(CONFIG_BUILD_DIR)/config.json $(USER_CONFIG_OPT)

GEN_TARGETS += $(CONFIG_BUILD_DIR)/config.json

$(CONFIG_BUILD_DIR)/config.mk: $(MAKEFILE_LIST)
	plpflags gen --input=$(PULP_CURRENT_CONFIG) $(configs_opt)$(FLAGS_OPT) --output-dir=$(CONFIG_BUILD_DIR) --makefile=$(CONFIG_BUILD_DIR)/config.mk $(properties) $(libs) $(apps) $(USER_CONFIG_OPT)

-include $(CONFIG_BUILD_DIR)/config.mk

conf: $(MAKEFILE_LIST) genconf $(GEN_TARGETS_FORCE)

flash:
	pulp-run $(pulpRunOpt) flash

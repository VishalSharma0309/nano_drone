#
# This makefile can be included by a module or application in order to generate some properties
# extracted from the architecture
#
# For that define the properties in PULP_PROPERTIES and include $(PULP_SDK_INSTALL)/rules/pulp_properties.mk

ifndef PULP_SDK_INSTALL
ifndef TARGET_INSTALL_DIR
$(error Either PULP_SDK_INSTALL or TARGET_INSTALL_DIR must be defined)
else
export PULP_SDK_INSTALL=$(TARGET_INSTALL_DIR)
endif
endif

ifndef PULP_SDK_WS_INSTALL
ifndef INSTALL_DIR
$(error Either PULP_SDK_WS_INSTALL or INSTALL_DIR must be defined)
else
export PULP_SDK_WS_INSTALL=$(INSTALL_DIR)
endif
endif

include $(PULP_SDK_INSTALL)/rules/pulp_defs.mk

ifdef PULP_PROPERTIES

properties := $(foreach prop,$(PULP_PROPERTIES), --property=$(prop))

$(CONFIG_BUILD_DIR)/props.mk: $(MAKEFILE_LIST) $(PULP_SDK_INSTALL)/rules/tools.mk
	plpinfo mkgen --makefile=$(CONFIG_BUILD_DIR)/props.mk $(properties)

include $(CONFIG_BUILD_DIR)/props.mk

endif

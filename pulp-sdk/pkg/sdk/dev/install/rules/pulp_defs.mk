#
# This makefile can be included by a module or application in order to get application flags depending
# on specified options such as the build folder
#

export PULP_CURRENT_CONFIG ?= system=wolfe

HAS_NAME = $(findstring @,$(PULP_CURRENT_CONFIG))
ifeq '$(HAS_NAME)' ''
PULP_CURRENT_CONFIG_NAME = $(subst /,.,$(subst =,.,$(subst :,_,$(PULP_CURRENT_CONFIG))))
else
PULP_CURRENT_CONFIG_NAME = $(firstword $(subst @, ,$(PULP_CURRENT_CONFIG)))
endif

BUILD_DIR          ?= $(CURDIR)/build
CONFIG_BUILD_DIR   ?= $(subst =,.,$(BUILD_DIR)/$(PULP_CURRENT_CONFIG_NAME))$(build_dir_ext)$(BUILD_DIR_EXT)
APP_BUILD_DIR      = $(CONFIG_BUILD_DIR)

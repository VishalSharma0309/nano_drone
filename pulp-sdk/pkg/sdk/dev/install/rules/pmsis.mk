ifeq '$(PMSIS_OS)' 'freertos'

APP_SRC 	= $(SRCS)
DEMO_SRC	+=
INC_PATH	+=

include $(GAP_SDK_HOME)/tools/rules/freeRTOS_rules.mk

else

ifeq '$(PMSIS_OS)' 'mbed'

TEST_C          = $(SRCS)
MBED_FLAGS     += -DMBED_CONF_RTOS_PRESENT=1

include $(GAP_SDK_HOME)/tools/rules/mbed_rules.mk

else

ifeq '$(PMSIS_OS)' 'zephyr'

ifdef RUNNER_CONFIG
override runner_args += --config-user=$(RUNNER_CONFIG)
endif

include $(PULP_SDK_HOME)/install/rules/zephyr.mk

else

ifdef RUNNER_CONFIG
export USER_CONFIG=$(RUNNER_CONFIG)
endif

PULP_APP = $(APP)
PULP_APP_FC_SRCS = $(SRCS) $(APP_SRCS)
PULP_CFLAGS = $(CFLAGS) $(APP_CFLAGS)
ifdef USE_PMSIS_BSP
PULP_LDFLAGS += -lpibsp
endif
ifdef USE_PMSIS_TOOLS
PULP_LDFLAGS += -lpitools
endif
ifdef USE_PMSIS_KERNELS
PULP_LDFLAGS += -lpikernels
endif

include $(PULP_SDK_HOME)/install/rules/pulp_rt.mk

endif

endif

endif
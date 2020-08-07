
#
# HEADER RULES
#

define declareInstallFile

$(PULP_SDK_INSTALL)/$(1): $(1)
	install -D $(1) $$@

INSTALL_HEADERS += $(PULP_SDK_INSTALL)/$(1)

endef


define declareWsInstallFile

$(PULP_SDK_WS_INSTALL)/$(1): $(1)
	install -D $(1) $$@

WS_INSTALL_HEADERS += $(PULP_SDK_WS_INSTALL)/$(1)

endef


$(foreach file, $(INSTALL_FILES), $(eval $(call declareInstallFile,$(file))))

$(foreach file, $(WS_INSTALL_FILES), $(eval $(call declareWsInstallFile,$(file))))


#
# CC RULES for domain: cluster
#

PULP_LIB_NAME_flasher-pulp ?= flasher-pulp


PULP_CL_EXTRA_SRCS_flasher-pulp = 
PULP_CL_EXTRA_ASM_SRCS_flasher-pulp = 
PULP_CL_EXTRA_OMP_SRCS_flasher-pulp = 

flasher-pulp_CL_OBJS =     $(patsubst %.cpp,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/%.o, $(patsubst %.c,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/%.o, $(PULP_APP_CL_SRCS_flasher-pulp) $(PULP_CL_SRCS_flasher-pulp) $(PULP_APP_CL_SRCS) $(PULP_APP_SRCS) $(PULP_CL_EXTRA_SRCS_flasher-pulp)))
flasher-pulp_CL_ASM_OBJS = $(patsubst %.S,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/%.o, $(PULP_APP_CL_ASM_SRCS_flasher-pulp) $(PULP_CL_ASM_SRCS_flasher-pulp) $(PULP_APP_CL_ASM_SRCS) $(PULP_APP_ASM_SRCS) $(PULP_CL_EXTRA_ASM_SRCS_flasher-pulp))
flasher-pulp_CL_OMP_OBJS = $(patsubst %.c,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/omp/%.o, $(PULP_APP_CL_OMP_SRCS_flasher-pulp) $(PULP_CL_OMP_SRCS_flasher-pulp) $(PULP_APP_CL_OMP_SRCS) $(PULP_APP_OMP_SRCS) $(PULP_CL_EXTRA_OMP_SRCS_flasher-pulp))

ifneq '$(flasher-pulp_CL_OMP_OBJS)' ''
PULP_LDFLAGS_flasher-pulp += $(PULP_OMP_LDFLAGS_flasher-pulp)
endif

-include $(flasher-pulp_CL_OBJS:.o=.d)
-include $(flasher-pulp_CL_ASM_OBJS:.o=.d)
-include $(flasher-pulp_CL_OMP_OBJS:.o=.d)

flasher-pulp_cl_cflags = $(PULP_CL_ARCH_CFLAGS) $(PULP_CFLAGS) $(PULP_CL_CFLAGS) $(PULP_CFLAGS_flasher-pulp) $(PULP_CL_CFLAGS_flasher-pulp) $(PULP_APP_CFLAGS_flasher-pulp)
flasher-pulp_cl_omp_cflags = $(flasher-pulp_cl_cflags) $(PULP_OMP_CFLAGS) $(PULP_CL_OMP_CFLAGS) $(PULP_OMP_CFLAGS_flasher-pulp) $(PULP_CL_OMP_CFLAGS_flasher-pulp)

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/%.o: %.c
	@mkdir -p `dirname $@`
	$(PULP_CL_CC) $(flasher-pulp_cl_cflags) -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/%.o: %.cpp
	@mkdir -p `dirname $@`
	$(PULP_CL_CC) $(flasher-pulp_cl_cflags) -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/%.o: %.S
	@mkdir -p `dirname $@`
	$(PULP_CL_CC) $(flasher-pulp_cl_cflags) -DLANGUAGE_ASSEMBLY -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/cl/omp/%.o: %.c
	@mkdir -p `dirname $@`
	touch libgomp.spec
	$(PULP_CL_CC) $(flasher-pulp_cl_omp_cflags) -MMD -MP -c $< -o $@

flasher-pulp_OBJS += $(flasher-pulp_CL_OBJS) $(flasher-pulp_CL_ASM_OBJS) $(flasher-pulp_CL_OMP_OBJS)



#
# CC RULES for domain: fabric_controller
#

PULP_LIB_NAME_flasher-pulp ?= flasher-pulp


PULP_FC_EXTRA_SRCS_flasher-pulp = /home/vishal/nano_drone/pulp-sdk/build/sdk/flasher/pulp/rt_conf.c /home/vishal/nano_drone/pulp-sdk/build/sdk/flasher/pulp/rt_pad_conf.c
PULP_FC_EXTRA_ASM_SRCS_flasher-pulp = 
PULP_FC_EXTRA_OMP_SRCS_flasher-pulp = 

flasher-pulp_FC_OBJS =     $(patsubst %.cpp,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/%.o, $(patsubst %.c,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/%.o, $(PULP_APP_FC_SRCS_flasher-pulp) $(PULP_FC_SRCS_flasher-pulp) $(PULP_APP_FC_SRCS)  $(PULP_FC_EXTRA_SRCS_flasher-pulp)))
flasher-pulp_FC_ASM_OBJS = $(patsubst %.S,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/%.o, $(PULP_APP_FC_ASM_SRCS_flasher-pulp) $(PULP_FC_ASM_SRCS_flasher-pulp) $(PULP_APP_FC_ASM_SRCS)  $(PULP_FC_EXTRA_ASM_SRCS_flasher-pulp))
flasher-pulp_FC_OMP_OBJS = $(patsubst %.c,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/omp/%.o, $(PULP_APP_FC_OMP_SRCS_flasher-pulp) $(PULP_FC_OMP_SRCS_flasher-pulp) $(PULP_APP_FC_OMP_SRCS)  $(PULP_FC_EXTRA_OMP_SRCS_flasher-pulp))

ifneq '$(flasher-pulp_FC_OMP_OBJS)' ''
PULP_LDFLAGS_flasher-pulp += $(PULP_OMP_LDFLAGS_flasher-pulp)
endif

-include $(flasher-pulp_FC_OBJS:.o=.d)
-include $(flasher-pulp_FC_ASM_OBJS:.o=.d)
-include $(flasher-pulp_FC_OMP_OBJS:.o=.d)

flasher-pulp_fc_cflags = $(PULP_FC_ARCH_CFLAGS) $(PULP_CFLAGS) $(PULP_FC_CFLAGS) $(PULP_CFLAGS_flasher-pulp) $(PULP_FC_CFLAGS_flasher-pulp) $(PULP_APP_CFLAGS_flasher-pulp)
flasher-pulp_fc_omp_cflags = $(flasher-pulp_fc_cflags) $(PULP_OMP_CFLAGS) $(PULP_FC_OMP_CFLAGS) $(PULP_OMP_CFLAGS_flasher-pulp) $(PULP_FC_OMP_CFLAGS_flasher-pulp)

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/%.o: %.c
	@mkdir -p `dirname $@`
	$(PULP_FC_CC) $(flasher-pulp_fc_cflags) -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/%.o: %.cpp
	@mkdir -p `dirname $@`
	$(PULP_FC_CC) $(flasher-pulp_fc_cflags) -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/%.o: %.S
	@mkdir -p `dirname $@`
	$(PULP_FC_CC) $(flasher-pulp_fc_cflags) -DLANGUAGE_ASSEMBLY -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_flasher-pulp)/fc/omp/%.o: %.c
	@mkdir -p `dirname $@`
	touch libgomp.spec
	$(PULP_FC_CC) $(flasher-pulp_fc_omp_cflags) -MMD -MP -c $< -o $@

flasher-pulp_OBJS += $(flasher-pulp_FC_OBJS) $(flasher-pulp_FC_ASM_OBJS) $(flasher-pulp_FC_OMP_OBJS)



#
# LINKER RULES for application: flasher-pulp
#

$(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP): $(flasher-pulp_OBJS)
	mkdir -p `dirname $@`
	$(PULP_LD) $(PULP_ARCH_LDFLAGS) -MMD -MP -o $@ $^ $(PULP_LDFLAGS) $(PULP_LDFLAGS_flasher-pulp)

$(PULP_SDK_INSTALL)/bin/$(PULP_APP): $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP)
	mkdir -p `dirname $@`
	cp $< $@

disopt ?= -d

dis:
	$(PULP_OBJDUMP) $(PULP_ARCH_OBJDFLAGS) $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) $(disopt)

extract:
	for symbol in $(symbols); do $(PULP_PREFIX)readelf -s $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) | grep $$symbol | gawk '{print $$2}' > $(CONFIG_BUILD_DIR)/$(PULP_APP)/$$symbol.txt; done

disdump:
	$(PULP_OBJDUMP) $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) $(disopt) > $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP).s
	@echo
	@echo  "Disasembled binary to $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP).s"

TARGETS += $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP)
CLEAN_TARGETS += $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) $(flasher-pulp_OBJS)
RUN_BINARY = $(PULP_APP)/$(PULP_APP)
INSTALL_TARGETS += $(PULP_SDK_INSTALL)/bin/$(PULP_APP)


header:: $(INSTALL_HEADERS) $(WS_INSTALL_HEADERS)

fullclean::
	rm -rf $(CONFIG_BUILD_DIR)

clean:: $(GEN_TARGETS) $(CONFIG_BUILD_DIR)/config.mk
	rm -rf $(CLEAN_TARGETS)

prepare:: $(GEN_TARGETS) $(CONFIG_BUILD_DIR)/config.mk
	pulp-run $(pulpRunOpt) prepare

runner:: $(GEN_TARGETS) $(CONFIG_BUILD_DIR)/config.mk
	pulp-run $(pulpRunOpt) $(RUNNER_CMD)

power:: $(GEN_TARGETS) $(CONFIG_BUILD_DIR)/config.mk
	pulp-run $(pulpRunOpt) power

gen: $(GEN_TARGETS_FORCE)

build:: $(GEN_TARGETS) $(CONFIG_BUILD_DIR)/config.mk $(TARGETS)

all:: conf build prepare

install:: $(INSTALL_TARGETS)

run::
	pulp-run $(pulpRunOpt)

.PHONY: clean header prepare all install run


#
# Copyright (C) 2018 ETH Zurich and University of Bologna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from padframe.padframe import Padframe
import shutil

mk_top_pattern = """
# This makefile has been generated for a specific configuration and is bringing
# all flags and rules needed for compiling for this configuration.
# In case the rules are not suitable but flags are still needed, INCLUDE_NO_RULES
# can be defined in the application makefile.
# The 2 included makefiles can also be copied to application, customized and 
# included instead of the one from the SDK.

ifndef PULP_SDK_INSTALL
export PULP_SDK_INSTALL=$(TARGET_INSTALL_DIR)
export PULP_SDK_WS_INSTALL=$(INSTALL_DIR)
endif

-include {flags_path}

ifndef INCLUDE_NO_RULES
-include {rules_path}
endif
"""

mk_header_pattern = """
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
"""

mk_lib_c_pattern = """
CLEAN_DIRS += $(CONFIG_BUILD_DIR)
"""

mk_c_pattern = """

#
# CC RULES for domain: {domain_name}
#

PULP_LIB_NAME_{lib_name} ?= {lib_name}


PULP_{domain_up}_EXTRA_SRCS_{lib_name} = {extra_src}
PULP_{domain_up}_EXTRA_ASM_SRCS_{lib_name} = {extra_asm_src}
PULP_{domain_up}_EXTRA_OMP_SRCS_{lib_name} = {extra_omp_src}

{lib_name}_{domain_up}_OBJS =     $(patsubst %.cpp,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/%.o, $(patsubst %.c,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/%.o, $(PULP_{type}_{domain_up}_SRCS_{lib_name}) $(PULP_{domain_up}_SRCS_{lib_name}) $(PULP_{type}_{domain_up}_SRCS) {no_domain_src} $(PULP_{domain_up}_EXTRA_SRCS_{lib_name})))
{lib_name}_{domain_up}_ASM_OBJS = $(patsubst %.S,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/%.o, $(PULP_{type}_{domain_up}_ASM_SRCS_{lib_name}) $(PULP_{domain_up}_ASM_SRCS_{lib_name}) $(PULP_{type}_{domain_up}_ASM_SRCS) {no_domain_asm_src} $(PULP_{domain_up}_EXTRA_ASM_SRCS_{lib_name}))
{lib_name}_{domain_up}_OMP_OBJS = $(patsubst %.c,$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/omp/%.o, $(PULP_{type}_{domain_up}_OMP_SRCS_{lib_name}) $(PULP_{domain_up}_OMP_SRCS_{lib_name}) $(PULP_{type}_{domain_up}_OMP_SRCS) {no_domain_omp_src} $(PULP_{domain_up}_EXTRA_OMP_SRCS_{lib_name}))

ifneq '$({lib_name}_{domain_up}_OMP_OBJS)' ''
PULP_LDFLAGS_{lib_name} += $(PULP_OMP_LDFLAGS_{lib_name})
endif

-include $({lib_name}_{domain_up}_OBJS:.o=.d)
-include $({lib_name}_{domain_up}_ASM_OBJS:.o=.d)
-include $({lib_name}_{domain_up}_OMP_OBJS:.o=.d)

{lib_name}_{domain}_cflags = $(PULP_{domain_up}_ARCH_CFLAGS) $(PULP_CFLAGS) $(PULP_{domain_up}_CFLAGS) $(PULP_CFLAGS_{lib_name}) $(PULP_{domain_up}_CFLAGS_{lib_name}) $(PULP_{type}_CFLAGS_{lib_name})
{lib_name}_{domain}_omp_cflags = $({lib_name}_{domain}_cflags) $(PULP_OMP_CFLAGS) $(PULP_{domain_up}_OMP_CFLAGS) $(PULP_OMP_CFLAGS_{lib_name}) $(PULP_{domain_up}_OMP_CFLAGS_{lib_name})

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/%.o: %.c
	@mkdir -p `dirname $@`
	$(PULP_{domain_up}_CC) $({lib_name}_{domain}_cflags) -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/%.o: %.cpp
	@mkdir -p `dirname $@`
	$(PULP_{domain_up}_CC) $({lib_name}_{domain}_cflags) -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/%.o: %.S
	@mkdir -p `dirname $@`
	$(PULP_{domain_up}_CC) $({lib_name}_{domain}_cflags) -DLANGUAGE_ASSEMBLY -MMD -MP -c $< -o $@

$(CONFIG_BUILD_DIR)/$(PULP_LIB_NAME_{lib_name})/{domain}/omp/%.o: %.c
	@mkdir -p `dirname $@`
	touch libgomp.spec
	$(PULP_{domain_up}_CC) $({lib_name}_{domain}_omp_cflags) -MMD -MP -c $< -o $@

{lib_name}_OBJS += $({lib_name}_{domain_up}_OBJS) $({lib_name}_{domain_up}_ASM_OBJS) $({lib_name}_{domain_up}_OMP_OBJS)

"""

mk_lib_pattern = """

#
# AR RULES for library: {domain_name}
#

PULP_LIB_NAME_{lib_name} ?= {lib_name}
PULP_LIB_TARGET_NAME_{lib_name} ?= lib$(PULP_LIB_NAME_{lib_name}).a

$(CONFIG_BUILD_DIR)/lib$(PULP_LIB_NAME_{lib_name}).a: $({lib_name}_OBJS)  $(PULP_SDK_INSTALL)/rules/tools.mk
	@mkdir -p `dirname $@`
	@rm -f $@
	$(PULP_AR) -r $@ $^

$(PULP_SDK_INSTALL)/lib/{install_name}/$(PULP_LIB_TARGET_NAME_{lib_name}): $(CONFIG_BUILD_DIR)/lib$(PULP_LIB_NAME_{lib_name}).a
	@mkdir -p `dirname $@`
	cp $^ $@ 


TARGETS += $(CONFIG_BUILD_DIR)/lib$(PULP_LIB_NAME_{lib_name}).a
CLEAN_TARGETS += $(CONFIG_BUILD_DIR)/lib$(PULP_LIB_NAME_{lib_name}).a $($(PULP_LIB_NAME_{lib_name})_OBJS)
INSTALL_TARGETS += $(PULP_SDK_INSTALL)/lib/{install_name}/$(PULP_LIB_TARGET_NAME_{lib_name})

"""

mk_app_pattern = """

#
# LINKER RULES for application: {domain_name}
#

$(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP): $({lib_name}_OBJS)
	mkdir -p `dirname $@`
	$(PULP_LD) $(PULP_ARCH_LDFLAGS) -MMD -MP -o $@ $^ $(PULP_LDFLAGS) $(PULP_LDFLAGS_{lib_name})

$(PULP_SDK_INSTALL)/bin/$(PULP_APP): $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP)
	mkdir -p `dirname $@`
	cp $< $@

disopt ?= -d

dis:
	$(PULP_OBJDUMP) $(PULP_ARCH_OBJDFLAGS) $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) $(disopt)

extract:
	for symbol in $(symbols); do $(PULP_PREFIX)readelf -s $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) | grep $$symbol | gawk '{{print $$2}}' > $(CONFIG_BUILD_DIR)/$(PULP_APP)/$$symbol.txt; done

disdump:
	$(PULP_OBJDUMP) $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) $(disopt) > $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP).s
	@echo
	@echo  "Disasembled binary to $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP).s"

TARGETS += $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP)
CLEAN_TARGETS += $(CONFIG_BUILD_DIR)/$(PULP_APP)/$(PULP_APP) $({lib_name}_OBJS)
RUN_BINARY = $(PULP_APP)/$(PULP_APP)
INSTALL_TARGETS += $(PULP_SDK_INSTALL)/bin/$(PULP_APP)

"""


mk_rules_pattern = """
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
"""

def get_core_version(config, name):
  if name == 'fc': return config.get('fc/version')
  else: return config.get('pe/version')

def get_core_archi(config, name):
  if name == 'fc': return config.get('fc/archi')
  else: return config.get('pe/archi')

def get_core_isa(config, name):
  if name == 'fc': return config.get('fc/isa')
  else: return config.get('pe/isa')

def get_core_name(config, name):
  name = get_core_version(config, name)
  name += '-rvc' if get_core_isa(config, name).find('C') != -1 else ''
  return name


class Config(object):

  def __init__(self, name, defines, config):
    self.defines = defines
    self.name = name
    self.config = config

  def gen(self, file):

    file.write('#ifndef __PULP_%s_CONFIG_H__\n' % self.name.upper())
    file.write('#define __PULP_%s_CONFIG_H__\n' % self.name.upper())
    file.write('\n')
    file.write('#include "archi/pulp_defs.h"\n')
    file.write('\n')

    for define in self.defines:
      if define[1] != None: file.write('#define %s %s\n' % (define[0], define[1]))
      else: file.write('#define %s\n'% define[0])


    for section_desc in self.config.get('user-sections'):
        section_name, mem_name = section_desc.split('@')

        file.write("extern unsigned char __%s_start;\n" % section_name)
        file.write("extern unsigned char __%s_size;\n" % section_name)
        file.write("static inline void *rt_user_section_%s_start() { return (void *)&__%s_start; }\n" % (section_name, section_name))
        file.write("static inline int rt_user_section_%s_size() { return (int)&__%s_size; }\n" % (section_name, section_name))



    file.write('\n')
    file.write('#endif\n')



class Gvsoc(object):

  def __init__(self, name, config, flags, apps, build_dir):
    self.config = config
    self.flags = flags
    self.apps = apps
    self.build_dir = build_dir
    self.name = name

  def set_flags(self, flags):
    #coreExt = []
#
#    #if self.config.get('pulp_chip') == 'GAP':
#    #  coreExt.append('gap8')
#
#    #for ext in coreExt:
    #  flags.add_runner_flag('--core-ext="%s"' % ext)

    if len(self.apps) != 0:

      binaries = []
      for binary in self.apps:
        binaries.append('%s/%s' % (binary.name, binary.name))

      chip = 'pulp_chip/%s' % (self.config.get('pulp_chip'))

      self.flags.add_runner_flag('--binary={name}/{name}'.format(name=self.apps[0].name))
          
      self.config.set('plt_loader/binaries', '%s/%s' % (self.apps[0].name, self.apps[0].name))
        #self.config.set('plt_loader/binaries', '%s' % (os.path.join(os.environ.get('PULP_SDK_INSTALL'), 'bin', 'boot-%s' % self.config.get('pulp_chip'))))

      if self.flags.flags.config_path != None:
        with open(self.flags.flags.config_path, 'w') as file:
          self.config.dump_to_file(file)



class Rtl(object):

    def __init__(self, config, flags, apps, build_dir):
        self.config = config
        self.flags = flags
        self.apps = apps
        self.build_dir = build_dir

    def set_flags(self, flags):

       if len(self.apps) != 0:

          config_path = os.path.join(self.build_dir, 'config.json')

          #with open(config_path, 'w') as file:
          #  self.config.dump_to_file(file)

          self.flags.add_runner_flag('--binary={name}/{name}'.format(name=self.apps[0].name))
          
          #if self.config.get('use_sdk_rom'):
          #  self.flags.add_runner_flag('--boot-binary=%s' % (os.path.join(os.environ.get('PULP_SDK_INSTALL'), 'bin', 'boot-%s' % self.config.get('pulp_chip'))))


class Hsa(object):

    def __init__(self, config, flags, apps, build_dir):
        self.config = config
        self.flags = flags
        self.apps = apps
        self.build_dir = build_dir

    def set_flags(self, flags):

       if len(self.apps) != 0:

          config_path = os.path.join(self.build_dir, 'config.json')

          with open(config_path, 'w') as file:
            self.config.dump_to_file(file)

          self.flags.add_runner_flag('--binary={name}/{name}'.format(name=self.apps[0].name))
          
class Fpga(object):

    def __init__(self, config, flags, apps, build_dir):
        self.config = config
        self.flags = flags
        self.apps = apps
        self.build_dir = build_dir

    def set_flags(self, flags):

       if len(self.apps) != 0:

          config_path = os.path.join(self.build_dir, 'config.json')

          with open(config_path, 'w') as file:
            self.config.dump_to_file(file)

          self.flags.add_runner_flag('--binary={name}/{name}'.format(name=self.apps[0].name))
          #self.flags.add_runner_flag('--boot-binary=%s' % (os.path.join(os.environ.get('PULP_SDK_INSTALL'), 'bin', 'boot-%s' % self.config.get('pulp_chip'))))

class Board(object):

    def __init__(self, config, flags, apps, build_dir):
        self.config = config
        self.flags = flags
        self.apps = apps
        self.build_dir = build_dir

    def set_flags(self, flags):

       if len(self.apps) != 0:

          config_path = os.path.join(self.build_dir, 'config.json')

          with open(config_path, 'w') as file:
            self.config.dump_to_file(file)

          self.flags.add_runner_flag('--binary={name}/{name}'.format(name=self.apps[0].name))
          #self.flags.add_runner_flag('--boot-binary=%s' % (os.path.join(os.environ.get('PULP_SDK_INSTALL'), 'bin', 'boot-%s' % self.config.get('pulp_chip'))))


class Platform(object):

  def __init__(self, config, flags, apps, build_dir):
    self.plt = None
    self.config = config
    self.build_dir = build_dir

    plt_name = config.get('platform')

    if plt_name == 'gvsoc':
      self.plt = Gvsoc(plt_name, config, flags, apps, build_dir)
    elif plt_name == 'rtl':
      self.plt = Rtl(config, flags, apps, build_dir)
    elif plt_name == 'hsa':
      self.plt = Hsa(config, flags, apps, build_dir)
    elif plt_name == 'fpga':
      self.plt = Fpga(config, flags, apps, build_dir)
    elif plt_name == 'board':
      self.plt = Board(config, flags, apps, build_dir)

    self.plt_name = plt_name

    fs_config = config.get_config('fs')
    if fs_config is not None and len(apps) != 0:
      fs_config.set('boot_binary', '{name}/{name}'.format(name=apps[0].name))

  def set_flags(self, flags):
    flags.add_runner_flag('--dir=%s' % self.build_dir)

    if self.plt != None:
      self.plt.set_flags(flags)



class Pulp_rt2(object):

    def __init__(self, config, build_dir):
        self.config = config
        self.build_dir = build_dir
        self.gen_rt_conf(build_dir)

    def gen_rt_conf(self, build_dir):

        system_config = self.config.get_config('system_tree')
        board_config = system_config.get_config('board')

        # Generate padframe configuration for runtime
        padframe_conf = self.config.get_config('padframe')

        if padframe_conf is not None and padframe_conf.get_config('pads') is not None:

            padframe = Padframe(padframe_conf, self.config.get_config('pads/config'))

            profile_conf = self.config.get_config("pads/default_profile")

            if profile_conf is None:
              profile_conf = 'default'

            padframe.gen_rt_conf(os.path.join(build_dir, 'rt_pad_conf.c'), profile_conf)

        with open(os.path.join(build_dir, 'rt_conf.c'), 'w') as file:
            file.write('#include "rt/rt_api.h"\n')
            file.write('\n')

            iodev = self.config.get('rt/iodev')
            if iodev == "uart":
              file.write('unsigned int __rt_iodev = 1;\n')

    


            platform = 0
            if self.config.get('platform') == 'fpga':
              platform = 1
            elif self.config.get('platform') == 'rtl':
              platform = 2
            elif self.config.get('platform') == 'gvsoc':
              platform = 3
            elif self.config.get('platform') == 'board':
              platform = 4
            file.write('unsigned int __rt_platform = %d;\n' % platform)
            file.write('\n')

            file.write('rt_dev_t __rt_devices[] = {\n')

            #board = self.config.get_config('board')
            #devices = board.get_config('devices')
            #if devices is not None:
            #    for device in devices():
            #        file.write('  {"%s", %d},' % (device, 0))

            nb_devices = 0

            bindings = board_config.get('tb_bindings')
            if bindings is not None:
                for binding in bindings:
                    master_comp, master_port = binding[0].split('->')
                    slave_comp, slave_port = binding[1].split('->')
                    if master_comp == 'chip':
                        periph = slave_comp
                        port = master_port
                    elif slave_comp == 'chip':
                        periph = master_comp
                        port = slave_port
                    else:
                        continue

                    dev_conf = board_config.get_config(periph)
                    desc = '(void *)NULL'
                    itf = 0
                    
                    if port.find('hyper') != -1 or port.find('spim') != -1:
                      if periph.find('hyperflash') != -1:
                        desc = '(void *)&hyperflash_desc'
                      elif periph.find('spiflash') != -1:
                        desc = '(void *)&spiflash_desc'
                      else:
                        desc = '(void *)NULL'

                    elif port.find('cpi') != -1:
                      itf = port.replace('cpi', '')
                      if dev_conf != None:
                        model = dev_conf.get_config('model')
                        if model != None:
                          desc = '(void *)&%s_desc' % model

                    elif port.find('i2s') != -1:
                      if dev_conf != None:
                        model = dev_conf.get_config('model')
                        if model != None:
                          desc = '(void *)&%s_desc' % model

                    file.write('  {"%s", -1, %s, %s, {{%s}}},\n' % (periph, itf, desc, ''))
                    nb_devices += 1



            bindings = None
            if board_config is not None:
                bindings = board_config.get_config('bindings')
                system_bindings = system_config.get_config('bindings')
            if bindings is not None:
                for binding_group in bindings():
                    if type(binding_group[0]) != list:
                        binding_group = [binding_group]

                    channel = 0
                    channel_offset = 0
                    subchannel = None

                    for binding in binding_group:

                      master = binding[0]

                      if channel_offset == 0:
                          slave = binding[1]

                          if 'self.' in slave:
                            slave = slave.split('.')[1]
                            for binding in system_bindings():
                              if binding[0] == 'board.' + slave:
                                slave = binding[1].split('.')[0]
                          else:
                            slave = slave.split('.')[0]


                      comp, port = master.split('.')
                      comp_config = self.config.get_config('board/chip')
                      if comp_config.get_config('pads') is not None:
                        channel |= comp_config.get_config('pads').get_config(port).get('udma_channel') << channel_offset
                        subchannel = comp_config.get_config('pads').get_config(port).get('udma_subchannel')

                      if subchannel is not None:
                        channel |= subchannel << (channel_offset + 4)

                      if channel_offset == 0:
                        custom_options = ''
                        desc = '(void *)NULL'
                        dev_conf = system_config.get_config(slave)
                        if port.find('hyper') != -1 or port.find('spim') != -1:
                          if slave.find('hyperflash') != -1:
                            desc = '(void *)&hyperflash_desc'
                          elif slave.find('spiflash') != -1:
                            desc = '(void *)&spiflash_desc'
                          else:
                            desc = '(void *)NULL'

                          custom_options = '%d' % (self.config.get_config('board/%s' % slave).get_int('size'))
                        elif port.find('cpi') != -1:
                          if dev_conf != None:
                            model = dev_conf.get_config('model')
                            if model != None:
                              desc = '(void *)&%s_desc' % model

                        elif port.find('i2s') != -1:
                          if dev_conf != None:
                            model = dev_conf.get_config('model')
                            if model != None:
                              desc = '(void *)&%s_desc' % model

                      channel_offset += 8

                    file.write('  {"%s", 0x%x, -1, %s, {{%s}}},\n' % (slave, channel, desc, custom_options))
                    nb_devices += 1

            file.write('};\n')

            file.write('\n')
            
            file.write('int __rt_nb_devices = %d;\n' % nb_devices)


    def set_c_flags(self, flags):
        if self.config.get('fc') is not None:
            flags.add_define(['ARCHI_HAS_FC', '1'])
            flags.add_define(['PLP_HAS_FC', '1'])
        if not self.config.get_bool('rt/libc'):
            flags.add_inc_folder(
                '%s/include/io' % os.environ.get('PULP_SDK_INSTALL'))
        else:
            flags.add_define(['__RT_USE_LIBC', '1'])

        if self.config.get('soc/cluster') is not None and self.config.get('rt/start-all'):
            if not self.config.get('rt/fc-start') or self.config.get('rt/cluster-start'):
                flags.add_define(['__RT_CLUSTER_START', '1'])

        if self.config.get('pulp_chip') != 'gap':
            flags.add_define(['PLP_NO_BUILTIN', '1'])

        flags.add_c_flags(self.config.get('rt/cflags'))


        if self.config.get('l2_priv0') is not None:
            flags.add_define(['__RT_ALLOC_L2_MULTI', '1'])

        flags.add_extra_src(os.path.join(self.build_dir, 'rt_conf.c'), 'c', 'fc')

        if self.config.get_config('padframe') is not None and self.config.get_config('padframe').get_config('pads') is not None:
            flags.add_extra_src(os.path.join(self.build_dir, 'rt_pad_conf.c'), 'c', 'fc')


        if self.config.get('cluster/nb_pe') is not None:
            flags.add_define(['ARCHI_NB_PE', self.config.get('cluster/nb_pe')])

    def set_ld_flags(self, flags):

        if self.config.get_config('rt/bsp'):
          flags.add_arch_lib('pibsp')

        flags.add_arch_lib(self.config.get_config('rt/mode'))
        if self.config.get_config('rt/mode') != 'rtbare':
          if self.config.get_bool('rt/libc'):
              flags.add_arch_lib('c')
          else:
              flags.add_arch_lib('rtio')

        flags.add_arch_lib(self.config.get_config('rt/mode'))

        if self.config.get('pulp_chip').find('vivosoc') != -1:
          flags.add_arch_lib('rt-analog')

        if self.config.get('pulp_chip_family').find('bigpulp') != -1 and self.config.get('pulp_chip') not in ['bigpulp-standalone']:
          flags.add_arch_lib('archi_host')
          flags.add_arch_lib('vmm')

        flags.add_lib('gcc')
        flags.add_option('-nostartfiles')
        flags.add_option('-nostdlib')
        flags.add_option('-Wl,--gc-sections')

class Runtime(object):

  def __init__(self, config, build_dir):
    self.rt = None
    self.config = config

    if not config.get_bool('rt/no-rt'):
      if config.get('rt/type') == 'pulp-rt':
        self.rt = Pulp_rt2(config, build_dir)


  def set_c_flags(self, flags):
    if self.rt != None:
      self.rt.set_c_flags(flags)

    if self.config.get_bool('rt/openmp') and self.config.get('rt/openmp-rt') == 'libgomp':
      flags.add_omp_c_flag('-fopenmp -I%s/include/libgomp' % os.environ.get('PULP_SDK_INSTALL'))
      if self.config.get('pulp_chip_family') == 'bigpulp':
        flags.add_omp_c_flag('-I%s/include/libgomp/bigpulp' % os.environ.get('PULP_SDK_INSTALL'))
      else:
        flags.add_omp_c_flag('-I%s/include/libgomp/pulp' % os.environ.get('PULP_SDK_INSTALL'))
    else:
      flags.add_omp_c_flag('-fopenmp -mnativeomp')


    flags.add_inc_folder('%s/include' % os.environ.get('PULP_SDK_INSTALL'))
    flags.add_define(['__%s__' % self.config.get('pulp_rt_version').upper(), '1'])
    flags.add_define(['%s' % self.config.get('pulp_rt_version').upper(), '1'])
    flags.add_define(['PULP_RT_VERSION_RELEASE', '0'])
    flags.add_define(['PULP_RT_VERSION_BENCH', '1'])
    flags.add_define(['PULP_RT_VERSION_PROFILE0', '2'])
    flags.add_define(['PULP_RT_VERSION_PROFILE1', '3'])
    flags.add_define(['PULP_RT_VERSION_DEBUG', '4'])
    flags.add_define(['PULP_RT_VERSION', 'PULP_RT_VERSION_%s' % self.config.get('pulp_rt_version').upper()])

    flags.add_define(['__PULP_OS__', None])
    flags.add_define(['__PULPOS__', None])
    flags.add_define(['PULP', None])
    flags.add_define(['__PULP__', None])

    flags.add_c_flag('-fdata-sections -ffunction-sections')

  def set_ld_flags(self, flags):
    if self.rt != None:
      self.rt.set_ld_flags(flags)

    install_name = self.config.get('install_name')
    if install_name is None:
      install_name = self.config.get('pulp_chip')

    flags.add_inc_folder('%s/lib/%s' % (os.environ.get('PULP_SDK_INSTALL'), install_name))

    board_name = self.config.get('board/name')
    if board_name is not None:
      flags.add_inc_folder('%s/lib/%s/%s' % (os.environ.get('PULP_SDK_INSTALL'), install_name, board_name))


    if self.config.get_bool('rt/openmp') and self.config.get('rt/openmp-rt') == 'libgomp':
      flags.add_omp_ldflag('-lgomp')
    else:
      flags.add_omp_ldflag('-lomp')


def get_toolchain_info(core_config, core_family, core_version, has_fpu, compiler=None):
    version = None
    ld_toolchain = None
    
    if compiler is None:
        compiler = 'gcc'

    if core_family == 'or1k':
      if core_version == 'or10nv2':
         toolchain = '$(OR10NV2_GCC_TOOLCHAIN)'
      else: 
         toolchain = '$(OR1K_GCC_TOOLCHAIN)'
    else:
      if core_version in ['zeroriscy', 'microriscy']:
        toolchain = '$(PULP_RISCV_%s_TOOLCHAIN_CI)' % compiler.upper()
        ld_toolchain = '$(PULP_RISCV_GCC_TOOLCHAIN_CI)'
        version = "3"
      elif core_version.find('ri5cyv2') != -1:
        version = "3"
        toolchain = '$(PULP_RISCV_%s_TOOLCHAIN_CI)' % compiler.upper()
        ld_toolchain = '$(PULP_RISCV_GCC_TOOLCHAIN_CI)'
      elif core_config.get('isa').find('rv64') != -1:
          toolchain = '$(RISCV64_GCC_TOOLCHAIN)'
      else:
        toolchain = '$(RISCV_GCC_TOOLCHAIN)'

    if ld_toolchain is None:
      ld_toolchain = toolchain

    return toolchain, ld_toolchain, version

def get_toolchain(core_config, core_family, core_version, has_fpu, compiler):
    toolchain, ld_toolchain, version = get_toolchain_info(core_config, core_family, core_version, has_fpu, compiler)
    return toolchain, ld_toolchain

def get_toolchain_version(core_config):
    toolchain, ld_toolchain, version = get_toolchain_info(core_config, core_config.get('archi'), core_config.get('version'), core_config.get('isa').find('F') != -1)
    return version



class Arch(object):

  def __init__(self, name, chip, chip_family, chipVersion, core, core_isa, core_config, config):
    self.name = name
    self.chip = chip
    self.chip_family = chip_family
    self.board = config.get('board/name')
    self.core = core
    self.chipVersion = chipVersion
    self.core_config = core_config
    self.has_fpu = core_isa != None and core_isa.find('F') != -1
    self.config = config

    arch_flags = None
    objd_flags = None
    c_flags = ''
    ext_name = ''
    isa = 'I'

    self.compiler = config.get('compiler')
    if self.compiler is None:
        self.compiler = 'gcc'

    isa = core_config.get('march')

    if self.chip_family == 'gap':
      c_flags = ' -mPE=8 -mFC=1'
      ld_flags = ' -mPE=8 -mFC=1'
      isa='imcXgap8'
    elif self.chip in ['vega', 'gap9']:
      c_flags = ' -mPE=8 -mFC=1'
      ld_flags = ' -mPE=8 -mFC=1'
      isa='imcXgap9'
    elif self.chip.find('oprecomp') != -1:
      isa='imcXgap9'
    elif core_config.get('version') == 'zeroriscy':   
      c_flags += ' -DRV_ISA_RV32=1'
    elif core_config.get('version') == 'microriscy':          
      c_flags += ' -DRV_ISA_RV32=1'
    elif core_config.get('version').find('ri5cyv2') != -1:
      pass
    elif core_config.get('version').find('ri5cyv1') != -1: 
      pass
    elif core_config.get('version').find('ri5cy') != -1: 
      # Bit operations are removed on honey as the compiler assumes the new
      # semantic for p.fl1
      ext_name = 'Xpulpv0 -mnobitop'
      isa = 'IM'
    else:
      isa = core_config.get('isa')

      if self.has_fpu and core_config.get('march') is None:  isa += 'F'

    toolchain_version = get_toolchain_version(core_config)

    if toolchain_version is not None:
      toolchain_version = int(toolchain_version)

    compiler_args = core_config.get('compiler_args')
    if compiler_args is not None:
      c_flags += ' ' + ' '.join(compiler_args)

    name = '%s%s' % (isa, ext_name)

    if toolchain_version is not None and toolchain_version >= 3:
      c_flags += ' -D__riscv__'
      name = 'rv32' + name.lower()

    self.arch_flags = ''  
    self.objd_flags = ''
    if name != '':
      if arch_flags is not None:
        self.arch_flags += ' %s' % arch_flags
      else:
        self.arch_flags += ' -march=%s' % name + c_flags
      if objd_flags is not None:
        self.objd_flags += ' %s' % objd_flags
      else:
        self.objd_flags += '-Mmarch=%s' % name

    if core_config.get('isa').find('rv64') != -1:
      self.arch_flags += ' -mcmodel=medany'

    #if self.has_fpu:  self.arch_flags += ' -mhard-float'

  def set_c_flags(self, flags):

    flags.add_arch_c_flag(self.arch_flags)

    coreStr = None
    if self.core_config.get('version').find('ri5cyv2') != -1 or self.core_config.get('version') in ['zeroriscy', 'microriscy']:
       coreStr = 'CORE_RISCV_V4'
    elif self.core_config.get('version').find('ri5cyv1') != -1:
       coreStr = 'CORE_RISCV_V3'
    elif self.core_config.get('version').find('ri5cy') != -1:
       coreStr = 'CORE_RISCV_V2'
    elif self.core_config.get('version').find('riscv') != -1:
       coreStr = 'CORE_RISCV_V1'

    flags.add_define(['__%s__' % self.core_config.get('implementation'), '1'])

    flags.add_define(['PULP_CHIP', 'CHIP_%s' % self.chip.upper().replace('-', '_')])
    if self.board is not None:
      flags.add_define(['CONFIG_%s'  % self.board.upper().replace('-', '_'), '1'])
    if self.chip_family is not None:
      flags.add_define(['CONFIG_%s'  % self.chip_family.upper().replace('-', '_'), '1'])
    else:
      flags.add_define(['CONFIG_%s'  % self.chip.upper().replace('-', '_'), '1'])
    flags.add_define(['PULP_CHIP_STR', '%s' % self.chip.replace('-', '_')])
    if self.chip_family is not None:
      flags.add_define(['PULP_CHIP_FAMILY', 'CHIP_%s' % self.chip_family.upper().replace('-', '_')])
      flags.add_define(['PULP_CHIP_FAMILY_STR', '%s' % self.chip_family.replace('-', '_')])
    if self.chipVersion is not None:
      flags.add_define(['PULP_CHIP_VERSION', self.chipVersion])
    if coreStr is not None:
      flags.add_define(['PULP_CORE', coreStr])
    if not self.has_fpu: flags.add_define(['FP_SW_EMUL', '1'])
    else: flags.add_define(['HARD_FLOAT', '1'])

    if self.core_config.get('defines') is not None:
      for define in self.core_config.get('defines'):
          flags.add_define([define, '1'])

  def get_ld_flags(self):
    return [self.arch_flags]

  def get_objd_flags(self):
    return [self.objd_flags]




class Toolchain(object):

  def __init__(self, name, core, core_family, core_isa, core_config, max_isa_name, compiler):

    self.name = name
    self.max_isa_name = max_isa_name
    has_fpu = core_isa is not None and core_isa.find('F') != -1

    self.compiler = compiler
    if self.compiler is None:
        self.compiler = 'gcc'

    toolchain, ld_toolchain = get_toolchain(core_config, core_family, core_config.get('version'), has_fpu, self.compiler)

    if core_family == 'or1k':

      if core == 'or1k':
        self.pulp_ar = 'bin/or1kle-elf-ar'
        self.pulp_ld = 'bin/or1kle-elf-gcc'
        self.pulp_objdump = 'bin/or1kle-elf-objdump'
        self.pulp_prefix = 'bin/or1kle-elf-'
        self.pulp_cc = 'bin/or1kle-elf-gcc -mnopostmod -mnomac -mnominmax -mnoabs -mnohwloop -mnovect -mnocmov'
      else:
        self.pulp_ar = 'bin/or1kle-elf-ar'
        self.pulp_ld = 'bin/or1kle-elf-gcc'
        self.pulp_objdump = 'bin/or1kle-elf-objdump'
        self.pulp_prefix = 'bin/or1kle-elf-'
        self.pulp_cc = 'bin/or1kle-elf-gcc -mreg=28'
      self.user_toolchain = 'PULP_OR1K_GCC_TOOLCHAIN'

    else:

      if core_config.get('isa').find('rv64') != -1:
        size = 64
      else:
        size = 32

      if compiler == 'llvm':
          self.pulp_ld = 'bin/riscv%d-unknown-elf-gcc' % size
          self.pulp_objdump = 'bin/riscv%d-unknown-elf-objdump' % size
          self.pulp_prefix = 'bin/riscv%d-unknown-elf-' % size
          self.pulp_cc = 'bin/clang -target riscv32-unknown-elf -I%s/riscv32-unknown-elf/include -D__LLVM__ -D__have_long64=0 -D_XOPEN_SOURCE=0' % os.environ.get('PULP_RISCV_GCC_TOOLCHAIN_CI')
          self.pulp_ar = 'bin/riscv%d-unknown-elf-ar' % size
      else:
          self.pulp_ld = 'bin/riscv%d-unknown-elf-gcc' % size
          self.pulp_objdump = 'bin/riscv%d-unknown-elf-objdump' % size
          self.pulp_prefix = 'bin/riscv%d-unknown-elf-' % size
          self.pulp_cc = 'bin/riscv%d-unknown-elf-gcc ' % size
          self.pulp_ar = 'bin/riscv%d-unknown-elf-ar' % size

      self.user_toolchain = 'PULP_RISCV_%s_TOOLCHAIN' % (self.compiler.upper())

    self.toolchain = toolchain
    self.ld_toolchain = ld_toolchain

  def mkgen(self, file):
    file.write('ifdef %s\n' % self.user_toolchain)
    file.write('PULP_%s_CC = $(%s)/%s\n' % (self.name.upper(), self.user_toolchain, self.pulp_cc))
    file.write('PULP_CC = $(%s)/%s\n' % (self.user_toolchain, self.pulp_cc))
    file.write('PULP_AR ?= $(%s)/%s\n' % (self.user_toolchain, self.pulp_ar))
    file.write('PULP_LD ?= $(%s)/%s\n' % (self.user_toolchain, self.pulp_ld))
    file.write('PULP_%s_OBJDUMP ?= $(%s)/%s\n' % (self.name.upper(), self.user_toolchain, self.pulp_objdump))
    if self.max_isa_name == self.name: file.write('PULP_OBJDUMP ?= $(%s)/%s\n' % (self.user_toolchain, self.pulp_objdump))
    file.write('else\n')
    file.write('PULP_%s_CC = %s/%s\n' % (self.name.upper(), self.toolchain, self.pulp_cc))
    file.write('PULP_CC = %s/%s\n' % (self.toolchain, self.pulp_cc))
    file.write('PULP_AR ?= %s/%s\n' % (self.toolchain, self.pulp_ar))
    file.write('PULP_LD ?= %s/%s\n' % (self.ld_toolchain, self.pulp_ld))
    file.write('PULP_%s_OBJDUMP ?= %s/%s\n' % (self.name.upper(), self.toolchain, self.pulp_objdump))
    if self.max_isa_name == self.name: file.write('PULP_OBJDUMP ?= %s/%s\n' % (self.toolchain, self.pulp_objdump))
    file.write('endif\n')










class Plt_flags(object):

  def __init__(self, config, flags):
    self.runner_flags = []
    self.config = config
    self.flags = flags

  def add_runner_flag(self, flag):
    self.runner_flags.append(flag)

  def mkgen(self, file, apps):
    Platform(self.config, self, apps, self.flags.get_build_dir()).set_flags(self)

    file.write('pulpRunOpt        += %s\n' % (' '.join(self.runner_flags)))


class C_flags_domain(object):

  def __init__(self, full_name, name, config, flags, chip, chip_family, chipVersion, core, core_family, core_isa, core_config, include_no_domain=False, max_isa_name=None):
    self.name = name
    self.full_name = full_name
    self.max_isa_name = max_isa_name

    self.include_no_domain = include_no_domain
    self.arch_c_flags      = []
    self.c_flags      = []
    self.omp_c_flags      = []
    self.inc_folders  = []
    self.includes     = []
    self.defines      = []
    self.extra_src    = {}
    self.sys_config = config

    Runtime(config, flags.get_build_dir()).set_c_flags(self)
    self.toolchain = Toolchain(name=name, core=core, core_family=core_family, core_isa=core_isa, core_config=core_config, max_isa_name=max_isa_name, compiler=config.get('compiler'))
    self.arch = Arch(name=name, chip=chip, chip_family=chip_family, chipVersion=chipVersion, core=core, core_isa=core_isa, core_config=core_config, config=config)
    self.arch.set_c_flags(flags=self)
    
    self.add_include('%s/%s_config.h' % (flags.get_build_dir(), name))

    self.config = Config(self.name, self.defines, config)

    for inc in self.inc_folders:
      self.c_flags.append('-I%s' % inc)

  def add_inc_folder(self, folder):
    self.inc_folders.append(folder)

  def add_extra_src(self, src, name, domain):
    if self.extra_src.get(name) == None:
      self.extra_src[name] = {}
    if self.extra_src.get(name).get(domain) == None:
      self.extra_src.get(name)[domain] = []
    self.extra_src.get(name).get(domain).append(src)

  def get_extra_src(self, name, domain):
    if self.extra_src.get(name) == None: return ''
    if self.extra_src.get(name).get(domain) == None: return ''
    return ' '.join(self.extra_src.get(name).get(domain))

  def add_define(self, define):
    self.defines.append(define)

  def add_include(self, folder):
    self.includes.append(folder)

  def add_c_flag(self, flag):
    self.c_flags.append(flag)

  def add_c_flags(self, flags):
    self.c_flags += flags

  def add_omp_c_flag(self, flag):
    self.omp_c_flags.append(flag)

  def add_arch_c_flag(self, flag):
    self.arch_c_flags.append(flag)

  def gen(self, path):
    file_path = os.path.join(path, '%s_config.h' % (self.name))
    with open(file_path, 'w') as file:
      self.config.gen(file)

  def mkgen(self, file):


    for inc in self.includes:
      self.c_flags.append('-include %s' % inc)


    file.write('PULP_%s_ARCH_CFLAGS ?= %s\n' % (self.name.upper(), ' '.join(self.arch_c_flags)))

    name = self.name.upper()
    #file.write('PULP_%s_LDFLAGS   := $(PULP_ARCH_%s_LDFLAGS) %s $(PULP_%s_LDFLAGS)\n' % (name, name, ' '.join(self.ld_flags), name))
    file.write('PULP_%s_CFLAGS    += %s\n' % (name, ' '.join(self.c_flags)))

    file.write('PULP_%s_OMP_CFLAGS    += %s\n' % (name, ' '.join(self.omp_c_flags)))

    self.toolchain.mkgen(file)

    file.write('PULP_ARCH_%s_OBJDFLAGS ?= %s\n' % (name, ' '.join(self.arch.get_objd_flags())))
    if self.max_isa_name == self.name:
      file.write('PULP_ARCH_OBJDFLAGS ?= %s\n' % (' '.join(self.arch.get_objd_flags())))

  def mkgen_common(self, file, name, type):

    no_domain_src = '$(PULP_APP_SRCS)' if self.include_no_domain else ''
    no_domain_omp_src = '$(PULP_APP_OMP_SRCS)' if self.include_no_domain else ''
    no_domain_asm_src = '$(PULP_APP_ASM_SRCS)' if self.include_no_domain else ''



    file.write(mk_c_pattern.format(domain_name=self.full_name, domain=self.name, domain_up=self.name.upper(), type=type, lib_name=name,
      pulpChip=self.sys_config.get('pulp_chip'), pulpChipVersion=self.sys_config.get('pulp_chip_version'),
      pulpCompiler=self.sys_config.get('pulp_compiler'), pulpRtVersion=self.sys_config.get('pulp_rt_version'),
      pulpCoreArchi=get_core_version(self.sys_config, self.name), no_domain_omp_src=no_domain_omp_src, no_domain_src=no_domain_src, no_domain_asm_src=no_domain_asm_src,
      extra_src=self.get_extra_src('c', self.name), extra_asm_src=self.get_extra_src('asm', self.name), extra_omp_src=self.get_extra_src('omp', self.name)))

  def mkgen_lib(self, file, name):
    self.mkgen_common(file, name, 'LIB')

  def mkgen_app(self, file, name):
    self.mkgen_common(file, name, 'APP')

class Ld_flags_domain(object):

  def __init__(self, flags, full_name, name, config, chip, chip_family, chipVersion, core, core_family, core_isa, core_config):
    self.name = name
    self.full_name = full_name
    self.config = config
    self.options = []
    self.ld_flags = []
    self.arch_libs = []
    self.libs = []
    self.omp_ldflags = []
    self.inc_folders = []

    self.arch = Arch(name=name, chip=chip, chip_family=chip_family, chipVersion=chipVersion, core=core, core_isa=core_isa, core_config=core_config, config=config)
    Runtime(config, flags.get_build_dir()).set_ld_flags(self)

  def mkgen(self, file):
    file.write('PULP_ARCH_LDFLAGS ?= %s\n' % (' '.join(self.arch.get_ld_flags())))
    ld_flags = ' '.join(self.options)
    for inc in self.inc_folders:
      ld_flags += ' -L%s' % inc
    for lib in self.arch_libs:
      ld_flags += ' -l{lib_name}'.format(lib_name=lib, pulpChip=self.config.get('pulp_chip'), pulpChipVersion=self.config.get('pulp_chip_version'), pulpCompiler=self.config.get('pulp_compiler'), pulpRtVersion=self.config.get('pulp_rt_version'))
    for lib in self.libs:
      ld_flags += ' -l%s' % lib

    file.write('PULP_LDFLAGS_%s = %s\n' % (self.name, ld_flags))

    file.write('PULP_OMP_LDFLAGS_%s = %s\n' % (self.name, ' '.join(self.omp_ldflags)))

  def add_arch_lib(self, lib):
    self.arch_libs.append(lib)

  def add_lib(self, lib):
    self.libs.append(lib)

  def add_omp_ldflag(self, flag):
    self.omp_ldflags.append(flag)

  def add_inc_folder(self, inc):
    self.inc_folders.append(inc)

  def add_option(self, option):
    self.options.append(option)

  def mkgen_rules(self, file):

    pass

  def mkgen_app(self, file, name):
    pass



class Lib_domain(object):

  def __init__(self, name, config, c_domains):
    self.name = name
    self.c_domains = c_domains
    self.config = config

  def mkgen(self, file):
    for c_domain in self.c_domains:
      c_domain.mkgen_lib(file, self.name)

    install_name = self.config.get('install_name')
    if install_name is None:
      install_name = self.config.get('pulp_chip')

    file.write(mk_lib_pattern.format(
      domain_name=self.name, domain=self.name, domain_up=self.name.upper(), lib_name=self.name,
      pulpChip=self.config.get('pulp_chip'), pulpChipVersion=self.config.get('pulp_chip_version'),
      pulpCompiler=self.config.get('pulp_compiler'), pulpRtVersion=self.config.get('pulp_rt_version'),
      pulpCoreArchi=get_core_version(self.config, self.name), install_name=install_name))


class App_domain(object):

  def __init__(self, name, config, c_domains, ld_domain, build_dir):
    self.name = name
    self.c_domains = c_domains
    self.ld_domain = ld_domain
    self.config = config
    self.link_script = '%s.ld' % os.path.join(build_dir, self.name)
    self.prop_link_script = '%s_config.ld' % os.path.join(build_dir, self.name)
    if not config.get_bool('rt/no-link-script'):
      ld_domain.add_option('-L%s -T%s' % (os.path.join(os.environ.get('PULP_SDK_INSTALL'), 'rules'), 
        os.path.join(self.config.get('pulp_chip_family'), 'link.ld')))

  def mkgen(self, file):
    for c_domain in self.c_domains:
      c_domain.mkgen_app(file, self.name)

    self.ld_domain.mkgen_app(file, self.name)

    file.write(mk_app_pattern.format(domain_name=self.name, domain=self.name, domain_up=self.name.upper(), lib_name=self.name,
      pulpChip=self.config.get('pulp_chip'), pulpChipVersion=self.config.get('pulp_chip_version'),
      pulpCompiler=self.config.get('pulp_compiler'), pulpRtVersion=self.config.get('pulp_rt_version'),
      pulpCoreArchi=get_core_version(self.config, self.name)
    ))



class Flags_internals(object):

  def __init__(self, config, build_dir, libs=[], properties=[], apps=[], out_config=None):
    self.config = config
    self.build_dir = build_dir

    self.config_path = out_config

    self.c_domains = []
    self.ld_domains = []

    self.libs = []
    self.properties = properties
    self.apps = []

    if self.config.get('fc') != None:
      fc_name = 'fc'
    else:
      fc_name = 'pe'

    self.plt_flags = Plt_flags(config, self)

    fc_include_no_domain = True
    max_isa_name = 'fc'
    ld_core_name = 'fc'

    if self.config.get('soc/cluster') is not None and not self.config.get('rt/fc-start'):
      fc_include_no_domain = False

    if self.config.get('soc/cluster'):
      max_isa_name = 'cl'
      ld_core_name = 'pe'

    if self.config.get('cluster') != None:
      cl_c_domain = C_flags_domain(full_name='cluster', name='cl', config=config, flags=self, chip=config.get('pulp_chip'), chip_family=config.get('pulp_chip_family'), chipVersion=config.get('pulp_chip_version'), core=get_core_version(config, 'cl'), core_family=get_core_archi(config, 'cl'), core_isa=get_core_isa(config, 'cl'), core_config=config.get_config('pe'), include_no_domain=not fc_include_no_domain, max_isa_name=max_isa_name)
      self.c_domains.append(cl_c_domain)

    if self.config.get('fc') != None:
      fc_c_domain = C_flags_domain(full_name='fabric_controller', name='fc', config=config, flags=self, chip=config.get('pulp_chip'), chip_family=config.get('pulp_chip_family'), chipVersion=config.get('pulp_chip_version'), core=get_core_version(config, 'fc'), core_family=get_core_archi(config, 'fc'), core_isa=get_core_isa(config, 'fc'), core_config=config.get_config('fc'), include_no_domain=fc_include_no_domain, max_isa_name=max_isa_name)
      self.c_domains.append(fc_c_domain)
    elif self.config.get('host') == None:
      fc_c_domain = C_flags_domain(
        full_name='fabric_controller', name='fc', config=config, flags=self,
        chip=config.get('pulp_chip'),
        chip_family=config.get('pulp_chip_family'),
        chipVersion=config.get('pulp_chip_version'),
        core=get_core_version(config, 'pe'),
        core_family=get_core_archi(config, 'pe'),
        core_isa=get_core_isa(config, 'pe'),
        core_config=config.get_config('pe'),
        max_isa_name=max_isa_name
      )
      self.c_domains.append(fc_c_domain)

    if self.config.get('host') != None:
      host_c_domain = C_flags_domain(full_name='fabric_controller', name='host', config=config, flags=self, chip=config.get('pulp_chip'), chip_family=config.get('pulp_chip_family'), chipVersion=config.get('pulp_chip_version'), core=get_core_version(config, 'host'), core_family=get_core_archi(config, 'host'), core_isa=get_core_isa(config, 'host'), core_config=config.get_config('host'), max_isa_name=max_isa_name)
      self.c_domains.append(host_c_domain)

    for lib in libs:
      self.libs.append(Lib_domain(lib, config, self.c_domains))

    app_core_config = config.get_config('fc')
    if app_core_config is None:
      app_core_config = config.get_config('host')
    if app_core_config is None or self.config.get('soc/cluster'):
      app_core_config = config.get_config('pe')

    for app in apps:
      ld_domain = Ld_flags_domain(
        flags=self, full_name=app, name=app, config=config,
        chip=config.get('pulp_chip'),
        chip_family=config.get('pulp_chip_family'),
        chipVersion=config.get('pulp_chip_version'),
        core=get_core_version(config, ld_core_name),
        core_family=get_core_archi(config, ld_core_name),
        core_isa=get_core_isa(config, ld_core_name), core_config=app_core_config
      )
      self.apps.append(App_domain(app, config, self.c_domains, ld_domain, build_dir=build_dir))
      self.ld_domains.append(ld_domain)


  def get_build_dir(self):
    return self.build_dir

  def mkgen(self, path, makefile):

    flags_path = os.path.join(path, '__flags.mk')
    rules_path = os.path.join(path, '__rules.mk')

    with open(makefile, 'w') as file:
      file.write(mk_top_pattern.format(flags_path=flags_path, rules_path=rules_path))

    with open(flags_path, 'w') as file:

      for prop in self.properties:
        value = self.config.get(prop)
        if value != None:
          file.write('%s = %s\n' % (prop, value))

      #file.write('PULP_LDFLAGS      := $(PULP_ARCH_LDFLAGS) %s $(PULP_LDFLAGS)\n' % (' '.join(self.ld_flags)))
      #file.write('PULP_CFLAGS       := $(PULP_ARCH_CFLAGS) %s $(PULP_CFLAGS)\n' % (' '.join(self.c_flags)))
      file.write('PULP_LDFLAGS      += %s\n' % '')
      file.write('PULP_CFLAGS       += %s\n' % '')

      for domain in self.c_domains:
        domain.mkgen(file)


      for domain in self.ld_domains:
        domain.mkgen(file)

      self.plt_flags.mkgen(file, self.apps)



    with open(rules_path, 'w') as file:

      file.write(mk_header_pattern.format())

      for lib in self.libs:
        lib.mkgen(file)

      for app in self.apps:
        app.mkgen(file)

      file.write(mk_rules_pattern.format())


  def gen(self, path):
    for domain in self.c_domains:
      domain.gen(path)


  def dump(self):
    pass

class Flags(object):

  def __init__(self, parser, options):
    self.parser = parser
    self.options = options

  def gen(self, config, path, makefile=False, libs=[], properties=[], apps=[],
    out_config=None):

    try:
        os.makedirs(path)
    except:
        pass

    for opt in self.options:
      if opt.find('=') != -1: 
        name, value = opt.split('=')
      else:
        name = opt
        value = True
      config.set('options/%s' % name, value)

    flags = Flags_internals(config, path, libs=libs, properties=properties, apps=apps, out_config=out_config)

    if makefile != None:
      flags.mkgen(path, makefile=makefile)



    if out_config != None:
      with open(out_config, 'w') as file:
        config.dump_to_file(file)


    flags.gen(path)

  def dump(self, config):
    flags = Flags(config, path)
    flags.dump()

  def add_args(self):  
    self.parser.add_argument("--no-build-wopt", dest="buildWopt", action="store_false", default=True, help="Deactivate all warning-related options during build")

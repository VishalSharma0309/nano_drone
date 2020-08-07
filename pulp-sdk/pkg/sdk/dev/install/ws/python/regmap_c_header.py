#
# Copyright (C) 2018 ETH Zurich, University of Bologna
# and GreenWaves Technologies
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

# Authors: Germain Haugou, ETH (germain.haugou@iis.ee.ethz.ch)


import os.path

c_head_pattern = """
/* THIS FILE HAS BEEN GENERATED, DO NOT MODIFY IT.
 */

/*
 * Copyright (C) 2018 ETH Zurich, University of Bologna
 * and GreenWaves Technologies
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"""

def get_c_desc(name):
    return name.replace('\n', ' ').encode('ascii', 'ignore').decode('ascii')

def get_c_name(name):
    return name.replace('/', '_').replace('.', '_').encode('ascii', 'ignore').decode('ascii')


class Header(object):

    def __init__(self, name, path):
        self.file = open(path, 'w')
        self.name = name
        self.file.write(c_head_pattern)
        def_name = get_c_name(path).upper()
        self.file.write('#ifndef __%s__\n' % def_name)
        self.file.write('#define __%s__\n' % def_name)
        self.file.write('\n')
        self.file.write('#if !defined(LANGUAGE_ASSEMBLY) && !defined(__ASSEMBLER__)\n')
        self.file.write('\n')
        self.file.write('#include <stdint.h>\n')
        self.file.write('#include "archi/utils.h"\n')
        self.file.write('\n')
        self.file.write('#endif\n')
        self.file.write('\n')

    def close(self):
        self.file.write('\n')
        self.file.write('#endif\n')



class Constant(object):

    def dump_to_header(self, header):
        header.file.write('#define %s_%s %s\n' % (get_c_name(header.name).upper(), get_c_name(self.name).upper(), self.value))



class Regfield(object):

    def dump_to_header(self, header, reg_name):
        field_name = '%s_%s' % (get_c_name(reg_name), get_c_name(self.name).upper())
        access_str = ''
        if self.access is not None:
          access_str = ' (access: %s)' % self.access
        if self.desc != '' or access_str != '':
          header.file.write('// %s%s\n' % (get_c_desc(self.desc), access_str))
        header.file.write('#define %-60s %d\n' % (field_name + '_BIT', self.bit))
        header.file.write('#define %-60s %d\n' % (field_name + '_WIDTH', self.width))
        header.file.write('#define %-60s 0x%x\n' % (field_name + '_MASK', ((1<<self.width)-1)<<self.bit))
        reset = self.reset

        if reset is None and self.reg_reset is not None:
          reset = (self.reg_reset >> self.bit) & ((1<<self.width) - 1)

        if reset is not None:
            header.file.write('#define %-60s 0x%x\n' % (field_name + '_RESET', reset))

    def dump_macros(self, header, reg_name=None):
        header.file.write('\n')
        field_name = '%s_%s' % (get_c_name(reg_name), get_c_name(self.name).upper())
        header.file.write('#define %-50s (ARCHI_BEXTRACTU((value),%d,%d))\n' % (field_name + '_GET(value)', self.width, self.bit))
        header.file.write('#define %-50s (ARCHI_BEXTRACT((value),%d,%d))\n' % (field_name + '_GETS(value)', self.width, self.bit))
        header.file.write('#define %-50s (ARCHI_BINSERT((value),(field),%d,%d))\n' % (field_name + '_SET(value,field)', self.width, self.bit))
        header.file.write('#define %-50s ((val) << %d)\n' % (field_name + '(val)', self.bit))



class Register(object):

    def dump_to_header(self, header):

        if self.offset is not None:
            header.file.write('\n')
            if self.desc != '':
                header.file.write('// %s\n' % get_c_desc(self.desc))
            header.file.write('#define %-40s 0x%x\n' % ('%s_%s_OFFSET' % (get_c_name(header.name).upper(), get_c_name(self.name).upper()), self.offset))

    def dump_fields_to_header(self, header):

        for name, field in self.fields.items():
            header.file.write('\n')
            reg_name = '%s_%s' % (get_c_name(header.name).upper(), get_c_name(self.name).upper())
            field.dump_to_header(reg_name=reg_name, header=header)

    def dump_struct(self, header):
        header.file.write('\n')
        header.file.write('typedef union {\n')
        header.file.write('  struct {\n')

        current_index = 0
        current_pad = 0
        for name, field in self.fields.items():
            if current_index < field.bit:
                header.file.write('    unsigned int padding%d:%-2d;\n' % (current_pad, field.bit - current_index))
                current_pad += 1

            current_index = field.bit + field.width

            header.file.write('    unsigned int %-16s:%-2d; // %s\n' % (get_c_name(field.name).lower(), field.width, get_c_desc(field.desc)))

        header.file.write('  };\n')
        header.file.write('  unsigned int raw;\n')
        header.file.write('} __attribute__((packed)) %s_%s_t;\n' % (get_c_name(header.name).lower(), get_c_name(self.name).lower()))

    def dump_vp_class(self, header):
        if self.width in [1, 8, 16, 32, 64]:
            header.file.write('\n')
            header.file.write('class vp_%s_%s : public vp::reg_%d\n' % (get_c_name(header.name).lower(), get_c_name(self.name).lower(), self.width))
            header.file.write('{\n')
            header.file.write('public:\n')

            reg_name = '%s_%s' % (get_c_name(header.name).upper(), get_c_name(self.name).upper())
            for name, field in self.fields.items():
                field_name = '%s_%s' % (get_c_name(reg_name), get_c_name(field.name).upper())
                header.file.write('  inline void %s_set(uint%d_t value) { this->set_field(value, %s_BIT, %s_WIDTH); }\n' % (get_c_name(field.name).lower(), self.width, field_name, field_name))
                header.file.write('  inline uint%d_t %s_get() { return this->get_field(%s_BIT, %s_WIDTH); }\n' % (self.width, get_c_name(field.name).lower(), field_name, field_name))

            header.file.write('};\n')

    def dump_macros(self, header=None):
        reg_name = '%s_%s' % (get_c_name(header.name).upper(), get_c_name(self.name).upper())
        for name, field in self.fields.items():
            field.dump_macros(header, reg_name)

    def dump_access_functions(self, header=None):
        reg_name = '%s_%s' % (get_c_name(header.name), get_c_name(self.name))

        if self.offset is not None:
            header.file.write("\n")
            header.file.write("static inline uint32_t %s_get(uint32_t base) { return ARCHI_READ(base, %s_OFFSET); }\n" % (reg_name.lower(), get_c_name(reg_name).upper()));
            header.file.write("static inline void %s_set(uint32_t base, uint32_t value) { ARCHI_WRITE(base, %s_OFFSET, value); }\n" % (reg_name.lower(), get_c_name(reg_name).upper()));



class Regmap(object):

    def dump_regs_to_header(self, header):

        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS\n')
        header.file.write('//\n')

        for name, register in self.registers.items():
            register.dump_to_header(header)

    def dump_regfields_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS FIELDS\n')
        header.file.write('//\n')

        for name, register in self.registers.items():
            register.dump_fields_to_header(header=header)

    def dump_structs_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS STRUCTS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#if !defined(LANGUAGE_ASSEMBLY) && !defined(__ASSEMBLER__)\n')

        for name, register in self.registers.items():
            register.dump_struct(header=header)

        header.file.write('\n')
        header.file.write('#endif\n')

    def dump_vp_structs_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS STRUCTS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#ifdef __GVSOC__\n')

        for name, register in self.registers.items():
            register.dump_vp_class(header=header)

        header.file.write('\n')
        header.file.write('#endif\n')


    def dump_regmap_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS GLOBAL STRUCT\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#if !defined(LANGUAGE_ASSEMBLY) && !defined(__ASSEMBLER__)\n')

        header.file.write('\n')
        header.file.write('typedef struct {\n')

        for name, register in self.registers.items():
            desc = ''
            if register.desc != '':
                desc = ' // %s' % register.desc
            header.file.write('  unsigned int %-16s;%s\n' % (get_c_name(register.name).lower(), desc))

        header.file.write('} __attribute__((packed)) %s_%s_t;\n' % (get_c_name(header.name), get_c_name(self.name)))

        header.file.write('\n')
        header.file.write('#endif\n')


    def dump_accessors_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS ACCESS FUNCTIONS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#if !defined(LANGUAGE_ASSEMBLY) && !defined(__ASSEMBLER__)\n')

        for name, register in self.registers.items():
            register.dump_access_functions(header=header)


        header.file.write('\n')
        header.file.write('#endif\n')



    def dump_macros_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS FIELDS MACROS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#if !defined(LANGUAGE_ASSEMBLY) && !defined(__ASSEMBLER__)\n')

        for name, register in self.registers.items():
            register.dump_macros(header=header)


        header.file.write('\n')
        header.file.write('#endif\n')

    def dump_groups_to_header(self, header):

        for name, group in self.regmaps.items():

            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')

            header.file.write('//\n')
            header.file.write('// GROUP %s\n' % name)
            header.file.write('//\n')

            if group.offset is not None:
                header.file.write('\n')
                header.file.write('#define %-40s 0x%x\n' % ('%s_%s_OFFSET' % (get_c_name(header).name.upper(), get_c_name(name).upper()), group.offset))

            group.dump_to_header(header)


    def dump_constants_to_header(self, header):

        if len(self.constants) != 0:
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// CUSTOM FIELDS\n')
            header.file.write('//\n')

        for name, constant in self.constants.items():
            constant.dump_to_header(header=header)

    def dump_to_header(self, header, header_path):
        header.file.write('#include "%s_regs.h"\n' % (header_path))
        header.file.write('#include "%s_regfields.h"\n' % (header_path))
        header.file.write('#include "%s_structs.h"\n' % (header_path))
        header.file.write('#include "%s_regmap.h"\n' % (header_path))
        header.file.write('#include "%s_accessors.h"\n' % (header_path))
        header.file.write('#include "%s_macros.h"\n' % (header_path))
        header.file.write('#include "%s_groups.h"\n' % (header_path))
        header.file.write('#include "%s_constants.h"\n' % (header_path))





def dump_to_header(regmap, name, header_path):
    header_file = Header(name, header_path + '.h')
    regmap.dump_to_header(header_file, os.path.basename(header_path))
    header_file.close()

    header_file = Header(name, header_path + '_regs.h')
    regmap.dump_regs_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_regfields.h')
    regmap.dump_regfields_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_structs.h')
    regmap.dump_structs_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_gvsoc.h')
    regmap.dump_vp_structs_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_regmap.h')
    regmap.dump_regmap_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_accessors.h')
    regmap.dump_accessors_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_macros.h')
    regmap.dump_macros_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_groups.h')
    regmap.dump_groups_to_header(header_file)
    header_file.close()

    header_file = Header(name, header_path + '_constants.h')
    regmap.dump_constants_to_header(header_file)
    header_file.close()

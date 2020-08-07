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

# Authors: Germain Haugou, ETH (germain.haugou@iis.ee.ethz.ch)


import collections
from prettytable import PrettyTable
import json_tools as js
import pytablewriter


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

class Rst_file(object):
    def __init__(self, path, name):
        self.file = open(path, "w")

    def close(self):
        self.file.close()

    def get_file(self):
        return self.file

class Header_file(object):

    def __init__(self, path, name):
        self.file = open(path, 'w')
        self.name = name
        self.file.write(c_head_pattern)
        def_name = path.replace('/', '_').replace('.', '_').upper()
        self.file.write('#ifndef __%s__\n' % def_name)
        self.file.write('#define __%s__\n' % def_name)
        self.file.write('\n')
        self.file.write('#ifndef LANGUAGE_ASSEMBLY\n')
        self.file.write('\n')
        self.file.write('#include <stdint.h>\n')
        self.file.write('#include "archi/utils.h"\n')
        self.file.write('\n')
        self.file.write('#endif\n')
        self.file.write('\n')
#include <stdint.h>
#include "archi/utils.h"

    def close(self):
        self.file.write('\n')
        self.file.write('#endif\n')


class Register_field(object):

    def __init__(self, name, config):
        self.bit = config.get_child_int('bit')
        self.width = config.get_child_int('width')
        self.access = config.get_child_str('access')
        self.reset = config.get_child_int('reset')
        self.desc = config.get_child_str('desc')
        self.full_name = config.get_child_str('name')
        self.name = name

    def get_row(self):
        if self.width == 1:
            bit = '%d' % self.bit
        else:
            bit = '%d:%d' % (self.bit + self.width - 1, self.bit)

        return [bit, self.access, self.name, self.desc]



    def dump_doc(self, table, dump_regs=False, reg_name=None, reg_reset=None, header_file=None):
        if header_file is None:
            row = []
            if dump_regs:
                row += ['', '', '', '']

            table.add_row(row + self.get_row())
        else:
            field_name = '%s_%s' % (reg_name, self.name.upper())
            access_str = ''
            if self.access is not None:
                access_str = ' (access: %s)' % self.access
            if self.desc != '' or access_str != '':
                header_file.file.write('// %s%s\n' % (self.desc, access_str))
            header_file.file.write('#define %-60s %d\n' % (field_name + '_BIT', self.bit))
            header_file.file.write('#define %-60s %d\n' % (field_name + '_WIDTH', self.width))
            header_file.file.write('#define %-60s 0x%x\n' % (field_name + '_MASK', ((1<<self.width)-1)<<self.bit))
            reset = self.reset
            if reset is None and reg_reset is not None:
                reset = (reg_reset >> self.bit) & ((1<<self.width) - 1)
            header_file.file.write('#define %-60s 0x%x\n' % (field_name + '_RESET', reset))

    def dump_macros(self, reg_name=None, header_file=None):
        header_file.file.write('\n')
        field_name = '%s_%s' % (reg_name, self.name.upper())
        header_file.file.write('#define %-50s (ARCHI_BEXTRACTU((value),%d,%d))\n' % (field_name + '_GET(value)', self.width, self.bit))
        header_file.file.write('#define %-50s (ARCHI_BEXTRACT((value),%d,%d))\n' % (field_name + '_GETS(value)', self.width, self.bit))
        header_file.file.write('#define %-50s (ARCHI_BINSERT((value),(field),%d,%d))\n' % (field_name + '_SET(value,field)', self.width, self.bit))
        header_file.file.write('#define %-50s ((val) << %d)\n' % (field_name + '(val)', self.bit))

    def dump_reg_table_to_rst(self, table):
        table.append(self.get_row())

class Register(object):

    def __init__(self, name, regmap, config):

        self.fields = collections.OrderedDict([])
        self.config = config
        self.name = name
        self.regmap = regmap

        self.desc = config.get_child_str('desc')
        self.offset = config.get_child_int('offset')
        self.width = config.get_child_int('width')
        self.reset = config.get_child_int('reset')

        content = config.get('content')
        if content is not None:
            for name, field in content.get_items().items():
                self.fields[name] = Register_field(name, field)

    def get_group_path(self):
        return self.regmap.get_group_path()

    def get_offset(self):
        parent_offset = self.regmap.get_offset()

        if parent_offset is not None:
            return parent_offset + self.offset
        else:
            return self.offset

    def get_full_name(self):
        group = self.regmap.get_group_path()

        if group is not None:
            return group + ':' + self.name
        else:
            return self.name


    def clone(self, regmap):
        new_reg = Register(self.name, regmap, self.config)
        regmap.registers[self.name] = new_reg

    def dump_doc(self, table, dump_regs_fields, header_file=None):

        if header_file is None:
            row = [self.get_full_name(), '0x%x' % self.get_offset(), self.width, self.desc]
            if dump_regs_fields:
                row += ['', '', '', '']

            table.add_row(row)

            if dump_regs_fields:
                for name, field in self.fields.items():
                    field.dump_doc(table, dump_regs=True)
        else:
            header_file.file.write('\n')
            if self.desc != '':
                header_file.file.write('// %s\n' % self.desc)
            header_file.file.write('#define %-40s 0x%x\n' % ('%s_%s_OFFSET' % (header_file.name.upper(), self.name.upper()), self.offset))


    def dump_doc_fields(self, header_file=None):

        if header_file is None:
            x = PrettyTable(['Bit #', 'R/W', 'Name', 'Description'])
            x.align = 'l'

            for name, field in self.fields.items():
                field.dump_doc(x)

            print (self.desc)
            print (x)
            print ('\n')
        else:
            for name, field in self.fields.items():
                header_file.file.write('\n')
                reg_name = '%s_%s' % (header_file.name.upper(), self.name.upper())
                field.dump_doc(table=None, reg_name=reg_name, reg_reset=self.reset, header_file=header_file)

    def dump_struct(self, header_file=None):
        header_file.file.write('\n')
        header_file.file.write('typedef union {\n')
        header_file.file.write('  struct {\n')

        for name, field in self.fields.items():
            header_file.file.write('    unsigned int %-16s:%-2d; // %s\n' % (field.name, field.width, field.desc))


        header_file.file.write('  };\n')
        header_file.file.write('  unsigned int raw;\n')
        header_file.file.write('} __attribute__((packed)) %s_%s_t;\n' % (header_file.name, self.name))

    def dump_macros(self, header_file=None):
        reg_name = '%s_%s' % (header_file.name.upper(), self.name.upper())
        for name, field in self.fields.items():
            field.dump_macros(reg_name, header_file)

    def dump_access_functions(self, header_file=None):
        reg_name = '%s_%s' % (header_file.name, self.name)

        header_file.file.write("\n")
        header_file.file.write("static inline uint32_t %s_get(uint32_t base) { return ARCHI_READ(base, %s_OFFSET); }\n" % (reg_name, reg_name.upper()));
        header_file.file.write("static inline void %s_set(uint32_t base, uint32_t value) { ARCHI_WRITE(base, %s_OFFSET, value); }\n" % (reg_name, reg_name.upper()));

    def dump_reg_table_to_rst(self, rst):
        writer = pytablewriter.RstGridTableWriter()
        writer.table_name = self.name
        writer.header_list = ['Bit #', 'R/W', 'Name', 'Description']

        table = []
        for name, field in self.fields.items():
            field.dump_reg_table_to_rst(table)

        writer.value_matrix = table

        writer.stream = rst.get_file()
        writer.write_table()


class Custom(object):

    def __init__(self, config, name=None, parent=None):
        self.name = name
        self.config = config
        self.parent = parent


    def dump_doc_rec(self, header, name, obj):
        obj_type = obj.get_child_str('type')

        if obj_type == 'constant':
            value = obj.get_child_str('value')
            header.file.write('#define %s_%s %s\n' % (header.name.upper(), name.upper(), value))



    def dump_doc(self, header=None):

        if header is not None:
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// CUSTOM FIELDS\n')
            header.file.write('//\n')

            for name, obj in self.config.get_items().items():
                self.dump_doc_rec(header, name, obj)




class Regmap(object):

    def __init__(self, config, name=None, parent=None):
        self.templates = collections.OrderedDict()
        self.registers = collections.OrderedDict()
        self.groups = collections.OrderedDict()
        self.customs = collections.OrderedDict()
        self.parent = parent
        self.name = name
        self.offset = None
        self.config = config

        if name is None:
            self.__parse_elems(config)
        else:
            self.__parse_elem(name, config)

    def get_offset(self):
        offset = 0
        parent_offset = None
        if self.parent is not None:
            parent_offset = self.parent.get_offset()
        if parent_offset is not None:
            offset += parent_offset
        if self.offset is not None:
            offset += self.offset
        return offset

    def get_group_path(self):
        parent_path = None
        if self.parent is not None:
            parent_path = self.parent.get_group_path()

        if parent_path is not None:
            return parent_path + ':' + self.name
        else:
            return self.name

        return self.name

    def __parse_elems(self, config):

        for name, obj in config.get_items().items():
            self.__parse_elem_from_type(name, obj)

    def __get_template(self, name):
        if self.templates.get(name) is not None:
            return self.templates.get(name)

        if self.parent is not None:
            return self.parent.__get_template(name)

        return None



    def __parse_elem_from_type(self, name, config):
        if type(config) not in [js.config_object]:
            return

        obj_type = config.get_child_str('type')

        if obj_type is not None:

            if obj_type == 'template':
                self.templates[name] = Template(config, parent=self)
                return

            elif obj_type == 'register':
                self.registers[name] = Register(name, self, config)
                return

            elif obj_type == 'group':
                self.groups[name] = Regmap(config, name=name, parent=self)
                return

            elif obj_type == 'custom':
                self.customs[name] = Custom(config, name=name, parent=self)
                return

        self.__parse_elem(name, config)


    def __parse_elem(self, name, config):

        self.offset = config.get_child_int('offset')
        if self.offset is not None:
            self.offset = self.offset
        template = config.get_child_str('template')
        if template is not None:
            self.__get_template(template).clone(self)
            return

        self.__parse_elems(config)

    def dump_doc_regs_rec(self, table, dump_regs_fields, header_file=None):

        for name, register in self.registers.items():
            register.dump_doc(table, dump_regs_fields=dump_regs_fields, header_file=header_file)


    def dump_doc_regs(self, dump_regs_fields=False, header=None):

        if header is None:
            rows = ['Name', 'Offset', 'Width', 'Description']
            if dump_regs_fields:
                rows += ['Field bit #', 'Field R/W', 'Field name', 'Field description']

            table = PrettyTable(rows)
            table.align = 'l'

            self.dump_doc_regs_rec(table, dump_regs_fields=dump_regs_fields)

            print (table)

        else:
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// REGISTERS\n')
            header.file.write('//\n')
            self.dump_doc_regs_rec(None, dump_regs_fields=dump_regs_fields, header_file=header)


    def dump_doc_regs_fields(self, header=None):

        if header is not None:
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// REGISTERS FIELDS\n')
            header.file.write('//\n')

        for name, register in self.registers.items():
            register.dump_doc_fields(header_file=header)

        if header is not None:
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// REGISTERS STRUCTS\n')
            header.file.write('//\n')
            header.file.write('\n')
            header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

            for name, register in self.registers.items():

                register.dump_struct(header_file=header)

            header.file.write('\n')
            header.file.write('#endif\n')


            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// REGISTERS GLOBAL STRUCT\n')
            header.file.write('//\n')
            header.file.write('\n')
            header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

            header.file.write('\n')
            header.file.write('typedef struct {\n')

            for name, register in self.registers.items():
                desc = ''
                if register.desc != '':
                    desc = ' // %s' % register.desc
                header.file.write('  unsigned int %-16s;%s\n' % (register.name, desc))

            header.file.write('} __attribute__((packed)) %s_%s_t;\n' % (header.name, self.name))

            header.file.write('\n')
            header.file.write('#endif\n')


            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// REGISTERS ACCESS FUNCTIONS\n')
            header.file.write('//\n')
            header.file.write('\n')
            header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

            for name, register in self.registers.items():
                register.dump_access_functions(header_file=header)


            header.file.write('\n')
            header.file.write('#endif\n')



            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// REGISTERS FIELDS MACROS\n')
            header.file.write('//\n')
            header.file.write('\n')
            header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

            for name, register in self.registers.items():
                register.dump_macros(header_file=header)


            header.file.write('\n')
            header.file.write('#endif\n')



    def dump_memmap_to_rst(self, rst):
        for name, register in self.registers.items():
            register.dump_reg_table_to_rst(rst)

    def dump_memmap(self, dump_regs=False, dump_regs_fields=False, header=None):

        if header is None:
            if dump_regs_fields and not dump_regs:
                self.dump_doc_regs_fields(header=header)
            else:
                self.dump_doc_regs(dump_regs_fields=dump_regs_fields, header=header)
        else:
            if dump_regs:
                self.dump_doc_regs(dump_regs_fields=dump_regs_fields, header=header)

            if dump_regs_fields:
                self.dump_doc_regs_fields(header=header)


            for name, group in self.groups.items():

                header.file.write('\n')
                header.file.write('\n')
                header.file.write('\n')

                header.file.write('//\n')
                header.file.write('// GROUP %s\n' % name)
                header.file.write('//\n')

                offset = group.config.get_child_int('offset')
                if offset is not None:
                    header.file.write('\n')
                    header.file.write('#define %-40s 0x%x\n' % ('%s_%s_OFFSET' % (header.name.upper(), name.upper()), offset))


                if dump_regs:
                    group.dump_doc_regs(dump_regs_fields=dump_regs_fields, header=header)

                if dump_regs_fields:
                    group.dump_doc_regs_fields(header=header)

            for name, custom in self.customs.items():
                custom.dump_doc(header=header)



    def clone(self, regmap):
        regmap.groups[self.name] = Regmap(self.config, name=self.name, parent=regmap)


class Template(Regmap):

    def clone(self, regmap):

        for name, group in self.groups.items():
            group.clone(regmap)

        for name, register in self.registers.items():
            register.clone(regmap)

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

import pandas as pd
import regmap as rmap

def get_name(field):
    if field[0].isdigit():
        field = '_' + field
    return field.replace(' ', '_')

def get_description(field):
    return field.replace('\n', ' ').replace('\r', ' ')

def import_xls(regmap, path):
    xlsx = pd.ExcelFile(path)

    ipreglist = None
    ipregmap = None
    ipfsmfmtmap = None

    for sheet_name in xlsx.sheet_names:

        if sheet_name.find('IPREGLIST') == 0:
            ipreglist = xlsx.parse(sheet_name)
        elif sheet_name.find('IPREGMAP') == 0:
            ipregmap = xlsx.parse(sheet_name)
        elif sheet_name.find('IPFSMFMTMAP') == 0:
            ipfsmfmtmap = xlsx.parse(sheet_name)

    if ipreglist is not None:
        for index, row in ipreglist.iterrows():
            regmap.add_register(
                rmap.Register(
                  name=str(row['Register Name']),
                  offset=int(row['Address'], 0),
                  width=row['Size'],
                  desc=str(row['Description'])
                )
            )

    if ipregmap is not None:
        for index, row in ipregmap.iterrows():
            reg_name = row['Register']

            reg = regmap.get_register(reg_name)

            if row['Bit field'] == '-':
                continue

            if reg is None:
                raise Exception("Found bitfield for unknown register: " + reg_name)

            reg.add_regfield(
                rmap.Regfield(
                    name=str(row['Bit field']),
                    width=int(row['Size']),
                    bit=int(row['Bit Position']),
                    access=str(row['Host Access Type']),
                    desc=get_description(str(row['Description'])),
                    reg_reset=reg.reset
                )
            )

    if ipfsmfmtmap is not None:
        for index, row in ipfsmfmtmap.iterrows():
            reg_name = '%s_%s' % (row['Register name'], row['Format Name'])

            reg = regmap.get_register(reg_name)

            if reg is None:
                reg = regmap.add_register(
                    rmap.Register(
                      name=reg_name,
                      offset=None,
                      width=row['Size'],
                      desc=get_description(row['Description'])
                    ))

            if row['Bit field'] == '-':
                continue

            reg.add_regfield(
                rmap.Regfield(
                    name=get_name(row['Bit field']),
                    width=int(row['Size']),
                    bit=int(row['Bit Position']),
                    access=str(row['Host Access Type']),
                    desc=get_description(row['Description']),
                    reg_reset=reg.reset
                )
            )

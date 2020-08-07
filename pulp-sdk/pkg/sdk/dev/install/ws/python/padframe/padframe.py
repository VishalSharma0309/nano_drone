
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


from collections import OrderedDict
from math import log

class Profile_pad(object):

    def __init__(self, pad, alternate):
        self.pad = pad
        self.alternate = alternate


class Profile(object):

    def __init__(self, padframe, name, config, user_config):

        self.padframe = padframe
        self.name = name
        self.alternates = {}
        self.groups = OrderedDict()

        all_pads = {}
        all_pads.update(config.items())
        if user_config is not None:
          all_pads.update(user_config.items())

        for pad_name, pad_config in all_pads.items():
            if pad_name == 'alternates':
                continue
            pad = padframe.get_pad_from_name(pad_name)
            alternate = pad.get_alternate_from_name(pad_config.get("alternate"))
            self.alternates[pad_name] = alternate
            for group in alternate.get_groups():
                if self.groups.get(group) is None:
                    self.groups[group] = []
                self.groups[group].append(Profile_pad(pad, alternate))

    def get_groups(self):
        return self.groups

class Alternate(object):

    def __init__(self, config):
        self.name = config.get('name')
        self.groups = config.get('groups')

    def get_groups(self):
        return self.groups


class Pad(object):

    def __init__(self, name, config):
        self.name = name
        self.id = config.get_int('id')
        self.position = config.get('position')
        if self.position is None:
          self.position = '-'
        self.alternates = []
        self.alternates_dict = {}
        alternates = config.get('alternates')
        if alternates is not None:
            for alternate in alternates:
                alternate_obj = Alternate(alternate)
                self.alternates.append(alternate_obj)
                self.alternates_dict[alternate_obj.name] = alternate_obj

    def get_alternate(self, id):
        return self.alternates[id]

    def get_alternate_from_name(self, name):
        return self.alternates_dict[name]


class Padframe(object):

    def __init__(self, config, user_config=None):
        self.config = config
        self.profiles_dict = OrderedDict()
        self.profiles = []
        self.pads_dict = OrderedDict()
        self.pads = []
        self.groups = OrderedDict()
        self.nb_alternate = config.get_int('nb_alternate')
        self.first_alternate = config.get_int('first_alternate')
        self.user_config = user_config

        pads = config.get_config('pads')
        if pads is not None:
            for pad_name, pad_conf in pads.items():
                pad = Pad(pad_name, pad_conf)
                self.pads_dict[pad_name] = pad
                for i in range(len(self.pads), pad.id+1):
                  self.pads.append(None)

                self.pads[pad.id] = pad

        profiles = config.get_config('profiles')

        if profiles is not None:
            for profile_name, profile_conf in profiles.items():
                user_profile = None
                if user_config is not None:
                  user_profile = user_config.get_config(profile_name)
                profile = Profile(self, profile_name, profile_conf, user_profile)
                self.profiles_dict[profile_name] = profile
                self.profiles.append(profile)

    def get_profile(self, name):
        return self.profiles_dict.get(name)

    def get_profiles(self):
        return self.profiles

    def get_pad_from_id(self, pad_id):
        return self.pads[pad_id]

    def get_pad_from_name(self, name):
        return self.pads_dict[name]

    def get_pads(self):
        return self.pads


    def gen_rt_conf(self, filepath, default_profile="default"):
      nb_bit_per_pad = int(log(self.nb_alternate, 2))
      nb_pad = len(self.get_pads())
      nb_pad_per_word = int(32 / nb_bit_per_pad)
      nb_words = int((nb_pad * nb_bit_per_pad + 31)/ 32)

      with open(filepath, 'w') as file:

          file.write('#include "rt/rt_data.h"\n')
          file.write('\n')

          default_profile = self.get_profile(default_profile)

          profile_list = [ default_profile ]
          for profile in self.get_profiles():
              if profile != default_profile:
                  profile_list.append(profile)

          for profile in profile_list:
              file.write('static unsigned int __rt_padframe_%s[] = {' % profile.name)

              pad_id = self.first_alternate
              if pad_id == None:
                pad_id = 0

              for word in range(0, nb_words):
                  value = 0
                  for word_index in range (0, nb_pad_per_word):

                      pad = self.get_pad_from_id(pad_id)
                      alternate_id = 0
                      alternate = profile.alternates.get(pad.name)
                      if alternate is not None:
                        alternate_id = pad.alternates.index(alternate)

                      value = value | ( alternate_id << (word_index * nb_bit_per_pad))

                      pad_id += 1
                      if pad_id >= nb_pad:
                        break

                  file.write(' 0x%8.8x,' % value)

              file.write('};\n')
              file.write('\n')

          file.write('rt_padframe_profile_t __rt_padframe_profiles[] = {\n')
          for profile in profile_list:
            file.write('  { .name="%s", .config=__rt_padframe_%s },\n' % (profile.name, profile.name))
          file.write('};\n')
          file.write('\n')

          file.write('int __rt_nb_profile = %d;\n' % len(profile_list))


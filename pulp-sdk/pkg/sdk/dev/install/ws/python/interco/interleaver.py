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
 
import vp_core as vp
import math as m

class component(vp.component):

    implementation = 'interco.interleaver_impl'

    def build(self):
      if self.get_json().get_child_int('stage_bits') == 0:
        nb_slaves = self.get_json().get_child_int('nb_slaves')
        self.get_json().set('stage_bits', m.ceil(m.log2(nb_slaves)))
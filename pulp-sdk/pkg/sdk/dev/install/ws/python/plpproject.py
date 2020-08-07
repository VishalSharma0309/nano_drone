
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


import plptools as plp

class PkgDep(plp.PkgDep):

  def __init__(self, *kargs, **kwargs):
    super(PkgDep, self).__init__(*kargs, **kwargs)

class Package(plp.Package):

  def __init__(self, *kargs, **kwargs):
    super(Package, self).__init__(*kargs, **kwargs)

class ArtifactoryServer(object):
  def __init__(self, name, url, ssl_verify=True):
    self.name = name
    self.url = url
    self.ssl_verify = ssl_verify


class Module(plp.Module):

  def __init__(self, *kargs, **kwargs):
    super(Module, self).__init__(*kargs, **kwargs)


class BuildStep(object):

  def __init__(self, name, command):
    self.name = name
    self.command = command


class Group(plp.Group):

  def __init__(self, *kargs, **kwargs):
    super(Group, self).__init__(*kargs, **kwargs)


class BuildStepMap(object):

  def __init__(self, name, stepList):
    self.name = name
    self.stepList = stepList


class BuildSteps(object):

  def __init__(self, stepList):
    self.stepList = stepList
    self.steps = {}
    for step in stepList:
      self.steps[step.name] = step

  def get(self, name): return self.steps.get(name).stepList

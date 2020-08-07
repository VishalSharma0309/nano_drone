
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


from twisted.internet import protocol, reactor, endpoints
import os
import shlex
import sys

class Builder_command(protocol.ProcessProtocol):

  def __init__(self, name=None, cmd=None, path=None, deps=[], env={}, callback=None, *kargs, **kwargs):
    super(Builder_command, self).__init__()
    self.log = ''
    self.closed = False
    self.status = False
    self.cmd = cmd
    self.callback = callback
    self.kargs = kargs
    self.kwargs = kwargs
    self.path = path
    self.deps = deps
    self.up_deps = []
    self.name = name
    self.builder_callback = None
    self.env = env
    self.dump_log = False
    self.register_deps()

  def set_callback(self, callback=None, *kargs, **kwargs):
    self.callback = callback
    self.kargs = kargs
    self.kwargs = kwargs

  def __str__(self): return '%s: %s' % (self.name, self.cmd)

  def dump(self):
    print (str(self))

  def register_deps(self):
    # In case we have dependencies, we need to register ourself on them to be enqueued
    # When they are finished
    # Be careful, some of them might already have finished, don't register them
    self.nbDeps = 0

    for dep in self.deps:
      if not dep.closed: 
        self.nbDeps += 1
        dep.register_dep(self)

  def end_of_dep(self):
    self.nbDeps -= 1
    return self.nbDeps == 0

  def register_dep(self, dep):
    self.up_deps.append(dep)

  def appendOutput(self, data):
    if self.stdout:
      sys.stdout.write(data)
    self.log += data

  def outReceived(self, data):
    self.appendOutput(data.decode('utf-8', errors='ignore'))

  def dataReceived(self, data):
    self.appendOutput(data.decode('utf-8', errors='ignore'))

  def __handle_end(self):
    self.closed = True

    if self.stdout_cached:
      print (self.log)

    if self.builder_callback != None:
      self.builder_callback(self)

    if self.callback != None:
      self.callback(*self.kargs, **self.kwargs)

  def close(self, kill=False):
    if self.closed: return True
    os.killpg(self.pid, signal.SIGKILL)

  def run(self, log, stdout, stdout_cached, callback):
    self.dump_log = log
    self.stdout = stdout
    self.stdout_cached = stdout_cached
    self.builder_callback = callback
    if self.cmd != None:
      print ()
      print ('\033[1m' + '%s' % self.name + '\033[0m' + ': %s' % (self.cmd))
      args = shlex.split(self.cmd)
      self.p = reactor.spawnProcess(self,path=self.path, executable=args[0], args=args, usePTY=True, env=self.env)
      self.gid = os.getpgid(self.p.pid)
      self.pid = self.p.pid
    else:
      self.status = True
      self.__handle_end()

  def processEnded(self, reason):
    if reason.value.exitCode == None:
      self.appendOutput('Process was killed\n')
      self.status = False
    else:
      self.appendOutput('Reached EOF with exit status ' + str(reason.value.exitCode) + '\n')
      self.status = reason.value.exitCode == 0

    self.__handle_end()

class Builder(object):

  def __init__(self, nb_threads=1, log=None, stdout=False, stdout_cached=False):

    self.nb_threads = nb_threads
    self.runnings = []
    self.pendings = []
    self.commands = {}
    self.empty_callback = None
    self.nb_pendings = 0
    self.log = log
    self.stdout = stdout
    self.stdout_cached = stdout_cached
    self.status = 0
    
  def run(self, cmd):
    self.runnings.append(cmd)
    cmd.run(log=self.log, stdout=self.stdout, callback=self.cmd_end, stdout_cached=self.stdout_cached)

  def cmd_end(self, cmd):

    self.runnings.remove(cmd)

    if not cmd.status:
      return self.stop(-1)

    self.nb_pendings -= 1

    for dep in cmd.up_deps:
      if dep.end_of_dep():
        self.enqueue_ready(dep)

    if self.nb_pendings == 0 and self.empty_callback != None:
      self.empty_callback()
      self.empty_callback = None

    if len(self.pendings) > 0 and len(self.runnings) <   self.nb_threads:
      cmd = self.pendings.pop()
      self.run(cmd)



  def get_command(self, name):
    return self.commands.get(name)

  def enqueue_ready(self, cmd):

    if len(self.runnings) >= self.nb_threads:

      self.pendings.append(cmd)
      return

    self.run(cmd)


  def enqueue(self, cmd):

    self.nb_pendings += 1

    if cmd.name != None:
      self.commands[cmd.name] = cmd

    #cmd.register_deps()

    # Only enqueue the command if it has no dependency
    # It will be enqueued later on by the dependency itself when it finishes
    if cmd.nbDeps == 0:

      self.enqueue_ready(cmd)

  def stop(self, status):
    self.status = status

    if reactor.running: 
      reactor.stop()

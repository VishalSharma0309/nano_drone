
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
import os.path
import imp
import plpartifactory
import subprocess
import plptools_builder
from twisted.internet import reactor
import hashlib
import collections
from plpobjects import *
try:
    from plptest_runner import *
except:
    pass
import datetime
import plpdownloader
import shutil
import json_tools as js
import pulp_config as plpconf


version_file_pattern = """
import plpproject as plp

ProjectConfig = c = {
}

c['package_versions'] = {
  %s
}

c['module_versions'] = {
  %s
}
"""

testset_file_pattern = """
from plptest import *

TestConfig = c = {}

tests = Testset(
  name  = 'tests',
  files = [ 
    %s
  ]
)

c['testsets'] = [ tests ]
"""



def get_git_version(path):
    if not os.path.exists(path):
        return None
    cwd = os.getcwd()
    os.chdir(path)
    gitVersion = subprocess.check_output('git log -n 1 --format=format:%H'.split()).decode('utf-8')
    os.chdir(cwd)
    return gitVersion

def is_git_modified(path):
    cwd = getRootDir()
    os.chdir(path)
    isModified = os.system('git diff-index --quiet HEAD --') != 0
    gitVersion = subprocess.check_output('git log -n 1 --format=format:%H'.split()).decode('utf-8')
    os.chdir(cwd)
    return isModified


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_root_dir():
  result = os.environ.get('PULP_PROJECT_HOME')
  if result == None: raise Exception('PULP_PROJECT_HOME is not defined, please source init.sh')
  return result


class Sourceme(object):

    def __init__(self, path, name):
        try:
            os.makedirs(path)
        except Exception:
            pass
        self.csh_file = open(os.path.join(path, '%s.csh' % name), 'w')
        self.sh_file = open(os.path.join(path, '%s.sh' % name), 'w')

    def add_export(self, key, value):
        self.csh_file.write('setenv %s %s\n' % (key, value))
        self.sh_file.write('export %s=%s\n' % (key, value))

    def add_sourceme(self, sh_name, csh_name):
        self.csh_file.write('source %s\n' % (csh_name))
        self.sh_file.write('source %s\n' % (sh_name))

    def gen(self):
        self.csh_file.close()
        self.sh_file.close()


class Cmd_group(object):

    def __init__(self, callback=None, *kargs, **kwargs):
        self.finished = False
        self.callback = callback
        self.enqueued = 0
        self.kargs = kargs
        self.kwargs = kwargs
        self.status = True

    def set_callback(self, callback=None, *kargs, **kwargs):
        self.callback = callback
        self.kargs = kargs
        self.kwargs = kwargs

    def inc_enqueued(self):
        self.enqueued += 1

    def dec_enqueued(self, command=None):
        self.enqueued -= 1

        if command is not None:
            self.status = self.status and command.status
        if not self.status or self.callback is not None and self.enqueued == 0 and self.finished:
            self.callback(*self.kargs, **self.kwargs)

    def set_finished(self):
        self.finished = True
        if self.enqueued == 0:
          reactor.callLater(0, self.callback, *self.kargs, **self.kwargs)


class Group(object):
  def __init__(self, name, modules):
    self.name = name
    self.modules = modules
    self.modules_names = []
    for module in modules: self.modules_names.append(module.name)


class Module(object):
    def __init__(self, name, path=None, url=None, steps=[], deps=[], parameters=[], env={}, testsets=[], restrict=None):
        self.name = name
        self.path = path
        self.url = url
        self.stepsList = steps
        self.parameters = parameters
        self.deps = deps
        self.env = env
        self.testsets = testsets
        self.steps = collections.OrderedDict()
        for step in steps:
            self.steps[step.name] = step
        self.version = None
        self.git_version = None
        self.restrict = restrict
        self.active_configs = []

    def set_pkg(self, pkg):
        self.pkg = pkg

    def get_build_dir(self):
        return os.path.join(self.pkg.get_build_dir(), self.name)

    def is_active(self):
        return self.active

    def is_active_config(self, config):
        return config.get_name() in self.active_configs

    def __find_active_config(self, configs):

        result = False

        for config in configs:
            if self.restrict is None or eval(self.restrict):
                self.active_configs.append(config.get_name())
                result = True

        return result

    def check_configs(self, configs):
        self.active = self.__find_active_config(configs)

    def set_root_dir(self, path):
        self.root_dir = path
        self.abs_path = os.path.join(path, self.path)

    def get_abspath(self):
        return self.abs_path

    def get_version(self):
        if self.version is not None:
            return self.version
        if self.git_version is None:
            self.git_version = get_git_version(self.path)
        return self.git_version

    def dumpMsg(self, pkg, cmd):
        print ()
        print ('\033[1m' + 'MODULE %s:%s command %s' % (pkg.name, self.name, cmd) + '\033[0m')




    def update(self):
      new_version = get_git_version(self.path)
      if new_version is not None:
        self.version = new_version

    def get_testsets(self):

      if not self.is_active():
        return []

      testsets = []
      for testset in self.testsets:
        testsets.append([self.name.replace('-', '_'), os.path.join(self.path, testset)])
      return testsets

    def get_env_for_command(self, pkg, config=None):

        env = os.environ.copy()
        env['PKG_DIR'] = pkg.get_absolute_path()
        pkg.get_env(env)

        for key, value in self.env.items():
            env[key] = eval(value)

        if config is not None:
            env['PULP_CURRENT_CONFIG'] = config.get_name()

        return env

    def enqueue_steps(self, builder, pkg, cmd_group, configs, steps):

        self.builder = builder

        # First create a proxy job with nothing to execute so that other modules
        # which depends on it can wait for the completion of all module jobs
        # This job will inherit the job dependencies and will trigger module
        # jobs when it is ready

        self.nb_pending_configs = 0

        deps = []
        for dep in self.deps:
            # A module must be built for each package, thus module commands are registered
            # in the builder with both package and module names to differentiate them
            # And depend on the right module
            dep_job = builder.get_command('%s:%s:last' % (pkg, dep.name))
            if dep_job != None: deps.append(dep_job)

        cmd_group.inc_enqueued()
        module_job = plptools_builder.Builder_command(
          name='%s:%s' % (pkg, self.name), deps=deps)
        module_job.set_callback(callback=cmd_group.dec_enqueued, command=module_job)
        builder.enqueue(cmd=module_job)

        configs_last_cmd = []
        job_configs = []

        for configId in range(0, len(configs)):

            config = configs[configId]

            if not self.is_active_config(config):
                continue

            config_last_cmd = None

            # Extract the items from the config on which the module is sentitive to check
            # if we should consider it as already processed
            job_config = config.get_name_from_items(self.parameters)
            if job_config in job_configs: continue
            job_configs.append(job_config)

            self.nb_pending_configs += 1

            # The first step always depend on the module job, to get triggered when all module deps are finished
            prev_step = module_job
            for i in range(0, len(steps)):
                step = steps[i]
                if self.steps.get(step) == None: continue
                # Then each step depends on the previous one to execute them sequentially
                # Only the last step has a callback to update the module
                else: name = '%s:%s:%s' % (pkg, self.name, step)
                if len(self.parameters) != 0: name += ' (%s)' % (config.name)
                cmd_group.inc_enqueued()
                prev_step = plptools_builder.Builder_command(
                  name=name, cmd=self.steps.get(step).command, path=self.abs_path,
                  env=self.get_env_for_command(pkg, config), deps=[prev_step])
                prev_step.set_callback(callback=cmd_group.dec_enqueued, command=prev_step)
                builder.enqueue(cmd=prev_step)
                config_last_cmd = prev_step

            if config_last_cmd != None: configs_last_cmd.append(config_last_cmd)

        cmd_group.inc_enqueued()
        module_job = plptools_builder.Builder_command(name='%s:%s:last' % (pkg, self.name), deps=configs_last_cmd)
        module_job.set_callback(callback=cmd_group.dec_enqueued, command=module_job)
        builder.enqueue(cmd=module_job)

    def exec_cmd(self, cmd):
        cwd = os.getcwd()
        os.chdir(self.abs_path)
        self.dumpMsg(self, cmd)
        retval = os.system(cmd)
        os.chdir(cwd)
        return retval

    def sync(self):

        if os.path.exists(self.name):
            cwd = os.getcwd()
            os.chdir(self.name)

            if os.system('git fetch -t') != 0:
                return -1

            if os.system('git checkout %s' % self.get_version()) != 0:
                return -1

            os.chdir(cwd)

        return 0

    def checkout(self, pkg, builder, cmd_group):
        ret = 0
        if self.url is not None:
            self.dumpMsg(self, 'checkout')
            if not os.path.exists(self.abs_path):
                cmd = "git clone %s %s" % (self.url, self.abs_path)
                if os.system(cmd) != 0:
                    return -1
            cwd = os.getcwd()

            os.chdir(self.abs_path)

            # We may get an exception if the version is not specified, just
            # ignore it
            if self.version is not None:
                ret += os.system("git fetch")
                ret += os.system("git checkout %s" % (self.version))

                cmd = 'git log -n 1 --format=format:%H'.split()
                output = subprocess.check_output(cmd)
                if output.decode('utf-8') != self.version:
                    ret += os.system("git pull")

            os.chdir(cwd)

        step = self.steps.get('checkout')
        if step is not None:
            name = '%s:%s:checkout' % (pkg, self.name)
            cmd_group.inc_enqueued()
            cmd = plptools_builder.Builder_command(
                name=name, cmd=step.command, path=self.abs_path,
                env=self.get_env_for_command(pkg))
            cmd.set_callback(callback=cmd_group.dec_enqueued, command=cmd)
            builder.enqueue(cmd=cmd)

        return ret


class PkgDep(object):

    def __init__(self, pkg, restrict=None):
        self.pkg = pkg
        self.restrict = restrict

    def is_active(self, configs):
        if self.restrict is None:
            return True
        else:
            for config in configs:
                if eval(self.restrict):
                    return True
            return False


class Package(object):

    def __init__(self, name, path=None, modules=[], groups=[], build_deps=[],
                 exec_deps=[], artifact=True, restrict=None, env={},
                 sourceme=[], distrib_dep=True):
        self.branch = None
        self.name = name
        self.distrib_dep = distrib_dep
        self.path = 'pkg/%s' % (path)
        self.groups = collections.OrderedDict()
        self.build_deps = build_deps
        self.exec_deps = exec_deps
        self.build_deps_pkg = []
        for dep in build_deps:
            self.build_deps_pkg.append(dep.pkg)
        self.exec_deps_pkg = []
        for dep in exec_deps:
            self.exec_deps_pkg.append(dep.pkg)
        self.active = False
        self.buildable = False
        self.artifact = artifact
        self.restrict = restrict
        self.env = env
        self.sourceme = sourceme

        self.tagVersion = None
        self.version = 'dev'

        self.root_dir = None
        self.build_desc = None
        self.modules = collections.OrderedDict()
        for module in modules:
            self.modules[module.name] = module

        for group in groups:
            self.groups[group.name] = group
            for module in group.modules:
                if module not in self.modules:
                    self.modules[module.name] = module

    def __str__(self):
        return self.name

    def get_build_dir(self):
        return self.build_dir

    def get_install_dir(self):
        return self.get_absolute_path()

    def set_project(self, project, pobjs, branch=None):
        self.project = project
        self.pobjs = pobjs
        self.branch = branch
        for module in self.modules.values():
            module.set_pkg(self)

        self.build_dir = os.path.join(eval(self.project.config.get('root_build_dir')), self.name)

    def set_root_dir(self, path):
        self.root_dir = path
        self.abs_path = os.path.join(path, self.path)
        for module in self.modules.values():
            module.set_root_dir(path)

    def get_modules(self):
        return self.modules.values()

    def is_active(self):
        return self.active

    def set_active(self):
        self.active = True

    def is_buildable(self):
        return self.buildable

    def set_buildable(self):
        self.buildable

    def get_artifact_path(self, distrib):
        if self.distrib_dep:
            return ('%s/pulp/%s/mainstream/%s/0' %
                (distrib, self.name, self.get_version(no_tag=True)))
        else:
            return ('pulp/%s/mainstream/%s/0' %
                (self.name, self.get_version(no_tag=True)))

    def get_artifact(self, project, force=False):
        if not self.artifact:
            return

        print ('Get artifact for ' + self.name)

        if not os.path.exists(self.get_absolute_path()) or force:
          if os.path.exists(self.get_absolute_path()): 
              print ('Specified --force option, removing directory: ' + self.get_absolute_path())
              if os.path.isdir(self.get_absolute_path()) and not os.path.islink(self.get_absolute_path()): shutil.rmtree(self.get_absolute_path())
              else: os.unlink(self.get_absolute_path())
          return project.artifactory.get_artifact(self.name, self.get_absolute_path(), self.get_rel_path(), self.get_artifact_path(project.distrib), real_rel_path=self.get_real_rel_path())
        else:
          print ('\033[1m' + '%s' % (self.name) + '\033[0m' + ': Already at %s, remove directory to get it again' % (self.get_absolute_path()))

        return False
        
    def __find_active_config(self, configs):
        if self.restrict == None: return True

        for config in configs:
          if eval(self.restrict): return True

        return False


    def check_configs(self, configs):
        self.active = self.__find_active_config(configs)
        self.active_modules = collections.OrderedDict()
        for module in self.modules.values():
            module.check_configs(configs)
            if module.is_active(): self.active_modules[module.name] = module


    def get_exec_deps(self, only_pkg=True):
        if only_pkg: return self.exec_deps_pkg
        else: return self.exec_deps

    def get_build_deps(self, only_pkg=True):
        if only_pkg: return self.build_deps_pkg
        else: return self.build_deps

    def get_all_exec_deps(self, only_pkg=True):
        deps = []
        pkg_list = self.exec_deps_pkg if only_pkg else self.exec_deps
        for dep in pkg_list:
            list(set(deps).union(dep.get_all_exec_deps()))
        return deps

    def get_exec_deps_for_configs(self, configs):
        results = []
        for dep in self.exec_deps_pkg:
            if dep.__find_active_config(configs):
                results.append(dep)
                results += dep.get_exec_deps_for_configs(configs)
        return results


    def get_all_build_deps(self, only_pkg=True):
        deps = []
        pkg_list = self.build_deps_pkg if only_pkg else self.build_deps
        for dep in pkg_list:
            deps = list(set(deps).union([dep] + dep.get_all_exec_deps()))
        return deps

    def get_dependencies(self, project, configs, dep_list, alreadyGot=[],
                         force=False):

        for dep_obj in dep_list:
            if not dep_obj.is_active(configs):
                continue
            dep = dep_obj.pkg
            dep.get_exec_dependencies(
              project=project, configs=configs,
              alreadyGot=alreadyGot, force=force)
            dep_is_missing = dep.is_active() and not dep.is_buildable() \
                and dep not in alreadyGot
            if dep_is_missing:
                alreadyGot.append(dep)
                if dep.get_artifact(project, force=force):
                    dep.env_gen()

    def get_exec_dependencies(self, project, configs, alreadyGot=[],
                              force=False):
        self.get_dependencies(
            project=project, configs=configs,
            dep_list=self.get_exec_deps(only_pkg=False),
            alreadyGot=alreadyGot, force=force)

    def get_build_dependencies(self, project, configs, alreadyGot=[],
                               force=False):
        self.get_dependencies(
            project=project, configs=configs,
            dep_list=self.get_build_deps(only_pkg=False),
            alreadyGot=alreadyGot, force=force)

        for dep in self.get_exec_deps():
            dep.get_exec_dependencies(
                project=project, configs=configs, alreadyGot=alreadyGot,
                force=force)

    # A package is normally identified by the version given in the user project configuratio.
    # However, this can be overriden by the package hash version in case the package version is 'dev'
    # or by the tag version, if the package is being tagged
    def get_version(self, get_hash=True, no_dev_path=False, no_tag=False):
        if not no_tag and self.tagVersion != None: return self.tagVersion

        if self.version == 'dev' and no_dev_path:
            return self.project.get_version()

        if self.version == 'dev' and get_hash: return self.get_hash()
        elif self.version == None: return 'dev'
        else: return self.version
            
    def get_env(self, dict):
        for key, value in self.env.items():
          dict[key] = eval(value)

        for dep in self.get_build_deps():
          if not dep.is_active(): continue
          dep.get_env(dict)

    def get_hash_str(self):
          return self.project.get_version()
          hashStr = ''
          hashStr += '%s-%s' % (self.name, self.version)
          hashStr += '|top-%s' % (self.project.get_version())
          for dep in self.get_build_deps():
              hashStr += '|dep-%s-%s' % (dep.name, dep.get_hash())
          for moduleName, module in self.modules.items():
              hashStr += '|mod-%s-%s' % (module.name, module.get_version())

          return hashStr

    def get_hash(self):
        return self.project.get_version()
        m = hashlib.sha1()
        m.update(self.get_hash_str().encode('utf-8'))
        return m.hexdigest()
            

    def get_path(self, no_dev_path=False):
        # Don't get the hash as we want the package to be installed in the same folder whatever the hash in case the package version is 'dev'
        return os.path.join(self.path, self.get_version(get_hash=False, no_dev_path=no_dev_path))

    def get_tag_path(self, tag_version=None):
        if tag_version != None: version = tag_version
        elif self.tagVersion != None: version = self.tagVersion
        elif self.version is not None and self.version != 'dev':
            version = self.version
        else:
            version = self.project.get_version()

        return os.path.join(self.path, version)

    def get_absolute_path(self):
        return os.path.realpath(os.path.join(get_root_dir(), self.get_path()))

    def get_rel_path(self):
        # Don't get the hash as we want the package to be installed in the same folder whatever the hash in case the package version is 'dev'
        return os.path.join(self.name, self.get_version(get_hash=False))

    def get_real_rel_path(self):
        # Don't get the hash as we want the package to be installed in the same folder whatever the hash in case the package version is 'dev'
        return os.path.join(self.name, self.get_version(get_hash=True))

    def __get_ordered_modules(self, modules):

        for index in range(0, len(modules)):
          while True:
            module = self.modules.get(modules[index])
            moved = False
            if module.deps != None:
              for dep in module.deps:
                if not dep.name in modules: continue
                dep_index = modules.index(dep.name)
                if dep_index > index:
                  modules.pop(index)
                  modules.insert(dep_index+1, module.name)
                  moved = True
                  break

            if not moved: break

        return modules

    def __get_modules_from_groups(self, groups, modules):
        """
        Return the list of modules contained in the specified groups and contained by this package 
        """
        if modules == None: modules = []
        else: modules = list(set(modules).intersection(self.modules.keys()))
        for group in groups:
          if not group in self.groups.keys(): continue
          modules = list(set(modules).union(self.groups.get(group).modules_names))
        return modules

    def get_default_groups_and_modules(self, groups, modules):
        if len(groups) == 0 and len(modules) == 0: 
          if len(self.groups) != 0: groups = self.groups
          else: modules = self.modules
        return groups, modules


    def checkout(self, builder, cmd_group, groups=None, modules=None):
        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_modules_from_groups(groups, modules)
        for module_name in modules:
          module = self.modules.get(module_name)
          if not module.is_active(): continue
          if module.checkout(self, builder, cmd_group) != 0:
            return -1

        return 0

    def exec_cmd(self, cmd, groups=None, modules=None):
        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_modules_from_groups(groups, modules)
        for module_name in modules:
          module = self.modules.get(module_name)
          if not module.is_active(): continue
          if module.exec_cmd(cmd) != 0:
            return -1

        return 0

    def dump_env_to_file(self, file):

        for line in self.sourceme:
            if line[0] == 'exec_deps':
                for dep in self.get_exec_deps():
                    dep.dump_env_to_file(file)
            elif line[0] == 'property':
                file.add_export(line[1], line[2])
            elif line[0] == 'property_eval':
                file.add_export(line[1], eval(line[2]))
            elif line[0] == 'sourceme':
                file.add_sourceme(line[1], line[2])

    def get_exec_env(self, no_dev_path=False):
        exports = []
        sourceme = []
        for line in self.sourceme:
            if line[0] == 'property':
                exports.append([line[1], line[2]])
            elif line[0] == 'property_eval':
                if line[3] is not None:
                    exports.append([line[1], eval(line[3])])
            elif line[0] == 'sourceme':
                sourceme.append([line[1], line[2]])

        return [exports, sourceme]


    def env_gen(self):
        sourceme_file = Sourceme(path=self.get_absolute_path(),
                                 name='sourceme')

        self.dump_env_to_file(sourceme_file)

        sourceme_file.gen()

    def env_get(self):
        env = []
        for deps in self.get_build_deps() + self.get_exec_deps():
          env += deps.env_get()
        if len(self.sourceme) != 0:
          env.append(os.path.join(self.get_absolute_path(), 'sourceme'))
          
        return env

    def deploy(self, project, artifactory):
        if artifactory.deploy_artifact(name=self.name, path=self.get_artifact_path(project.distrib), rel_path=self.get_rel_path(), dir_path=self.get_absolute_path(), real_rel_path=self.get_real_rel_path()):
          old_version = self.version
          self.version = self.get_version(get_hash=True)
          self.env_gen()
          self.version = old_version

    def update(self, groups, modules):
        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_ordered_modules(self.__get_modules_from_groups(groups, modules))
        for name in modules:
          self.modules[name].update()

    def get_testsets(self, groups, modules):
        testsets = []
        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_ordered_modules(self.__get_modules_from_groups(groups, modules))
        for name in modules:
          testsets += self.modules[name].get_testsets()
        return testsets

    def build_callback(self, cmd_group, top_cmd_group):
        self.build_desc.set_end_date(datetime.datetime.today())
        if cmd_group.status:
            self.build_desc.set_status("success")
        else:
            self.build_desc.set_status("failure")
        self.db_build = self.build_desc.commit()
        top_cmd_group.dec_enqueued()

    def get_build(self, configs):
        deps = []
        for dep in self.get_all_build_deps():
            deps.append(dep.get_artifact_path(self.project.distrib))


        configs_name = []
        if configs != None:
          for config in configs:
            if config.get_name() is not None:
              configs_name.append(config.get_name())


        self.build_desc = Package_Build(
            self.pobjs, self.name, config=' '.join(configs_name), version=self.get_version(get_hash=True),
            artifact=self.get_artifact_path(self.project.distrib), deps=deps, branch=self.branch,
            commit_version=self.project.get_commit(), env=self.project.env)
        self.build_desc.set_start_date(datetime.datetime.today())
        self.build_desc.set_status("started")
        self.db_build = self.build_desc.commit()

    def end_tests(self, runner, top_end_tests):
        runner.plpobjects.dumpTestsToConsole()
        reportPath = os.getcwd()
        runner.plpobjects.dumpTestsToJunit(reportPath + '/junit-reports')
        self.build_desc.set_nb_tests(runner.plpobjects.getNbSuccess())
        self.build_desc.set_nb_passed(runner.plpobjects.getNbTests())
        self.db_build = self.build_desc.commit()
        runner.stop()
        #top_end_tests()

    def run_tests(self, runner, top_end_tests, args):
        runner.runTests(tests=args.testList, callback=self.end_tests, runner=runner, top_end_tests=top_end_tests)

    def test(self, top_end_tests, configs, args=None):
        self.get_build(configs)

        build_id = None
        if self.db_build is not None:
            build_id = self.db_build.id

        runner = TestRunner(nbThreads=args.threads, stdout=args.stdout,
            maxOutputLen=args.maxOutputLen, maxTimeout=args.maxTimeout,
            pobjs=self.pobjs, build=build_id)
        runner.addTestset('testset.cfg')
        for config in configs:
          runner.addConfig(config)
        runner.start(self.run_tests, runner, top_end_tests, args)

        return 0

    def sync(self, groups, modules):

        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_ordered_modules(
            self.__get_modules_from_groups(groups, modules))
        for name in modules:
            module = self.modules[name]
            if not module.is_active(): continue
            module.sync()


    def build(self, builder, cmd_group, configs, groups, modules, steps):

        self.get_build(configs)

        cmd_group.inc_enqueued()
        pkg_cmd_group = Cmd_group()
        pkg_cmd_group.set_callback(self.build_callback, pkg_cmd_group, cmd_group)

        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_ordered_modules(
            self.__get_modules_from_groups(groups, modules))
        for name in modules:
            module = self.modules[name]
            if not module.is_active(): continue
            module.enqueue_steps(builder, self, pkg_cmd_group, configs=configs,
                                 steps=steps)

        if len(modules) != 0:
            self.env_gen()

        pkg_cmd_group.set_finished()

    def downloader(self, configs, version):

        artifact_version = version
        if artifact_version is None:
            artifact_version = self.get_version()

        path = 'get-{pkg}-{version}-{distrib}.py'.format(
            pkg=self.name, version=artifact_version,
            distrib=self.project.distrib
        )
        #print ('Generating downloader for package {pkg} at: {path}'.format(
        #    pkg=self.name, path=path
        #))
        print ('{path}'.format(
            path=path
        ))
        downloader = plpdownloader.Downloader(self, configs, self.project.distrib, version)
        with open(path, 'w') as file:
            downloader.gen(file)
        return 0

    def clean(self, builder, cmd_group, configs, groups, modules, steps):
        groups, modules = self.get_default_groups_and_modules(groups, modules)
        modules = self.__get_ordered_modules(self.__get_modules_from_groups(groups, modules))
        for name in modules:
          module = self.modules[name]
          module.enqueue_steps(builder, self, cmd_group, configs=configs, steps=steps)



    def fullclean(self, packages=None):

        print ('Removing package build directory: ' + self.get_build_dir())
        print ('Removing package install directory: ' + self.get_install_dir())

        shutil.rmtree(self.get_build_dir(), ignore_errors=True)
        shutil.rmtree(self.get_install_dir(), ignore_errors=True)

        return 0

class Project(object):

    def __init__(self, path=None, tools_path=None, configName='project.cfg',
                 versionsName='versions.cfg', packages=None, force=False,
                 distrib=None, nb_threads=1, cmd_callback=None, log=None,
                 stdout=False, stdout_cached=False, db=False, db_info=None,
                 import_tests=False, branch=None, db_env=[], commit=None):

        if db_info is not None and os.path.exists(db_info):
            os.remove(db_info)

        self.pobjs = PulpObjects(
            db_import=db, import_tests=import_tests,
            db_info=db_info, db_env=db_env
        )

        if path is None:
            path = get_root_dir()
        self.path = path
        self.tools_path = tools_path
        self.force = force
        self.configSet = None
        self.config = collections.OrderedDict()
        self.cmd_callback = cmd_callback
        self.version = None
        self.branch = branch
        self.env = db_env
        self.commit = commit

        self.__find_distrib(distrib)

        # Load the user configuration, this will create the hierarchy of
        # modules and packaes
        self.__load_config(path=os.path.join(self.path, configName))
        self.version_file_path = os.path.join(self.path, versionsName)
        self.__load_config(path=self.version_file_path)

        # The user config should now have configured which system
        # configurations must be loaded
        self.__load_system_configs(configs=self.config.get('system_configs'))

        # Initialize packages, this will mark them as active or buildable
        # depending on the options
        self.__init_packages(
            packageList=self.config.get('packages'),
            buildablePackages=packages,
            pkg_versions=self.config.get('package_versions'),
            module_versions=self.config.get('module_versions'))

        # Get the artifact cache
        self.artifactory = plpartifactory.ArtifactRepositorySetCached(
            self.config.get('artifact_cache'),
            self.config.get('artifactory_servers'))

        self.builder = plptools_builder.Builder(
            nb_threads=nb_threads, log=log, stdout=stdout,
            stdout_cached=stdout_cached)

    def get_commit(self):
        if self.commit is not None:
            return self.commit
        else:
            return self.get_git_version()

    def get_git_version(self):
        return get_git_version(self.path)

    def get_version(self):
        if self.version is None:
            self.version = self.get_git_version()
        return self.version

    def start(self, callback=None, *args, **kwargs):

        if callback is not None:
            reactor.callWhenRunning(callback, *args, **kwargs)

        reactor.run()

    def __find_distrib(self, distrib):
        if distrib is None:
            distrib = os.environ.get('PULP_ARTIFACTORY_DISTRIB')

        if distrib is None:
            dist = subprocess.Popen(
                "lsb_release -a | grep Distributor | awk '{print $3}'",
                shell=True, stdout=subprocess.PIPE, universal_newlines=True
            ).stdout.read().strip()
            version = subprocess.Popen(
                "lsb_release -a | grep Release | awk '{print $2}'",
                shell=True, stdout=subprocess.PIPE, universal_newlines=True
            ).stdout.read().strip().split('.')[0]
            distrib = '%s_%s' % (dist, version)

            # Map all LinuxMint and Ubuntu < 16 versions to Ubuntu 14
            if distrib.find('LinuxMint') != -1 or distrib.find('Ubuntu') != -1:
                if dist != 'Ubuntu' or int(version.split('.')[0]) < 16:
                    distrib = 'Ubuntu_14'
                    version = '14'
        self.distrib = distrib

    def __load_config(self, path):

        try:
            module = imp.load_source('project', path)
        except Exception:
            raise Exception(
                bcolors.FAIL + 'Unable to open project configuration file: ' +
                path + bcolors.ENDC
            )

        try:
            self.config.update(module.ProjectConfig)
        except Exception:
            raise Exception(
                bcolors.FAIL +
                'Project configuration must define the ProjectConfig ' +
                'variable: ' +
                path + bcolors.ENDC)

    def get_package(self, name, check=True):
        pkg = self.packages.get(name)
        if pkg is None:
            raise Exception("Unknown package: " + name)
        else:
            return pkg

    def __init_packages(self, packageList, buildablePackages, pkg_versions,
                        module_versions):

        if packageList is None:
            packageList = []

        self.packages = collections.OrderedDict()
        self.modules = collections.OrderedDict()
        for pkg in packageList:
            self.packages[pkg.name] = pkg
            for module in pkg.get_modules():
                if self.modules.get(module.name) is None:
                    self.modules[module.name] = module

        self.buildablePackages = collections.OrderedDict()
        if buildablePackages is not None:
            for pkg in buildablePackages:
                self.get_package(pkg).set_buildable()
                self.buildablePackages[pkg] = self.packages.get(pkg)
        else:
            for pkg in self.packages.values():
                pkg.set_buildable()
                self.buildablePackages[pkg.name] = pkg

        for pkg in self.packages.values():
            pkg.check_configs(self.configs)

        if pkg_versions is not None:
            for key, value in pkg_versions.items():
                self.packages.get(key).version = value

        if module_versions is not None:
            for key, value in module_versions.items():
                if self.modules.get(key) is not None:
                    self.modules.get(key).version = value

        for pkg in self.packages.values():
            pkg.set_root_dir(self.path)
            pkg.set_project(self, self.pobjs, self.branch)

    def __load_system_configs(self, configs):
        self.configs = plpconf.get_configs_from_env()

    def get_buildable_packages(self, packages=None):
        """
        Return the list of packages which must be built (the other must be
        downloaded)
        In case packages is specified, this return the intersection of
        buildables and specified packages otherwise just buildables are
        returned.
        """
        if packages is None:
            return self.buildablePackages.values()
        else:
            pkgList = []
            for pkg in packages:
                pkgList.append(self.packages.get(pkg))
            return set(self.buildablePackages.values()).intersection(pkgList)

    def get_dependencies(self, packages=None):
        for pkg in self.get_buildable_packages(packages=packages):
            pkg.get_build_dependencies(
                project=self, configs=self.configs, force=self.force)
        reactor.callLater(0, self.cmd_callback)
        return 0

    def get_exec_dependencies(self, packages=None):
        for pkg in self.get_buildable_packages(packages=packages):
            pkg.get_exec_dependencies(
                project=self, configs=self.configs, force=self.force)
        reactor.callLater(0, self.cmd_callback)
        return 0

    def checkout(self, packages=None, groups=None, modules=None , deps=False):
        cmd_group = Cmd_group(self.cmd_callback)
        built_list = []
        for pkg in self.get_buildable_packages(packages=packages):
            if deps:
                for dep in pkg.get_all_build_deps() + pkg.get_all_exec_deps():
                    if not dep in built_list and dep.is_active():
                        built_list.append(dep)
                        if dep.checkout(self.builder, cmd_group, groups=groups, modules=modules) != 0:
                            return -1

            if not pkg in built_list:
                if pkg.checkout(self.builder, cmd_group, groups=groups, modules=modules) != 0:
                    return -1
        cmd_group.set_finished()

        return 0

    def exec_cmd(self, cmd, packages=None, groups=None, modules=None):
        cmd_group = Cmd_group(self.cmd_callback)
        for pkg in self.get_buildable_packages(packages=packages):
            if pkg.exec_cmd(cmd, groups=groups, modules=modules) != 0:
                return -1
        cmd_group.set_finished()
        return 0


    def end_tests(self):
        self.nb_tests -= 1
        if self.nb_tests == 0:
            runner.stop()

    def run_tests(self, runner, args):
        runner.runTests(tests=args.testList, callback=self.end_tests, runner=runner)

    def test(self, packages=None, args=None):
        self.nb_tests = 0
        for pkg in self.get_buildable_packages(packages=packages):
            self.nb_tests += 1
            self.__testset(packages=[pkg.name])
            pkg.test(self.end_tests, self.configs, args=args)

        return 0

    def env_gen(self, packages=None):
        envs = []
        for pkg in self.get_buildable_packages(packages=packages):
            envs += pkg.env_get()

        defs = []
        config_string = os.environ.get('PULP_CURRENT_CONFIG')
        if config_string is not None:
            defs.append(['PULP_CURRENT_CONFIG', config_string])
        config_string_args = os.environ.get('PULP_CURRENT_CONFIG_ARGS')
        if config_string_args is not None:
            defs.append(['PULP_CURRENT_CONFIG_ARGS', config_string_args])

        with open('sourceme.sh', 'w') as file:
            for env_var in defs:
                file.write('export %s=%s\n' % (env_var[0], env_var[1]))
            for env in envs:
                file.write('if [ -e %s.sh ]; then source %s.sh; fi\n' % (env, env))

        with open('sourceme.csh', 'w') as file:
            for env_var in defs:
                file.write('setenv %s %s\n' % (env_var[0], env_var[1]))
            for env in envs:
                file.write('if ( -e %s.csh ) source %s.csh\n' % (env, env))

        self.cmd_callback()
        return 0

    def deploy(self, packages=None):
        for pkg in self.get_buildable_packages(packages=packages):
            pkg.deploy(project=self, artifactory=self.artifactory)
        reactor.callLater(0, self.cmd_callback)
        return 0

    def update(self, packages=None, groups=None, modules=None):
        for pkg in self.get_buildable_packages(packages=packages):
            pkg.update(groups=groups, modules=modules)
        reactor.callLater(0, self.cmd_callback)
        return 0

    def __testset(self, packages=None, groups=[], modules=[]):
        testsets = []
        for pkg in self.get_buildable_packages(packages=packages):
            testsets += pkg.get_testsets(groups=groups, modules=modules)

            with open('testset.cfg', 'w') as file:
                testsets_list = []
                for testset in testsets:
                    testsets_list.append('"%s"' % testset[1])
                file.write(testset_file_pattern %
                    (',\n    '.join(testsets_list)))

    def testset(self, packages=None, groups=None, modules=None):
        self.__testset(packages=packages, groups=groups, modules=modules)
        reactor.callLater(0, self.cmd_callback)
        return 0

    def build(self, packages=None, groups=None, modules=None, deps=False):
        cmd_group = Cmd_group(self.cmd_callback)

        steps = None
        if self.config.get('build_steps') is not None:
            steps = self.config.get('build_steps').get('build')

        built_list = []

        for pkg in self.get_buildable_packages(packages=packages):

            if deps:
                for dep in pkg.get_all_build_deps() + pkg.get_all_exec_deps():
                    if not dep in built_list and dep.is_active():
                        built_list.append(dep)

                        dep.build(self.builder, cmd_group, configs=self.configs,
                                  groups=groups, modules=modules, steps=steps)

            if not pkg in built_list:
                built_list.append(pkg)

                pkg.build(self.builder, cmd_group, configs=self.configs,
                          groups=groups, modules=modules, steps=steps)

        cmd_group.set_finished()

        return 0

    def sync(self, packages=None, groups=None, modules=None):
        for pkg in self.get_buildable_packages(packages=packages):

                pkg.sync(groups=groups, modules=modules)

        self.cmd_callback()

        return 0

    def downloader(self, packages=None, version=None):

        buildable_pkg = self.get_buildable_packages(
            packages=packages
        )
        for pkg in buildable_pkg:
            if pkg.downloader(configs=self.configs, version=version) != 0:
                return -1

        self.cmd_callback()

        return 0



    def fullclean(self, packages=None):

        for pkg in self.get_buildable_packages(packages=packages):
            if pkg.fullclean():
                return -1

        self.cmd_callback()

        return 0



    def clean(self, packages=None, groups=None, modules=None, deps=False):

        cmd_group = Cmd_group(self.cmd_callback)

        steps = None
        if self.config.get('build_steps') is not None:
            steps = self.config.get('build_steps').get('clean')

        built_list = []

        for pkg in self.get_buildable_packages(packages=packages):

            if deps:
                for dep in pkg.get_all_build_deps() + pkg.get_all_exec_deps():
                    if not dep in built_list and dep.is_active():
                        built_list.append(dep)

                        dep.clean(self.builder, cmd_group, configs=self.configs,
                                  groups=groups, modules=modules, steps=steps)

            if not pkg in built_list:
                pkg.clean(self.builder, cmd_group, configs=self.configs,
                          groups=groups, modules=modules, steps=steps)

        cmd_group.set_finished()

        return 0

    def gen_version_file(self):

        packages = []
        modules = []

        for pkg in self.packages.values():
            packages.append("'%s': '%s'" % (pkg.name, pkg.version))

            for module in pkg.modules.values():
                modules.append("'%s': '%s'" % (module.name, module.version))

        with open(self.version_file_path, 'w') as file:
            file.write(version_file_pattern % (',\n  '.join(packages), ',\n  '.join(modules)))

    def versions(self):
        self.gen_version_file()
        reactor.callLater(0, self.cmd_callback)
        return 0

    def stop(self, status):
        self.builder.stop(status)

    def get_status(self):
        return self.builder.status

    def dump_db(self, packages, builds=False, tests=False, branches=[]):
        self.pobjs.dump(builds=builds, tests=tests, branches=branches)
        return 0

    def drop_all(self):
        self.pobjs.drop_all()
        return 0

    def dump_db_tests(self, packages, branches=[], xls=None, config=None,
                      mail=None, url=None, author_email=None, build=None,
                      env=[]):
        self.pobjs.dump_tests(branches=branches, xls=xls, user_config=config,
                              mail=mail, url=url, author_email=author_email,
                              build=build, env=env)
        return 0

    def check_reg(self, packages, branches=[], config=None, build=None,
                  env=[]):
        return self.pobjs.check_reg(
            branches=branches, user_config=config, test_build=build, env=env)

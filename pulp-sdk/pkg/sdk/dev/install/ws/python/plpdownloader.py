
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

downloader_pattern = """#!/usr/bin/env python3

# This file has been auto-generated and can be used for downloading the SDK it has
# been generated for.

import os
import tarfile
import os.path
import argparse


src="59b44701b6ac8390a97936cbd049256fc2917212"

artefacts=[
  {artefacts}
]

exports=[
  {exports}
]

sourceme=[
  {sourceme}
]

pkg=["{pkg}", "{pkg_version}"]

parser = argparse.ArgumentParser(description='PULP downloader')

parser.add_argument('command', metavar='CMD', type=str, nargs='*',
                   help='a command to be execute')

parser.add_argument("--path", dest="path", default=None, help="Specify path where to install packages and sources")

args = parser.parse_args()

if len(args.command ) == 0:
    args.command = ['get']

if args.path != None:
    path = os.path.expanduser(args.path)
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

for command in args.command:

    if command == 'get' or command == 'download':

        dir = os.getcwd()

        if command == 'get':
            if not os.path.exists('pkg'): os.makedirs('pkg')

            os.chdir('pkg')

        for artefactDesc in artefacts:
            artefact = artefactDesc[0]
            path = os.path.join(dir, artefactDesc[1])
            urlList = artefact.split('/')
            fileName = urlList[len(urlList)-1]

            if command == 'download' or not os.path.exists(path):

                if os.path.exists(fileName):
                    os.remove(fileName)

                if os.system('wget --no-check-certificate %s' % (artefact)) != 0:
                    exit(-1)

                if command == 'get':
                    os.makedirs(path)
                    t = tarfile.open(os.path.basename(artefact), 'r')
                    t.extractall(path)
                    os.remove(os.path.basename(artefact))

        os.chdir(dir)

    if command == 'get' or command == 'download' or command == 'env':

        if not os.path.exists('env'):
            os.makedirs('env')

        filePath = 'env/env-%s-%s.sh' % (pkg[0], pkg[1])
        with open(filePath, 'w') as envFile:
            #envFile.write('export PULP_ENV_FILE_PATH=%s\\n' % os.path.join(os.getcwd(), filePath))
            #envFile.write('export PULP_SDK_SRC_PATH=%s\\n' % os.environ.get("PULP_SDK_SRC_PATH"))
            envFile.write('export %s=%s\\n' % ('PULP_PROJECT_HOME', os.getcwd()))
            for export in exports:
                envFile.write('export %s=%s\\n' % (export[0], export[1].replace('$PULP_PROJECT_HOME', os.getcwd())))
            for env in sourceme:
                envFile.write('source %s\\n' % (env[0].replace('$PULP_PROJECT_HOME', os.getcwd())))
            #envFile.write('if [ -e "$PULP_SDK_SRC_PATH/init.sh" ]; then source $PULP_SDK_SRC_PATH/init.sh; fi')

        #filePath = 'env/env-%s-%s.csh' % (pkg[0], pkg[1])
        #with open(filePath, 'w') as envFile:
        #    envFile.write('setenv PULP_ENV_FILE_PATH %s\\n' % os.path.join(os.getcwd(), filePath))
        #    envFile.write('setenv PULP_SDK_SRC_PATH %s\\n' % os.environ.get("PULP_SDK_SRC_PATH"))
        #    for env in envFileStrCsh:
        #        envFile.write('%s\\n' % (env.replace('@PULP_PKG_HOME@', os.getcwd())))
        #    envFile.write('if ( -e "$PULP_SDK_SRC_PATH/init.sh" ) then source $PULP_SDK_SRC_PATH/init.sh; endif')

    if command == 'src':

        if os.path.exists('.git'):
            os.system('git checkout %s' % (src))
        else:
            os.system('git init .')
            os.system('git remote add -t \* -f origin git@kesch.ee.ethz.ch:pulp-sw/pulp_pipeline.git')
            os.system('git checkout %s' % (src))

"""

class Downloader(object):

    def __init__(self, pkg, configs, distrib, version):
        self.pkg = pkg
        self.configs = configs
        self.distrib = distrib
        self.version = version
        if version is not None:
            self.pkg.tagVersion = version

    def gen(self, file):

        artifacts = []
        exports = []
        sourceme = []

        if len(self.configs)  == 0:
            packages = [self.pkg] + self.pkg.get_exec_deps()
        else:
            packages = [self.pkg] + self.pkg.get_exec_deps_for_configs(self.configs)


        for dep in packages:

            if not dep.artifact:
                continue

            artifact_path = self.pkg.project.artifactory.get_artifact_path(
                dep.get_artifact_path(self.distrib))

            for path in self.pkg.project.artifactory.get_artifact_path(
                dep.get_artifact_path(self.distrib)):

                artifact_info = '["%s", "%s"]' % (path, dep.get_tag_path())
                artifacts.append(artifact_info)

        for pkg in packages:
            result = pkg.get_exec_env(no_dev_path=True)
            for key, value in result[0]:
                exports.append('["%s", "%s"]' % (key, value))
            for key, value in result[1]:
                sourceme.append('["%s", "%s"]' % (key, value))

        file.write(downloader_pattern.format(
            artefacts=',\n  '.join(artifacts),
            exports=',\n  '.join(exports),
            sourceme=',\n  '.join(sourceme),
            pkg=self.pkg.name,
            pkg_version=self.pkg.get_version()
        ))

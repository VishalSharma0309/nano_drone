
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


import os.path
from artifactory import ArtifactoryPath
import tarfile
import subprocess
import os
#import MySQLdb as mdb
import time
import logging
import sys
import datetime
import tempfile
import shutil

class ArtifactRepository(object):

  def __init__(self, name, server, ssl_verify=True):
    self.ssl_verify = ssl_verify
    self.name = name
    self.server = server

  def get_path(self, path):
    return ArtifactoryPath(self.server + '/' + path + "/", auth=self.get_auth(), verify=self.ssl_verify)
          
  def get_auth(self):
    passStr = os.environ.get("PULP_ARTIFACTORY_USER")
    if passStr == None: raise Exception('PULP_ARTIFACTORY_USER must be set with proper user/password information')
    user, passwd = passStr.split(':')
    return (user, passwd)

  def deploy_artifact(self, name, path, dir_path=None, file_path=None):

    if dir_path != None:
      with tempfile.TemporaryDirectory() as tmpdirname:
        cwd = os.getcwd()
        os.chdir(dir_path)
        artefact_name = name + '.tar.bz2'
        file_path = os.path.join(tmpdirname, artefact_name)
        print ("Creating tarball at %s" % (file_path))
        t = tarfile.open(file_path, 'w:bz2')
        t.add('.')
        t.close()
        os.chdir(cwd)

        artefact_path = path + '/' + artefact_name
        print ("Deploying %s to %s" % (file_path, self.get_path(artefact_path)))
        self.get_path(artefact_path).deploy_file(file_path)

    else:
      print ("Deploying %s to %s" % (file_path, self.get_path(path)))
      self.get_path(path).deploy_file(file_path)



  def get_artifact(self, path, pkg_path, unpack):

    for p in self.get_path(path):

      outPath = os.path.join(pkg_path, os.path.basename(str(p)))
      if not os.path.exists(os.path.dirname(outPath)):
          os.makedirs(os.path.dirname(outPath))
      out = open(outPath, 'wb')
      fd = p.open()
      out.write(fd.read())
      out.close()
      if unpack:
          # There is sometime a strange issue with NFS, wait a bit until the file is properly closed
          time.sleep(1)
          if outPath.find('manifest.ini') != -1: continue
          logging.debug("Unpacking file (path: %s)" % (outPath))
          t = tarfile.open(outPath, 'r')
          t.extractall(pkg_path)
          os.remove(outPath)
          t.close()

  def get_artifact_path(self, path):

    return self.get_path(path)








# This class is proxy for several artifactory servers
# It allows automatically duplicating artifacts over several artifactory servers
class ArtifactRepositorySet(object):

  def __init__(self, descs=[]):
    servers = []
    default = os.environ.get('PULP_ARTIFACTORY_SERVER')
    for desc in descs:
      server = ArtifactRepository(name=desc.name, server=desc.url, ssl_verify=desc.ssl_verify)
      if default == desc.name: servers.insert(0, server)
      else: servers.append(server)

    self.servers = servers
      

  def deploy_artifact(self, name, path, dir_path=None, file_path=None):
    print ("Pushing artifact (name: %s, path: %s, dir_path: %s, file_path: %s)" % (name, path, dir_path, file_path))

    for server in self.servers:
        try:
            print ("Trying to push artifact to this server: %s" % server.server)
            server.deploy_artifact(name, path, dir_path, file_path)
            return
        except:
            print ("Failed to push artifact to this server (%s), skipping it: " % server.server, sys.exc_info()[1])


  def get_artifact(self, path, pkg_path, unpack):
    print ("Getting artifact (path: %s, unpack: %s)" % (path, unpack))

    for server in self.servers:
        try:
            print ("Trying to get artifact from this server: %s" % server.server)
            server.get_artifact(path, pkg_path, unpack)
            return True
        except:
            print ("Failed to get artifact in this server (%s), skipping it: " % server.server, sys.exc_info()[1])

    raise Exception("Didn't manage to get artifact from any artifactory")

  def get_artifact_path(self, path):

    for server in self.servers:
        try:
            return server.get_artifact_path(path)
        except:
            pass

    return None



class ArtifactRepositorySetCached(object):

  def __init__(self, path, servers, distrib=None):
    super(ArtifactRepositorySetCached, self).__init__()

    rCachePath = os.environ.get('PULP_ARTIFACT_RCACHE')
    if rCachePath == None: rCachePath = path
    self.rPath = rCachePath
    self.wPath = os.environ.get('PULP_ARTIFACT_WCACHE')

    self.servers = ArtifactRepositorySet(servers)
  

  def __get_artifact_from_cache(self, name, dst_path, cache_path):

    pkgPath = os.path.join(self.rPath, cache_path)

    if not os.path.exists(pkgPath): return False
    
    try:
      try:
        os.makedirs(os.path.dirname(dst_path))
      except:
        pass

      print ('\033[1m' + '%s' % (name) + '\033[0m' + ': Found in cache at %s, creating symlink at %s' % (pkgPath, dst_path))
      os.symlink(pkgPath, dst_path)
      return True
    except:
      return False

  def __push_artifact_to_cache(self, name, path, rel_path):
    pkgPath = os.path.join(self.wPath, rel_path)

    if os.path.exists(pkgPath):
      print ('Removing cached artifact at %s' % (pkgPath))
      if os.path.isdir(pkgPath) and not os.path.islink(pkgPath): shutil.rmtree(pkgPath)
      else: os.unlink(pkgPath)

    print ('Copying artefact from %s to %s' % (path, pkgPath))
    shutil.copytree(path, pkgPath)


  def deploy_artifact(self, name, path, dir_path=None, rel_path=None, file_path=None, real_rel_path=None):
    written = False
    if self.wPath != None:
      self.__push_artifact_to_cache(name=name, path=dir_path, rel_path=real_rel_path)
      self.__get_artifact_from_cache(name, os.path.join(os.path.dirname(os.path.dirname(dir_path)), real_rel_path), real_rel_path)
      written = True

    self.servers.deploy_artifact(name=name, path=path, dir_path=dir_path, file_path=file_path)

    return written


  def get_artifact(self, name, dst_path, cache_path, artifact_path, real_rel_path=None):

    if self.__get_artifact_from_cache(name, dst_path, real_rel_path): return False

    if self.wPath!= None:
      self.servers.get_artifact(artifact_path, os.path.join(self.wPath, cache_path), True)
      self.__get_artifact_from_cache(name, dst_path, real_rel_path)
    else:
      self.servers.get_artifact(artifact_path, dst_path, True)

    return True

  def get_artifact_path(self, path):

    return self.servers.get_artifact_path(path)

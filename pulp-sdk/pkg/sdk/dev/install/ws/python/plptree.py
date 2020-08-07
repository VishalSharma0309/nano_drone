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
 

import json
import os.path
from collections import OrderedDict
import plpuserconfig
import shlex
import Regmap as regmap
import os
import os.path

class Generic_elem(object):

    def __init__(self, path):
        self.path = path

    def get_tree(self, graph, args=[]):
        if type(graph) == list:
            return List_elem(graph, self.path)
        elif type(graph) == dict or type(graph) == OrderedDict:
            return Tree_elem(graph, self.path, args=args)
        else:
            return Value_elem(graph)

    def get_string(self, root=None):
        if root != None: tree_dict = self.get(root, rec=True)
        else: tree_dict = self.get_dict()
        return json.dumps(tree_dict, indent='  ')


    def dump(self, root=None):
        print (self.get_string(root=root))

    def dump_doc_internal(self, dump_regs=False, dump_regs_fields=False, header=None):
        pass


    def dump_memmap(self, root=None, dump_regs=False, dump_regs_fields=False, header=None):
        if root is not None:
            graph = self.get(root, rec=True)
            tree = self.get_tree(graph)
            tree.dump_memmap(dump_regs=dump_regs, dump_regs_fields=dump_regs_fields, header=header)
            return

        self.dump_doc_internal(dump_regs=dump_regs, dump_regs_fields=dump_regs_fields, header=header)



class List_elem(Generic_elem):
  def __init__(self, graph, path):
    super(List_elem, self).__init__(path)
    self.elems = []
    for elem in graph:
      self.elems.append(self.get_tree(elem))

  def dump_doc_internal(self, dump_regs=False, dump_regs_fields=False, header=None):
      for elem in self.elems:
          elem.dump_doc_internal(dump_regs=dump_regs, dump_regs_fields=dump_regs_fields)

  def browse(self, callback, *kargs, **kwargs):
      for elem in self.elems:
        elem.browse(callback, *kargs, **kwargs)

  def get_elem(self, index):
    return self.elems[index]

  def __delitem__(self, key):
    del self.elems[key]

  def __getitem__(self, key):
    return self.elems[key]

  def __setitem__(self, key, value):
    self.elems[key] = value

  def __call__(self): return self.get_dict(serialize=False)

  def merge(self, tree):
    for i in range(0, len(tree.elems)):
      self.elems.append(tree[i])


  def get_dict(self, serialize=True):
    result = []
    for elem in self.elems:
      result.append(elem.get_dict(serialize=serialize))
    return result

  def set(self, name, value, set_first=False):
    if name == None:
      if set_first:
        self.elems.append(self.get_tree(value))
        return True
      else:
        return False
    else:
      is_set = False
      for elem in self.elems:
        is_set = is_set or elem.set(name, value, set_first=set_first)
      return is_set

  def get(self, name, rec, tree):
    if name == None: 
      if tree: return self
      else: return self.get_dict()
      #else: return self.elems[0].get(None, False, False)
    else:
      for elem in self.elems:
        value = elem.get(name, rec, tree)
        if value != None:
          return value
      return None

  def dump_help(self, name=None, root=None):
      for elem in self.elems:
        elem.dump_help(name=name)


class Value_elem(Generic_elem):
    def __init__(self, graph):
        self.value = graph

    def browse(self, callback, *kargs, **kwargs):
        pass

    def get_int(self):
        if type(self.value) == str:
            return int(self.value, 0)
        else:
            return self.value

    def get_bool(self):
        if type(self.value) == str:
            return self.value == "True" or self.value == "true"
        elif self.value is None:
            return False
        else:
            return self.value

    def merge(self, tree):
        self.value = tree.value

    def __call__(self):
        return self.value

    def get_value(self):
        return self.value

    def get_dict(self, serialize=True):
        if serialize:
            if self.value is None or type(self.value) in [int, str, bool, float]:
                return self.value
            else:
                return str(self.value)
        else:
            return self.value

    def set(self, name, value, set_first=False):
        if name is None:
            self.value = value
            return True
        return False

    def get(self, name, rec, tree):
        if name is None:
            return self.get_dict()
        else:
            return None

    def dump_help(self, name=None, root=None):
        pass



def find_config(config, path=None):
  all_paths = os.environ['PULP_CONFIGS_PATH'].split(':')
  if path is not None:
    all_paths = all_paths + [path]

  for path in all_paths:
    full_path = os.path.join(path, config)
    if os.path.exists(full_path):
      return full_path

  return None



class Tree_elem(Generic_elem):

  def __init__(self, config_dict, path, name=None, args=[], config_name=None):
    super(Tree_elem, self).__init__(path)
    self.props = OrderedDict()
    self.name = name
    self.config_name = config_name

    dump = False

    if 'soc' in config_dict.keys():
      dump = True

    for key, value in config_dict.items():

      if key == 'includes':
        for inc in value:
          tree = get_config_tree_from_file(find_config(inc, self.path), args=args)
          self.merge(tree)

      elif key == 'includes_eval':
        config = self
        for inc in value:
          tree = get_config_tree_from_file(find_config(eval(inc), self.path), args=args)
          self.merge(tree)

      else:

        child_args = []
        for arg in args:
          if arg[0][0] == '*' or arg[0][0] == key:
            child_args.append([arg[0][1:], arg[1]])
          elif (arg[0][0] in ['*', '**']) and (arg[0][1] == key):
            child_args.append([arg[0][2:], arg[1]])
          elif arg[0][0] == '**':
            child_args.append(arg)

        set_prop = False

        for arg in args:
          if (len (arg[0]) == 1 and arg[0][0] == key) or (len(arg[0]) == 2 and arg[0][0] in ['*', '**'] and arg[0][1] == key):
            self.set_prop(key, Value_elem(arg[1]))
            set_prop = True

        if not set_prop:
          self.set_prop(key, self.get_tree(value, args=child_args))

  def dump_doc_internal(self, dump_regs=False, dump_regs_fields=False, header=None):
      regmap_conf = self.props.get('regmap')
      if regmap_conf is not None:
          regmap.Regmap(regmap_conf.get_dict()).dump_memmap(dump_regs=dump_regs, dump_regs_fields=dump_regs_fields, header=header)
      else:
          for elem in self.props.values():
              elem.dump_doc_internal(dump_regs=dump_regs, dump_regs_fields=dump_regs_fields, header=header)

  def browse(self, callback, *kargs, **kwargs):
    callback(self, *kargs, **kwargs)
    for key, value in self.props.items():
      value.browse(callback, *kargs, **kwargs)


  def __str__(self): return self.get_config_name()

  def dump_help(self, name=None, root=None):
    prop_help = self.props.get('help')
    if prop_help is not None:
      print ('')
      print ('  ' + name + ' group:')
      for key in prop_help.keys():
        full_name = key
        if name is not None:
          full_name = '%s/%s' % (name, key)
        print ('    %-40s %s' % (full_name, prop_help.get(key)))

    for key, prop in self.props.items():
      full_name = key
      if name is not None:
        full_name = '%s/%s' % (name, key)
      prop.dump_help(name=full_name)

  def get_config_name(self):
    if self.config_name is not None:
        return self.config_name
    else:
        return self.name

  def keys(self):
    return self.props.keys()

  def items(self):
    return self.props.items()

  def get_name(self, nice=False): 
    if not nice: return self.name
    return self.name.replace('=', '.').replace(':', '_')

  def set_prop(self, key, value):
    if key in self.props:
      self.props.get(key).merge(value)
    else:
      self.props[key] = value
      self.__dict__[key] = value

  def merge(self, tree):
    for key, value in tree.props.items():
      if self.props.get(key) != None:
        self.props.get(key).merge(value)
      else:
        self.set_prop(key, value)

  def get_int(self, name):
    value = self.get(name)
    if type(value) == str: return int(value, 0)
    else: return value

  def get_bool(self, name):
    value = self.get(name)
    if type(value) == str: return value == "True" or value == "true"
    elif value is None:
        return False
    else: return value

  def get_config(self, name):
    return self.get(name, tree=True)

  def get_prop(self, name):
    return self.props.get(name)

  def get(self, name, rec=False, tree=False):

    # TODO this is to keep compatiblity with old sources
    # Get rid of it as soon as everything is ported to the new flow
    if name   == 'pulpChip'        : name = 'pulp_chip'
    elif name == 'pulpChipFamily'  : name = 'pulp_chip_family'
    elif name == 'pulpChipVersion' : name = 'pulp_chip_version'
    elif name == 'pulpCompiler'    : name = 'pulp_compiler'
    elif name == 'pulpRtVersin'    : name = 'pulp_rt_version'
    elif name == 'pulpCoreArchi'   : name = 'pe/version'
    elif name == 'pulpCoreFamily'  : name = 'pe/archi'
    elif name == 'pulpFcCoreArchi' : name = 'fc/version'
    elif name == 'pulpFcCoreFamily': name = 'fc/archi'
    elif name == 'stackSize'       : name = 'stack_size'
    elif name == 'fcStackSize'     : name = 'fc_stack_size'

    if name == None:
      if tree: return self
      elif rec: return self.get_dict()
      else: 
        default = self.props.get('default')
        if default != None:
          return default.value
        else:
          return list(self.props.keys())[0]
    else:
      name_list = name.split('/')
      parent_name = name_list[0]
      elem = self.props.get(parent_name)
      if elem == None:
        for prop in self.props.values():
          value = prop.get(name, rec, tree)
          if value != None: return value
        return None
      else:
        child_name = None if len(name_list) == 1 else '/'.join(name_list[1:])
        return elem.get(child_name, rec, tree)



  def __set(self, name, value, set_first):
    if name == None:
      # In case name is None, it means we are in the item where the property must be set
      # As we are a dictionary, this means removing all items except the one specified
      keys = list(self.props.keys())
      is_set = False
      for prop_name in keys:
        if prop_name != value: 
          del self.props[prop_name]
          is_set = True
      return is_set
    else:
      # We haven't reached yet the point in the hierarchy where the property must be set
      # Either the property name matches one of the properties and then only this one is set
      # otherwise we propagate to all properties
      name_list = name.split('/')
      parent_name = name_list[0]
      elem = self.props.get(parent_name)
      if elem == None:
        is_set = False

        if set_first and len(name_list) == 1:
          is_set = True
          self.set_prop(parent_name, self.get_tree(value))

        else:
          for prop in self.props.values():
            is_set = is_set or prop.set(name, value, set_first=set_first)

        return is_set
      else:
        child_name = None if len(name_list) == 1 else '/'.join(name_list[1:])
        return elem.set(child_name, value, set_first=set_first)

  def set(self, name, value, set_first=None):
    if set_first != None:
      self.__set(name, value, set_first=set_first)
    else:
      if not self.__set(name, value, set_first=False):
        self.__set(name, value, set_first=True)

  def get_dict(self, serialize=True):
    result = OrderedDict()
    for key,value in self.props.items():
      result[key] = value.get_dict(serialize=serialize)
    return result

  def dump_to_file(self, file, root=None):
    if root != None: tree_dict = self.get(root, rec=True)
    else: tree_dict = self.get_dict()
    file.write(json.dumps(tree_dict, indent='  '))

  def get_name_from_items(self, items):
    result = []
    for item in items:
      value = self.get(item)
      if value == None: continue
      result.append("%s=%s" % (item, value))
    return ":".join(result)



def get_config_tree_from_file(file, name='', args=[], path=None):

  try:
      os.makedirs(os.path.dirname(file))
  except:
      pass

  with open(file, 'r') as fd:
    config_dict = json.load(fd, object_pairs_hook=OrderedDict)
  if path is None:
    path = os.path.dirname(file)
  return Tree_elem(config_dict=config_dict, path=path, name=name, args=args)

def get_config_tree_from_dict(config_dict, name='', path=None, args=[], config_name=''):
  return Tree_elem(config_dict=config_dict, name=name, path=path, args=args, config_name=config_name)

def get_config_tree_from_string(config_str, path=None):
  config_dict = json.loads(config_str, object_pairs_hook=OrderedDict)
  return get_config_tree_from_dict(config_dict, path=path)


def get_config_name(config):
    if config.find('@') != -1:
        return config.split('@')[0]
    else:
        return config

  
def get_config_items_from_string(config):
  result = OrderedDict()
  name = config

  if config != '':
    if config.find('@') != -1:
        name, config = config.split('@')

    for item in config.split(':'):
      key, value = item.split('=')
      result[key] = value

  return [name, result]

def append_args(config_tree, args, args_init):

    # Then append the configuration options
    if args is not None:
        current_args = []
        if config_tree.get('config_args') is not None:
            current_args = shlex.split(config_tree.get_config('config_args'))

        config_tree.set('config_args', args_init)

        for item in shlex.split(args.replace(':', ' ')):
            if '=' in item:
                key, value = item.split('=', 1)
            else:
                key = item
                value = 'true'

            if not item in current_args:
                key = key.replace('**/', '')
                if key[0] == '/':
                  key = key[1:]
                config_tree.set(key, value)

def get_configs(config_files=None, config_string=None, path=None, config_file=None, no_args=False, no_config_args=False):

    if config_string is None:
        config_string = ''

    if config_files is None:
        config_files = [os.path.join('pulp.json')]

    config_tree_set = []

    if path is None:
        path = os.environ.get('PULP_CONFIGS_PATH')

    if config_file is not None:
        config_tree = get_config_tree_from_file(config_file)
        if not no_config_args:
          args = plpuserconfig.Args(os.environ.get('PULP_CURRENT_CONFIG_ARGS'))
          append_args(config_tree, args.get_string(), args.get_string_init())
        config_tree_set.append(config_tree)


    else:
      # For each specified configuration, first get a tree of all possible
      # configurations and specialize it to reflect the configuration
      for config in shlex.split(config_string.replace(';', ' ')):

          args = plpuserconfig.Args(os.environ.get('PULP_CURRENT_CONFIG_ARGS'))

          args_list = []
          for key, value in plpuserconfig.Args(os.environ.get('PULP_CURRENT_CONFIG_ARGS_NEW')).get().items():
            args_list.append([key.split('/'), value])

          full_config = config

          if config != '' and config.find('config_file') == -1:
              if config.find('@') != -1:
                  config_name, config_value = config.split('@')
              else:
                  config_value = config

              for item in config_value.split(':'):
                  key, value = item.split('=')

                  if key[0] != '/':
                      key = '**/' + key
                  args_list.append([key.split('/'), value])


          if config.find('config_file') != -1:
              config_name = None
              if config.find('@') != -1:
                  config_name, config = config.split('@')

              for item in config.split(':'):
                  key, value = item.split('=')

                  if key == 'config_file':
                    config_tree = get_config_tree_from_file(value, name=full_config, args=args_list, path=path)
                  elif key == 'user_config_file':
                    top = userconfig.top_new.Top(config_path=value, props=os.environ.get('PULP_TEMPLATE_PROPS'), args=os.environ.get('PULP_TEMPLATE_ARGS'))
                    system_config, system_config_args = top.gen_config()
                    for arg in system_config_args:
                      args_list.append([arg[0].split('/'), arg[1]])
 

                    config_tree = get_config_tree_from_dict(config_dict=system_config, path=path, args=args_list, name=config, config_name=config_name)
                  else:
                    key, value = item.split('=')
                    if key[0] == '/':
                      key = key[1:]
                    config_tree.set(key, value)

          # First check if the configuration contains a template to properly
          # take it into account
          config_name, config_items = get_config_items_from_string(config)
          if config_items.get('template') is not None:
              # In case there is a template first generate the high-level config
              # from the template

              template = eval('plpuserconfig.' + config_items.get('template') + '_template')(args)
              template_config = template.get_config()

              # Then get the system config from it
              top = userconfig.top.Top(name=config_items.get('template'), config=template_config)
              system_config = top.gen_config()
              config_tree = get_config_tree_from_dict(
                config_dict=system_config, name=config, path=path, args=args_list
              )

          elif config.find('config_file') == -1:
            # Otherwise just build the possible set of configurations
            # from the detailed system configurations
            config_tree = None
            for config_file in config_files:
                if os.path.exists(os.path.abspath(config_file)):
                    config_file = os.path.abspath(config_file)
                elif os.path.exists(os.path.join(path, config_file)):
                    config_file = os.path.join(path, config_file)
                tree = get_config_tree_from_file(config_file, name=config, args=args_list)
                if config_tree is None:
                    config_tree = tree
                else:
                    config_tree.merge(tree)

          # For the specialization, take each specified item and set it into the
          # tree this will specialize it.
          if config != '' and config.find('config_file') == -1:
              if config.find('@') != -1:
                  config_tree.config_name, config_value = config.split('@')
              else:
                  config_value = config

              for item in config_value.split(':'):
                  key, value = item.split('=')
                  if key[0] == '/':
                    key = key[1:]
                  config_tree.set(key, value)

          # Then append the configuration options
          if not no_args:
            append_args(config_tree, args.get_string(), args.get_string_init())
          
          config_tree_set.append(config_tree)

          config_ext_str = os.environ.get('PULP_CONFIG_EXT')
          if config_ext_str is not None:
              config_ext = get_config_tree_from_string(config_ext_str, path=path)
              config_tree.merge(config_ext)

    return config_tree_set


def get_configs_from_file(path):
  return get_configs(config_file=path)

def get_configs_from_env(config_def=None, configs=[], path=None, config_file=None):
  result = None
  if len(configs) != 0:
    configString = ';'.join(configs)
  else:
    configString = os.environ.get('PULP_CURRENT_CONFIG')
    if configString == None:
      configString = os.environ.get('PULP_CONFIGS')

  return get_configs(config_files=config_def, config_string=configString, path=path, config_file=config_file)

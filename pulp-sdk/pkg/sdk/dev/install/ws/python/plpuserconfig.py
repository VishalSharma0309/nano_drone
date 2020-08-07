#!/usr/bin/env python3

import json
from collections import OrderedDict
import shlex

class Args(object):

    def __init__(self, args):
        self.args = OrderedDict({})
        if args is not None:
            for item in shlex.split(args.replace(':', ' ')):
                if '=' in item:
                    key, value = item.split('=', 1)
                else:
                    key = item
                    value = 'true'

                if self.args.get(key) is not None:
                    if type(self.args[key]) == list:
                        self.args[key].append(value)
                    else:
                        self.args[key] = [self.args[key], value]
                else:
                    self.args[key] = value

        self.args_init = self.args.copy()

    def get(self):
        return self.args

    def pop(self, name):
        result = self.args.get(name)
        if result is not None:
            del self.args[name]
        return result

    def __get_string(self, args):
        result = []
        for key, name in args.items():
            if type(name) != list:
                name = [name]

            for item in name:
                result.append('%s=%s' % (key, item))

        return ' '.join(result)


    def get_string(self):
        return self.__get_string(self.args)

    def get_string_init(self):
        return self.__get_string(self.args_init)


class Comp(object):

    def __init__(self):
        self.comps = OrderedDict({})
        self.bindings = []

    def add_comp(self, name, comp):
        self.comps[name] = comp

    def is_active(self):
        return True

    def add_binding(self, master, slave):
        self.bindings.append([master, slave])

    def is_active_comp(self, name):
        return 'self.' in name or self.comps[name].is_active()

    def gen(self):
        result = OrderedDict({})
        for name, comp in self.comps.items():
            if comp.is_active():
                result[name] = comp.gen()

        bindings = []
        for binding in self.bindings:
            master, slave = binding
            if self.is_active_comp(master) and self.is_active_comp(slave):
                bindings.append(binding)
        if len(bindings) != 0:
            result['bindings'] = bindings


        return result


class Chip(Comp):

    def __init__(self, name):
        super(Chip, self).__init__()
        self.name = 'chip_' + name

    def gen(self):
        result = OrderedDict({})
        result['comp'] = self.name
        return result



class Pulp_chip(Comp):

    def __init__(self, name):
        super(Pulp_chip, self).__init__()
        self.name = name

    def gen(self):
        result = OrderedDict({})
        result['comp'] = self.name + '_name'
        return result


class Camera(Comp):

    def __init__(self, args):
        super(Camera, self).__init__()
        self.camera = args.pop('camera')

    def is_active(self):
        return self.camera is not None

    def gen(self):
        result = OrderedDict({})
        result['comp'] = self.camera
        return result



class Microphone(Comp):

    def __init__(self, args):
        super(Microphone, self).__init__()


    def is_active(self):
        return True

    def gen(self):
        result = OrderedDict({})
        result['comp'] = 'microphone'
        return result


class Hyperram(Comp):

    def __init__(self, args):
        super(Hyperram, self).__init__()
        self.hyperram = args.pop('hyperram')

    def is_active(self):
        return self.hyperram is not None

    def gen(self):
        result = OrderedDict({})
        result['comp'] = 'hyperram'
        return result


class Hyperflash(Comp):

    def __init__(self, args):
        super(Hyperflash, self).__init__()
        self.hyperflash = args.pop('hyperflash')

    def is_active(self):
        return self.hyperflash is not None

    def gen(self):
        result = OrderedDict({})
        result['comp'] = 'hyperflash'
        return result



class Spiflash(Comp):

    def __init__(self, args):
        super(Spiflash, self).__init__()
        self.spiflash = args.pop('spiflash')

    def is_active(self):
        return self.spiflash is not None

    def gen(self):
        result = OrderedDict({})
        result['comp'] = 'spiflash'
        return result


class Board(Comp):

    def gen(self):
        result = super(Board, self).gen()
        result['comp'] = 'board'
        return result



class common_template(object):

    def __init__(self):
        self.periphs = []
        self.boards = []
        self.comps = OrderedDict({})

    def add_periph(self, periph):
        self.periphs.append(periph)

    def add_board(self, board):
        self.boards.append(board)

    def add_comp(self, name, comp):
        self.comps[name] = comp

    def gen(self):
        result = OrderedDict({})
        for name, comp in self.comps.items():
            result[name] = comp.gen()
        return result


class pulpv4_template(common_template):

    def __init__(self, chip, args={}):
        super(pulpv4_template, self).__init__()

        system = Comp()
        self.system = system

        board = Board()
        system.add_comp('board', board)
        

        pulp_chip = Pulp_chip(name=chip)
        chip = Chip(name=chip)
        board.add_comp(name='chip', comp=chip)
        board.add_comp(name='pulp_chip', comp=pulp_chip)
        board.add_binding('chip', 'self.camera')

        camera = Camera(args)
        system.add_comp(name='camera', comp=camera)

        founds = []
        for key, value in args.get().items():
            if key.find('microphone') == 0 and key.find('/') == -1:
                founds.append(key)
                microphone = Microphone(args)
                system.add_comp(name=key, comp=microphone)
                board.add_binding('chip', 'self.%s' % (key))

        for found in founds:
            args.pop(found)

        hyperram = Hyperram(args)
        board.add_comp(name='hyperram', comp=hyperram)
        board.add_binding('chip', 'hyperram')

        hyperflash = Hyperflash(args)
        board.add_comp(name='hyperflash', comp=hyperflash)
        board.add_binding('chip', 'hyperflash')

        spiflash = Spiflash(args)
        board.add_comp(name='spiflash', comp=spiflash)
        board.add_binding('chip', 'spiflash')

        system.add_binding('board', 'camera')
        #system.add_binding('board', 'microphone')


    def gen(self, path):
        config = self.system.gen()

        config.dump()

        with open(path, 'w') as file:
            json.dump(config, file, indent='  ')

    def get_config(self):
        config = self.system.gen()
        return self.system.gen()


class gap_template(pulpv4_template):

    name = 'gap'

    def __init__(self, args={}):
        super(gap_template, self).__init__(chip=self.name, args=args)



class wolfe_template(pulpv4_template):

    name = 'wolfe'

    def __init__(self, args={}):
        super(wolfe_template, self).__init__(chip=self.name, args=args)


class vivosoc3_template(pulpv4_template):

    name = 'vivosoc3'

    def __init__(self, args={}):
        super(vivosoc3_template, self).__init__(chip=self.name, args=args)



class quentin_template(pulpv4_template):

    name = 'quentin'

    def __init__(self, args={}):
        super(quentin_template, self).__init__(chip=self.name, args=args)


class pulpissimo_template(pulpv4_template):

    name = 'pulpissimo'

    def __init__(self, args={}):
        super(pulpissimo_template, self).__init__(chip=self.name, args=args)


class pulpino_template(pulpv4_template):

    name = 'quentin'

    def __init__(self, args={}):
        super(pulpino_template, self).__init__(chip=self.name, args=args)


templates = [
    gap_template, wolfe_template, quentin_template, pulpino_template,
    vivosoc3_template, pulpissimo_template
]


def get_templates_names():
    result = []
    for template in templates:
        result.append(template.name)
    return result

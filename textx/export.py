#-*- coding: utf-8 -*-
#######################################################################
# Name: export.py
# Purpose: Export of textX based models and metamodels to dot file
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from const import MULT_ZEROORMORE, MULT_ONEORMORE, MULT_ONE
from textx import BASE_TYPE_NAMES
from metamodel import TextXClass

PRIMITIVE_PYTHON_TYPES = [int, float, str, bool]

HEADER = '''
    digraph xtext {
    fontname = "Bitstream Vera Sans"
    fontsize = 8
    node[
        shape=record,
        style=filled,
        fillcolor=gold
    ]
    edge[dir=black,arrowtail=empty]


'''

def metamodel_export(metamodel, file_name):
    processed_set = set()


    with open(file_name, 'w') as f:
        f.write(HEADER)

        for name, cls in metamodel.items():
            attrs = ""
            for attr in cls._attrs.values():
                arrowtail = "arrowtail=diamond, " if attr.cont else ""
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = "list[{}]".format(attr.cls.__name__) \
                        if mult_list else attr.cls.__name__
                if attr.cls.__name__ in BASE_TYPE_NAMES:
                    attrs += "+{}:{}\\l".format(attr.name, attr_type)
                else:
                    mult = attr.mult if not attr.mult == MULT_ONE else ""
                    f.write('{} -> {}[{}dir=both, headlabel="{} {}"]\n'\
                        .format(id(cls), id(attr.cls), arrowtail, attr.name, mult))
            f.write('{}[ label="{{{}|{}}}"]\n'.format(\
                    id(cls), name, attrs))

            inheritance = ""
            for inherited_by in cls._inh_by:
                f.write('{} -> {} [dir=back]\n'\
                        .format(id(cls), id(metamodel[inherited_by.__name__])))

            f.write("\n")

        f.write("\n}\n")


def model_export(model, file_name):

    processed_set = set()

    with open(file_name, 'w') as f:
        f.write(HEADER)

        def _export(obj):

            if obj in processed_set or type(obj) in PRIMITIVE_PYTHON_TYPES:
                return

            processed_set.add(obj)

            attrs = ""
            obj_cls = obj.__class__
            name = ""
            for attr_name, attr in obj_cls._attrs.items():

                attr_value = getattr(obj, attr_name)

                endmark = 'arrowtail=diamond dir=both' if attr.cont else ""

                # Plain attributes
                if attr.cls.__name__ in BASE_TYPE_NAMES:
                    if attr_name == 'name':
                        name = attr_value
                    else:
                        attrs += "{}:{}={}\\l".format(attr_name, type(attr_value)\
                                .__name__, attr_value)

                # Object references
                elif isinstance(attr_value, TextXClass):
                    f.write('{} -> {} [label="{}" {}]\n'.format(id(obj), id(attr_value),
                        attr_name, endmark))
                    _export(attr_value)

                # List of references or primitive values
                elif type(attr_value) is list:
                    if attr.cls.__name__ in BASE_TYPE_NAMES:
                        attrs += "{}:list=[".format(attr_name)
                        attrs += ",".join(attr_value)
                        attrs += "]\\l"
                    else:
                        for idx, list_obj in enumerate(attr_value):
                            f.write('{} -> {} [label="{}:{}" {}]\n'\
                                    .format(id(obj), id(list_obj), attr_name, idx, endmark))
                            _export(list_obj)

            name = "{}:{}".format(name,obj_cls.__name__)

            f.write('{}[label="{{{}|{}}}"]\n'.format(id(obj), name, attrs))

        _export(model)

        f.write('\n}\n')



import sys

import nltk
from nltk.corpus import dependency_treebank
from nltk.classify.maxent import MaxentClassifier
from nltk.classify.util import accuracy

VALID_TYPES = set(['s', 'l', 'r'])

class Transition:
    def __init__(self, type, edge=None):
        self._type = type
        self._edge = edge
        assert self._type in VALID_TYPES

    def pretty_print(self, sentence):
        if self._edge:
            a, b = self._edge
            return "%s\t(%s, %s)" % (self._type,
                                     sentence.get_by_address(a)['word'],
                                     sentence.get_by_address(b)['word'])
        else:
            return self._type


def transition_sequence(sentence):
    """
    Return the sequence of shift-reduce actions that reconstructs the input sentence.
    """
    node_list = sentence.nodelist
    stack = list()
    buff = list()

    #initial state
    stack.append(node_list.pop(0))
    buff = node_list

    counter = 0
    while stack:
        # left action
        if stack[-1]['tag'] != 'TOP':
            if stack[-1]['head'] == buff[0]['address']:
                # left action
                yield Transition('l', (buff[0]['address'], stack[-1]['address']))
                stack.pop()
            elif (stack[-1]['address'] == buff[0]['head']) \
                and (buff[0]['address'] not in [x['head'] for x in buff[1:]]):
                # right action
                yield Transition('r', (stack[-1]['address'], buff[0]['address']))
                buff.pop(0)
                buff.insert(0, stack.pop())
            else:
                # shift
                yield Transition('s')
                stack.append(buff.pop(0))
        else:
            if len(buff) == 1:
                # right action
                yield Transition('r', (stack[-1]['address'], buff[0]['address']))
                buff.pop(0)
                buff.insert(0, stack.pop())
            else:
                # shift
                yield Transition('s')
                stack.append(buff.pop(0))
    yield Transition('s')
    stack.append(buff.pop(0))

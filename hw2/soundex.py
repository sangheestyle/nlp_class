# Author: Sanghee Kim
# Date: September 19, 2014

from fst import FST
import string, sys
from fsmutils import composechars, trace

def letters_to_numbers():
    """
    Returns an FST that converts letters to numbers as specified by
    the soundex algorithm
    """

    # Let's define our first FST
    f1 = FST('soundex-generate')

    # Indicate that '1' is the initial state
    states = ['q1', 'q2', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6']
    for state in states:
        f1.add_state(state)

    f1.initial_state = 'q1'

    # Set all the final states
    for state in ['q2', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6']:
        f1.set_final(state)

    # Add the rest of the arcs
    for letter in string.ascii_lowercase:
        f1.add_arc('q1', 'q2', (letter), (letter))
        if letter in set('aehiouwy'):
            for state in ['q2', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6']:
                f1.add_arc(state, state, (letter), ())
        else:
            if letter in set('bfpv'):
                for state in ['q2', 'n2', 'n3', 'n4', 'n5', 'n6']:
                    f1.add_arc(state, 'n1', (letter), ('1'))
                f1.add_arc('n1', 'n1', (letter), ())
            elif letter in set('cgjkqsxz'):
                for state in ['q2', 'n1', 'n3', 'n4', 'n5', 'n6']:
                    f1.add_arc(state, 'n2', (letter), ('2'))
                f1.add_arc('n2', 'n2', (letter), ())
            elif letter in set('dt'):
                for state in ['q2', 'n1', 'n2', 'n4', 'n5', 'n6']:
                    f1.add_arc(state, 'n3', (letter), ('3'))
                f1.add_arc('n3', 'n3', (letter), ())
            elif letter in set('l'):
                for state in ['q2', 'n1', 'n2', 'n3', 'n5', 'n6']:
                    f1.add_arc(state, 'n4', (letter), ('4'))
                f1.add_arc('n4', 'n4', (letter), ())
            elif letter in set('mn'):
                for state in ['q2', 'n1', 'n2', 'n3', 'n4', 'n6']:
                    f1.add_arc(state, 'n5', (letter), ('5'))
                f1.add_arc('n5', 'n5', (letter), ())
            elif letter in set('r'):
                for state in ['q2', 'n1', 'n2', 'n3', 'n4', 'n5']:
                    f1.add_arc(state, 'n6', (letter), ('6'))
                f1.add_arc('n6', 'n6', (letter), ())
    return f1

def truncate_to_three_digits():
    """
    Create an FST that will truncate a soundex string to three digits
    """

    # Ok so now let's do the second FST, the one that will truncate
    # the number of digits to 3
    f2 = FST('soundex-truncate')

    # Indicate initial and final states
    states = ['1', 'd1', 'd2', 'd3']

    for state in states:
        f2.add_state(state)

    f2.initial_state = '1'

    for state in ['d1', 'd2', 'd3']:
        f2.set_final(state)

    # Add the arcs
    for letter in string.letters:
        f2.add_arc('1', '1', (letter), (letter))

    for index, state in enumerate(states):
        if index > 0:
            for n in range(10):
                f2.add_arc(states[index-1], states[index], str(n), str(n))

    for n in range(10):
        f2.add_arc('d3', 'd3', str(n), ())

    return f2

def add_zero_padding():
    # Now, the third fst - the zero-padding fst
    f3 = FST('soundex-padzero')

    states = ['1', '2', '3', '4']

    for state in states:
        f3.add_state(state)

    f3.initial_state = '1'
    f3.set_final('4')

    for letter in string.letters:
        f3.add_arc('1', '1', letter, letter)

    for number in range(1, 10):
        f3.add_arc('1', '2', str(number), str(number))
        f3.add_arc('2', '3', str(number), str(number))
        f3.add_arc('3', '4', str(number), str(number))

    f3.add_arc('2', '4', (), '00')
    f3.add_arc('3', '4', (), '0')
    return f3

if __name__ == '__main__':
    user_input = raw_input().strip()
    f1 = letters_to_numbers()
    f2 = truncate_to_three_digits()
    f3 = add_zero_padding()

    if user_input:
        print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))

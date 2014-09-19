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
    f2.add_state('1')
    f2.initial_state = '1'
    f2.set_final('1')

    # Add the arcs
    for letter in string.letters:
        f2.add_arc('1', '1', (letter), (letter))

    for n in range(10):
        f2.add_arc('1', '1', str(n), str(n))

    return f2

def add_zero_padding():
    # Now, the third fst - the zero-padding fst
    f3 = FST('soundex-padzero')

    f3.add_state('1')
    f3.add_state('2')
    
    f3.initial_state = '1'
    f3.set_final('2')

    for letter in string.letters:
        f3.add_arc('1', '1', letter, letter)
    for number in xrange(10):
        f3.add_arc('1', '1', str(number), str(number))
    
    for n in range(10):
        f3.add_arc('1', '2', (), '000')
    return f3

if __name__ == '__main__':
    user_input = raw_input().strip()
    f1 = letters_to_numbers()
    f2 = truncate_to_three_digits()
    f3 = add_zero_padding()

    if user_input:
        trace(f1, user_input)
        #print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))

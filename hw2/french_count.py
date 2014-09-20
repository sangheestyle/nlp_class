import sys
from fst import FST
from fsmutils import composewords
from fsmutils import trace

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    return list("%03i" % integer)

def french_count():
    f = FST('french')

    # start
    f.add_state('start')

    # hundreads digit
    f.add_state('h1') # 0
    f.add_state('h2') # 1 - 9

    # tenth digit
    f.add_state('t1') # 0
    f.add_state('t2') # 1
    f.add_state('t3') # 1
    f.add_state('t4') # 1
    f.add_state('t5') # 1

    # end(digit)
    f.add_state('d1')

    f.initial_state = 'start'
    f.set_final('d1')

    # 3rd digit
    for ii in xrange(10):
        if ii == 0:
            f.add_arc('start', 'h1', str(ii), ())
            f.add_arc('h1', 't1', str(ii), ())
            f.add_arc('h2', 't4', str(ii), ())
            f.add_arc('t3', 'd1', str(ii), ())
            f.add_arc('t4', 'd1', str(ii), ())
            f.add_arc('t2', 'd1', str(ii), [kFRENCH_TRANS[10]])
            f.add_arc('t5', 'd1', str(ii), [kFRENCH_TRANS[10]]) #dix
        elif ii == 1:
            f.add_arc('start', 'h2', str(ii), [kFRENCH_TRANS[100]]) # hundread
            f.add_arc('h1', 't2', str(ii), ())
            f.add_arc('h2', 't2', str(ii), ())
            f.add_arc('t3', 'd1', str(ii), [kFRENCH_AND + " " + kFRENCH_TRANS[1]])
            f.add_arc('t4', 'd1', str(ii), [kFRENCH_TRANS[ii]])
        elif ii == 7:
            f.add_arc('h1', 't5', str(ii), [kFRENCH_TRANS[60]])
            f.add_arc('h2', 't5', str(ii), [kFRENCH_TRANS[60]])
        elif ii == 9:
            eighty = kFRENCH_TRANS[4] + " " + kFRENCH_TRANS[20]
            f.add_arc('h1', 't5', str(ii), [eighty])
            f.add_arc('h2', 't5', str(ii), [eighty])
        else:
            if ii == 8:
                eighty = kFRENCH_TRANS[4] + kFRENCH_TRANS[20]
                f.add_arc('h1', 't3', str(ii), [eighty])
                f.add_arc('h2', 't3', str(ii), [eighty])
            else:
                f.add_arc('h1', 't3', str(ii), [kFRENCH_TRANS[ii * 10]])
                f.add_arc('h2', 't3', str(ii), [kFRENCH_TRANS[ii * 10]])

            f.add_arc('t3', 'd1', str(ii), [kFRENCH_TRANS[ii]])


        # 2 to 9
        if ii > 1 and ii < 10:
            # hundread
            hundread = kFRENCH_TRANS[ii] + " " + kFRENCH_TRANS[100]
            f.add_arc('start', 'h2', str(ii), [hundread])
            f.add_arc('t3', 'd1', str(ii), [kFRENCH_TRANS[ii]])
            f.add_arc('t4', 'd1', str(ii), [kFRENCH_TRANS[ii]])

    for ii in xrange(1, 10):
        f.add_arc('t1', 'd1', str(ii), [kFRENCH_TRANS[ii]])

    for ii in xrange(1, 7):
        f.add_arc('t2', 'd1', str(ii), [kFRENCH_TRANS[ii]])
        f.add_arc('t5', 'd1', str(ii), [kFRENCH_TRANS[ii+10]])

    for ii in xrange(7, 10):
        f.add_arc('t2', 'd1', str(ii), [kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[ii]])
        f.add_arc('t5', 'd1', str(ii), [kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[ii]])

    return f


if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
    f = french_count()
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))

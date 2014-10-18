from string import punctuation
from math import log
import pickle

from numpy import logaddexp
from scipy.stats import poisson

from nltk.corpus import dependency_treebank as dt

kROOT = "<ROOT>"
kNEG_INF = float("-inf")
TL = []


def correct_positions(dependency_parse):
    """
    Given a correct NLTK parse tree, return an iterator over the correct
    tuples.  Excludes punctuation.
    """

    for ii in dependency_parse.to_conll(10).split('\n'):
        if not ii:
            continue

        fields = ii.split('\t')
        child_pos = int(fields[0])
        head_pos = int(fields[6])
        child_word = fields[1]
        if not all(x in punctuation for x in child_word):
            yield (head_pos, child_pos)


def dependency_element(dependency_parse, key='word'):
    """
    Returns an iterator over the elements in the original sentence (given the key)

    @param key The key of the element to return
    """
    pos = 1
    while dependency_parse.contains_address(pos):
        yield dependency_parse.get_by_address(pos)[key].lower()
        pos += 1


class BigramInterpScoreFunction:
    """
    Class that matches score function API.  Uses cached score function values.
    """

    def __init__(self, pickled_word, pickled_tag):
        """
        Read cached scores from a file
        """

        self._word_scores = pickle.load(open(pickled_word, 'rb'))
        self._tag_scores = pickle.load(open(pickled_tag, 'rb'))
        self._poisson = poisson(1.9)

    def word_score(self, h_word, c_word):
        if h_word != kROOT and all(x in punctuation for x in h_word):
            val = kNEG_INF
        elif c_word == kROOT:
            val = kNEG_INF
        else:
            val = self._word_scores.get((h_word, c_word), -100)
        #print(h_word, c_word, val)
        return val

    def tag_score(self, h_tag, c_tag):
        val = self._tag_scores.get((h_tag, c_tag), -100)
        #print(h_tag, c_tag, val)
        return val

    def dist_score(self, h_ind, c_ind):
        val = self._poisson.pmf(abs(h_ind - c_ind))
        #print(h_ind, c_ind, val)
        return log(val)

    def __call__(self, h_word, c_word, h_tag, c_tag, h_pos=0, c_pos=0):
        """
        Given a potential dependency, give score
        """

        val = logaddexp(self.word_score(h_word, c_word),
                        self.tag_score(h_tag, c_tag))
        val = logaddexp(val, self.dist_score(h_pos, c_pos))

        return val

def unlabeled_accuracy(truth, answer):
    """
    Returns the accuracy as the number edges right and the total number of
    edges.
    """
    right = 0
    total = 0
    answer_lookup = dict((y, x) for x, y in answer)

    for parent, child in correct_positions(truth):
        total += 1
        if answer_lookup[child] == parent:
            right += 1

    return right, total


class EisnerParser:
    """
    Parses a sentence using Eisner's algorithm
    """

    def __init__(self, sentence, tag_sequence, score_function):
        self._chart = {}
        self._pointer = {}
        self._sent = [kROOT] + sentence
        self._tags = [kROOT] + tag_sequence
        self._sf = score_function
        self.initialize_chart()

    def initialize_chart(self):
        """
        Create a chart with singleton spans
        """
        start_points = range(0, len(self._sent))
        end_points = range(0, len(self._sent))
        right_dir = [True, False]
        complete = [True, False]

        for s in start_points:
            for e in end_points:
                for r in right_dir:
                    for c in complete:
                        score = None
                        if s == e:
                            score = 0.0
                        self._chart[(s, e, r, c)] = score

    def get_score(self, start, stop, right_dir, complete):
        return self._chart[(start, stop, right_dir, complete)]

    def reconstruct(self):
        """
        Return an iterator over edges in the discovered dependency parse tree
        """

        return self._reconstruct((0, len(self._sent) - 1, True, True))

    def _rec(self, span):
        lst = self._pointer[span]
        lhs = lst[0]
        rhs = lst[1]

        if len(lst) == 3:
            edge = lst[2]
            TL.append(edge)

        if lhs[0] != lhs[1]:
            self._rec(lhs)

        if rhs[0] != rhs[1]:
            self._rec(rhs)

    def _reconstruct(self, span):
        self._rec(span)
        return TL

    def _generate_cal_seq(self):
        num_sent = len(self._sent)
        for diff in xrange(1, num_sent):
            for s in xrange(0, num_sent):
                for e in xrange(0, num_sent):
                    if (s <= e) and (e-s == diff):
                        yield s, e

    def _cal_stri(self, s, e):
        qq = list(xrange(s, e))
        total = []
        for q in qq:
            f1 = self.get_score(s, q, True, True)
            f2 = self.get_score(q+1, e, False, True)
            ld = self._sf.word_score(self._sent[s],self._sent[e])
            total.append(f1 + f2 + ld)
        i = total.index(max(total))
        return max(total), [(s, qq[i], True, True), (qq[i]+1, e, False, True), (s, e)]

    def _cal_stli(self, s, e):
        qq = list(xrange(s, e))
        total = []
        for q in qq:
            f1 = self.get_score(s, q, True, True)
            f2 = self.get_score(q+1, e, False, True)
            ld = self._sf.word_score(self._sent[e],self._sent[s])
            total.append(f1 + f2 + ld)
        i = total.index(max(total))
        return max(total), [(s, qq[i], True, True), (qq[i]+1, e, False, True), (e, s)]

    def _cal_strc(self, s, e):
        qq = list(xrange(s+1, e+1))
        total = []
        for q in qq:
            f1 = self.get_score(s, q, True, False)
            f2 = self.get_score(q, e, True, True)
            total.append(f1 + f2)
        i = total.index(max(total))
        return max(total), [(s, qq[i], True, False), (qq[i], e, True, True)]

    def _cal_stlc(self, s, e):
        qq = list(xrange(s, e))
        total = []
        for q in qq:
            f1 = self.get_score(s, q, False, True)
            f2 = self.get_score(q, e, False, False)
            total.append(f1 + f2)
        i = total.index(max(total))
        return max(total), [(s, qq[i], False, True), (qq[i], e, False, False)]

    def fill_chart(self):
        """
        Complete the chart and fill in back pointers
        """
        for s, e in self._generate_cal_seq():
            k1 = (s, e, True, False)
            k2 = (s, e, False, False)
            k3 = (s, e, True, True)
            k4 = (s, e, False, True)
            self._chart[k1], self._pointer[k1] = self._cal_stri(s, e)
            self._chart[k2], self._pointer[k2] = self._cal_stli(s, e)
            self._chart[k3], self._pointer[k3] = self._cal_strc(s, e)
            self._chart[k4], self._pointer[k4] = self._cal_stlc(s, e)

def custom_sf():
    """
    Return a custom score function that obeys the BigramScoreFunction interface.
    It can use information stored in the local file sf.dat
    """
    # Complete this if you want extra credit
    return None

if __name__ == "__main__":

    # Load the score function
    sf = BigramInterpScoreFunction("tb_counts.words", "tb_counts.tag")

    total_right = 0
    total_edges = 0

    for ss in dt.parsed_sents():
        words = list(dependency_element(ss, 'word'))
        tags = list(dependency_element(ss, 'tag'))

        chart = EisnerParser(words, tags, sf)

        chart.initialize_chart()
        chart.fill_chart()

#        for ii, jj in correct_positions(ss):
        for ii, jj in chart.reconstruct():
            # Subtract 1 to account for the head we added
            print(ii, jj, words[ii - 1], words[jj - 1],
                  tags[ii - 1], tags[jj - 1],
                  sf(words[ii - 1], words[jj - 1],
                     tags[ii - 1], tags[jj - 1], ii, jj))

        right, edges = unlabeled_accuracy(ss, chart.reconstruct())

        total_right += right
        total_edges += edges

        print("============================ Acc (%i): %f" % \
                  (total_edges, float(total_right) / float(total_edges)))

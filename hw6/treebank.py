# Name: Sanghee Kim
# Subject: Homework 6
# Date: Oct, 17 2014


import nltk
from collections import defaultdict

class PcfgEstimator:
    """
    Estimates the production probabilities of a PCFG
    """
    
    def __init__(self):
        self._counts = defaultdict(nltk.FreqDist)

    def add_sentence(self, sentence):
        """
        Add the sentence to the dataset
        """

        assert isinstance(sentence, nltk.tree.Tree), \
               "Can only add counts from a tree"

        for p in sentence.productions():
            if isinstance(p.rhs()[0], nltk.grammar.Nonterminal):
                rhs_string = " ".join(r.symbol() for r in p.rhs())
            else:
                rhs_string = " ".join(p.rhs())
            self._counts[p.lhs().symbol()].update(nltk.FreqDist([rhs_string]))

    def query(self, lhs, rhs):
        """
        Returns the MLE probability of this production
        """
        
        return self._counts[lhs].freq(rhs)

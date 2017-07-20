from __future__ import unicode_literals
from gensim.models import KeyedVectors
from itertools import permutations, combinations_with_replacement
import language_check
import os
import sys
import re

# Lists derived from https://en.wikipedia.org/wiki/Wikipedia:List_of_English_contractions
simple_contractions = {
    re.compile(r"\bcan'?t\b", re.I | re.U): "cannot",
    re.compile(r"\bcan'?t'?ve\b", re.I | re.U): "cannot have",
    re.compile(r"\b'?cause\b", re.I | re.U): "because",
    re.compile(r"\bcould'?ve\b", re.I | re.U): "could have",
    re.compile(r"\bcouldn'?t\b", re.I | re.U): "could not",
    re.compile(r"\bcouldn'?t'?ve\b", re.I | re.U): "could not have",
    re.compile(r"\bdidn'?t\b", re.I | re.U): "did not",
    re.compile(r"\bdoesn'?t\b", re.I | re.U): "does not",
    re.compile(r"\bdon'?t\b", re.I | re.U): "do not",
    re.compile(r"\bdoin'?\b", re.I | re.U): "doing",
    re.compile(r"\bgimme'?\b", re.I | re.U): "give me",
    re.compile(r"\bgoin'?\b", re.I | re.U): "going",
    re.compile(r"\bgonna'?\b", re.I | re.U): "going to",
    re.compile(r"\bhadn'?t\b", re.I | re.U): "had not",
    re.compile(r"\bhadn'?t'?ve\b", re.I | re.U): "had not have",
    re.compile(r"\bhasn'?t\b", re.I | re.U): "has not",
    re.compile(r"\bhaven'?t\b", re.I | re.U): "have not",
    re.compile(r"\bhe'?d'?ve\b", re.I | re.U): "he would have",
    re.compile(r"\bhow'?d\b", re.I | re.U): "how did",
    re.compile(r"\bhow'?d'?y\b", re.I | re.U): "how do you",
    re.compile(r"\bhow'?ll\b", re.I | re.U): "how will",
    re.compile(r"\bI'?d'?ve\b", re.I | re.U): "I would have",
    # May replace the abbreviation "im" as in Instant Messenger.
    # If this abbreviation is in your data remove the "?"
    re.compile(r"\bI'?m\b", re.I | re.U): "I am",
    re.compile(r"\bI'?ve\b", re.I | re.U): "I have",
    re.compile(r"\bisn'?t\b", re.I | re.U): "is not",
    re.compile(r"\bit'?d'?ve\b", re.I | re.U): "it would have",
    re.compile(r"\blet'?s\b", re.I | re.U): "let us",
    re.compile(r"\bma'?am\b", re.I | re.U): "madam",
    re.compile(r"\bmayn'?t\b", re.I | re.U): "may not",
    re.compile(r"\bmight'?ve\b", re.I | re.U): "might have",
    re.compile(r"\bmightn'?t\b", re.I | re.U): "might not",
    re.compile(r"\bmightn'?t'?ve\b", re.I | re.U): "might not have",
    re.compile(r"\bmust'?ve\b", re.I | re.U): "must have",
    re.compile(r"\bmustn'?t\b", re.I | re.U): "must not",
    re.compile(r"\bmustn'?t'?ve\b", re.I | re.U): "must not have",
    re.compile(r"\bnothin'?\b", re.I | re.U): "nothing",
    re.compile(r"\bneedn'?t\b", re.I | re.U): "need not",
    re.compile(r"\bneedn'?t'?ve\b", re.I | re.U): "need not have",
    re.compile(r"\bo'?clock\b", re.I | re.U): "of the clock",
    re.compile(r"\boughtn'?t\b", re.I | re.U): "ought not",
    re.compile(r"\boughtn'?t'?ve\b", re.I | re.U): "ought not have",
    re.compile(r"\bshan'?t\b", re.I | re.U): "shall not",
    re.compile(r"\bsha'?n'?t\b", re.I | re.U): "shall not",
    re.compile(r"\bshan'?t'?ve\b", re.I | re.U): "shall not have",
    re.compile(r"\bshe'?d'?ve\b", re.I | re.U): "she would have",
    re.compile(r"\bshould'?ve\b", re.I | re.U): "should have",
    re.compile(r"\bshouldn'?t\b", re.I | re.U): "should not",
    re.compile(r"\bshouldn'?t'?ve\b", re.I | re.U): "should not have",
    re.compile(r"\bso'?ve\b", re.I | re.U): "so have",
    re.compile(r"\bsomethin'?\b", re.I | re.U): "something",
    re.compile(r"\bthat'?d'?ve\b", re.I | re.U): "that would have",
    re.compile(r"\bthere'?d'?ve\b", re.I | re.U): "there would have",
    re.compile(r"\bthey'?d'?ve\b", re.I | re.U): "they would have",
    re.compile(r"\bthey'?re\b", re.I | re.U): "they are",
    re.compile(r"\bthey'?ve\b", re.I | re.U): "they have",
    re.compile(r"\bto'?ve\b", re.I | re.U): "to have",
    re.compile(r"\bu\b", re.I | re.U): "you",
    re.compile(r"\bwasn'?t\b", re.I | re.U): "was not",
    re.compile(r"\bwe'?d'?ve\b", re.I | re.U): "we would have",
    re.compile(r"\bwe'll\b", re.I | re.U): "we will",
    re.compile(r"\bwe'?ll'?ve\b", re.I | re.U): "we will have",
    re.compile(r"\bwe'?re\b", re.I | re.U): "we are",
    re.compile(r"\bwe'?ve\b", re.I | re.U): "we have",
    re.compile(r"\bweren'?t\b", re.I | re.U): "were not",
    re.compile(r"\bwhat'?re\b", re.I | re.U): "what are",
    re.compile(r"\bwhat'?ve\b", re.I | re.U): "what have",
    re.compile(r"\bwhen'?ve\b", re.I | re.U): "when have",
    re.compile(r"\bwhere'?d\b", re.I | re.U): "where did",
    re.compile(r"\bwhere'?ve\b", re.I | re.U): "where have",
    re.compile(r"\bwho'?ve\b", re.I | re.U): "who have",
    re.compile(r"\bwhy'?ve\b", re.I | re.U): "why have",
    re.compile(r"\bwill'?ve\b", re.I | re.U): "will have",
    re.compile(r"\bwon'?t\b", re.I | re.U): "will not",
    re.compile(r"\bwon'?t'?ve\b", re.I | re.U): "will not have",
    re.compile(r"\bwould'?ve\b", re.I | re.U): "would have",
    re.compile(r"\bwouldn'?t\b", re.I | re.U): "would not",
    re.compile(r"\bwouldn'?t'?ve\b", re.I | re.U): "would not have",
    re.compile(r"\by'?all\b", re.I | re.U): "you all",
    re.compile(r"\by'?all'?d\b", re.I | re.U): "you all would",
    re.compile(r"\by'?all'?d'?ve\b", re.I | re.U): "you all would have",
    re.compile(r"\by'?all'?re\b", re.I | re.U): "you all are",
    re.compile(r"\by'?all'?ve\b", re.I | re.U): "you all have",
    re.compile(r"\byou'?d'?ve\b", re.I | re.U): "you would have",
    re.compile(r"\byou'?re\b", re.I | re.U): "you are",
    re.compile(r"\byou'?ve\b", re.I | re.U): "you have"
}

contextual_contractions = {
    re.compile(r"\bain'?t\b", re.I | re.U): ["am not", "are not", "is not", "has not", "have not"],
    re.compile(r"\baren'?t\b", re.I | re.U): ["are not", "am not"],
    re.compile(r"\bhe'?d\b", re.I | re.U): ["he had", "he would"],
    re.compile(r"\bhe'll\b", re.I | re.U): ["he shall", "he will"],
    re.compile(r"\bhe'?ll'?ve\b", re.I | re.U): ["he shall have", "he will have"],
    re.compile(r"\bhe'?s\b", re.I | re.U): ["he has", "he is"],
    re.compile(r"\bhow'?s\b", re.I | re.U): ["how has", "how is", "how does"],
    # "id" is a common abbreviation for Identification.
    # If this abbrevaiation does NOT appear in your data add the "?"
    re.compile(r"\bI'd\b", re.I | re.U): ["I had", "I would"],
    re.compile(r"\bI'll\b", re.I | re.U): ["I shall", "I will"],
    re.compile(r"\bI'?ll'?ve\b", re.I | re.U): ["I shall have", "I will have"],
    re.compile(r"\bit'?d\b", re.I | re.U): ["it had", "it would"],
    re.compile(r"\bit'?ll\b", re.I | re.U): ["it shall", "it will"],
    re.compile(r"\bit'?ll'?ve\b", re.I | re.U): ["it shall have", "it will have"],
    re.compile(r"\bit'?s\b", re.I | re.U): ["it has", "it is"],
    re.compile(r"\bshe'?d\b", re.I | re.U): ["she had", "she would"],
    re.compile(r"\bshe'll\b", re.I | re.U): ["she shall", "she will"],
    re.compile(r"\bshe'?ll'?ve\b", re.I | re.U): ["she shall have", "she will have"],
    re.compile(r"\bshe'?s\b", re.I | re.U): ["she has", "she is"],
    # May replace the abbreviation "sos" as in Save Our Souls.
    # If this abbreviation is in your data remove the "?"
    re.compile(r"\bso'?s\b", re.I | re.U): ["so as", "so is"],
    re.compile(r"\bthat'?d\b", re.I | re.U): ["that would", "that had"],
    re.compile(r"\bthat'?s\b", re.I | re.U): ["that has", "that is"],
    re.compile(r"\bthere'?d\b", re.I | re.U): ["there had", "there would"],
    re.compile(r"\bthere'?s\b", re.I | re.U): ["there has", "there is"],
    re.compile(r"\bthey'?d\b", re.I | re.U): ["they had", "they would"],
    re.compile(r"\bthey'?ll\b", re.I | re.U): ["they shall", "they will"],
    re.compile(r"\bthey'?ll'?ve\b", re.I | re.U): ["they shall have", "they will have"],
    re.compile(r"\bwe'd\b", re.I | re.U): ["we had", "we would"],
    re.compile(r"\bwhat'?ll\b", re.I | re.U): ["what shall", "what will"],
    re.compile(r"\bwhat'?ll'?ve\b", re.I | re.U): ["what shall have", "what will have"],
    re.compile(r"\bwhat'?s\b", re.I | re.U): ["what has", "what is"],
    re.compile(r"\bwhen'?s\b", re.I | re.U): ["when has", "when is"],
    re.compile(r"\bwhere'?s\b", re.I | re.U): ["where has", "where is"],
    re.compile(r"\bwho'?ll\b", re.I | re.U): ["who shall", "who will"],
    re.compile(r"\bwho'?ll'?ve\b", re.I | re.U): ["who shall have", "who will have"],
    re.compile(r"\bwho'?s\b", re.I | re.U): ["who has", "who is"],
    re.compile(r"\bwhy'?s\b", re.I | re.U): ["why has", "why is"],
    re.compile(r"\byou'?d\b", re.I | re.U): ["you had", "you would"],
    re.compile(r"\byou'?ll\b", re.I | re.U): ["you shall", "you will"],
    re.compile(r"\byou'?ll'?ve\b", re.I | re.U): ["you shall have", "you will have"],
}

expansions = {
    re.compile(r"\bare\s+not\b", re.I | re.U): "aren't",
    re.compile(r"\bcannot\b", re.I | re.U): "can't",
    re.compile(r"\bcould\s+have\b", re.I | re.U): "could've",
    re.compile(r"\bcould\s+not\b", re.I | re.U): "couldn't",
    re.compile(r"\bdid\s+not\b", re.I | re.U): "didn't",
    re.compile(r"\bdoes\s+not\b", re.I | re.U): "doesn't",
    re.compile(r"\bdo\s+not\b", re.I | re.U): "don't",
    re.compile(r"\bgot\s+to\b", re.I | re.U): "gotta",
    re.compile(r"\bhad\s+not\b", re.I | re.U): "hadn't",
    re.compile(r"\bhas\s+not\b", re.I | re.U): "hasn't",
    re.compile(r"\bhave\s+not\b", re.I | re.U): "haven't",
    re.compile(r"\bhe\s+had\b", re.I | re.U): "he'd",
    re.compile(r"\bhe\s+would\b", re.I | re.U): "he'd",
    re.compile(r"\bhe\s+shall\b", re.I | re.U): "he'll",
    re.compile(r"\bhe\s+will\b", re.I | re.U): "he'll",
    re.compile(r"\bhe\s+has\b", re.I | re.U): "he's",
    re.compile(r"\bhe\s+is\b", re.I | re.U): "he's",
    re.compile(r"\bhow\s+did\b", re.I | re.U): "how'd",
    re.compile(r"\bhow\s+would\b", re.I | re.U): "how'd",
    re.compile(r"\bhow\s+will\b", re.I | re.U): "how'll",
    re.compile(r"\bhow\s+has\b", re.I | re.U): "how's",
    re.compile(r"\bhow\s+is\b", re.I | re.U): "how's",
    re.compile(r"\bhow\s+does\b", re.I | re.U): "how's",
    re.compile(r"\bI\s+had\b", re.I | re.U): "I'd",
    re.compile(r"\bI\s+would\b", re.I | re.U): "I'd",
    re.compile(r"\bI\s+shall\b", re.I | re.U): "I'll",
    re.compile(r"\bI\s+will\b", re.I | re.U): "I'll",
    re.compile(r"\bI\s+am\b", re.I | re.U): "I'm",
    re.compile(r"\bI\s+have\b", re.I | re.U): "I've",
    re.compile(r"\bis\s+not\b", re.I | re.U): "isn't",
    re.compile(r"\bit\s+would\b", re.I | re.U): "it'd",
    re.compile(r"\bit\s+shall\b", re.I | re.U): "it'll",
    re.compile(r"\bit\s+will\b", re.I | re.U): "it'll",
    re.compile(r"\bit\s+has\b", re.I | re.U): "it's",
    re.compile(r"\bit\s+is\b", re.I | re.U): "it's",
    re.compile(r"\bmay\s+have\b", re.I | re.U): "may've",
    re.compile(r"\bmight\s+not\b", re.I | re.U): "mightn't",
    re.compile(r"\bmight\s+have\b", re.I | re.U): "might've",
    re.compile(r"\bmust\s+not\b", re.I | re.U): "mustn't",
    re.compile(r"\bmust\s+have\b", re.I | re.U): "must've",
    re.compile(r"\bneed\s+not\b", re.I | re.U): "needn't",
    re.compile(r"\bof\s+the\s+clock\b", re.I | re.U): "o'clock",
    re.compile(r"\bought\s+not\b", re.I | re.U): "oughtn't",
    re.compile(r"\bshall\s+not\b", re.I | re.U): "shan't",
    re.compile(r"\bshe\s+had\b", re.I | re.U): "she'd",
    re.compile(r"\bshe\s+would\b", re.I | re.U): "she'd",
    re.compile(r"\bshe\s+shall\b", re.I | re.U): "she'll",
    re.compile(r"\bshe\s+will\b", re.I | re.U): "she'll",
    re.compile(r"\bshe\s+has\b", re.I | re.U): "she's",
    re.compile(r"\bshe\s+is\b", re.I | re.U): "she's",
    re.compile(r"\bshould\s+have\b", re.I | re.U): "should've",
    re.compile(r"\bshould\s+not\b", re.I | re.U): "shouldn't",
    re.compile(r"\bsomebody\s+has\b", re.I | re.U): "somebody's",
    re.compile(r"\bsomebody\s+is\b", re.I | re.U): "somebody's",
    re.compile(r"\bsomeone\s+has\b", re.I | re.U): "someone's",
    re.compile(r"\bsomeone\s+is\b", re.I | re.U): "someone's",
    re.compile(r"\bsomething\s+has\b", re.I | re.U): "something's",
    re.compile(r"\bsomething\s+is\b", re.I | re.U): "something's",
    re.compile(r"\bthat\s+shall\b", re.I | re.U): "that'll",
    re.compile(r"\bthat\s+will\b", re.I | re.U): "that'll",
    re.compile(r"\bthat\s+are\b", re.I | re.U): "that're",
    re.compile(r"\bthat\s+has\b", re.I | re.U): "that's",
    re.compile(r"\bthat\s+is\b", re.I | re.U): "that's",
    re.compile(r"\bthat\s+would\b", re.I | re.U): "that'd",
    re.compile(r"\bthat\s+had\b", re.I | re.U): "that'd",
    re.compile(r"\bthere\s+had\b", re.I | re.U): "there'd",
    re.compile(r"\bthere\s+would\b", re.I | re.U): "there'd",
    re.compile(r"\bthere\s+are\b", re.I | re.U): "there're",
    re.compile(r"\bthere\s+has\b", re.I | re.U): "there's",
    re.compile(r"\bthere\s+is\b", re.I | re.U): "there's",
    re.compile(r"\bthese\s+are\b", re.I | re.U): "these're",
    re.compile(r"\bthey\s+had\b", re.I | re.U): "they'd",
    re.compile(r"\bthey\s+would\b", re.I | re.U): "they'd",
    re.compile(r"\bthey\s+shall\b", re.I | re.U): "they'll",
    re.compile(r"\bthey\s+will\b", re.I | re.U): "they'll",
    re.compile(r"\bthey\s+are\b", re.I | re.U): "they're",
    re.compile(r"\bthey\s+have\b", re.I | re.U): "they've",
    re.compile(r"\bthis\s+has\b", re.I | re.U): "this's",
    re.compile(r"\bthis\s+is\b", re.I | re.U): "this's",
    re.compile(r"\bthose\s+are\b", re.I | re.U): "those're",
    re.compile(r"\bwas\s+not\b", re.I | re.U): "wasn't",
    re.compile(r"\bwe\s+had\b", re.I | re.U): "we'd",
    re.compile(r"\bwe\s+would\b", re.I | re.U): "we'd",
    re.compile(r"\bwe\s+would\s+have\b", re.I | re.U): "we'd've",
    re.compile(r"\bwe\s+will\b", re.I | re.U): "we'll",
    re.compile(r"\bwe\s+are\b", re.I | re.U): "we're",
    re.compile(r"\bwe\s+have\b", re.I | re.U): "we've",
    re.compile(r"\bwere\s+not\b", re.I | re.U): "weren't",
    re.compile(r"\bwhat\s+did\b", re.I | re.U): "what'd",
    re.compile(r"\bwhat\s+shall\b", re.I | re.U): "what'll",
    re.compile(r"\bwhat\s+will\b", re.I | re.U): "what'll",
    re.compile(r"\bwhat\s+are\b", re.I | re.U): "what're",
    re.compile(r"\bwhat\s+has\b", re.I | re.U): "what's",
    re.compile(r"\bwhat\s+is\b", re.I | re.U): "what's",
    re.compile(r"\bwhat\s+does\b", re.I | re.U): "what's",
    re.compile(r"\bwhat\s+have\b", re.I | re.U): "what've",
    re.compile(r"\bwhen\s+has\b", re.I | re.U): "when's",
    re.compile(r"\bwhen\s+is\b", re.I | re.U): "when's",
    re.compile(r"\bwhere\s+did\b", re.I | re.U): "where'd",
    re.compile(r"\bwhere\s+are\b", re.I | re.U): "where're",
    re.compile(r"\bwhere\s+has\b", re.I | re.U): "where's",
    re.compile(r"\bwhere\s+is\b", re.I | re.U): "where's",
    re.compile(r"\bwhere\s+does\b", re.I | re.U): "where's",
    re.compile(r"\bwhere\s+have\b", re.I | re.U): "where've",
    re.compile(r"\bwhich\s+has\b", re.I | re.U): "which's",
    re.compile(r"\bwhich\s+is\b", re.I | re.U): "which's",
    re.compile(r"\bwho\s+would\b", re.I | re.U): "who'd",
    re.compile(r"\bwho\s+had\b", re.I | re.U): "who'd",
    re.compile(r"\bwho\s+did\b", re.I | re.U): "who'd",
    re.compile(r"\bwho\s+would\s+have\b", re.I | re.U): "who'd've",
    re.compile(r"\bwho\s+shall\b", re.I | re.U): "who'll",
    re.compile(r"\bwho\s+will\b", re.I | re.U): "who'll",
    re.compile(r"\bwho\s+are\b", re.I | re.U): "who're",
    re.compile(r"\bwho\s+has\b", re.I | re.U): "who's",
    re.compile(r"\bwho\s+is\b", re.I | re.U): "who's",
    re.compile(r"\bwho\s+does\b", re.I | re.U): "who's",
    re.compile(r"\bwho\s+have\b", re.I | re.U): "who've",
    re.compile(r"\bwhy\s+did\b", re.I | re.U): "why'd",
    re.compile(r"\bwhy\s+are\b", re.I | re.U): "why're",
    re.compile(r"\bwhy\s+has\b", re.I | re.U): "why's",
    re.compile(r"\bwhy\s+is\b", re.I | re.U): "why's",
    re.compile(r"\bwhy\s+does\b", re.I | re.U): "why's",
    re.compile(r"\bwill\s+not\b", re.I | re.U): "won't",
    re.compile(r"\bwould\s+have\b", re.I | re.U): "would've",
    re.compile(r"\bwould\s+not\b", re.I | re.U): "wouldn't",
    re.compile(r"\byou\s+had\b", re.I | re.U): "you'd",
    re.compile(r"\byou\s+would\b", re.I | re.U): "you'd",
    re.compile(r"\byou\s+shall\b", re.I | re.U): "you'll",
    re.compile(r"\byou\s+will\b", re.I | re.U): "you'll",
    re.compile(r"\byou\s+are\b", re.I | re.U): "you're",
    re.compile(r"\byou\s+have\b", re.I | re.U): "you've",
}


class Contractions(object):
    """Expand and contract common English contractions in text.

    Uses a combination of pattern replacement, grammar checking, and Word Mover's Distance.
    """

    def __init__(self, w2v_path=None, lang_code='en-US'):
        """w2v_path is a path to an embedding model used for calculating the Word Mover's Distance."""
        self.w2v_path = w2v_path
        self.lang_code = lang_code
        self.w2v_model = None

    def load_models(self):
        if not os.path.exists(self.w2v_path):
            print("Word2Vec model not found at {}".format(self.w2v_path))
            sys.exit(1)
        try:
            self.w2v_model = KeyedVectors.load_word2vec_format(self.w2v_path, binary=True)
        except:
            print("Error loading Word2Vec model")
            raise

        try:
            self.lc_tool = language_check.LanguageTool(self.lang_code)
        except:
            print("Error initializing LanguageTool")
            raise

    def _expand_text(self, text):
        """Expand contractions in text using a faster but imprecise method"""
        for pattern, rep in simple_contractions.items():
            text = pattern.sub(rep, text)
        for pattern, options in contextual_contractions.items():
            if pattern.search(text):
                hyp = []
                for opt in options:
                    # Assumes all uses of the pattern are the same in one text which doesn't always hold
                    text1 = pattern.sub(opt, text)
                    hyp.append((text1, self.w2v_model.wmdistance(
                        text.split(), text1.split()), len(self.lc_tool.check(text1))))
                # The text of the first item is most likely correct
                text = sorted(hyp, key=lambda x: (x[2], x[1]))[0][0]
        return text

    def _expand_text_precise(self, text):
        """Expand contractions in text using a much slower but more precise method"""
        for pattern, rep in simple_contractions.items():
            text = pattern.sub(rep, text)
        for pattern, options in contextual_contractions.items():
            if pattern.search(text):
                hyp = []
                for perm_set in (set(permutations(comb)) for comb in combinations_with_replacement(options, len(options))):
                    for perm in perm_set:
                        text1 = text
                        for opt in perm:
                            text1 = pattern.sub(opt, text1, count=1)
                        hyp.append((text1, self.w2v_model.wmdistance(
                                    text.split(), text1.split()), len(self.lc_tool.check(text1))))
                # The text of the first item is most likely correct
                text = sorted(hyp, key=lambda x: (x[2], x[1]))[0][0]
        return text

    def expand_texts(self, texts, precise=False):
        """Return a generator over an iterable of text where each result has common contractions expanded"""
        if self.w2v_model is None:
            self.load_models()

        if precise:
            _fn = self._expand_text_precise
        else:
            _fn = self._expand_text

        for text in texts:
            yield _fn(text)

    def contract_texts(self, texts):
        """Return a generator over an iterable of text where each result has contracted common expansions"""
        for text in texts:
            for pattern, rep in expansions.items():
                text = pattern.sub(rep, text)
            yield text

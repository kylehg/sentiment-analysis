"""
Utilities for working with the DUC corpus.
Author: Kyle Hardgrave (kyleh@seas)
Date: 2012-11-14
"""
import os

WORDNET_ROOT = '/home1/k/kyleh/nlp/wordnet-affect-emotion-lists'



def get_emotion_words(emotion, wordnet_path=WORDNET_ROOT):
  """Return a set of the words representing an emotion."""
  with open(os.path.join(wordnet_path, '%s.txt' % emotion)) as f:
    return set(word for word in f.read().split() if not word[1] == '#')

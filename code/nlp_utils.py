"""
Some generally useful NLP funcitons.
Author: Kyle Hardgrave (kyleh@seas)
"""

from nltk.tokenize import sent_tokenize, word_tokenize


def get_sents(str_or_file):
  """Given a string for a file handler, return a list of tokenized
  sentences from that string/file."""
  try:
    str_or_file = str_or_file.read()
  except AttributeError:
    pass
  return sent_tokenize(str_or_file)


def get_words(str_or_file):
  """Given a string for a file handler, return a list of tokenized
  and lowercased words from that string/file."""
  return [word.lower()
          for sent in get_sents(str_or_file)
          for word in word_tokenize(sent)]


def normalize_whitespace(text):
  """Given a string, return that string with all the whitespace 
  replaced with a single space."""
  return ' '.join(text.trim().split())

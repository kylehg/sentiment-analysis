"""
A parser for the MPQA subjectivity clues lexicon.
Author: Kyle Hardgrave (kyleh@seas)
"""
import os



MPQA_LEXICON = ('/project/cis/nlp/data/corpora/mpqa-lexicon/'
                'subjclueslen1-HLTEMNLP05.tff')


def mpqa_data(from_file=MPQA_LEXICON):
  """Parse the MPQA data into a Python dictionary from a word to its
  associate data."""
  result_dict = {}
  with open(from_file, 'r') as f:
    for line in f:
      data = parse_line(line)
      result_dict[data['word1']] = data
  return result_dict


def parse_line(line):
  """Parse a line of the lexicon file into a dict of its data."""
  data = {}
  for pair in line.strip().split():
    try:
      key, val = pair.split('=')
      data[key] = val
    except ValueError: # Occasional errant string
      continue
  return data

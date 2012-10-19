"""
A parse for the MPQA subjectivity clues lexicon.
Found here: /project/cis/nlp/data/corpora/mpqa-lexicon
Author: Kyle Hardgrave (kyleh@seas)
"""
import os



CORPUS_ROOT = '/project/cis/nlp/data/corpora/mpqa-lexicon'
LEXICON_FILE = os.path.join(CORPUS_ROOT, 'subjclueslen1-HLTEMNLP05.tff')


def mpqa_data(from_file=LEXICON_FILE):
  """Parse the MPQA data into a Python dictionary."""
  result_dict = {}
  with open(from_file, 'r') as f:
    for line in f:
      word, data = parse_line(line)
      result_dict[word] = data
  return result_dict


def parse_line(line):
  """Parse a line of the lexicon file into a word and a dict of its data."""
  data = {}
  for pair in line.strip().split():
    try:
      key, val = pair.split('=')
      data[key] = val
    except ValueError: # Occasional errant string
      continue
  data['val'] = ((1 if data['type'] == 'weaksubj' else 2) * 
                 (1 if data['priorpolarity'] == 'positive' else -1))
  return data['word1'], data


if __name__ == '__main__':
  # TODO
  try:
    print "Loading MPQA lexicon from '%s'" % LEXICON_FILE
  except IOError:
    print "Error: Couldn't open file"

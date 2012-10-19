"""
Compare the human and machine summaries with the normal versions.
Author: Kyle Hardgrave (kyleh@seas)
"""
import re
from collections import defaultdict
from os import listdir
from os.path import join, isdir
from xml.dom.minidom import parse

from nltk.tokenize import sent_tokenize, word_tokenize


CORPUS_ROOT = '/project/cis/xtag2/DUC/DUC2001/data'
DOCS_ROOT = join(CORPUS_ROOT, 'test/docs/test')
SUMS_ROOT = join(CORPUS_ROOT, 'eval/see.models')
WORDNET_ROOT = '/home1/k/kyleh/nlp/wordnet-affect-emotion-lists'



def get_documents(root=DOCS_ROOT):
  """Return a map from topic id to documents."""
  return { folder: [doc for doc in listdir(join(root, folder))]
           for folder in listdir(root) if isdir(join(root, folder)) }


def get_doc_sents(filepath):
  """Return a list of sentence tokens in a XML DUC file."""
  dom = parse(filepath)
  text = dom.getElementsByTagName('TEXT')[0].firstChild.data
  # Only a single space between words.
  text = ' '.join(text.split())
  #headline = dom.getElementsByTagName('HEAD')[0].firstChild.data
  #return (text, sent_tokenize(text))
  return sent_tokenize(text)


def get_summaries(root=SUMS_ROOT):
  """Get all the summaries."""
  sums = {}
  for doc in listdir(root):
    docset, doctype = doc.split('.')[:2]
    docset = docset.lower()
    try:
      doc_dict = sums[docset]
    except KeyError:
      doc_dict = sums[docset] = { 'multidoc': [], 'singledoc': [] }
    if doctype == 'M':
      doc_dict['multidoc'] += [doc]
    else:
      doc_dict['singledoc'] += [doc]
  return sums


def get_words(sents):
  """Return a list of word tokens from a list of sentence tokens."""
  return [word for word in word_tokenize(sents)]


def get_doc_stats(words, emotion_words, sentiment_words):
  """Return a dictionaries of frequencies of different sentiment
  things in a document.

  num_words: int
  pos_strong: int
  pos_weak: int
  neg_strong: int
  neg_weak: int
  emotion_words: int
  anger_words: int
  disgust_words: int
  feat_words: int
  joy_words: int
  sadness_words: int
  surprise_words: int
  """
  doc_data = defaultdict(lambda: 0)
  for word in words:

    # Sentiment
    doc_data['num_words'] += 1
    try:
      sentiment_info = sentiment_words[word]
      if sentiment_info['val'] == 2:
        doc_data['pos_strong'] += 1
      elif sentiment_info['val'] == 1:
        doc_data['pos_weak'] += 1
      elif sentiment_info['val'] == -1:
        doc_data['neg_weak'] += 1
      elif sentiment_info['val'] == -2:
        doc_data['neg_strong'] += 1
    except KeyError:
      pass

    # Emotion
    if word in emotion_words['anger']:
      doc_data['anger_words'] += 1
    if word in emotion_words['disgust']:
      doc_data['disgust_words'] += 1
    if word in emotion_words['fear']:
      doc_data['fear_words'] += 1
    if word in emotion_words['joy']:
      doc_data['joy_words'] += 1
    if word in emotion_words['sadness']:
      doc_data['sadness_words'] += 1
    if word in emotion_words['surprise']:
      doc_data['surprise_words'] += 1
      


def get_emotion_words(emotion, wordnet_path=WORDNET_ROOT):
  """Return a set of the words representing an emotion."""
  with open(join(wordnet_path, '%s.txt' % emotion)) as f:
    return set(word for word in f.read().split() if not word[1] == '#')



def format_and_print_docset(docset):
  """Prepare a list of docs from a docset for annotating. Currently only
  inputs."""
  docset_path = join(DOCS_ROOT, 'd12b')
  for doc in listdir(docset_path):
    print "Writing %s" % doc
    with open('%s.txt' % doc, 'w') as f:
      for sent in get_doc_sents(join(docset_path, doc)):
        f.write(sent + '\n')


if __name__ == '__main__':
  pass
  

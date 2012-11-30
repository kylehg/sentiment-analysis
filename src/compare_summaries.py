"""
Compare the human and machine summaries with the normal versions.
Author: Kyle Hardgrave (kyleh@seas)
"""

import traceback
from collections import defaultdict, namedtuple
from os import listdir
from os.path import join, isdir

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from nltk.tokenize import sent_tokenize, word_tokenize

import duc
import mpqa
import r_utils
import wordnet

PROJECT_ROOT = '/project/cis/xtag2/DUC'
DUC2001 = make_duccorpus('2001', PROJECT_ROOT, 'data/test/docs/test',
                         'data/eval/see.models')
DUC2002 = make_duccorpus('2002', PROJECT_ROOT, 'data/test/docs/docs', 
                         ('results/abstracts/phase1/SEEmodels/'
                          'SEE.edited.abstracts.in.edus'))
DUC2003 = make_duccorpus('2003', PROJECT_ROOT, 'testdata/task4/docs', 
                         'results/SEE.duc2003.abstracts/models')
DUC2004 = make_duccorpus('2004', PROJECT_ROOT, 'testdata/tasks1and2/t1.2/docs',
                         'results/ROUGE/eval/models/2')


def get_documents(root):
  """Return a list of (docset_id, docset_docs) tuples, where
  docset_docs is a list of the document names in the given docset."""
  return sorted([(folder, [doc for doc in listdir(join(root, folder))])
                 for folder in listdir(root) if isdir(join(root, folder))])


def get_doc_sents(filepath):
  """Return a list of sentence tokens in a XML DUC file."""
  try:
    with open(filepath) as f:
      soup = BeautifulStoneSoup(f.read())
      tag = soup.findAll('text')[0].contents
      text = ' '.join([content.string for content in tag
                       if content.string is not None])
      text = ' '.join(text.split()) # Only a single space between words.
      return sent_tokenize(text)
  except Exception:
    print '**Trouble parsing doc', filepath
    print traceback.format_exc()
    return []



def get_summaries(docset, root):
  """Get all the summaries for a given docset."""
  return sorted([doc for doc in listdir(root)
                 if doc.startswith(docset.upper())])


def get_summary_sents(filepath):
  """Return a list of sentence tokens from a HTML summary file.
  Note: these aren't exactly real sentences, but we pretend they are."""
  try:
    with open(filepath) as f:
      soup = BeautifulSoup(f.read())
      tags = soup.body.findAll('a', href=True)
      text = ' '.join([tag.string for tag in tags
                       if tag.string is not None])
      return sent_tokenize(text)
  except Exception:
    print '**Trouble parsing summary', filepath
    print traceback.format_exc()
    return []


def format_and_print_docset(docset_root, docset):
  """Prepare a list of docs from a docset for annotating. Currently only
  inputs."""
  docset_path = join(docset_root, docset)
  for doc in listdir(docset_path):
    print "Writing %s" % doc
    with open('%s.txt' % doc, 'w') as f:
      for sent in get_doc_sents(join(docset_path, doc)):
        f.write(sent + '\n')


def get_docset_words(docset_id, docset_docs, docset_root):
  docset_path = join(docset_root, docset_id)
  return [word
          for doc in docset_docs
          for word in get_words(get_doc_sents(join(docset_path, doc)))]


def get_summary_words(docset_id, sums_root):
  """Return the tokenized words for summaries in a given docset."""
  return [word
          for summary in get_summaries(docset_id, sums_root)
          for word in get_words(get_summary_sents(join(sums_root, summary)))]


def get_words(sents):
  """Return a list of word tokens from a list of sentence tokens."""
  return [word for sent in sents for word in word_tokenize(sent)]


def get_doc_stats(words, emotion_words, sentiment_words):
  """Return a dictionaries of frequencies of different sentiment
  things in a document.

    word_count: int
    sentiment:
      count: int
      positive_count: int
      negative_count: int
      strongsubj_count: int
      weaksubj_count: int
      positive_weaksubj_count: int
      positive_strongsubj_count: int
      negative_weaksubj_count: int
      negative_strongsubj_count: int
    emotion:
      count: int
      anger_count: int
      disgust_count: int
      feat_count: int
      joy_count: int
      sadness_count: int
      surprise_count: int
  """
  doc_data = {
    'word_count': 0,
    'sentiment': defaultdict(lambda: 0),
    'emotion': defaultdict(lambda: 0),
    'words': defaultdict(lambda: set())
    }

  for word in words:
    doc_data['word_count'] += 1

    # Sentiment
    try:
      word_sentiments = sentiment_words[word]
    except KeyError:
      pass
    else:
      # Add the word and count it only once
      doc_data['words']['sentiment'].add(word)
      sentiment_stats['count'] += 1

      # A word may have multiple sentiments
      for strength, polarity in word_sentiments[1:]:
        sentiment_stats = doc_data['sentiment']
        sentiment_stats['%s_count' % polarity] += 1
        sentiment_stats['%s_count' % strength] += 1
        sentiment_stats['%s_%s_count' % (polarity, strength)] += 1


    # Emotion
    for emotion, emotion_word_set in emotion_words.iteritems():
      if word in emotion_word_set:
        doc_data['emotion']['count'] += 1
        doc_data['emotion']['%s_count' % emotion] += 1
        doc_data['words']['emotion'].add(word)
        break

  return doc_data


def get_two_stats_vectors(roots):
  emotion_words = {emotion: wordnet.get_word_emotion_map()
                     for emotion in ['anger', 'disgust', 'fear', 'joy',
                                     'sadness', 'surprise']}
  sentiment_words = mpqa.get_word_sentiment_map()
  doc_stats, summary_stats = [], []
  for docs_root, sums_root in roots:
    docsets = get_documents(docs_root)

    for docset_id, docset_docs in docsets:
      doc_vector = get_doc_stats(
        get_docset_words(docset_id, docset_docs, docs_root),
        emotion_words, sentiment_words)
      doc_stats.append(doc_vector)
      summary_vector = get_doc_stats(
        get_summary_words(docset_id[:-1], sums_root), emotion_words,
        sentiment_words)
      summary_stats.append(summary_vector)


  return doc_stats, summary_stats




if __name__ == '__main__':
  docs, summaries = get_two_stats_vectors([(DOCS_ROOT01, SUMS_ROOT01)])
#                                           (DOCS_ROOT02, SUMS_ROOT02),
#                                           (DOCS_ROOT03, SUMS_ROOT03)])

  sentiment_args =  ['count', 'negative_count', 'negative_weaksubj_count',
                     'negative_strongsubj_count', 'positive_count',
                     'positive_weaksubj_count', 'positive_strongsubj_count']
  emotion_args = ['count', 'anger_count', 'disgust_count', 'fear_count',
                  'joy_count', 'sadness_count', 'surprise_count']

  # Sentiment
  print '# Sentiment'
  for sentiment_type in sentiment_args:
    print sentiment_type
    print 'Docs', [float(doc['sentiment'][sentiment_type]) / doc['word_count']
                   for doc in docs]
    print 'Summaries', [(float(summary['sentiment'][sentiment_type]) /
                         summary['word_count'])
                        for summary in summaries]
    print
  print

  # Emotion
  print '# Emotion'
  for emotion_type in emotion_args:
    print emotion_type
    print 'Docs', [float(doc['emotion'][emotion_type]) / doc['word_count']
                   for doc in docs]
    print 'Summaries',  [(float(summary['emotion'][emotion_type]) /
                          summary['word_count'])
                         for summary in summaries]
  print 'Done'

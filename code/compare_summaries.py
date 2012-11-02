"""
Compare the human and machine summaries with the normal versions.
Author: Kyle Hardgrave (kyleh@seas)
"""
from collections import defaultdict
from os import listdir
from os.path import join, isdir
from pprint import pprint
from xml.dom.minidom import parse

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from nltk.tokenize import sent_tokenize, word_tokenize

from parse_mpqa import mpqa_data


CORPUS_ROOT = '/project/cis/xtag2/DUC/DUC2001/data'
DOCS_ROOT = join(CORPUS_ROOT, 'test/docs/test')
SUMS_ROOT = join(CORPUS_ROOT, 'eval/see.models')
WORDNET_ROOT = '/home1/k/kyleh/nlp/wordnet-affect-emotion-lists'



def get_documents(root=DOCS_ROOT):
  """Return a map from topic id to documents."""
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
    raise


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
    raise


def get_summaries(docset, root=SUMS_ROOT):
  """Get all the summaries."""
  return [join(root, doc)
          for doc in listdir(root) if doc.startswith(docset.upper())]


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
    'emotion': defaultdict(lambda: 0)
    'words': {
      'emotion': defaultdict(lambda: set()),
      'sentiment': defaultdict(lambda: set())
      }
    }

  for word in words:
    # Sentiment
    doc_data['word_count'] += 1
    try:
      word_sentiment = sentiment_words[word]
      strength = word_sentiment['type']
      polarity = word_sentiment['priorpolarity']

      sentiment_stats = doc_data['sentiment']
      sentiment_stats['count'] += 1
      sentiment_stats['%s_count' % polarity] += 1
      sentiment_stats['%s_count' % strength] += 1
      sentiment_stats['%s_%s_count' % (polarity, strength)] += 1

      doc_data['words']['sentiment'].add(word)
    except KeyError:
      pass

    # Emotion
    for emotion, emotion_word_set in emotion_words.iteritems():
      if word in emotion_word_set:
        doc_data['emotion']['count'] += 1
        doc_data['emotion']['%s_count' % emotion] += 1
        doc_data['words']['emotion'].add(word)
        break

  return doc_data


def get_emotion_words(emotion, wordnet_path=WORDNET_ROOT):
  """Return a set of the words representing an emotion."""
  with open(join(wordnet_path, '%s.txt' % emotion)) as f:
    return set(word.replace('_', ' ')
               for word in f.read().split() if not word[1] == '#')


def format_and_print_docset(docset):
  """Prepare a list of docs from a docset for annotating. Currently only
  inputs."""
  docset_path = join(DOCS_ROOT, docset)
  for doc in listdir(docset_path):
    print "Writing %s" % doc
    with open('%s.txt' % doc, 'w') as f:
      for sent in get_doc_sents(join(docset_path, doc)):
        f.write(sent + '\n')


def get_docset_words(docset_id, docset_docs):
  docset_path = join(DOCS_ROOT, docset_id)
  return [word
          for doc in docset_docs
          for word in get_words(get_doc_sents(join(docset_path, doc)))]

def get_summary_words(docset_id):
  return [word
          for summary_path in get_summaries(docset_id)
          for word in get_words(get_summary_sents(summary_path))]

def get_two_stats_vectors():
  emotion_words = {emotion: get_emotion_words(emotion)
                   for emotion in ['anger', 'disgust', 'fear', 'joy',
                                   'sadness', 'surprise']}
  sentiment_words = mpqa_data()

  docsets = get_documents()
  doc_stats, summary_stats = [], []
  
  for docset_id, docset_docs in docsets:
    doc_stats.append(get_doc_stats(get_docset_words(docset_id, docset_docs),
                                   emotion_words, sentiment_words))
    summary_stats.append(get_doc_stats(get_summary_words(docset_id[:-1]),
                                       emotion_words, sentiment_words))

  return doc_stats, summary_stats




if __name__ == '__main__':
  docs, summaries = get_two_stats_vectors()
  
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

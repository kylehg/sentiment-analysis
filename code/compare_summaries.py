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
  return { folder: [doc for doc in listdir(join(root, folder))]
           for folder in listdir(root) if isdir(join(root, folder)) }


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
      text = ' '.join([tag.string for tag in tags])
      return sent_tokenize(text)
  except Exception:
    print '**Trouble parsing summary', filepath
    raise


def get_summaries(docset, root=SUMS_ROOT):
  """Get all the summaries."""
  return [doc for doc in listdir(root) if doc.startswith(docset.upper())]


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
    except KeyError:
      pass

    # Emotion
    for emotion, emotion_word_set in emotion_words.iteritems():
      if word in emotion_word_set:
        doc_data['emotion']['count'] += 1
        doc_data['emotion']['%s_count' % emotion] += 1
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
  docset_path = join(DOCS_ROOT, 'd12b')
  for doc in listdir(docset_path):
    print "Writing %s" % doc
    with open('%s.txt' % doc, 'w') as f:
      for sent in get_doc_sents(join(docset_path, doc)):
        f.write(sent + '\n')



if __name__ == '__main__':
  emotion_words = {emotion: get_emotion_words(emotion)
                   for emotion in ['anger', 'disgust', 'fear', 'joy',
                                   'sadness', 'surprise']}
  sentiment_words = mpqa_data()

  docsets = get_documents()
  def get_docset_words(docset_id, docset_docs):
    docset_path = join(DOCS_ROOT, docset_id)
    return [word
            for doc in docset_docs
            for word in get_words(get_doc_sents(join(docset_path, doc)))]
  doc_stats = [get_doc_stats(get_docset_words(docset_id, docset_docs),
                             emotion_words, sentiment_words)
              for docset_id, docset_docs in docsets.iteritems()]
  pprint(doc_stats)

#
#              for docset_id in docsets.iterkeys()]
#
#  fp = '/project/cis/xtag2/DUC/DUC2001/data/test/docs/d12b/AP880903-0092'
#  print get_doc_stats(get_words(get_doc_sents(fp)), emotion_words,
#                      sentiment_words)


"""
Utilities for working with the DUC corpus.
Author: Kyle Hardgrave (kyleh@seas)
Date: 2012-11-14
"""

import traceback
from collections import namedtuple
from os import listdir
from os.path import join, isdir

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

from nlp_utils import get_words, normalize_whitespace


# A DUC corpus from a given year:
#   year: The year string
#   docs_path: The full path to the docsets
#   sums_path: The full path to the summaries
DucCorpus = namedtuple('DucCorpus', ['year', 'doc_path', 'sum_path'])

# A docset within a given DUC corpus
#   id: The docset ID, sans author letter, e.g., 'd17'
#   docs: An (ordered) list of the full paths of the docset docs.
#   sums: An (ordered) list of the full paths of the docset summaries.
DocSet = namedtuple('DocSet', ['id', 'docs', 'sums'])


def make_duccorpus(year, project_root, docs_dir, sums_dir):
  """Make a DucCorpus given a project root, year, and paths to the
  documents and summaries."""
  root = join(project_root, 'DUC' + year)
  return DucCorpus(year, join(root, docs_dir), join(root, sums_dir))


def make_docset(corpus, docset_id):
  """Given a DucCorpus and a docset_id string, return the
  corresponding DocSet."""
  docs = [join(corpus.doc_path, docset_id, doc)
          for doc in listdir(join(corpus.doc_path, docset_id))]
  sums = [join(corpus.sum_path, summary)
          for summary in listdir(corpus.sum_path)
          if summary.startswith(docset_id[:-1].upper())]
  return DocSet(docset_id, sorted(docs), sorted(sums))


def get_docsets(corpus):
  """Given a DucCorpus, return an ordered list of DocSets."""
  return sorted([make_docset(corpus, docset_id)
                 for docset_id in listdir(corpus.doc_path)])


def get_doc_sums(docset, doc_id, multidoc=False):
  """Given a docset and a document id, return a list of the full paths
  of its corresponding summaries (possibly including multidocs)."""
  return sorted([sumary for summary in docset.sums
                 if ((basename(summary) == doc_id + '.html') or
                     (multidoc and basename(summary).split('.')[1] == 'M'))])


def get_doc_words(doc_path):
  """Given a document file path, return a list of words in that document."""
  try:
    with open(filepath) as f:
      soup = BeautifulStoneSoup(f.read())
      tag = soup.findAll('text')[0].contents
      text = ' '.join([content.string for content in tag
                       if content.string is not None])
      return get_words(normalize_whitespace(text))
  except Exception:
    print '**Trouble parsing doc', filepath
    raise


def get_sum_words(sum_path):
  """Given a summary file path, return a list of words in that summary."""
  raise NotImplementedError



if __name__ == '__main__':
  import doctest
  doctest.testfile('test_duc.txt')

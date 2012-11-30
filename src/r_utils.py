"""
Utilities for working with R.
Author: Kyle Hardgrave (kyleh@seas)
"""


def make_r_vector(vector, name=None):
  """Given an iterable and an optional name, return a string that
  can be used as a vector in R.

  v = (1, 2, 3, 4)
  >>> make_r_vector(v)
  "c(1, 2, 3, 4)"
  >>> make_r_vector(v, 'my_vector')
  "my_vector <- c(1, 2, 3, 4)"
  """
  csv = ', '.join(vector)
  if name:
    return '%s <- c(%s)' % (name, csv)
  else:
    return 'c(%s)' % csv

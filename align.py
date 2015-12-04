#!/usr/bin/python

"""Align columns of tabular CSV data, truncating fields where nessecary.

Example:

  $ align.py <<EOF
  aa,a,aaa
  b,bbb,bb
  ccc,cc,c
  EOF

  aa   a    aaa
  b    bbb  bb
  ccc  cc   c
"""

import csv
import curses
import optparse
import sys

from itertools import imap, starmap, izip_longest


def ScreenWidth():
  """Return current width of terminal screen (number of columns)."""
  curses.setupterm()
  return curses.tigetnum('cols')


def LongestFields(table):
  """Return list of longest field length in each column."""
  widths = ()
  for row in table:
    widths = starmap(max, izip_longest(widths, imap(len, row), fillvalue=0))
  return list(widths)


def MaxWidth(screen_width, column_widths):
  """Calculate width at which to truncate fields in order to fit rows on screen.

  Args:
    screen_width: terminal screen width in number of columns.
    column_widths: list of widths for each column of the table.

  Returns:
    Longest displayable field width.
  """
  n = len(column_widths)
  limit = screen_width - (n - 1) * 2
  col = 0
  column_widths = sorted(column_widths)
  for i in xrange(n):
    if col + (n - i) * column_widths[i] > limit:
      return (limit - col) / (n - i)
    col += column_widths[i]

  return screen_width


def Format(table, column_widths, max_width):
  """Format tabular table as aligned lines.

  Args:
    table: list of rows, each row a list of fields.
    width: width of each column (== length of longest field in each column).
    max_width: longest displayable field width.

  Returns:
    Sequence of lines, each representing a formatted row of the table.
  """
  column_widths = [min(w, max_width) for w in column_widths]

  def FormatRow(row):
    for i in xrange(len(row)):
      if len(row[i]) > max_width:
        yield '%s..  ' % row[i][:max_width-2]
      else:
        yield row[i].ljust(column_widths[i] + 2)

  for row in table:
    yield ''.join(FormatRow(row))


def ParseArgs():
  """Process command line arguments."""
  parser = optparse.OptionParser("usage: %prog [-d delim] [-w width]")

  parser.add_option('-d', '--delimiter', dest='delimiter', default=',',
                    help='field delimiter to use.')

  parser.add_option('-w', '--screen-width', type='int', dest='screen_width',
                    default=None, help='screen width.')

  return parser.parse_args()


def main():
  options, _ = ParseArgs()
  try:
    table = [row for row in csv.reader(sys.stdin, delimiter=options.delimiter)]
    column_widths = LongestFields(table)
    screen_width = options.screen_width if options.screen_width else ScreenWidth()
    max_width = MaxWidth(screen_width, column_widths)

    for line in Format(table, column_widths, max_width):
      print line

  except (ValueError, IOError, OSError) as err:
    sys.stderr.write('%s\n', err)


if __name__ == '__main__':
    main()

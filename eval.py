#!/usr/bin/python3
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

"""
This program is to compute the accuracy, given a file containing your results
and a file containing the correct results.
"""

if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " file-containing-your-results file-containing-correct-results")
    sys.exit(2)

correct = 0
cnt = 0

fh1_lines = open(sys.argv[1]).readlines()
fh2_lines = open(sys.argv[2]).readlines()

if len(fh1_lines) != len(fh2_lines):
    print("WARNING: The two files do not have same number of lines!")
    print("Your output has %d lines while the answer has %d lines" % (len(fh1_lines), len(fh2_lines)))

for i in range(len(fh1_lines)):
    line1 = fh1_lines[i]
    line2 = fh2_lines[i]

    res1 = line1.split()[0]
    res2 = line2.split()[0]
    cnt += 1
    if res1 == res2:
        correct += 1

acc = correct * 100.0 / cnt
print("accuracy: %s / %s (%s%%)" % (correct, cnt, round(acc, 2)))

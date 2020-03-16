#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re
import nltk
import sys
import getopt
import math
import copy
import time

WINDOW_SIZE = 4
dict_label = {'malaysian': 0, 'indonesian': 0, 'tamil': 0}

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')
    start = time.time()
    # Language model
    dict_lm = {} 
    input_file = open(in_file, 'r')
    for line in input_file:
        [label, text] = line.split(' ', 1)
        # Generate 4-gram phrase
        strings = []
        # Q1: delete Period at end of the sentence?
        for i in range(len(text)-WINDOW_SIZE):
            strings.append(text[i: i + WINDOW_SIZE])
        # Count the phrase and feed them into language model
        for string in strings:
            if string not in dict_lm:
                # Initialize the language model
                dict_lm[string] = {}
                for tmp_label in dict_label:  
                    dict_lm[string][tmp_label] = 0
                dict_lm[string][label] = 1
            else:
                dict_lm[string][label] += 1
    input_file.close()
    # Calculate the total word count of each language
    for key, value in dict_lm.items():
        for key_l in dict_label:
            dict_label[key_l] += dict_lm[key][key_l]
    add_one = len(dict_lm)  # add-one smoothing
    dict_lm_pro = copy.deepcopy(dict_lm) # Use probability instead of count
    for key, value in dict_lm_pro.items():
        for key_l in dict_label:
            dict_lm_pro[key][key_l] = (dict_lm[key][key_l] + 1)/(add_one + dict_label[key_l]) # Formula told on lecture
    end = time.time()
    print('build language models successfully')
    print('execution time: '+ str(end-start)+ 's')
    return (dict_lm_pro)

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    input_file = open(in_file, 'r')
    output_file = open(out_file, 'w')
    # threshold of extraterrestrial aliens
    threshold = 0.5
    for line in input_file:
        label_pro = {'malaysian': 0, 'indonesian': 0, 'tamil': 0}
        strings = []
        miss_count = 0
        # Generate 4-gram phrase
        for i in range(len(line)-WINDOW_SIZE):
            strings.append(line[i: i + WINDOW_SIZE])
        # Calculate the probability
        for string in strings:
            # Ignore if phrase got absent
            if string not in LM:
                miss_count += 1
                continue
            # Use log instead of multiply
            for key in dict_label:
                label_pro[key] += math.log(LM[string][key])
        miss_pro = miss_count / len(strings)
        if miss_pro > threshold:
            result = "other"
        else:
            # Select the maximum of three languages
            result = sorted(
                label_pro.items(), key=lambda label_pro: label_pro[1], reverse=True)[0][0]
        output_file.write(result + " " + line)
    input_file.close()
    output_file.close()
    print('test language models successfully')


def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)

#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from search_engine import SearchEngine

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # initialize the class
    search_engine = SearchEngine('dictionary.txt', 'postings.txt')

    with open(queries_file, 'r') as file, \
         open(results_file, 'w') as file_result:
        i = 0
        lines = file.readlines()
        for line in lines:            
            i = i + 1
            # get result and convert it to string
            result = search_engine.search(line)
            result = map(str, result)
            if i == len(lines):
                str1 = ' '.join(result)
            else:
                str1 = ' '.join(result) + '\n'

            # save the result to file
            file_result.write(str1)

    return

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)

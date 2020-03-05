#!/usr/bin/python3

import sys
import math
import array
import numpy as np
from enum import Enum
from inverted_index import InvertedIndex
from nltk.stem.porter import PorterStemmer

class OpType(Enum):
    NOT = 0
    AND = 1
    OR = 2
    AND_NOT = 3
    OR_NOT = 4
    
class SearchEngine:
    """ SearchEngine is a class dealing with real-time querying

    Args:
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings
    """
    
    precedence = { 'NOT': 0, 'AND': 1, 'OR': 2, '(': 4, ')': 5 }
    def __init__(self, dictionary_file, postings_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.index = InvertedIndex(dictionary_file, postings_file)
        self.doc_set, self.dictionary = self.index.LoadDict()
        self.skip_pointers = self.index.LoadSkippointers()
        self.total_postings = np.array(list(self.doc_set), dtype = np.int32)

    """ search and return docIds according to the boolean expression

    Args: 
        expr: the boolean expression

    Returns:
        docIds: the list of docIds which match the query in increasing order
    """
    def search(self, expr):
        # get the tokens from the expr
        terms, tokens = self._parse_expr(expr)
        terms.append('  ')

        # get the posting lists from the InvertedIndex class
        # postings = self.index.LoadTerms(terms)
        postings_lists = self.index.LoadTerms(terms)

        # execute the boolean operations in the expr by group
        group_no = 0
        last_type = False
        exec_stack = []

        tokens.append('  ')
        for token in tokens:
            if token == OpType.NOT:
                if type(exec_stack[-1]) == OpType:
                    group_no += 1
                    self._exec_group(group_no, exec_stack, postings_lists)
                exec_stack[-1][1] = not exec_stack[-1][1]
                last_type = False
                continue

            cur_type = token == OpType.AND or token == OpType.OR
            same = token == exec_stack[-1] if exec_stack else False
            
            if last_type and not same:
                group_no += 1
                self._exec_group(group_no, exec_stack, postings_lists)

            if cur_type:
                exec_stack.append(token)
            else:
                exec_stack.append([token, False, 0])
                
            last_type = cur_type

        # return the list of docIds
        return self._get_postings(exec_stack[0], postings_lists)[0]

    """ exec a group of boolean operations

    Args:
        group_no: the no. of the group
        exec_stack: the stack holds operations and terms
        postings_lists: the dictionary with terms to posting lists mapping
    """
    def _exec_group(self, group_no, exec_stack, postings_lists):
        assert exec_stack, 'empty execution stack'

        terms = []
        term_num = 1
        op = exec_stack[-1]
        while exec_stack and term_num:
            last = exec_stack[-1]
            if type(last) == OpType:
                term_num += 1
            else:
                term_num -= 1
                terms.append(last)
                
            exec_stack.pop()
            
        # change the execution order
        self._optimize_merge(op, terms, postings_lists)

        # merge the posting lists
        result = self._merge_group(op, terms, postings_lists)

        # add the intermediate term
        exec_stack.append(['  %d'%group_no, False, 0])
        postings_lists['  %d'%group_no] = result

    """ optimize the merging process based on merging cost

    Agrs:
        op: the type of merging operation
        terms: the terms need to be merged
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
        terms: the list in optimized merging order
    """
    def _optimize_merge(self, op, terms, postings_lists):
        total_size = self.total_postings.size

        flag = False
        min_pos = 0
        total_max_pos = 0
        total_min_pos = 0
        min_cost = total_size + 1
        for i, term in enumerate(terms):
            term[2] = postings_lists[term[0]][0].size
            if op == OpType.OR:
                if term[1]:
                    term[2] = total_size - term[2]
            else:
                if term[2] < terms[total_min_pos][2]:
                    total_min_pos = i
                if term[2] > terms[total_max_pos][2]:
                    total_max_pos = i
                if not term[1] and term[2] < terms[min_pos][2]:
                    min_pos = i
                    flag = True

        if op == OpType.AND:
            if terms[total_min_pos][1]:
                if not flag:
                    min_pos = total_max_pos
                terms[min_pos][2] = -1

        terms.sort(key=lambda key: key[2])
        return terms

    """ merge the terms based on the order of the terms in the list

    Args:
        op: the type of merging operation
        terms: the list of terms to be merged
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
        result: return the merged list of the terms
    """
    def _merge_group(self, op, terms, postings_lists):
        # get the fisrt postings list
        result_set = self._get_postings(terms[0], postings_lists)

        for i in range(1, len(terms)):
            # optimize merging when list is empty
            if result_set[0].size == 0:
                if op == OpType.AND:
                    return result_set
                elif op == OpType.OR:
                    result_set = self._get_postings(terms[i], postings_lists)
                    continue

            # optimize and not operation
            exec_op = op
            if op == OpType.AND and terms[i][1]:
                terms[i][1] = False
                exec_op = OpType.AND_NOT

            # get right set
            right_set = self._get_postings(terms[i], postings_lists)

            # merge the postings lists
            result_set = self._merge_postings(result_set, exec_op, right_set)

        return result_set

    """ merge the two sets passed in based on the op type

    Args:
        op: the type of merging operation
        set1: the set on the left hand side to be merged
        set2: the set on the right hand side to be merged
    """
    def _merge_postings(self, set1, op, set2):
        p1, p2 = 0, 0
        skip1, skip2 = 0, 0
        postings1, pointers1 = set1[0], set1[1]
        postings2, pointers2 = set2[0], set2[1]
        len1, len2 = postings1.size, postings2.size
        result = array.array('i')

        def f1(doc, p, skip, postings, pointers):
            if skip < pointers.size - 1 and p == pointers[skip]:
                skip += 1
                if postings[pointers[skip]] <= doc:
                    return pointers[skip], skip
            return p + 1, skip

        def f2(doc, p, skip, postings, pointers):
            if skip < pointers.size - 1 and p == pointers[skip]:
                skip += 1
                if postings[pointers[skip]] <= doc:
                    for i in range(p+1, pointers[skip]):
                        result.append(postings[i])
                    return pointers[skip], skip
            return p + 1, skip

        def f3(p, length, postings):
            while p < length:
                result.append(postings[p])
                p += 1

        if op == OpType.AND:
            while p1 < len1 and p2 < len2:
                doc1, doc2 = postings1[p1], postings2[p2]
                if doc1 == doc2:
                    result.append(doc1)
                    p1, p2 = p1 + 1, p2 + 1
                elif doc1 < doc2:
                    p1, skip1 = f1(doc2, p1, skip1, postings1, pointers1)
                else:
                    p2, skip2 = f1(doc1, p2, skip2, postings2, pointers2)
        elif op == OpType.AND_NOT:
            while p1 < len1 and p2 < len2:
                doc1, doc2 = postings1[p1], postings2[p2]
                if doc1 < doc2:
                    result.append(doc1)
                    p1, skip1 = f2(doc2, p1, skip1, postings1, pointers1)
                elif doc1 == doc2:
                    p1, p2 = p1 + 1, p2 + 1
                else:
                    p2, skip2 = f1(doc1, p2, skip2, postings2, pointers2)
            f3(p1, len1, postings1)
        elif op == OpType.OR:
            while p1 < len1 and p2 < len2:
                doc1, doc2 = postings1[p1], postings2[p2]
                if doc1 == doc2:
                    result.append(doc1)
                    p1, p2 = p1 + 1, p2 + 1
                elif doc1 < doc2:
                    result.append(doc1)
                    p1, skip1 = f2(doc2, p1, skip1, postings1, pointers1)
                else:
                    result.append(doc2)
                    p2, skip2 = f2(doc1, p2, skip2, postings2, pointers2)
            f3(p1, len1, postings1)
            f3(p2, len2, postings2)

        result = np.frombuffer(result, dtype=np.int32)
        return (result, self.index.GetSkipPointers(result.size))

    """ get the postings list of the term

    Args:
        term: the term which wants to the corresponding postings list
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
        postings: the postings list corresponding to the term
    """
    def _get_postings(self, term, postings_lists):
        # get postings_list if there is not NOT operation
        if not term[1]:
            return postings_lists[term[0]]

        not_term = '~' + term[0]
        if not_term in postings_lists:
            return postings_lists[not_term]
        else:
            postings = postings_lists[term[0]][0]
            postings = np.setdiff1d(self.total_postings, postings)
            postings = (postings, self.index.GetSkipPointers(postings.size))
            postings_lists[not_term] = postings
            return postings

    """ parse the query based on the Shunting-yard algorithm

    Args: 
        expr: the boolean expression

    Returns:
        terms: a list contains all the terms appeared in the boolean expression
        postfix_expr: a list of operations and operands which knowns as Reverse Polish notation
    """
    def _parse_expr(self, expr):
        parenthese = 0
        op_stack = []
        output_stack = []
        precedence = SearchEngine.precedence
        porter_stemmer = PorterStemmer()

        terms = set()
        tokens = self._tokenize_expr(expr)
        for token in tokens:
            if token == '(':
                op_stack.append(token)
                parenthese += 1
                continue
            if token == ')':
                assert parenthese > 0, "wrong query expression, parentheses are not matched"

                while op_stack[-1] != '(':
                    op = OpType[op_stack.pop()]
                    output_stack.append(op)

                parenthese -= 1
                op_stack.pop()
            elif token in precedence:
                while len(op_stack) and precedence[token] > precedence[op_stack[-1]]:
                    op = OpType[op_stack.pop()]
                    output_stack.append(op)

                op_stack.append(token)
            else:
                token = porter_stemmer.stem(token).lower()
                output_stack.append(token)
                terms.add(token)

        while len(op_stack):
            op = OpType[op_stack.pop()]
            output_stack.append(op)

        return list(terms), output_stack

    """ tokenize the expr into tokens

    Args:
        expr: the expr to be tokenized

    Returns:
        tokens: the list of tokens
    """
    def _tokenize_expr(self, expr):
        start = 0
        tokens = []

        for i, c in enumerate(expr):
            if str.isspace(c) or c == '(' or c == ')':
                if start != i:
                    tokens.append(expr[start:i])
                if c == '(' or c == ')':
                    tokens.append(c)

                start = i + 1

        if start < len(expr):
            tokens.append(expr[start:])

        return tokens

if __name__ == '__main__':

    search_engine = SearchEngine('dictionary.txt', 'postings.txt')
    print(search_engine.search('grower AND NOT relief'))

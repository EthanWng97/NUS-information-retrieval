This is the README file for A0213835H-A0214251W's  submission

== Python Version ==

We're using Python Version 3.7.4 and 3.7.6 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

We divide the whole program into two parts, the construction part and the search
part. The former is to build the inverted index, build the skip pointers corresponding
to the postings and save the index into file. The latter is to load the inverted index,
parse the boolean expression query, search all the documents that meet the expression and
save the results into file. We adopt the object-oriented programming approach to build
the whole project, which greatly reduces the coupling between two parts.

[Index]
As for the index part, we use the following steps to process a request.
Build Index:
    1. Read every line within each file in the directory and do tokenization, stemming.
    2. Add the cleaned tokens to the dictionary and the doc id to the postings list
    3. Create every single skip pointer list according to the length of the total_doc.
	We do this because of two reasons:
	    1. reduce redundancy of each word when creating posting list. (words with the same doc frequency have same skip pointers).
	    2. no create too many intermediate skip pointer list when do searching.

Save to File:
    1. Save all skip pointer list to posting file
    2. Read the postings, then sort the posting list of each word, save this to file and record the position in the file
    3. After saving postings, save the total doc id and the dictionary including words and position in the postings file to dictionary file.

Load Postings:
    1. Seek the position from dictionary file of word.
    2. Load the posting of word
    3. Operate the length of posting to generate skip pointers

[Search]
As for the search part, we use the following steps to process a request.
   1. Parse the query string based on the Shunting-yard algorithm,
      we will get a list of operations and operands which are known as Reverse Polish notations.
   2. Load postings lists for the terms in the expression from the postings.txt file.
      For terms that appear multiple times in the query, we just load once to reduce memory cost.
   3. Divide the boolean expression into multiple groups based on the parsing result,
      each group contains only one type of boolean operation such as AND, OR. NOT operation
      won't be executed immediately because calculating the complement is very expensive.

      [For each group]: e.g. (aaa AND bbb AND ~ccc)    ~ccc = NOT ccc
                             (aaa OR ~bbb OR ~ccc)
      3.1 We will calculate the cost of merging. For the complement of the postings list,
          the cost is the total number of documents minus the postings list length. Since we
	  handled the and not operations separately, the cost of the complement equals to
	  the length of the list when the group's operation is AND.
      3.2 After we get the cost of each term, we will change the order of terms to reduce the
          time complexity of merging based on the cost of each term.
      3.3 Then we will merge all the terms in the group in the optimized order.
          3.3.1 For the term that needs to perform NOT operation, we will do it at this step.
	  3.3.2 We optimize the merging process by processing the empty postings list separately,
	        which will reduce the unnecessary copies, e.g. [] OR [1, 2, 3, 4, 5].
	  3.3.3 We deal with the AND NOT operation separately because it can be done in linear
	        time complexity. We also implement the skip pointers to accelerate the merging.
   4. After we get the result of the group, we add the result term into the rest boolean expression
      and keep on executing until we get the final result of the expression.
   5. Print the final result and go to the next query.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

* inverted_index.py: The file contains the InvertedIndex class which helps to build, load and dump the inverted index.
* search_index.py: The file contains the SearchEngine class which helps to search the result of the boolean expression query.
* index.py: The file in this assignment using InvertedIndex to build the index and dump to file.
* search.py: The file in this assignment using SearchEngine to get the result of the boolean expression query.
* README.txt: This file contains this sentence which gives an overview of this assignment.
* ESSAY.txt: This file contains essay questions mentioned on HW#2

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0214251W-A0213835H, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

* Complete all the requirements
* Good programming habits, clear comments
* Good performance:
  * Try our best to avoid complementing postings list
  * Avoid frequent copying data by processing empty lists separately.
  * Optimize AND NOT operation separately.
  * Avoid loading same term multiple times to save time and space
  * Set total skip pointer list instead each word to speed up indexing and searching

== References ==

* [To search some Python functions](https://devdocs.io/python/)
* [Numpy Reference](https://docs.scipy.org/doc/numpy/reference/)
* [NLTK API](https://www.nltk.org/api/nltk.html)
* [Shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm)

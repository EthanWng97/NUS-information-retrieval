This is the README file for E0509874's submission

== Python Version ==

I'm (We're) using Python Version 3.7.6 for this assignment.
Also 3.6.9 on the Google Colab

== General Notes about this assignment ==

1. In the beginning, I'd like to use a 2D-list to store the data, then I found that I cannot use indices as a string(name of each element) to find the data. Finally using dictionary instead to solve the problem.
`TypeError: list indices must be integers or slices, not str`
2. During the building phase, I set WINDOW_SIZE to generate a 4-gram phrase and them count them, feeding them into a language model mentioned in the slides. 
    Afterward, I calculate the total word of each language and add-one smoothing to formulate the probability of each phrase which is the final progress of the language model.
3. As for the testing phase, after generating a 4-gram phrase from testing text, I use math.log instead of multiply to solve the 0*0.1 problem. 
    To classify the "other" text, I set a miss_count and threshold and get 100% accuracy when evaluating the program.Essay questions

== Files included with this submission ==

build_test_LM.py    # source code
ESSAY.txt           # Essay questions
README.txt          # overview of HW #1

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, E0509874, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, E0509874, did not follow the class rules regarding homework
assignment, because of the following reason:

I suggest that I should be graded as follows:

<Please fill in>

== References ==

https://nlp.stanford.edu/IR-book/html/htmledition/language-models-for-information-retrieval-1.html


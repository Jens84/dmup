# -*- coding: utf-8 -*-

"""Module that handles pickle objects.

Functions:
save_object -- save a pickle object
load_object -- load an object from a pickle file
update_classifiers -- train a classifier and save it as pickle object
"""

import cPickle as pickle
import os
import dialog
import markov


def save_object(obj, filename):
    """Save pickle object with specified name.

    Arguments:
    obj -- object to be saved into a pickle file
    filename -- desired name of the pickle file to be saved

    Return values:
    -
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(__location__, filename)

    with open(path, 'wb') as output:
        pickle.dump(obj, output)


def load_object(filename):
    """Load pickle file.

    Arguments:
    filename -- name of the pickle file to be loaded

    Return values:
    pickle object
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(__location__, filename)

    with open(path, 'rb') as f:
        return pickle.load(f)


def update_classifiers():
    """Train and save classifier pickle files.

    Arguments:
    -

    Return values:
    -
    """
    trainTypeQClassifier = dialog.trainTypeQuestion()
    trainWhQuestionClassifier = dialog.trainWhQuestion(1)
    trainDescOtherQuestionClassifier = dialog.trainWhQuestion(2)
    trainDescHQuestionClassifier = dialog.trainWhQuestion(3)
    trainDescWhQuestionClassifier = dialog.trainWhQuestion(4)
    posNegWords = dialog.getPosNegWords()
    trainSentencesMarkov = markov.Markov()

    # Save classifier that determines the general type of question
    save_object(trainTypeQClassifier, 'classifierTypeQ.pkl')
    # Save classifier that determines the type of "WhQuestion"
    save_object(trainWhQuestionClassifier, 'classifierWhQ.pkl')
    # Save classifier that determines the type of "DescriptionOther"
    save_object(trainDescOtherQuestionClassifier, 'classifierDescOtherQ.pkl')
    # Save classifier that determines the type of "DescriptionH"
    save_object(trainDescHQuestionClassifier, 'classifierDescHQ.pkl')
    # Save classifier that determines the type of "DescriptionWh"
    save_object(trainDescWhQuestionClassifier, 'classifierDescWhQ.pkl')
    # Save markov chains from sentenes dataset
    save_object(trainSentencesMarkov.getMarkov(), 'markovSentences.pkl')
    # Save pos/neg words
    save_object(posNegWords, 'posNegWords.pkl')

# Call function update_classifiers to update the classifier files
# Comment this line once the classifiers generation is done to gain performance
update_classifiers()

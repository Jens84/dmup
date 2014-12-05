import learn
import urllib
import urllib2
import bs4
from nltk.corpus import wordnet as wn


def getSubject(question, ind):
    subject = ""
    qTags = tokenizeFromStanfordNLP(question)
    if qTags[ind][0].lower() == 'you':
        subject = "I "
    elif qTags[ind][0].lower() == 'i':
        subject = "you "
    elif (qTags[ind][1] == 'DT'
            and (qTags[ind + 1][1] not in
                    ['VB', 'VBD', 'VBP', 'VBN', 'VBG', 'VBZ', 'MD'])):
        subject = qTags[ind][0] + " " + qTags[ind + 1][0] + " "
    elif qTags[ind][1] == 'DT':
        subject = qTags[ind][0] + " "
    elif qTags[ind][1] in ['NNP', 'NNPS']:
        i = ind
        while (qTags[i][1] in ['NNP', 'NNPS']):
            subject += qTags[i][0] + " "
            i += 1
    else:
        subject = qTags[ind][0] + " "

    return subject


def getObject(question, subject, verbs, isYesNoQuestion):
    object = ""
    qTags = tokenizeFromStanfordNLP(question)
    # print qTags
    # Find the sentence's object
    for word, tag in qTags:
        # This is the subject
        if(word in subject.replace(" ", "") or
           word in verbs or
           word.lower() in ["does", "do"]):
            continue
        if (word == "you" and subject == "I "or
           word == "I" and subject == "you ") and isYesNoQuestion:
            continue
        if(tag in ['DT', 'IN', 'JJ', 'NN', 'NNS', 'NNP', 'NNPS', 'RB', 'PRP']):
            if word.lower() == "me":
                object += ' you'
            else:
                object += ' ' + word
        else:
            if(object != ""):
                break

    return object


def getVerbs(question, subject):
    qTags = tokenizeFromStanfordNLP(question)
    verbs = [word for word, tag in qTags
             if (tag in ['VB', 'VBD', 'VBP', 'VBN', 'VBG', 'VBZ', 'MD'] and
                 word != subject.replace(' ', ''))]
    if verbs[0].lower() == 'are' and subject == 'I ':
        verbs[0] = 'am'
    elif verbs[0].lower() == 'am' and subject == 'you ':
        verbs[0] = 'are'
    elif (subject.lower() in ["he ", "she ", "it "]
          and verbs[0][len(verbs[0]) - 1] != 's'):
        verbs[0] += "s"

    return [v.lower() for v in verbs]


def tokenizeFromStanfordNLP(sentence):
    params = urllib.urlencode({'query': sentence})
    req = urllib2.Request("http://nlp.stanford.edu:8080/parser/index.jsp")
    response = urllib2.urlopen(req, params).read()
    soup = bs4.BeautifulSoup(response)
    parsed = soup.find('h3', text='Tagging').find_next('div')
    sTags = []
    for d in parsed.find_all('div'):
        e = d.string.strip().split('/')
        sTags.append((e[0], e[1]))
    return sTags


def nounify(verb_word):
    """ Transform a verb to the closest noun: die -> death. """
    verb_synsets = wn.synsets(verb_word, pos="v")

    # Word not found
    if not verb_synsets:
        return []

    # Get all verb lemmas of the word
    verb_lemmas = [l for s in verb_synsets
                   # for l in s.lemmas if s.name.split('.')[1] == 'v']
                   for l in s.lemmas() if s.name().split('.')[1] == 'v']

    # Get related forms
    derivationally_related_forms = [(l, l.derivationally_related_forms())
                                    for l in verb_lemmas]

    # filter only the nouns
    related_noun_lemmas = [l for drf in derivationally_related_forms
                           for l in drf[1]
                           # if l.synset.name.split('.')[1] == 'n']
                           if l.synset().name().split('.')[1] == 'n']

    # Extract the words from the lemmas
    # words = [l.name for l in related_noun_lemmas]
    words = [l.name() for l in related_noun_lemmas]
    len_words = len(words)

    # Build the result in the form of
    # a list containing tuples (word, probability)
    result = [(w, float(words.count(w)) / len_words) for w in set(words)]
    result.sort(key=lambda w: -w[1])

    # return all the possibilities sorted by probability
    return result


class Classify():
    _classifierTypeQ = None
    _classifierWhQ = None
    _classifierDescDescOtherQ = None
    _classifierDescDescHQ = None
    _classifierDescDescWhQ = None

    def __init__(self):
        self._posNegWords = learn.pickleHandler.load_object('posNegWords.pkl')
        # load classifiers from pickle files
        self._classifierTypeQ = (learn.pickleHandler.
                                 load_object('classifierTypeQ.pkl'))
        self._classifierWhQ = (learn.pickleHandler.
                               load_object('classifierWhQ.pkl'))
        self._classifierDescOtherQ = (learn.pickleHandler.
                                      load_object('classifierDescOtherQ.pkl'))
        self._classifierDescHQ = (learn.pickleHandler.
                                  load_object('classifierDescHQ.pkl'))
        self._classifierDescWhQ = (learn.pickleHandler.
                                   load_object('classifierDescWhQ.pkl'))

    def classifyTypeQuestion(self, question):
        return self._classifierTypeQ.classify(
            learn.dialog.dialogue_act_features(question))

    def classifyWhQuestion(self, question):
        """Return type of question previously labeled as whQuestion.

        Classifies the given question using previously trained Naive Bayes
        classifiers.

        Arguments:
        question -- string containing a question to be classified

        Return values:
        "Entity", "Place", "Reason", "TimeWhen", "TimeWhat", "Manner",
        "Composition", "Meaning", "Abbreviation", "Age", "Duration",
        "Quantity", "Frequency", "Dimension", "LookAndShape"
        """
        # Classify the subtype of the "wh" Question
        whType = self._classifierWhQ.classify(
            learn.dialog.dialogue_act_features(question))
        if whType == "DescriptionOther":
            descriptionType = self._classifierDescOtherQ.classify(
                learn.dialog.dialogue_act_features(question))
            return descriptionType
        if whType == "DescriptionH":
            descriptionType = self._classifierDescHQ.classify(
                learn.dialog.dialogue_act_features(question))
            return descriptionType
        if whType == "DescriptionWh":
            descriptionType = self._classifierDescWhQ.classify(
                learn.dialog.dialogue_act_features(question))
            return descriptionType
        return whType

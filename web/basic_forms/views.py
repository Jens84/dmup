from django.shortcuts import render

from basic_forms.models import Question
from basic_forms.models import QuestionForm

import turbot


def index(request):
    answer = ""
    if request.method == 'POST':
        q = QuestionForm(request.POST)
        if q.is_valid():
            q.save()
        answer = turbot.Turbot(Question.objects.latest('id'))

    try:
        last_question = Question.objects.latest('id')

    except:
        last_question = ""

    context = {'last_question': last_question}
    context = {'answer': answer}
    return render(request, 'basic_forms/index.html', context)
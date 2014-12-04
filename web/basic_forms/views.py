from django.shortcuts import render

from basic_forms.models import Question
from basic_forms.models import QuestionForm

import turbot


class MainView():
    _dialog = None
    _definition = None

    def __init__(self):
        if not self._dialog:
            self._dialog = turbot.Dialog()
        if not self._definition:
            self._definition = turbot.Definition()

    def index(self, request):
        answer = ""
        if request.method == 'POST':
            q = QuestionForm(request.POST)
            if q.is_valid():
                q.save()

            last = Question.objects.latest('id')
            answer = self._dialog.answer(last.content)

        try:
            last_question = Question.objects.latest('id')

        except:
            last_question = ""

        context = {'last_question': last_question.content, 'answer': answer}
        return render(request, 'basic_forms/index.html', context)

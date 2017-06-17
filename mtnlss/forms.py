from django.forms import ModelForm,CharField
from django import forms
from mtnlss.models import *

class VariableForm(ModelForm):
    prefix='variable'
    class Meta:
        model= Variable
        fields=['name']

class ProjectForm(ModelForm):
    prefix = "proj"
    class Meta:
        model = Project
        fields=["title"]

class PaperForm(ModelForm):
    class Meta:
        model = Paper
        fields=["title","authors","publication","year","sample_size"]
        widgets = {
            'year': forms.TextInput(attrs={"size":10}),
            'sample_size': forms.TextInput(attrs={"size":7}),
        }

class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields=["text"]
    
class AnswersForm(forms.Form):
    def __init__(self, thePaper, *args, **kwargs):
        ###########
        super(forms.Form, self).__init__(*args, **kwargs)
        initial_arguments = kwargs.get('initial', None)
#         if initial_arguments:
#             for k in initial_arguments:
#                 print(k,initial_arguments[k])
#                 self.fields[k] = initial_arguments[k]
#                 print(self.fields)
#         else:
        questions = Question.objects.filter(project=thePaper.project)
        for q in questions:
            qid = q.id
            self.fields['question_'+str(qid)] = forms.CharField(label=q.text)
            answer = Answer.objects.filter(paper=thePaper,question=q)
            if len(answer)>0:
                answer = answer[0]
                self.fields['question_'+str(qid)].initial = answer.value
            else:
                pass
        
    
    
    
    
    
    
    
    
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import *
from mtnlss.forms import *
from mtnlss.models import *
from django.forms import inlineformset_factory
from django.http import HttpResponse
from viewHelpers import *
import math


def home(request):
    newProjForm = ProjectForm()
    return render(request, 'mtnlss/home.html',{'newProjForm':newProjForm})

def proj(request):
    #called when the proj page is loaded
    form = None
    newPaperform = PaperForm()
    if request.method == 'GET':
        projID = request.GET['id']
        theProj = Project.objects.get(pk=projID)
        form = ProjectForm(instance=theProj)
    else:
        form = ProjectForm()
        
    return render(request, 'mtnlss/proj.html', {'form': form,'newPaperForm':newPaperform})

def addProj(request):
    form = ProjectForm(request.POST)
    
    if form.is_valid():
        data = form.cleaned_data
        title = data['title']
        theProj = Project(title=title)
        theProj.save()
        return HttpResponse("Done")
    else:
        return HttpResponse("Error")

def projsList(request):
    allProjs = Project.objects.all()
    return render(request, 'mtnlss/projsList.html',{'projs':allProjs})

def editProjTitle(request,projID):
    theProj = Project.objects.get(pk=projID)
    form = ProjectForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        title = data['title']
        theProj.title = title
        theProj.save()
        return HttpResponse("Done")
    else:
        return HttpResponse("Error")

def addPaper(request,projID):
    #Called when the user presses 'save' to add a new paper
    form = PaperForm(request.POST)
    if form.is_valid():
        thePaper = form.instance
        thePaper.project = Project.objects.get(pk=projID)
        thePaper.save()
        return papersList(request,"no",projID)
    else:
        return papersList(request,"yes",projID)


def papersList(request, returnInvalidForm, projID):
    #called whenever the papersList in the proj page is loaded or refreshed
    theProj = Project.objects.get(pk=projID)
    newPaperForm = None
    if returnInvalidForm == "no":
        newPaperForm = PaperForm()
    else:
        newPaperForm = PaperForm(request.POST)
    return render(request,'mtnlss/papersList.html', {'project': theProj,'newPaperForm':newPaperForm})


def deletePaper(request,paperID):
    try:
        Paper.objects.filter(id=paperID).delete()
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")

def deleteProj(request,projID):
    try:
        Project.objects.filter(id=projID).delete()
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")

def questionsList(request,returnInvalidForm,projID):
    #called whenever the QuestionsList in the proj page is loaded or refreshed
    theProj = Project.objects.get(pk=projID)
    newQuestionForm = None
    if returnInvalidForm == "no":
        newQuestionForm = QuestionForm()
    else:
        newQuestionForm = QuestionForm(request.POST)
    return render(request,'mtnlss/questionsList.html', {'project': theProj,'newQuestionForm':newQuestionForm})

def addQuestion(request,projID):
    #Called when the user presses 'save' to add a new paper
    form = QuestionForm(request.POST)
    if form.is_valid():
        theQ = form.instance
        theQ.project = Project.objects.get(pk=projID)
        theQ.save()
        return questionsList(request,"no",projID)
    else:
        return questionsList(request,"yes",projID)
    
def deleteQuestion(request,questionID):
    try:
        Question.objects.filter(id=questionID).delete()
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")

def paper(request, paperID):
    #Called when the paper page (the JS box) is loaded
    p = Paper.objects.get(pk=paperID)
    form = PaperForm(instance=p)
    answersForm = AnswersForm(p)
    varsHiddenCode = getVarsDivCode(paperID)
    corsHiddenCode = getCorsDivCode(paperID)
    return render(request, 'mtnlss/paper.html', {'form': form,'hiddenCode':varsHiddenCode+corsHiddenCode, 'answersForm':answersForm})

def corTable(request,paperID):
    p = Paper.objects.get(pk=paperID)
    vars = p.getVarsOrdered()
    thisPaperVarsIDs = vars.values_list('id',flat=True)
    otherProjVars = Variable.objects.filter(project=p.project).exclude(id__in=thisPaperVarsIDs)
    varForm = VariableForm()
    return render(request, 'mtnlss/corTable.html', {'varCount':range(len(vars)), 'otherProjVars': otherProjVars, 'varForm':varForm, 'varsLen':len(vars)});

def addExistingVariable(request,paperID):
    varID = request.POST.get('thevar')
    addExistingVariableToDB(varID,paperID)
    varsDivCode = getVarsDivCode(paperID)
    return HttpResponse(varsDivCode)
    
def addNewVariable(request,paperID):
    varForm = VariableForm(request.POST)
    if varForm.is_valid():
        n = varForm.cleaned_data['name']
        p = Paper.objects.get(pk=paperID)
        newVar = Variable(name=n, project=p.project)
        newVar.save()
        addExistingVariableToDB(newVar.id,paperID)
        varsDivCode = getVarsDivCode(paperID)
        return HttpResponse(varsDivCode)
    else:
        print(varForm)
        return HttpResponse("Error")
    
def detatchVariable(request,paperID):
    p = Paper.objects.get(pk=paperID)
    v = Variable.objects.get(pk=request.POST["varid"])
    vp = VarPaper.objects.filter(paper=p,var=v)
    vp.delete()
    return HttpResponse("Done")
    
def moveRow(request,paperID):
    #Swaps the "order"s for the two Variable objects in their relation to the current paper
    p = Paper.objects.get(pk=paperID)
    otherV = Variable.objects.get(pk=request.POST["otherid"])
    thisV = Variable.objects.get(pk=request.POST["thisid"])
    thisvp = VarPaper.objects.filter(paper=p,var=thisV)[0]
    othervp = VarPaper.objects.filter(paper=p,var=otherV)[0]
    temp = thisvp.order
    thisvp.order = othervp.order
    othervp.order = temp
    thisvp.save()
    othervp.save()
    return HttpResponse("Done")
    
def getHiddenDivs(request,paperID):
    corsCode = getCorsDivCode(paperID)
    varsCode = getVarsDivCode(paperID)
    return HttpResponse(corsCode+varsCode)
    
def saveCorrelations(request,paperID):
    try:
        p = Paper.objects.get(pk=paperID)
        corsInDB = Correlation.objects.filter(paper=p)
        updatedSomething = False
        handledKeys = {}
        #Iterate through the Correlation objects for this paper, for each one find the new value we just got from the user, and update it.
        for c in corsInDB:
            key1 = str(c.var1.id)+"_"+str(c.var2.id)
            key2 = str(c.var2.id)+"_"+str(c.var1.id)
            theKey = None
            if key1 in request.POST:
                theKey = key1
            elif key2 in request.POST:
                theKey = key2
            else:
                continue
            handledKeys.update({theKey:""})
            newCorValue = request.POST[theKey]
            if newCorValue=="":
                c.delete()
                updatedSomething = True
                continue
            try:
                newCorValue = Decimal(newCorValue)
                if(c.value != newCorValue):
                    c.value = newCorValue
                    c.save()
                    updatedSomething = True
            except: 
                return HttpResponse("Error")
        #Now look for correlations that are being added for the first time and therefore don't have a Correlation object in the DB
        for k in request.POST:
            if not k in handledKeys:
                updatedSomething = True
                newVal = request.POST[k]
                [varid1,varid2] = k.split("_")
                v1 = Variable.objects.get(pk=varid1)
                v2 = Variable.objects.get(pk=varid2)
                newC = Correlation(paper=p,value=newVal,var1=v1,var2=v2)
                newC.save()
        
        if updatedSomething:
            return HttpResponse("Done")
        else:
            return HttpResponse("nochange")
    except:
        return HttpResponse("Error")
        
def editPaper(request,paperID):
    existingData = Paper.objects.filter(id=paperID).values()[0]
    existingVersion = Paper.objects.get(pk=paperID)
    form = PaperForm(request.POST)
    if form.is_valid():
        form = PaperForm(request.POST, initial=existingData)
        if not form.has_changed():
            return HttpResponse("nochange")
        else:
            form = PaperForm(request.POST, instance=existingVersion)
            form.save()
            return HttpResponse("Done")
    else:
        return HttpResponse(form)
    
    
def deleteVars(request,projID):
    try:
        for varid in request.POST:
            var = Variable.objects.get(pk=varid)
            var.delete();
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")
    
def editVarName(request, projID):
    varid = request.POST["id"]
    newName = request.POST["name"]
    var = Variable.objects.get(pk=varid)
    var.name = newName
    var.save()
    return HttpResponse("Done")
    
def editAnswers(request,paperID):
    p = Paper.objects.get(pk=paperID)
    changeAnything = False
    for question in request.POST:
        if question!="csrfmiddlewaretoken":
            ans = request.POST[question]
            questionID = int(question.split("_")[-1])
            q = Question.objects.get(pk=questionID)
            answer = Answer.objects.filter(paper=p,question=q)
            if len(answer):
                answer = answer[0]
                oldVal = answer.value
                if oldVal==ans:
                    continue
                else:
                    changeAnything = True
                    answer.value = ans
                    answer.save()
            else:
                changeAnything = True
                answer = Answer(paper=p,question=q,value=ans)
                answer.save()
    if changeAnything:
        return HttpResponse("Done")
    else:
        return HttpResponse("nochange")

def analysisFirstPage(request,projID):
    theProj = Project.objects.get(pk=projID)
    vars = theProj.variable_set.all()
    varsDict = {}
    for v in vars:
        varsDict[v.id] = v.name
    return render(request,'mtnlss/analysisFirstPage.html', {'project': theProj,'varsDict': varsDict})

def analysisResult(request, projID):
    theProj = Project.objects.get(pk=projID)
    group1varids = request.POST.getlist('group1')
    group2varids = request.POST.getlist('group2')
    pairs,results = getAnalysisResults(theProj,group1varids,group2varids)
    
    return render(request,'mtnlss/analysisResult.html', {'project': theProj, 'pairs': pairs, 'results':results})
    
    
    
    
    
    
    
    
    
    
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import *
from mtnlss.forms import *
from mtnlss.models import *
from django.forms import inlineformset_factory
from django.http import HttpResponse
from viewHelpers import *
from sqlite3 import ProgrammingError
from django.db import transaction
import math
import csv
import re
from timeit import default_timer as timer


@login_required
def home(request):
    newProjForm = ProjectForm()
    return render(request, 'mtnlss/home.html',{'newProjForm':newProjForm})

@login_required
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

@login_required
def addProj(request):
    form = ProjectForm(request.POST)
    
    if form.is_valid():
        data = form.cleaned_data
        title = data['title']
        theProj = Project(title=title)
        theProj.save()
        theProj.admins.add(request.user)
        theProj.save()
        return HttpResponse("Done")
    else:
        return HttpResponse("Error")

@login_required
def projsList(request):
#     allProjs = Project.objects.all()
    try:
        allProjs = request.user.project_set.all()
    except:
        allProjs = []
    return render(request, 'mtnlss/projsList.html',{'projs':allProjs})

@login_required
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

@login_required
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


@login_required
def papersList(request, returnInvalidForm, projID):
    #called whenever the papersList in the proj page is loaded or refreshed
    theProj = Project.objects.get(pk=projID)
    newPaperForm = None
    if returnInvalidForm == "no":
        newPaperForm = PaperForm()
    else:
        newPaperForm = PaperForm(request.POST)
    return render(request,'mtnlss/papersList.html', {'project': theProj,'newPaperForm':newPaperForm})


@login_required
def deletePaper(request,paperID):
    try:
        Paper.objects.filter(id=paperID).delete()
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")

@login_required
def deleteProj(request,projID):
    try:
        Project.objects.filter(id=projID).delete()
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")

@login_required
def questionsList(request,returnInvalidForm,projID):
    #called whenever the QuestionsList in the proj page is loaded or refreshed
    theProj = Project.objects.get(pk=projID)
    newQuestionForm = None
    if returnInvalidForm == "no":
        newQuestionForm = QuestionForm()
    else:
        newQuestionForm = QuestionForm(request.POST)
    return render(request,'mtnlss/questionsList.html', {'project': theProj,'newQuestionForm':newQuestionForm})

@login_required
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
    
@login_required
def deleteQuestion(request,questionID):
    try:
        Question.objects.filter(id=questionID).delete()
        return HttpResponse("Done")
    except:
        return HttpResponse("Error")
@login_required
@login_required
def paper(request, paperID):
    #Called when the paper page (the JS box) is loaded
    p = Paper.objects.get(pk=paperID)
    form = PaperForm(instance=p)
    answersForm = AnswersForm(p)
    varsHiddenCode = getVarsDivCode(paperID)
    corsHiddenCode = getCorsDivCode(paperID)
    return render(request, 'mtnlss/paper.html', {'form': form,'hiddenCode':varsHiddenCode+corsHiddenCode, 'answersForm':answersForm})

@login_required
def corTable(request,paperID):
    p = Paper.objects.get(pk=paperID)
    vars = p.getVarsOrdered()
    thisPaperVarsIDs = vars.values_list('id',flat=True)
    otherProjVars = Variable.objects.filter(project=p.project).exclude(id__in=thisPaperVarsIDs)
    varForm = VariableForm()
    return render(request, 'mtnlss/corTable.html', {'varCount':range(len(vars)), 'otherProjVars': otherProjVars, 'varForm':varForm, 'varsLen':len(vars)});

@login_required
def addExistingVariable(request,paperID):
    varID = request.POST.get('thevar')
    addExistingVariableToDB(varID,paperID)
    hiddenDiv = getHiddenDivs(request, paperID)
    return HttpResponse(hiddenDiv)
    
@login_required
def addNewVariable(request,paperID):
    varForm = VariableForm(request.POST)
    if varForm.is_valid():
        n = varForm.cleaned_data['name']
        p = Paper.objects.get(pk=paperID)
        newVar = Variable(name=n, project=p.project)
        newVar.save()
        addExistingVariableToDB(newVar.id,paperID)
        hiddenDiv = getHiddenDivs(request, paperID)
        return HttpResponse(hiddenDiv)
    else:
        return HttpResponse("Error")
    
@login_required
def detatchVariable(request,paperID):
    p = Paper.objects.get(pk=paperID)
    v = Variable.objects.get(pk=request.POST["varid"])
    vp = VarPaper.objects.filter(paper=p,var=v)
    vp.delete()
    return HttpResponse("Done")
    
@login_required
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
    
@login_required
def getHiddenDivs(request,paperID):
    corsCode = getCorsDivCode(paperID)
    varsCode = getVarsDivCode(paperID)
    return HttpResponse(corsCode+varsCode)
    
@login_required
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
                if k.startswith("mean") or k.startswith("sd") or k.startswith("alpha"):
                    [type,varid] = k.split("_")
                    v = Variable.objects.get(pk=varid)
                    varpaper = VarPaper.objects.filter(var=v,paper=p)[0]
                    if type=="mean":
                        varpaper.mean = newVal
                    if type=="sd":
                        varpaper.sd = newVal
                    if type=="alpha":
                        varpaper.alpha = newVal    
                    varpaper.save()  
                else: 
                    [varid1,varid2] = k.split("_")
                    v1 = Variable.objects.get(pk=varid1)
                    v2 = Variable.objects.get(pk=varid2)
                    newC = Correlation(paper=p,value=newVal,var1=v1,var2=v2)
                    newC.save()
        
        if updatedSomething:
            return HttpResponse("Done")
        else:
            return HttpResponse("nochange")
    except Exception as e:
        print(e)
        return HttpResponse("Error")
        
@login_required
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
    
    
@login_required
def deleteVars(request,projID):
    try:
        for varid in request.POST:
            var = Variable.objects.get(pk=varid)
            var.delete();
        return HttpResponse("Done")
    except Exception, e:
        return HttpResponse("Error")

@login_required
def addGroupVar(request,projID):
    p = Project.objects.get(pk=projID)
    try:
        vars = []
        for varid in request.POST:
            var = Variable.objects.get(pk=varid)
            if var.isgroup:
                return HttpResponse("Error")
            vars.append(var)
        #Now add the new group var:
        n = getGroupName(vars,p)
        names = map(lambda x:x.name,vars)
        d = reduce(lambda x,y: x+", "+y,names)
        print(map(lambda x: x.name,vars))
        print(d)
        newVar = Variable(name=n, project=p, isgroup=True, description=d)
        newVar.save()
        for v in vars:
            newVar.variables.add(v)
        newVar.save()
        return HttpResponse(n+"  "+str(newVar.id))
    except Exception, e:
        print(e)
        return HttpResponse("Error")    

@login_required
def editVarName(request, projID):
    varid = request.POST["id"]
    newName = request.POST["name"]
    var = Variable.objects.get(pk=varid)
    var.name = newName
    var.save()
    return HttpResponse("Done")
    
@login_required
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

@login_required
def analysisFirstPage(request,projID):
    theProj = Project.objects.get(pk=projID)
    vars = theProj.variable_set.all()
    varsDict = {}
    for v in vars:
        varsDict[v.id] = v.name
    return render(request,'mtnlss/analysisFirstPage.html', {'project': theProj,'varsDict': varsDict})

@login_required
def analysisResult(request, projID):
    theProj = Project.objects.get(pk=projID)
    group1varids = request.POST.getlist('group1')
    group1varids = expandGroupVars(group1varids)
    group2varids = request.POST.getlist('group2')
    group2varids = expandGroupVars(group2varids)
#     print(group1varids)
#     print(group2varids)
    if not set(group1varids).isdisjoint(group2varids):
        return HttpResponse("Error: A group variable is on one side while one of its members is on the other side.")
    sig1 = request.POST['sig1']
    sig2 = request.POST['sig2']
    pairs,results = getAnalysisResults(theProj,group1varids,group2varids,float(sig1)/100,float(sig2)/100)
    if pairs==None:
        return HttpResponse(results)        #It's an error message
    
    return render(request,'mtnlss/analysisResult.html', {'project': theProj, 'pairs': pairs, 'results':results})
    
@login_required
def exportPapers(request):
    #This view creates and returns the downloadable file
    paperIDs = request.GET.get('paper_ids')
    paperIDs = paperIDs.split(',')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="CorrMeta_exported_paper_data.csv"'

    #Moderator varialbes (known as questiosn and answers in the DB):
    someRandomPaperInThisProj = Paper.objects.get(pk=paperIDs[0])
    proj = someRandomPaperInThisProj.project
    questions = proj.question_set.all()
    question_texts = list(questions.values_list('text', flat=True)) 
    
    writer = csv.writer(response)
    writer.writerow(['Paper Number', 'Paper Name', 'Authors', 'Year Published', 'Variable A', 'Variable B', 'Var A-Mean', 'Var A-SD', 'Var B-Mean', 'Var B-SD', 'Sample Size', 'Correlation Raw', 'Var A Alpha', 'Var B-Alpha']+question_texts)
    for paperID in paperIDs:
        thePaper = Paper.objects.get(pk=paperID)
        
        #Moderator varialbes (known as questions and answers in the DB):
        answers = []
        for q in questions:
            answerQS = Answer.objects.filter(question=q,paper=thePaper)
            if len(answerQS)>0:
                answer = answerQS[0].value
            else:
                answer = ""
            answers.append(answer)
        
        vars = thePaper.variables.all()
        for var1 in vars:
            for var2 in vars:
                if var1.id < var2.id:
                    #For every two distinct variables that belong to this paper:
                    varPaper1QS = VarPaper.objects.filter(var=var1,paper=thePaper)
                    if len(varPaper1QS)>0:
                        varPaper1 = varPaper1QS[0]
                    else:
                        #empty varPaper:
                        varPaper1 = VarPaper()
                    varPaper2QS = VarPaper.objects.filter(var=var2,paper=thePaper)
                    if len(varPaper2QS)>0:
                        varPaper2 = varPaper2QS[0]
                    else:
                        #empty varPaper:
                        varPaper2 = VarPaper()
                       
                    cor = var1.getCorrelation(var2,thePaper)
                    if len(cor)>0:
                        cor = getReadableDecimal(cor[0])
                    else:
                        cor = ""
                    writer.writerow([thePaper.id, thePaper.title, thePaper.authors, thePaper.year, var1.name, var2.name,varPaper1.mean, varPaper1.sd,varPaper2.mean, varPaper2.sd, thePaper.sample_size, cor, varPaper1.alpha, varPaper2.alpha]+answers)
                    
    

    return response
    
@login_required
def importFromFile(request):
    corsToSave = []
    vpsToSave = {}
    seenPapers = {}
    seenVars = {}
#     g1 = 0
#     g2 = 0
#     g3 = 0
    try:
        csvfile = request.FILES['myfile']
        projTitle = request.POST.get("projtitle")
        readCSV = csv.reader(csvfile, delimiter=',')
        proj = Project(title=projTitle)
        proj.save()
        proj.admins.add(request.user)
        proj.save()
        counter = 0
        modVars = []
        for row in readCSV:
#             g1s = timer()
            for i in range(len(row)):
                x = row[i]
                try:
                    x.decode('utf-8')
                except UnicodeError:
                    row[i] = re.sub(r'[^\x00-\x7f]',r' ',x)
            counter += 1
            if counter==1:
                colCounter = 13
                while True:
                    colCounter += 1
                    if len(row)>colCounter and row[colCounter] and len(row[colCounter]) > 0:
                        q = Question(project=proj,text=row[colCounter])
                        q.save()
                        modVars.append(q)
                    else:
                        break
                continue
            dflts = {}
            if len(row[2])>0:
                dflts["authors"]=row[2]
            if len(row[3])>0:
                dflts["year"]=row[3]
            if len(row[10])>0:
                dflts["sample_size"]=row[10]
#             g1e = timer()
#             g1 += (g1e-g1s)
#             
#             g2s = timer()
            ###
            if row[1] not in seenPapers:
                paper,c = Paper.objects.get_or_create(title=row[1], project=proj,defaults=dflts)
                seenPapers[row[1]] = paper
                ##Add the modVars for this paper
                for i in range(len(modVars)):
                    modVar = modVars[i]
                    if len(row)>14+i:
                        value = row[14+i]
                    else:
                        value = ""
                    if value and len(value)>0:
                        a = Answer(paper=paper,question=modVar,value=value)
                        a.save()
            else:
                paper = seenPapers[row[1]]
            
            if row[4] not in seenVars:
                var1,c = Variable.objects.get_or_create(name=row[4], project=proj)
                seenVars[row[4]] = var1
            else:
                var1 = seenVars[row[4]]
            
            if row[5] not in seenVars:
                var2,c = Variable.objects.get_or_create(name=row[5], project=proj)
                seenVars[row[5]] = var2
            else:
                var2 = seenVars[row[5]]
            ###
#             g2e = timer()
#             g2 += (g2e-g2s)
#             
#             g3s = timer()
            #Create the varPaper objects if you haven't already done so
            key = str(var1.id)+"__"+str(paper.id)
            if key not in vpsToSave:
                vpData = ["","",""]
                if len(row[6])>0:
                    vpData[0] = Decimal(row[6])
                if len(row[7])>0:
                    vpData[1] = Decimal(row[7])
                if len(row[12])>0:
                    vpData[2] = Decimal(row[12])
                vpsToSave[key] = [var1.id,paper.id]+vpData
            key = str(var2.id)+"__"+str(paper.id)
            if key not in vpsToSave:
                vpData = ["","",""]
                if len(row[8])>0:
                    vpData[0] = Decimal(row[8])
                if len(row[9])>0:
                    vpData[1] = Decimal(row[9])
                if len(row[13])>0:
                    vpData[2] = Decimal(row[13])
                vpsToSave[key] = [var2.id,paper.id]+vpData    
            cor = Correlation(var1=var1,var2=var2,paper=paper)
            if len(row[11])>0:
                cor.value=Decimal(row[11])
                corsToSave.append(cor)
#             g3e = timer()
#             g3 += (g3e-g3s)
#         
#         g4 = 0
#         g4s = timer()
        #Just to save time!
        with transaction.atomic():
            for vp,data in vpsToSave.iteritems():
                vp = addExistingVariableToDB(data[0],data[1])
                if data[2]!="":
                    vp.mean = data[2]
                if data[3]!="":
                    vp.sd = data[3]
                if data[4]!="":
                    vp.alpha = data[4]
                vp.save()
            for cor in corsToSave:
                cor.save()
#         g4e = timer()
#         g4 += (g4e-g4s)
#         print(g1,g2,g3,g4)
    except ProgrammingError:
        try:
            proj.delete()
        except:
            pass
        return HttpResponse("Please upload a file with unicode (UTF-8) formatting.")
#     except Exception, e:
#         return HttpResponse("Error parsing file in row "+str(counter)+": "+type(e).__name__+" "+str(e))
    if counter<3:
        proj.delete()
        return HttpResponse("No valid data rows were found on the file.")
    return HttpResponse("Done reading "+str(counter-1)+" rows.")

@login_required
def metaAnalysisFirstPage(request, projID):
    theProj = Project.objects.get(pk=projID)
    vars = theProj.variable_set.all()
    varsDict = {}
    for v in vars:
        varsDict[v.id] = v.name
    return render(request,'mtnlss/metaAnalysisFirstPage.html', {'project': theProj,'varsDict': varsDict})

@login_required
def metaAnalysisResult(request, projID):
    theProj = Project.objects.get(pk=projID)
    group1varids = request.POST.getlist('group1')
    sig1 = request.POST['sig1']
    sig2 = request.POST['sig2']
    results = fillMetaAnalTable(theProj, group1varids,float(sig1)/100,float(sig2)/100)
    if isinstance(results, basestring):
                return HttpResponse(results)    #It's an error message
    varNames = []
    for varid in group1varids:
        name = Variable.objects.get(pk=varid).name
        varNames.append(name)
    return render(request,'mtnlss/metaAnalysisResult.html', {'project': theProj, 'varNames':varNames, 'results':results, 'varCount':range(len(group1varids)), 'group1':group1varids, 'sig1':sig1, 'sig2':sig2})
    
@login_required
def metaAnalysisResultAsFile(request, projID):
    #This view creates and returns the downloadable file
    
    #Prepare the data
    theProj = Project.objects.get(pk=projID)
    group1varids = request.POST.getlist('group1')
    sig1 = request.POST['sig1']
    sig2 = request.POST['sig2']
    results = fillMetaAnalTable(theProj, group1varids,float(sig1)/100,float(sig2)/100)
    varNames = []
    for varid in group1varids:
        name = Variable.objects.get(pk=varid).name
        varNames.append(name)
    
    #Start writing in the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="CorrMeta_MetaAnalysis.csv"'

    writer = csv.writer(response)
    writer.writerow(['']+varNames)
    for i in range(len(varNames)):
        varName = varNames[i]
        writer.writerow([varName]+results[i])
    return response

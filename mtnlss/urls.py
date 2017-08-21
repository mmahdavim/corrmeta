from django.conf.urls import url, include
from django.contrib import admin
import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^proj/$', views.proj),
    url(r'^projslist/$', views.projsList),
    url(r'^addproj/$', views.addProj),
    url(r'^paper/(?P<paperID>.+)/$', views.paper),
    url(r'^editprojtitle/(?P<projID>.+)/$', views.editProjTitle),
    url(r'^addpaper/(?P<projID>.+)/$', views.addPaper),
    url(r'^deleteproj/(?P<projID>.+)/$', views.deleteProj),
    url(r'^paperslist/(?P<returnInvalidForm>.+)/(?P<projID>.+)/$', views.papersList),
    url(r'^deletepaper/(?P<paperID>.+)/$', views.deletePaper),
    url(r'^addquestion/(?P<projID>.+)/$', views.addQuestion),
    url(r'^questionslist/(?P<returnInvalidForm>.+)/(?P<projID>.+)/$', views.questionsList),
    url(r'^deletequestion/(?P<questionID>.+)/$', views.deleteQuestion),
    url(r'^deletevars/(?P<projID>.+)/$', views.deleteVars), 
    url(r'^editvarname/(?P<projID>.+)/$', views.editVarName),
    url(r'^analysisfirstpage/(?P<projID>.+)/$', views.analysisFirstPage, name='analysisfirstpage'),
    url(r'^analysisresult/(?P<projID>.+)/$', views.analysisResult, name='analysisresult'),
    url(r'^exportPapers/$', views.exportPapers, name='exportPapers'),
    url(r'^importfromfile/$', views.importFromFile, name='importfromfile'),
    url(r'^metaanalysisfirstpage/(?P<projID>.+)/$', views.metaAnalysisFirstPage, name='metaanalysisfirstpage'),
    url(r'^metaanalysisresult/(?P<projID>.+)/$', views.metaAnalysisResult, name='metaanalysisresult'),
    
    url(r'^addNewVariable/(?P<paperID>.+)/$', views.addNewVariable),
    url(r'^addExistingVariable/(?P<paperID>.+)/$', views.addExistingVariable),
    url(r'^corTable/(?P<paperID>.+)/$', views.corTable),   
    url(r'^detatchVariable/(?P<paperID>.+)/$', views.detatchVariable),
    url(r'^moverow/(?P<paperID>.+)/$', views.moveRow),
    url(r'^gethiddendivs/(?P<paperID>.+)/$', views.getHiddenDivs),
    url(r'^savecorrelations/(?P<paperID>.+)/$', views.saveCorrelations),
    url(r'^editpaper/(?P<paperID>.+)/$', views.editPaper),
    url(r'^editanswers/(?P<paperID>.+)/$', views.editAnswers),
]
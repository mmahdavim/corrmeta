# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_init

class Project(models.Model):
    title = models.CharField(max_length=140)
    admins = models.ManyToManyField(User)
    class Meta:
        ordering = ('id',)
    def getPapersSummary(self):
        result = ""
        counter = 0
        for paper in self.paper_set.all():
            counter += 1
            if counter>3:
                break
            result += "\""+paper.getShortName()+"\""+", "
        if len(result)==0:
            return result
        else:
            return result+"..."
            
class Variable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=140)
    def getCorrelation(self,v2,p):
        v1 = self
#         if sorted([v1.name,v2.name])[0] != v1:
#             temp = v1
#             v1 = v2
#             v2 = temp
        result = Correlation.objects.filter(paper=p, var1=v1, var2=v2).values_list('value',flat=True)
        if not result:
            result = Correlation.objects.filter(paper=p, var1=v2, var2=v1).values_list('value',flat=True)
        return result
    class Meta:
        unique_together = ('project', 'name',)


class Paper(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    authors = models.CharField(blank=True,null=True,max_length=140)
    publication = models.CharField(blank=True,null=True,max_length=140)
    year = models.IntegerField(blank=True,null=True)
    sample_size = models.IntegerField(blank=True,null=True)
    variables = models.ManyToManyField(Variable,through='VarPaper', related_name='its_paper')
    def getShortName(self):
        if len(self.title)<20:
            return self.title
        else:
            return self.title[:20]+"..."
    
    def getMidlengthName(self):
        if len(self.title)<38:
            return self.title
        else:
            return self.title[:38]+"..."
        
    def getVarsOrdered(self):
        return self.variables.order_by('varpaper__order')
    
    class Meta:
        ordering = ('id',)


class Question(models.Model):
    text = models.CharField(max_length=140)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    class Meta:
        ordering = ('id',)

class Answer(models.Model):
    value = models.CharField(blank=True,null=True,max_length=140)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('question', 'paper',)

    
class VarPaper(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    var = models.ForeignKey(Variable, on_delete=models.CASCADE)
    order = models.IntegerField()
    mean = models.DecimalField(blank=True,null=True,decimal_places=4,max_digits=10)
    sd = models.DecimalField(blank=True,null=True,decimal_places=4,max_digits=10)
    alpha = models.DecimalField(blank=True,null=True,decimal_places=4,max_digits=10)
    class Meta:
        unique_together = ('var', 'paper',)

# def extraInitForCorrelation(**kwargs):
#     #This should be run every time the constructor of Correlation is called to make sure that
#     #var1 refers to the variable that is alphabetically before the other one
#     var1 = kwargs['kwargs'].get('var1')
#     var2 = kwargs['kwargs'].get('var2')
#     if sorted([var1.name,var2.name])[0] != var1:
#         temp = var1
#         var1 = var2
#         var2 = temp

class Correlation(models.Model):
    #For paper p, what is the correlation between var1 and var2
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    value = models.DecimalField(blank=True,null=True,decimal_places=4,max_digits=10)
    var1 = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name="var1")
    var2 = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name="var2")
    

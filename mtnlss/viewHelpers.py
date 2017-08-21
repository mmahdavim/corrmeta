from mtnlss.models import *
from decimal import *
from django.db.models import Max
from itertools import chain
import math
from scipy.stats import norm

def addExistingVariableToDB(varID,paperID):
    p = Paper.objects.get(pk=paperID)
    proj = p.project
    maxOrder = VarPaper.objects.filter(paper=p).aggregate(Max('order'))['order__max']
    if maxOrder:
        newOrder = maxOrder+1
    else:
        newOrder =  1
    v = Variable.objects.get(pk=varID)
    vp = VarPaper(paper=p,var=v,order=newOrder)
    vp.save()
    return vp
    
    
  
def getReadableDecimal(value):
    if isinstance(value,Decimal):
        value = "%.4f" % value
    return str(value)


def getVarsDivCode(paperID):
    p = Paper.objects.get(pk=paperID)
    vars = p.getVarsOrdered()
    varsHiddenCode = "<div style='visibility:hidden' id='varsHiddenDiv'>\n\t"
    for i in range(len(vars)):
        var = vars[i]
        varsHiddenCode += "<div id='var_"+str(i+1)+"' data-name='"+var.name+"'>"+str(var.id)+"</div>"
    varsHiddenCode += "<div id='var_count'>"+str(len(vars))+"</div>"
    varsHiddenCode += "\n</div>\n"
    return varsHiddenCode


def getCorsDivCode(paperID):
    p = Paper.objects.get(pk=paperID)
    vars = p.getVarsOrdered()
    corsHiddenCode = "<div style='visibility:hidden' id='corsHiddenDiv'>\n\t"
    #The correlations:
    for i in range(len(vars)):
        for j in range(len(vars)):
            value = ""
            if i>j:
                valueInDB = vars[i].getCorrelation(vars[j],p)
                if len(valueInDB)>0:
                    value = valueInDB[0]
                value = getReadableDecimal(value)
                corsHiddenCode += "<div id='"+str(vars[i].id)+"____"+str(vars[j].id)+"'>"+value+"</div>"
    #The first special columns (mean, SD, etc.):
    for i in range(len(vars)):
        vp = VarPaper.objects.filter(var=vars[i], paper=p)
        if len(vp)>0 and vp[0]:
            mean = vp[0].mean
            sd = vp[0].sd
            alpha = vp[0].alpha
        else:
            mean = ""
            sd = ""
            alpha = ""
        if mean==None:
            mean = ""
        if sd==None:
            sd = ""
        if alpha==None:
            alpha = ""
        corsHiddenCode += "<div id='"+str(vars[i].id)+"____mean'>"+getReadableDecimal(mean)+"</div>"
        corsHiddenCode += "<div id='"+str(vars[i].id)+"____sd'>"+getReadableDecimal(sd)+"</div>"
        corsHiddenCode += "<div id='"+str(vars[i].id)+"____alpha'>"+getReadableDecimal(alpha)+"</div>"
        
    corsHiddenCode += "\n</div>\n"
    return corsHiddenCode

# def norm_s_inv(p):  
#     """Calculates the inverse of the standard normal distribution."""
# 
#     # Probability must be between 0 and 1
#     if p < 0 or p > 1:
#         return 0.00
# 
#     a = [-39.96968, 220.96609, -275.92851, 138.35775, -30.66479, 2.50662]
#     b = [-54.47609, 161.58583, -155.69897, 66.801311, -13.28068]
# 
#     q = p - 0.5
#     r = q * q
# 
#     return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)

def getAnalysisResults(theProj, group1varids, group2varids, h_sig1, h_sig2, forMeta=False):
    pairs = []
    h_sum_w2 = 0
    h_sum_wES2 = 0
    h_sum_wES = 0
    h_sum_w = 0
    h_sum_W = 0
    h_sum_Z = 0
    h_rmean = 0
    h_rcmean = 0
    
    #For any variable pair get all the correlations and add them to "pairs"
    h_N = 0
    for varid1 in group1varids:
        v1 = Variable.objects.get(pk=varid1)
        for varid2 in group2varids:
            v2 = Variable.objects.get(pk=varid2)
            cors1 = Correlation.objects.filter(var1=v1,var2=v2)
            cors2 = Correlation.objects.filter(var1=v2,var2=v1)
            cors = list(chain(cors1, cors2))
            for c in cors:
                item = {}
                if c.paper.sample_size==None:
                    continue
                item['paper_id'] = c.paper.id
                item['sample_size'] = c.paper.sample_size
                item['correlation'] = c.value
                item['var1'] = v1.name
                item['var2'] = v2.name
                pairs.append(item)
                h_N += c.paper.sample_size if c.paper.sample_size!=None else 0
                h_FZ = 0.5*math.log((1+c.value)/(1-c.value))
                h_SEF = 1/math.sqrt(c.paper.sample_size-3)if c.paper.sample_size!=None else 1
                h_Z = h_FZ/h_SEF
                h_AZ = h_FZ/math.sqrt(1*1*1)
                h_ASEF = h_SEF/math.sqrt(1*1*1)
                h_WF = 1/h_ASEF**2
                h_WF2 = h_WF**2
                h_A = math.sqrt(1*1*1)
                h_AR = float(c.value)/h_A
                h_W = c.paper.sample_size*(h_A**2) if c.paper.sample_size!=None else 0
                item['h_A'] = h_A
                item['h_W'] = h_W
                item['h_AR'] = h_AR
                item['h_AZ'] = h_AZ
                item['h_ASEF'] = h_ASEF
                h_sum_w2 += h_WF2
                h_sum_wES2 += h_WF*(h_AZ**2)
                h_sum_wES +=   h_WF*h_AZ
                h_sum_w += h_WF
                h_sum_W += h_W
                h_sum_Z += h_Z
                h_rmean += c.value*c.paper.sample_size if c.paper.sample_size!=None else 0
                h_rcmean += h_AR*c.paper.sample_size if c.paper.sample_size!=None else 0
    h_K = len(pairs)
    
    #This part is for the special case where we're using this function for MetaAnalysis Table
    if forMeta:
        if h_N==0:
            h_rcmean = "."
            h_cl_low_rc = "."
            h_cl_high_rc = "."
        else:
            h_rcmean = float(h_rcmean/h_N)
            h_siglev = norm.ppf(1-(1-h_sig1)/2)
            h_var_rc_toAdd =  [ float(x['h_W'])*((float(x['h_AR'])-h_rcmean)**2) for x in pairs ]
            h_var_rc = sum(h_var_rc_toAdd)/h_sum_W
            h_SDrc = math.sqrt(h_var_rc)
            h_SErc = h_SDrc/math.sqrt(h_K)
            h_cl_low_rc = h_rcmean - h_siglev*h_SErc
            h_cl_high_rc = h_rcmean + h_siglev*h_SErc
        results = {}
        results['rcmean'] = h_rcmean
        results['K'] = h_K
        results['N'] = h_N
        results['cl_low_rc'] = h_cl_low_rc
        results['cl_high_rc'] = h_cl_high_rc
        return results
        
        
    if h_N==0 or h_K<2:
        return None,None
    h_average = h_N/h_K
    h_AveZ = h_sum_wES/h_sum_w
    h_SEZes = math.sqrt(1/h_sum_w)
    h_ZZ = h_AveZ/h_SEZes
    h_rfisherfixed = (math.exp(2*h_AveZ)-1) / (math.exp(2*h_AveZ)+1)
    h_Zc = h_sum_Z/math.sqrt(h_K)
    h_siglev = norm.ppf(1-(1-h_sig1)/2)
    h_credsig =  norm.ppf(1-(1-h_sig2)/2)
    h_FSN = h_K * ((h_Zc/norm.ppf(h_sig1))**2 - 1)
    h_rmean = float(h_rmean/h_N)
    h_rcmean = float(h_rcmean/h_N)
    h_sigmar2_toAdd = [ float(x['sample_size'])*(float(x['correlation'])-h_rmean)**2 for x in pairs ]
    h_sigmar2 = sum(h_sigmar2_toAdd)/h_N
    h_SDr = math.sqrt(h_sigmar2)
    h_SEr = h_SDr/math.sqrt(h_K)
    h_sigmae2 = (1-h_rmean**2)**2 / ((h_N/h_K)-1)
    h_sigmap2 = h_sigmar2 - h_sigmae2
    if h_sigmap2<0:
        h_sigmap2 = 0
    h_sigmap = math.sqrt(h_sigmap2)
    h_percExp = (h_sigmae2/h_sigmap2)*100 if h_sigmap2!=0 else 100      #????????????
    h_cl_low_r = h_rmean - h_siglev*h_SEr
    h_cl_high_r = h_rmean + h_siglev*h_SEr
    h_cr_low_r = h_rmean - h_credsig*h_sigmap
    h_cr_high_r = h_rmean + h_credsig*h_sigmap
    h_var_rc_toAdd =  [ float(x['h_W'])*((float(x['h_AR'])-h_rcmean)**2) for x in pairs ]
    h_var_rc = sum(h_var_rc_toAdd)/h_sum_W
    h_AveVe_toAdd = [ float(x['h_W'])*( ((1-h_rmean**2)**2/(float(x['sample_size'])-1)) /(float(x['h_A'])**2) ) for x in pairs ]
    h_AveVe = sum(h_AveVe_toAdd)/h_sum_W
    h_Varp = h_var_rc - h_AveVe
    if h_Varp <0:
        h_Varp = 0
    h_SDp = math.sqrt(h_Varp)
    h_SDrc = math.sqrt(h_var_rc)
    h_SErc = h_SDrc/math.sqrt(h_K)
    h_cl_low_rc = h_rcmean - h_siglev*h_SErc
    h_cl_high_rc = h_rcmean + h_siglev*h_SErc
    h_cr_low_rc = h_rcmean - h_credsig*h_SDp
    h_cr_high_rc = h_rcmean + h_credsig*h_SDp
    
    h_cl_ES_low = h_AveZ - h_siglev*h_SEZes
    h_cl_ES_high = h_AveZ + h_siglev*h_SEZes
    h_Fisher_cl_low = (math.exp(2*h_cl_ES_low)-1) / (math.exp(2*h_cl_ES_low)+1)
    h_Fisher_cl_high = (math.exp(2*h_cl_ES_high)-1) / (math.exp(2*h_cl_ES_high)+1)
    h_Q = h_sum_wES2 - h_sum_wES**2/h_sum_w
    h_dr = h_K -1
    h_l2 = (h_Q - (h_K-1))/h_Q
    print(h_sum_w,h_sum_w2)
    h_T2 = (h_Q - (h_K -1)) / (h_sum_w - h_sum_w2/h_sum_w)
    if  h_Q <= h_K-1:
        h_l2 = 0
        h_T2 = 0
    for p in pairs:
        p['h_FisherWi'] = float(1/(h_T2 + p['h_ASEF']**2))
    h_sumWStar = sum([x['h_FisherWi'] for x in pairs])
    h_RE_AveZ_toAdd =  [x['h_FisherWi']*x['h_AZ'] for x in pairs]
    h_RE_AveZ = sum(h_RE_AveZ_toAdd)/h_sumWStar
    h_fisherrandom = (math.exp(2*h_RE_AveZ)-1) / (math.exp(2*h_RE_AveZ)+1)
    h_RESEz = 1/math.sqrt(h_sumWStar)
    h_RE_cl_ES_low = h_RE_AveZ - h_siglev*h_RESEz
    h_RE_cl_ES_high = h_RE_AveZ + h_siglev*h_RESEz
    h_RE_Fisher_cl_low = (math.exp(2*h_RE_cl_ES_low)-1) / (math.exp(2*h_RE_cl_ES_low)+1)
    h_RE_Fisher_cl_high = (math.exp(2*h_RE_cl_ES_high)-1) / (math.exp(2*h_RE_cl_ES_high)+1)
    
    results = {}
    results['N'] =  h_N
    results['K'] =  h_K
    results['average'] =  h_average
    results['sig1'] =  int(h_sig1*100)
    results['sig2'] =  int(h_sig2*100)
    results['FSN'] =  h_FSN
    results['Q'] =  h_Q
    results['dr'] =  h_dr
    results['l2'] =  h_l2*100
    results['rmean'] =  h_rmean
    results['sigmar2'] =  h_sigmar2
    results['SDr'] =  h_SDr
    results['SEr'] =  h_SEr
    results['sigmae2'] =  h_sigmae2
    results['sigmap2'] =  h_sigmap2
    results['sigmap'] =  h_sigmap
    results['percExp'] =  h_percExp
    results['cl_low_r'] =  h_cl_low_r
    results['cl_high_r'] =  h_cl_high_r
    results['cr_low_r'] =  h_cr_low_r
    results['cr_high_r'] =  h_cr_high_r
    results['rcmean'] =  h_rcmean
    results['var_rc'] =  h_var_rc
    results['AveVe'] =  h_AveVe
    results['Varp'] =  h_Varp
    results['SDp'] =  h_SDp
    results['SDrc'] =  h_SDrc
    results['SErc'] =  h_SErc
    results['cl_low_rc'] =  h_cl_low_rc
    results['cl_high_rc'] =  h_cl_high_rc
    results['cr_low_rc'] =  h_cr_low_rc
    results['cr_high_rc'] =  h_cr_high_rc
    results['AveZ'] =  h_AveZ
    results['SEZes'] =  h_SEZes
    results['rfisherfixed'] =  h_rfisherfixed
    results['Fisher_cl_low'] =  h_Fisher_cl_low
    results['Fisher_cl_high'] =  h_Fisher_cl_high
    results['cl_ES_low'] =  h_cl_ES_low
    results['cl_ES_high'] =  h_cl_ES_high
    results['RE_AveZ'] =  h_RE_AveZ
    results['RE_SEz'] =  h_RESEz
    results['rfisherrandom'] =  h_fisherrandom
    results['T2'] =  h_T2
    results['RE_cl_ES_low'] =  h_RE_cl_ES_low
    results['RE_cl_ES_high'] =  h_RE_cl_ES_high
    results['RE_Fisher_cl_low'] =  h_RE_Fisher_cl_low
    results['RE_Fisher_cl_high'] =  h_RE_Fisher_cl_high
    return pairs,results

def fillMetaAnalTable(theProj, varids,sig1,sig2):
    results = []
    for i in range(len(varids)):
        row = []
        for j in range(len(varids)):
            if i==j:
                row.append("1")
                continue
            analRes = getAnalysisResults(theProj, [varids[i]], [varids[j]], sig1, sig2, forMeta=True)
            if j<i:
                if analRes['rcmean']!=".":
                    row.append('% 6.4g' % analRes['rcmean'])
                else:
                    row.append(".")
            elif i<j:
                value = str(analRes['K'])+" ("+str(analRes["N"])+")"
                if "." not in [analRes['cl_low_rc'],analRes['cl_high_rc']] and analRes['cl_low_rc']*analRes['cl_high_rc']>0: #They had the same sign
                    value = value[:-1]+"**)"
                row.append(value)
                
        results.append(row)
    return results



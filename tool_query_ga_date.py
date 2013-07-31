#encoding=utf-8

################################################################################
# Copyright (c) 2013 zqicheng
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################

import sys,csv,os,re
import sample_utils
import cPickle as p
import time
import datetime
from datetime import date
import tool_read_config
import socket
import copy
import tool_class as tc

from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from math import ceil, floor

#读取恢复记录
def read_cPickle(infile):
    list=[]
    f=open(infile,'r')
    list=p.load(f)
    return list
    
#写结果
def write_result(list,outfile):
    '''
    write a txt
    
    ''' 
    target =outfile
    line=[]
    f=open(target,'ab') #open for 'w' writting
    for i in list:
        try:
            if isinstance(i, unicode):
                newj=i.encode('gbk')
            else:
                newj=i
        except:           
            print newj,i
            break
        f.write(i)
    f.close() #close the file   

    
#记录未完成队列
def write_cPickle(list,outfile):
    f = file(outfile, 'w')
    p.dump(list, f) # dump the object to a file
    f.close()

    
def get_api_query(service,queryVar):
  """Returns a query object to retrieve data from the Core Reporting API.
  Args:
    service: The service object built by the Google API Python client library.
  """  

  if queryVar['ids']=='':
    raise TypeError('Missing required parameter GAID')
  if queryVar['start_date']=='':
    raise TypeError('Missing required parameter Start_Date')
  if queryVar['end_date']=='':
    raise TypeError('Missing required parameter end_date')
  if queryVar['metrics']=='':
    raise TypeError('Missing required parameter metrics')
  if queryVar['metrics']!='': #set sort metrics
    if queryVar['sort']=='':
        sortLine=queryVar['metrics'].split(',')    
        queryVar['sort']='-'+str(sortLine[0])
  if queryVar['dimensions']=='':
    queryVar['dimensions']='ga:date'
  if queryVar['start_index']=='':
    queryVar['start_index']=1
  if queryVar['max_results']=='':
    queryVar['max_results']=50
    
  
  segment=queryVar['segment'],
  filters=queryVar['filters'],
      

  if queryVar['segment']=='':
    if queryVar['filters']=='':
        return service.data().ga().get(
          ids=queryVar['ids'],
          start_date=queryVar['start_date'],
          end_date=queryVar['end_date'],
          metrics=queryVar['metrics'],
          dimensions=queryVar['dimensions'],
          sort=queryVar['sort'],
    #      segment=queryVar['segment'],
    #      filters=queryVar['filters'],
          start_index=queryVar['start_index'],
          max_results=queryVar['max_results'])
    else:
        return service.data().ga().get(
          ids=queryVar['ids'],
          start_date=queryVar['start_date'],
          end_date=queryVar['end_date'],
          metrics=queryVar['metrics'],
          dimensions=queryVar['dimensions'],
          sort=queryVar['sort'],
    #      segment=queryVar['segment'],
          filters=queryVar['filters'],
          start_index=queryVar['start_index'],
          max_results=queryVar['max_results'])      
  elif queryVar['segment']!='':
    if queryVar['filters']=='':
        return service.data().ga().get(
          ids=queryVar['ids'],
          start_date=queryVar['start_date'],
          end_date=queryVar['end_date'],
          metrics=queryVar['metrics'],
          dimensions=queryVar['dimensions'],
          sort=queryVar['sort'],
          segment=queryVar['segment'],
    #      filters=queryVar['filters'],
          start_index=queryVar['start_index'],
          max_results=queryVar['max_results'])
    else:
        return service.data().ga().get(
          ids=queryVar['ids'],
          start_date=queryVar['start_date'],
          end_date=queryVar['end_date'],
          metrics=queryVar['metrics'],
          dimensions=queryVar['dimensions'],
          sort=queryVar['sort'],
          segment=queryVar['segment'],
          filters=queryVar['filters'],
          start_index=queryVar['start_index'],
          max_results=queryVar['max_results'])      


def get_report(results):
    info = results.get('profileInfo')
    tableid=info.get('tableId')
    profilename=info.get('profileName')
    headers = results.get('columnHeaders')
    sampleDate=results.get('containsSampledData')
    resultsAll=[]
    headerCon=['tableId','profileName','sampleDate']
    for header in headers:
        headerCon.append(header.get('name'))
    resultsAll.append(headerCon)
    if results.get('rows',[]):
        for row in results.get('rows'):
            newresults=[tableid,profilename,sampleDate]
            for irow in row:
                newresults.append(irow)
            resultsAll.append(newresults)
    return resultsAll 
            
            
            
def get_all_report(service,queryVar,max,outfile):
    list=[]
    start_index=int(queryVar['start_index'])
    max_results=int(max)
    if max_results<=10000:
        results = get_api_query(service,queryVar).execute()
        list=get_report(results)
        #print_result(list,outfile)
        #print 'Wirte Over'
    
    
    elif max_results>10000:
        results = get_api_query(service,queryVar).execute()
        list=get_report(results)
        resultsLen=results.get('totalResults')     
        print 'max:%d,totalResults:%d'% (max_results,resultsLen) 
        if(resultsLen>10000 and resultsLen>=max_results):
            while len(list)<max_results:
                new_start_index=start_index+len(list)-1 #set new start index
                dif_len=max_results-len(list)
                if dif_len>=10000:
                    new_max_results=10000
                else:
                    new_max_results=dif_len
                print 'len list:%d, max_results:%d,start_index:%d' %(len(list),new_max_results,new_start_index)
                new_queryVar=queryVar
                new_queryVar['start_index']=new_start_index
                new_queryVar['max_results']=new_max_results
                results = get_api_query(service,new_queryVar).execute()
                tmp_list=get_report(results)
                list.extend(tmp_list)
        elif(resultsLen>10000 and max_results>resultsLen):
            while len(list)<resultsLen:
                new_start_index=start_index+len(list)-1 #set new start index
                dif_len=resultsLen-len(list)
                if dif_len>=10000:
                    new_max_results=10000
                else:
                    new_max_results=dif_len
                print 'len list:%d, max_results:%d,start_index:%d' %(len(list),new_max_results,new_start_index)
                new_queryVar=queryVar
                new_queryVar['start_index']=new_start_index
                new_queryVar['max_results']=new_max_results
                results = get_api_query(service,new_queryVar).execute()
                tmp_list=get_report(results)
                list.extend(tmp_list)                
            #print len(list)
            #print_result(list,outfile)
        else:
            pass
            #results = get_api_query(service,queryVar).execute()  #no need query when max <10000
            #list=get_report(results)
            #print_result(list,outfile)
    return list
        
            
###need writer new print function    
def print_result(list,outfile,tc):
    innerlen=0
    target =outfile+'.csv'
    f=open(target,'ab') #open for 'w' writting
    csvwriter=csv.writer(f)
    for i in list:
        line=[]
        for j in i:
            try:
                if isinstance(j, unicode):
                    newj=j.encode('gbk')
                else:
                    newj=j
            except:           
                print newj,i
                break
            line.append(newj)
        if os.path.getsize(target)==0:
            csvwriter.writerow(line)
        else:
            if line[0]!='tableId':
                csvwriter.writerow(line)
        innerlen=innerlen+1
    tc.setTabLen(tc.getTabLen()+innerlen)
    print 'write csv:',innerlen
    f.close() #close the file


def get_inputQueryStack(queryVarList,file):
    """
    you should set a file ,ex:file=setdir+'\\date\\'+str(ctime)
    the outpath is file+outfilename
    """
    queryStack=tc.Stack()
    for queryVar in queryVarList:
        idList=queryVar['ids'].split(',')
        querytype=queryVar['querytype']
        outfilename=queryVar['outfilename']
        start_date=queryVar['start_date']
        end_date=queryVar['end_date']
        outfile=file+'_'+outfilename #Test change,need later del end_date
        for id in idList:            
            if queryVar['max_results']=='':
                max_results=50
            else:
                max_results=int(queryVar['max_results'])
            if queryVar['start_index']=='':
                start_index=1
            else:
                start_index=int(queryVar['start_index'])
            if querytype=='1':
                sday=datetime.datetime.strptime(start_date,'%Y-%m-%d')
                eday=datetime.datetime.strptime(end_date,'%Y-%m-%d')
                queryVar['start_date']=sday.strftime("%Y-%m-%d")
                queryVar['end_date']=eday.strftime("%Y-%m-%d")
                queryVar['ids']=id
                queryVar['outfilename']=outfile
                queryVar['max_results']=max_results
                queryStack.push(copy.deepcopy(queryVar))
                    
            if querytype=='0':
                sday=datetime.datetime.strptime(start_date,'%Y-%m-%d')
                eday=datetime.datetime.strptime(end_date,'%Y-%m-%d')
                print sday,eday
                day=eday-sday
                print int(day.days)+1
                if day.days>0:
                    for i in range (0,day.days+1):
                        stime=sday+datetime.timedelta(days=i)
                        new_start_date=stime.strftime("%Y-%m-%d")
                        nt_queryVar=queryVar
                        nt_queryVar['start_date']=new_start_date
                        nt_queryVar['end_date']=new_start_date
                        nt_queryVar['ids']=id
                        nt_queryVar['outfilename']=outfile+'_'+str(new_start_date)  #test change,need to del 
                        queryStack.push(copy.deepcopy(nt_queryVar))
                else:
                    print "the input date diff is %d,you should change date!!" % int(day.days)
                    sys.exit()
    return queryStack

def get_scheduleQueryStack(queryVarList,file,difday):
    """
    reture a query stack
    """
    queryStack=tc.Stack()
    for queryVar in queryVarList:
        idList=queryVar['ids'].split(',')
        querytype=queryVar['querytype']
        outfilename=queryVar['outfilename']
        start_date=queryVar['start_date']
        end_date=queryVar['end_date']
        outfile=file+'_'+outfilename
        for id in idList:            
            if queryVar['max_results']=='':
                max_results=50
            else:
                max_results=int(queryVar['max_results'])
            if queryVar['start_index']=='':
                start_index=1
            else:
                start_index=int(queryVar['start_index'])
            et=datetime.datetime.strptime(str(date.today()),'%Y-%m-%d')-datetime.timedelta(days=int(difday))
            stimeTostr=et.strftime("%Y-%m-%d")
            
            sday=datetime.datetime.strptime(start_date,'%Y-%m-%d')
            eday=datetime.datetime.strptime(end_date,'%Y-%m-%d')
            queryVar['start_date']=stimeTostr
            queryVar['end_date']=stimeTostr
            queryVar['ids']=id
            queryVar['outfilename']=outfile
            queryVar['max_results']=max_results
            queryStack.push(copy.deepcopy(queryVar))
                    
    return queryStack

  
    


def gui_get_date(configDict):
    proxyDict={}
    countCon=tc.Count()
    
    
    proxyDict['proxy']=configDict['proxy']
    proxyDict['proxyPort']=configDict['proxyPort']
    proxyDict['proxyIP']=configDict['proxyIP']
    FileList=configDict['filename']
    difdate=configDict['difdate']
    inType=configDict['inType']
    outType=configDict['outType']
    
    print "inType:%s,outtype:%s" % (inType,outType)
    
    setdir=os.path.abspath('.')
    erroLogger=tc.initlog(countCon.getErroLogger())#初始化Log地址
    runLogger=tc.initlog(countCon.getRunLogger())
    
    ctime=time.strftime('%Y%m%d',time.localtime())
    queryStack=tc.Stack()
    outfile=setdir+'\\date\\'+str(ctime) 
 
    if inType=='csv':
        queryVarList=tool_read_config.read_queryCsv(FileList)
        queryStack=get_inputQueryStack(queryVarList,outfile)
    elif inType=='sd':
        queryVarList=tool_read_config.read_queryCsv(FileList)    
        queryStack=get_scheduleQueryStack(queryVarList,outfile,difdate)#调度模式，获取3天前的数据
    elif inType=='qs':
        f=setdir+'\\date\\'+FileList
        print u'恢复模式，恢复文件为：',f
        queryStack=read_cPickle(f)
    else:
        print 'input error'
#        sys.exit()

    tryCon=3
    while tryCon>0:
        try:    
            service=sample_utils.initialize_service(proxyDict)
            break
        except socket.error,error:
            erroLogger.error('service:'+str(error))
            tryCon=tryCon-1
            time.sleep(10)
            service=None
            erroLogger.warning('tryCon:'+str(3-tryCon))
            print 'tryCon:'+str(3-tryCon)
    
    
    tryGet=3  
    resultList=[]
    while queryStack.length()!=0 and tryGet!=0 and service!=None:
        query=queryStack.pop()
        try:
            resultsList=get_all_report(service,query,query['max_results'],query['outfilename'])
            print 'len:',len(resultsList)
            if outType=='csv':
                print_result(resultsList,query['outfilename'],countCon)
            elif outType=='sql':
                print 'need coding....'
                #into_table(cur,resultsList)  #insert into mysql
            print 'still have queryList:%d'% queryStack.length()
        except Exception,error:
            print error
            erroLogger.error('get report:'+str(error))
            queryStack.push(query)
            tryGet=tryGet-1
            time.sleep(1)
            erroLogger.warning('tryGet:'+str(3-tryGet))
            print 'tryGet:'+str(3-tryGet)
    if queryStack.length()!=0:
        write_cPickle(queryStack,setdir+'\\date\\'+str(ctime)+'.qs')
        erroLogger.warning('query is stop'+str(queryStack.length()))
        return False
        
    if queryStack.length()==0:
        runLogger.warning('queryList is over:'+str(countCon.getTabLen()))
        return True
    
    
    



if __name__=='__main__':
    setdir=os.path.abspath('.')
    conf=tool_read_config.read_config(setdir+'\\conf.ini')
    print conf
    gui_get_date(conf)


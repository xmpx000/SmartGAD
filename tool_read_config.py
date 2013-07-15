#read config from input.csv;return a queryList.
#you can edit input.csv
#encoding=utf-8

import sys, os,re,csv

def read_queryCsv(infile):
    queryList=[]
    tmpline=[]
    confile=infile
    if os.path.isfile(confile)==True:
        try:            
            in_file=open(confile,'r')
            while True:
                line=in_file.readline()
                if not line:
                    break
                if line.strip('\n')=='':
                    break
    #need to change coder                       
                if line.startswith('#')==False:
                    tmpline.append(line.split(',')) 
            in_file.close()
        except IOError:
            print 'error joining'    
    else:
        print 'No file!'
    #read over,creat dict
    if len(tmpline)>0:
        for i in range(0,len(tmpline)/12):
            dict={}
            for j in range(0,12):
                x=i*12+j
                k=tmpline[x][0]
                iv=tmpline[x][1:]               
                v=','.join(iv).rstrip('\n')
                if v.count('\"')==0:
                    vv=v
                else:
                    vv=v.replace('\"','')
                dict[k]=vv
            if dict['start_date'].count('/'):
                st=dict['start_date'].replace('/','-')                
                dict['start_date']=st
            if dict['end_date'].count('/'):
                et=dict['end_date'].replace('/','-')
                dict['end_date']=et
            queryList.append(dict)
#return querylist
    return queryList

def read_config(infile):
    queryList=[]
    tmpline=[]
    confile=infile
    dict={}

    if os.path.isfile(confile)==True:
        try:            
            in_file=open(confile,'r')
            while True:
                line=in_file.readline()
                if not line:
                    break
                if line.startswith('#')==False:
                    tmpline.append(line.split(',')) 
            in_file.close()
        except IOError:
            print 'error joining'    
    else:
        print 'No file!'
    #read over,creat dict
    
    if len(tmpline)>0:
        for i in range(0,len(tmpline)):
            if tmpline[i][0].strip('\n')!='':
                tmp=tmpline[i][0].split('=')
                dict[tmp[0]]=tmp[1].rstrip('\n')
#return querylist
    return dict    
    

    
if __name__=='__main__':
    setdir=os.path.abspath('.')+'\\conf.ini'
    dictCon=read_config(setdir)
    for (k ,v) in dictCon.items():
        print k,v

 #--encofing UTF-8
#Author : Farhad Nadi
#version:399.12.1.0 
import logging as log

import ast
import json
# import pyodbc
import sqlalchemy as sal
from sqlalchemy import create_engine
from sqlalchemy.sql import text

import datetime
import enum


FORMAT = '%(levelname)s (%(asctime)s):\t%(message)s '
 
log.basicConfig(level=log.INFO, format=FORMAT)

class cls_mssql2rest():

    def __init__(self, server_name, database_name, user_name, Password, querys_dict ):
        self.server_name = server_name
        self.database_name = database_name
        self.user_name = user_name
        self.Password = Password
        querynormal = {}
        queryparametrics = {}
        for key,value in  querys_dict.items():
            if ":param" in value:
                queryparametrics[key] = value
            else:
                querynormal[key] = value

        # print(f'parametric :{queryparametrics}')
        # print(f'normal :{querynormal}')

        self.querys_dict = querynormal
        self.querys_parametric = queryparametrics

        self.connect()
    
    def returndatatype(self, a):
        # print(a,type(a))
        if a.isdigit():
            return "int"
        elif a.replace('.','',1).isdigit() and a.count('.') < 2:
            return "float"
        else:
            return "str"
        
    def connect(self): 
        cstr = f"mssql+pyodbc://{self.user_name}:{self.Password}@{self.server_name}/{self.database_name}?driver=ODBC Driver 17 for SQL Server?Trusted_Connection=yes"
        log.info(f'start connecting to database : {cstr}')
        self.engine = sal.create_engine(cstr)
        self.isconnected = self.engine is not None
        if self.isconnected:
            log.info(f"A connection has been made to {self.server_name}/{self.database_name}")
        else:
            log.error(f"Unable to establish a connection to the provided server. {self.server_name}/{self.database_name}")
    
    def ret_methods(self):
        return  json.loads(json.dumps(dict({"routes":','.join(self.querys_dict.keys())})) )


    def ret_methodsnamesastuple(self):
        result=[]
        log.info(f'keys :{self.querys_dict.keys()}')

        for key in list(self.querys_dict.keys()):    
            result.append(tuple(( key , key)))
        log.info(result)
        return result


    def retcols(self, queryname):
        with self.engine.connect() as con:                            
            if queryname in self.querys_dict:
                rs = con.execute(self.querys_dict[queryname].replace('select','select top 1 '))
                #coldic={"name":rs.keys(), "type":"","friendly_name":""}                                           
                colslst= []#rs.keys()
                val = dict( rs.fetchone() )


                for k in rs.keys():
                    # if "E_" not in k:
                    colslst.append({"name":k, "type":str(type(val[k]).__name__),"friendly_name":k})
        # print(json.dumps(colslst))     
        return json.loads(json.dumps(colslst,   ensure_ascii=False).replace('\n',''))
        

    def retquery_JSONDS(self, queryname):
        colsd =  (self.retcols(queryname))
        rowsd =  (self.retquery(queryname))
        alld = {}

        alld["columns"] = colsd
        alld["rows"] = rowsd
        # print(alld)
        return json.loads( json.dumps(alld,   ensure_ascii=False))#ast.literal_eval( {f'"columns":{self.retcols(queryname)}, "ROWS":{self.retquery(queryname)}'})

    def datetime_handler(self, x):
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("Unknown type")
    
    def returnQueryByParam(self, queryname, aparamvalue):

        if self.isconnected:
            with  self.engine.connect() as con:                            
                if queryname in self.querys_parametric.keys():
                    log.info(f'start of running a query with parameter [{queryname}:{aparamvalue}]')    
                    querstring = text(self.querys_parametric[queryname])
                                    
                    rs =con.execute(querstring, {"param":aparamvalue}).fetchall() 
                    ml=[]

                    for row in rs:                             
                        ml.append( json.loads(  json.dumps(dict(row),   ensure_ascii=False,  default = self.datetime_handler))         )
                                             
                    log.info(f"A total of {len(ml)} records returned.")
                    return ml#json.loads((json.dumps(ml, indent=4, ensure_ascii=False) ))       

                else:
                    log.error("an unknow error occured.")
                    return json.loads(('{"error":"Unknown query"}'))
        else:
            log.error('Connection is not established.')
            return json.loads('{"error":"no connection"}')
                    
    
    def retquery(self, queryname):  
        log.info(f"connection status {self.isconnected}")

        if self.isconnected:
            with  self.engine.connect() as con:                            
                if queryname in self.querys_dict:
                    log.info(f'executing query {queryname}')
                    rs =con.execute(self.querys_dict[queryname])
                    ml=[]

                    for row in rs:                             
                        ml.append( json.loads(  json.dumps(dict(row),   ensure_ascii=False,  default = self.datetime_handler))         )
                                             
                    log.info(f"A total of {len(ml)} records returned.")
                    return ml#json.loads((json.dumps(ml, indent=4, ensure_ascii=False) ))       

                else:
                    log.error("an unknow error occured.")
                    return json.loads(('{"error":"Unknown query"}'))
        else:
            log.error('Connection is not established.')
            return json.loads('{"error":"no connection"}')
                    


if __name__ == '__main__':
    server_name = '172.30.200.137'
    database_name = 'Farabar24'
    user ='DataManagement'
    password='Data@Management123'
    qz = {'rasad':'SELECT top 1 * FROM [fava].[V_آمارنامه_اطلاعات-رصدخانه_3120]', 
          'test2':'SELECT * FROM [fava].[V_سازمان-خدمات-موتوري_اطلاعات-مصرف-سوخت_1914]',          
          "ProjectByID":"SELECT  *  FROM [fava].[V_آمارنامه_اطلاعات-رصدخانه_3120] where [مقدار] = :param"
         }
    cls = cls_mssql2rest(server_name, database_name, user, password, qz)
    
    print(cls.retquery('rasad'))
    print(cls.returnQueryByParam('ProjectByID','6.3'))
 
    # print(cls.ret_methods())
    # engine = sal.create_engine(f'mssql+pyodbc://{user}:{password}@{server_name}/{database_name}?driver=SQL Server?Trusted_Connection=yes')

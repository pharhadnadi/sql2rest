
# from typing import Optional
 
from enum import Enum
import json
import os

from pydantic.networks import HttpUrl
from pydantic.types import FilePath
import sys
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
# import  pydantic
# from pydantic import BaseModel
import   _documentaions as docz

from cls_db2rest import cls_mssql2rest
from cls_db2rest import log
 

Dynaenum =[]
cls_sql2rest = None



# from fastapi.responses import HTMLResponse
# @app.get("/intro/", response_class=HTMLResponse)
# async def read_items():
#     return """
#     <html>
#         <head>
#             <title>Some HTML in here</title>
#         </head>
#         <body>
#             <h1>Look ma! HTML!</h1>
#         </body>
#     </html>
#     """
# SetQueries=Enum


_config=''
# if __name__ == '__main__':    
if 'DB_NAME' == os.environ:
    if  os.path.exists(str(os.environ)):
        _config = os.environ.get('DB_NAME')
        log.info(f'considering {_config} as config file.')
    else:
        log.error(f'no config file found in the specified path ({_config})')

   
if _config=='':
    log.info('trying to find default config file (db/db.json).')
    defconf = 'db/db.json'
    if  os.path.exists(defconf):   
        _config = defconf
        log.info(f'start to load default config file ({_config}).')
    else:
        log.error(f'Config file ({defconf}) not found.')

if len(_config)>0:    
    try:
        log.info(f'loading {_config}')
        file = open(_config)
        _configinfo = json.loads(file.read())

        myd={}
        for d in  _configinfo['methods'] :
            strmethodname = list(d)[0]
            strquery  = list(d.values())[0]
            myd.update({strmethodname: strquery})
            #adding a default sandbox to each method if method name does not contain any sandbox 
            if ('sandbox' not in strmethodname.lower()) :
                myd.update({f'{strmethodname}Sandbox': f'select top 100 * from ({strquery}) as query1 order by 1'})

        
        log.info(f"server ->{_configinfo['server']}")
        log.info(f"database ->{_configinfo['database']}")
        log.info(f"user ->{_configinfo['user']}")
        log.info(f"password ->{_configinfo['password']}")
        # log.info(f"queryz ->{myd}")


        cls_sql2rest =  cls_mssql2rest(
            _configinfo['server'],
            _configinfo['database'],
            _configinfo['user'],    
            _configinfo['password'],    
            myd 
        )

 
        Dynaenum  = cls_sql2rest.ret_methodsnamesastuple()


        SetQueries = Enum('queries',  Dynaenum)
        log.info(f'available query names : {SetQueries}')
        for i in myd.keys():
            log.info(f'<SERVER>:<PORT>/GET/{i}')              
    except:
        log.error(f'unexpected error: {sys.exc_info()[0]}')
         

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MS SQL Server Rest API Generator",
        version="399.12.0",
        description="Generateing REST API from MSSQL databases and limited to GET methods only.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://ict.isfahan.ir/Dorsapax/Data/Sub_29/Template/fava95/img/201628292130logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(title = "DB2REST, A Data Management Unit product, Isfahan Municipality ICT Org.",
              openapi_tags=docz.tags_metadata)

app.openapi = custom_openapi


@app.get("/", tags=["root"])
async def read_root():
    return {"state": "Up and listening."}

@app.get("/info",  tags=["info"])
async def get_info():
    return cls_sql2rest.ret_methods()

@app.get("/GET/{A_Query_Name}",  tags=["Query"])
async def get_query(A_Query_Name:SetQueries, request: Request):
    log.info(f'query the results set for : { request.client.host}/{A_Query_Name.name}')
    if cls_sql2rest.isconnected:
        
        return  (  cls_sql2rest.retquery(A_Query_Name.name))
    else:
        return {'message':"No connection."}
 

@app.get("/GET/{A_Query_Name}/JSONDS",  tags=["Query"])
async def get_query(A_Query_Name:SetQueries, request: Request):
    log.info(f'query the results set for : { request.client.host}/{A_Query_Name.name}')
    if cls_sql2rest.isconnected:
        return   cls_sql2rest.retquery_JSONDS(A_Query_Name.name)
    else:
        return {'message':"No connection."}
 


@app.get("/GET/{A_Query_Name}/{PramValue}")
async def get_query_param(A_Query_Name: str, PramValue:str, request: Request):
    log.info(f'Query the results set for : { request.client.host}/{A_Query_Name}/{PramValue}')
    if cls_sql2rest.isconnected:
        
        return  (  cls_sql2rest.returnQueryByParam(A_Query_Name, PramValue))
    else:
        return {'message':"No connection."}

# cls_mssql2rest = cls_mssql2rest(server_name, database_name, user, password, qz)


# server_name = '172.30.200.137'
#     database_name = 'Farabar24'
#     user ='DataManagement'
#     password='Data@Management123'
#     qz = {'rasad':'SELECT  *  FROM [fava].[V_آمارنامه_اطلاعات-رصدخانه_3120]', 'test2':'SELECT *  FROM [fava].[V_سازمان-خدمات-موتوري_اطلاعات-مصرف-سوخت_1914]'}
#     cls = 
#     print(cls.retquery('test2'))
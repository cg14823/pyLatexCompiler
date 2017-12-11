import os
import json
import shutil
import tempfile
import bottle
from bottle import Bottle, run, get, post, request, response, error, route
from postgresStore import PostgresFileStore
from s3filestore import S3FileStore
from latexCompile import pdflatex

def create_conf():
    "Get configuration from env"
    return {
        'port': os.environ['PORT'],
        'dbhost': os.environ['RDS_HOSTNAME'],
        'dbuser': os.environ['RDS_USERNAME'],
        'dbpass': os.environ['RDS_PASSWORD'],
        'dbname': os.environ['RDS_DB_NAME'],
        'dbport': os.environ['RDS_PORT'],
        'compilerSecret': os.environ['COMPILER_SECRET_KEY'],
        'bucket': os.environ['BUCKET_NAME']
    }


application = bottle.default_app()
conf = create_conf()
StatusCodes = {
    'OK': 200,
    'BadRequest': 400,
    'Unauthorized': 401,
    'Forbidden': 403,
    'NotFound': 404,
    'InternalServerError': 500,
}

stateStore = PostgresFileStore(dbname=conf['dbname'], host=conf['dbhost'], port=conf['dbport'], user=conf['dbuser'], password=conf['dbpass'])
fileStore = S3FileStore(bucket=conf['bucket'])

@get('/')
def landpage():
    return "HELLO"

@post('/compile')
def compile():
    "Get post request and compile"
    response.content_type = 'application/json'
    respObject = {}
    if request.headers.get('X-Compiler-Token') == conf['compilerSecret']:
        if 'uid' in request.json and 'projectName' in request.json:
            uid = request.json['uid']
            projectName = request.json['projectName']
            projectDetails = stateStore.GetProjectDetails(projectName, uid)

            if projectDetails == None:
                respObject = {'Error': 'Project details where not found'}
                response.status = StatusCodes['BadRequest']
                return json.dumps(respObject)
            
            projectFileDetails = stateStore.GetProjectFiles(projectDetails['pid'])
            if projectFileDetails == None:
                respObject = {'Error': 'Project file details where not found'}
                response.status = StatusCodes['BadRequest']
                return json.dumps(respObject)
            
            folder_uuid = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
            main_file = projectDetails['mainFile']

            for f in projectFileDetails:
                fileUrl = folder_uuid+"/"+f['fileName']
                fileKey = f['url']
                fileStore.get_file(fileUrl, fileKey)

            success, fileOut, logs = pdflatex(folder_uuid, main_file)

            if not success:
                cleanUp(folder_uuid)
                respObject = {'Error': 'Failed to compile', 'logs': logs}
                request.status = StatusCodes['InternalServerError']
                return json.dumps(respObject)
            
            fileName = fileOut[fileOut.rfind("/")+1:]
            fileStore.put_file(fileOut,fileName)
            cleanUp(folder_uuid)

            respObject = {'Error': '', 'logs': logs, 'Filename':fileName}
            response.status = StatusCodes['OK']
            return json.dumps(respObject)

        else:
            respObject = {'Error': 'user id or project name missing'}
            request.status = StatusCodes['BadRequest']
        
    else:
        respObject = {'Error': 'Not allowed'}
        response.status = StatusCodes['F=cooplatex-filesorbidden']
    
    return json.dumps(respObject)

@error(404)
def error404(error):
    print(error)
    print(request)
    response.status = StatusCodes['NotFound']
    response.content_type = 'application/json'
    return json.dumps({'ERROR':''})

def cleanUp(location):
    """ remove temp files """
    return shutil.rmtree(location)

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
"""This file will store al postgresql communications"""
import psycopg2

class PostgresFileStore:
    conn = []
    cursor = []
    def __init__(self,dbname, host, port, user, password):
        """ create new PostfresFileStore object """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self.cursor = self.conn.cursor()

    def Close(self):
        """ close connection """
        self.conn.close()
    
    def GetProjectFiles(self, projectID):
        """ Return the files that match projectID if no files are foudn return None"""
        query = "SELECT file_type, project_id, url, file_name FROM editor_files WHERE project_id=(%s);"
        data = [projectID]
        self.cursor.execute(query, data)
        files = self.cursor.fetchall()
        self.conn.commit()
        if len(files) == 0:
            return None
        
        fileData = []
        for vals in files:
            fileData.append({
                'type': vals[0],
                'pid': vals[1],
                'url': vals[2],
                'fileName':vals[3]
                })

        return fileData

    def GetProjectDetails(self, projectName, ownerID):
        """ Retrieves project details """
        query = "SELECT id, owner_id, name, main_file FROM editor_project WHERE name=(%s) AND owner_id=(%s);"
        data = [projectName, ownerID]
        self.cursor.execute(query, data)
        data = self.cursor.fetchone()
        self.conn.commit()
        if data == None:
            return data
        
        return {'pid': data[0], 'uid': data[1], 'name': data[2], 'mainFile': data[3]}

    def ProjectCompiled(self, projectName, ownerID, pdfName):
        """ Update Project data """
        query = "UPDATE editor_project SET compiled=1, compiled_file=(%s) WHERE name=(%s) and owner_id=(%s);"
        data = [pdfName,projectName, ownerID]
        self.cursor.execute(query,data)
        self.conn.commit()
        return 

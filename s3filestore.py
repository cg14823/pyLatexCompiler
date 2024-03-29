""" All interactions with s3 in this file """
import boto3

class S3FileStore:
    """s3FileStore is a class to interface with amazon s3"""
    def __init__(self, bucket, akid, secretKey):
        """ initalize s3FileStore object """
        session = boto3.session.Session(
            aws_access_key_id=akid,
            aws_secret_access_key=secretKey,
        )
        self.s3 = session.resource('s3')
        
        self.bucket = bucket
    
    def put_file(self, fileURL, fileName):
        """ upload file to s3 """
        f = open(fileURL, 'rb')
        self.s3.Bucket(self.bucket).put_object(
            Body=f,
            ContentType='application/pdf',
            Key=fileName
        )
        f.close()

    def get_file(self, fileURL, fileName):
        """ get files from s3 """
        with open(fileURL, "wb") as f:
            self.s3.Bucket(self.bucket).download_fileobj(fileName, f)
            f.close()
        return True
    
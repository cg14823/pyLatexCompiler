""" This file willl have the compile commands """
import subprocess

def pdflatex(location, filename):
    """ will run command pdflatex $FILE$ with path context location, return (success, file, logs)"""
    p = subprocess.run(['pdflatex',filename], cwd=location, stdout=subprocess.PIPE)
    if p.returncode != 0:
        return False, "", str(p.stdout)
    else:
        ind = filename.rfind('.')
        newFileName = location+"/"+filename[:ind]+".pdf"
        return True, newFileName, str(p.stdout)
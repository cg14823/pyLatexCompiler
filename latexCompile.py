""" This file willl have the compile commands """
import subprocess

def pdflatex(location, filename):
    """ will run command pdflatex $FILE$ with path context location, return (success, file, logs)"""
    p = subprocess.run(['pdflatex',filename], cwd=location, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, timeout=20)
    if p.returncode != 0:
        print("ERROR OCCURED")
        return False, "", str(p.stdout)
    else:
        print("COMPILED")
        ind = filename.rfind('.')
        newFileName = location+"/"+filename[:ind]+".pdf"
        return True, newFileName, str(p.stdout)
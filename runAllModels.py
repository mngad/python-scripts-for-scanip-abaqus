import time
from abaqus import mdb
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import ON,THREADS
from abaqus import *
from abaqusConstants import *
from driverUtils import executeOnCaeGraphicsStartup
from caeModules import *
from os import chdir
from os import listdir
from os.path import isfile, join
import sys
import subprocess
import odbAccess
import csv
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

input_directory = os.getcwd() + '/'
output_directory = os.getcwd() + '/' #gets current directory

def cleanup(mostrecent):
    print >> sys.__stdout__, 'Clearing up - removing other loaded models and clearing job list'
    for model in mdb.models.keys():
        if len(mdb.models.keys()) == 1:
           break
        else:
           if model != mostrecent:
              del mdb.models[model]
    for jobclean in mdb.jobs.keys():
        del mdb.jobs[jobclean]

def getfiles(mypath, filetype):
    print >> sys.__stdout__, 'Loading list of [chosen file type] files from chosen directory'
    caefilelist=[]
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f))]
    for files in onlyfiles:
        if files.endswith(filetype):
           caefilelist.append(files)
    return caefilelist

def runJob(modelname):
    from abaqusConstants import *
    from abaqus import *
    import step
    jobname = modelname + '_ABAQUS'
    myJob = mdb.Job(model=modelname, name=jobname)
    myJob.setValues(numCpus=8,numDomains=8,multiprocessingMode=THREADS)
    myJob.writeInput()
    mdb.saveAs(myJob.name)
    print >> sys.__stdout__, jobname
    mdb.models[modelname].steps['loading_step'].setValues(initialInc=0.1, minInc=0.0001, maxInc=1)
    myJob.submit(consistencyChecking=OFF)
    #wait for job to complete before opening the odb and checking the stiffness
    myJob.waitForCompletion()

def main():
    os.chdir(output_directory)
    cae_list = []
    cae_list = getfiles(input_directory, ".cae")
    if cae_list:
        for i, current_file in enumerate(cae_list):
            current_model = current_file[:-4]
            # Import the next model in the folder
            openMdb(pathName= input_directory + current_file)
            # Delete all models except the one just imported, and delete all present jobs
            cleanup(current_model)
            runJob(current_model)
        else:
            print >> sys.__stdout__, 'No Files in Dir'

main()

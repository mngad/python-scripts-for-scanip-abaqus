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
stiffness = ''



def getfiles(mypath, filetype):
    print >> sys.__stdout__, 'Loading list of [chosen file type] files from chosen directory'
    caefilelist=[]
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f))]
    for files in onlyfiles:
        if files.endswith(filetype):
           caefilelist.append(files)
    return caefilelist


def outputStiffness(modelNameforstiffness):
    from abaqusConstants import *
    from abaqus import *
    print >> sys.__stdout__, 'Outputting stiffness for model' + modelNameforstiffness
    odb = session.openOdb(name= input_directory + modelNameforstiffness + '_ABAQUS.odb')
    #odb = session.odbs[modelNameforstiffness + '_ABAQUS.odb' ]
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('RF',NODAL, ((COMPONENT, 'RF3'), )), ), nodeSets=('REFERENCE_POINT_PLATEN-1        1', ))
    x0 = 0
    x0 = session.xyDataObjects['RF:RF3 PI: PLATEN-1 N: 1']
    stiffness = x0
    session.writeXYReport(fileName=modelNameforstiffness + '.txt' , xyData=(x0, ))
    odb.close()
    #delete xy data so that the new one for the next model has the same name
    del session.xyDataObjects['RF:RF3 PI: PLATEN-1 N: 1']

def combineToOneFile():
#horrible function to combine all the files with stiffnesses into one file
    os.chdir(output_directory)
    txtList = []
    allfiles = [f for f in listdir(output_directory) if isfile(join(output_directory,f))]
    for files in allfiles:
        if files.endswith('.txt'):
            txtList.append(files)
    arrayOfStiffness = []
    o = open('allStiffness.txt', 'w')
    o.write('Interface Stiffness: ' + str(interfaceMod) + ' GPa \n')
    o.write('Cement Stiffness: ' + str(cementMod) + ' GPa \n')
    for currentfile in txtList:
        f = open(currentfile, 'r')
        i=0
        for line in f:
            if i == 10:
                print >> sys.__stdout__, line
                o.write(currentfile[:-4] + ': ' + line[35:])
                arrayOfStiffness.append(line)
            i = i + 1
        f.close()
    o.close()

def main():
    os.chdir(output_directory)
    cae_list = []
    cae_list = getfiles(input_directory, ".cae")
    if cae_list:
        for i, current_file in enumerate(cae_list):
            current_model = current_file[:-4]
            # Import the next model in the folder
            #mdb.ModelFromInputFile(name = current_model, inputFileName = os.path.join(input_directory, current_file))
            openMdb(pathName= input_directory + current_file)
            a = mdb.models[current_model].rootAssembly
            session.viewports['Viewport: 1'].setValues(displayedObject=a)
            a = mdb.models[current_model].rootAssembly
            session.viewports['Viewport: 1'].setValues(displayedObject=a)

            outputStiffness(current_model)
        else:
            print >> sys.__stdout__, 'No Files in Dir'
    combineToOneFile()

main()

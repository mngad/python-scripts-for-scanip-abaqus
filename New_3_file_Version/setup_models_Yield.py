from abaqus import *
from abaqusConstants import *
from driverUtils import executeOnCaeGraphicsStartup
from caeModules import *
from os import chdir
from os import listdir
from os.path import isfile, join
import sys
import subprocess
import displayGroupOdbToolset as dgo
import odbAccess
import csv

encastre_set = 'NS_INFERIOR_ENDCAP_WITH_ZMIN'
stepName = 'loading_step'
displacement = -1.0
#input_directory = 'D:\VP_SCAN\T1_CC3_T6_CC2_AfterVP_BA_#642_1487\Abaqus testing/'
#output_directory = 'D:\VP_SCAN\T1_CC3_T6_CC2_AfterVP_BA_#642_1487\Abaqus testing/'
#load_point_csv_path = 'D:\VP_SCAN\T1_CC3_T6_CC2_AfterVP_BA_#642_1487\Abaqus testing/loadPosition.csv'
input_directory = os.getcwd()
output_directory = os.getcwd()
load_point_csv_path = os.getcwd() + '/loadPosition.csv'
analytical_plate_radius = 75.0

plastic_behaviour = 0 # If 0, model configured elastic only. If 1, elastic plastic material definition added with yield strain set as below:
yield_strain = 0.01

input_directory = os.getcwd() + '/'
output_directory = os.getcwd() + '/' #gets current directory
#conversion_factory = 0.0135976641182
conversion_factory = 0.012529
cementMod=1.715
interfaceMod=1.715
E1=0.7
E2=0.7
E3=1.715
v=0.3
G=0.93
#=====================================================================
stiffness = ''


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

def changeMatProp(myModel):


    mdb.models[myModel].materials['PM_INTERFACE_HMG'].Plastic(
        table=((0.0065, 0.0), ))
    mdb.models[myModel].materials['PM_INTERFACE_HMG'].elastic.setValues(
        table=((1.715, 0.3), ), type=ISOTROPIC)
    mdb.models[myModel].materials
    for mat in mdb.models[myModel].materials.keys():
        myMat = mdb.models[myModel].materials[mat]
        if mat.startswith('PMGS'):
            rho = int(myMat.density.table[0][0])
            if rho<1:rho=1
            E = rho*conversion_factory
            nu = 0.3
            del myMat.elastic
            myMat.Elastic(table=((E, nu), ))
        if mat.startswith('PM_CEMENT'):
            rho = int(myMat.density.table[0][0])
            if rho<1:rho=1
            E = cementMod
            nu = 0.3
            del myMat.elastic
            myMat.Elastic(table=((E, nu), ))
    #mdb.models[myModel].steps['loading_step'].setValues(nlgeom=ON)

def getpart(modelname):
    print >> sys.__stdout__, 'Getting part and instance names'
    partname = mdb.models[modelname].parts.keys()
    partname = partname[0]
    instancename = mdb.models[modelname].rootAssembly.instances.keys()
    instancename = instancename[0]
    return partname, instancename

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

def deleteinteractions(modelname):
    print >> sys.__stdout__, 'Deleting existing interactions'
    for interaction in mdb.models[modelname].interactions.keys():
        del mdb.models[modelname].interactions[interaction]
    for interaction_property in mdb.models[modelname].interactionProperties.keys():
        del mdb.models[modelname].interactionProperties[interaction_property]

def adjust_matprops(modelname, yield_strain):
    print >> sys.__stdout__, 'Adjusting element Youngs Modulus and yield stress...'
    materials = mdb.models[modelname].materials
    material_names = materials.keys()
    for current_mat in material_names:
        if current_mat.endswith("GS"):
            old_density_table = materials[current_mat].density.table
            if not old_density_table:
                new_density = 1.0
                materials[current_mat].density.setValues(table = ((new_density,),))
                materials[current_mat].elastic.setValues(table = (((new_density * 1.0),0.3),))
    if plastic_behaviour == 1:
        for current_mat in material_names:
            if current_mat.endswith("GS"):
                current_modulus = materials[current_mat].elastic.table[0][0]
                new_yield_stress = current_modulus * yield_strain
                mdb.models[modelname].materials[current_mat].Plastic(table=((new_yield_stress, 0.0), ))

def instancePart(modelName, partName):
    print >> sys.__stdout__, 'Creating platen instance'
    p = mdb.models[modelName].parts[partName]
    mdb.models[modelName].rootAssembly.Instance(name=(partName + '-1'), part=p, dependent=ON)

def alignPlaten(modelName, loadPoints):
    # Create a datum plane offset by 0 from the xy axis (ie, in the plane of the superior endcap surface)
    a = mdb.models[modelName].rootAssembly
    a.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=loadPoints[2])

    a1 = mdb.models[modelName].rootAssembly
    f1 = a1.instances['platen-1'].faces
    d1 = a1.datums

    counter = 0
    for a in range(500):
        try:
            highlight(d1[a])
            counter = a
        except KeyError:
            continue

    a1.FaceToFace(movablePlane=f1[0], fixedPlane=d1[counter], flip=OFF, clearance=0.0)

def translatePlaten(modelName, loadPoints):
    a = mdb.models[modelName].rootAssembly
    a.translate(instanceList=('platen-1', ), vector=(loadPoints[0], loadPoints[1], loadPoints[2]))

def createAnalyticalPlate(modelName, radius):
    s = mdb.models[modelName].ConstrainedSketch(name='__profile__',
    sheetSize=(radius * 2.0))
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.ConstructionLine(point1=(0.0, (-1.0 * radius)), point2=(0.0, radius))
    s.FixedConstraint(entity=g[2])
    s.Line(point1=(0.0, 0.0), point2=(radius, 0.0))
    s.HorizontalConstraint(entity=g[3], addUndoState=False)
    p = mdb.models[modelName].Part(name='platen',
    dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
    p = mdb.models[modelName].parts['platen']
    p.AnalyticRigidSurfRevolve(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models[modelName].parts['platen']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models[modelName].sketches['__profile__']
    p = mdb.models[modelName].parts['platen']
    v1, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
    p.ReferencePoint(point=v1[1])

def applybcs(modelname, setName, disp):
    print >> sys.__stdout__, 'Applying boundary conditions'
    region = mdb.models[modelname].rootAssembly.sets[setName]
    mdb.models[modelname].EncastreBC(name='ENCASTRE', createStepName='Initial', region=region)

    a = mdb.models[modelname].rootAssembly
    r1 = a.instances['platen-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models[modelname].DisplacementBC(name='displacement', createStepName='loading_step', region=region, u1=0.0, u2=0.0, u3=disp, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

def meshTies(modelName):
    print >> sys.__stdout__, 'Applying internal constraints'
    surfaces = mdb.models[modelName].rootAssembly.surfaces.keys()
    superiorslave_entry = []
    superiormaster_entry = []
    inferiorslave_entry = []
    inferiormaster_entry = []
    interfaceInnerSlave = []
    interfaceInnerMaster = []
    interfaceOuterSlave = []
    interfaceOuterMaster = []


    for current_entry in surfaces:
        if current_entry.startswith("SF_INFERIOR_ENDCAP_WITH_VERTEBRAE"):
           inferiormaster_entry = current_entry
        if current_entry.startswith("SF_SUPERIOR_ENDCAP_WITH_VERTEBRAE"):
           superiormaster_entry = current_entry
        if current_entry.endswith("INFERIOR_ENDCAP"):
           inferiorslave_entry = current_entry
        if current_entry.endswith("SUPERIOR_ENDCAP"):
           superiorslave_entry = current_entry
        if current_entry.endswith("SF_VERTEBRAE_WITH_INTERFACE"):
           interfaceOuterSlave_entry = current_entry
        if current_entry.endswith("SF_INTERFACE_WITH_VERTEBRAE"):
           interfaceOuterMaster_entry = current_entry
        if current_entry.endswith("SF_CEMENT_WITH_INTERFACE"):
           interfaceInnerMaster_entry = current_entry
        if current_entry.endswith("SF_INTERFACE_WITH_CEMENT"):
           interfaceInnerSlave_entry = current_entry


    superiormaster = mdb.models[modelName].rootAssembly.surfaces[superiormaster_entry]
    superiorslave = mdb.models[modelName].rootAssembly.surfaces[superiorslave_entry]
    inferiormaster = mdb.models[modelName].rootAssembly.surfaces[inferiormaster_entry]
    inferiorslave = mdb.models[modelName].rootAssembly.surfaces[inferiorslave_entry]
    interfaceInnerMaster = mdb.models[modelName].rootAssembly.surfaces[interfaceInnerMaster_entry]
    interfaceInnerSlave = mdb.models[modelName].rootAssembly.surfaces[interfaceInnerSlave_entry]
    interfaceOuterMaster = mdb.models[modelName].rootAssembly.surfaces[interfaceOuterMaster_entry]
    interfaceOuterSlave = mdb.models[modelName].rootAssembly.surfaces[interfaceOuterSlave_entry]

    mdb.models[modelName].Tie(name='Superior_endcap_tie', master=superiormaster, slave=superiorslave, positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
    mdb.models[modelName].Tie(name='Inferior_endcap_tie', master=inferiormaster, slave=inferiorslave, positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
    mdb.models[modelName].Tie(name='cement_interface_tie', master=interfaceInnerMaster, slave=interfaceInnerSlave, positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
    mdb.models[modelName].Tie(name='interface_vert_tie', master=interfaceOuterMaster, slave=interfaceOuterSlave, positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)




    a = mdb.models[modelName].rootAssembly
    s1 = a.instances['platen-1'].faces
    side1Faces1 = s1.getSequenceFromMask(mask=('[#1 ]', ), )
    region1=regionToolset.Region(side1Faces=side1Faces1)
    region2=a.surfaces['SF_SUPERIOR_ENDCAP_WITH_ZMAX']
    mdb.models[modelName].Tie(name='platen_constraint', master=region1,
        slave=region2, positionToleranceMethod=COMPUTED, adjust=ON,
        tieRotations=ON, thickness=ON)


def saveinpcae(modelname, outputpath):
    print >> sys.__stdout__, 'Creating job'
    jobname = modelname+ 'setup'
    print jobname
    mdb.Job(name=jobname, model=modelname, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=50, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT, numDomains=1, numCpus=1)
    os.chdir(outputpath)
    print >> sys.__stdout__, 'Saving .cae file'
    mdb.saveAs(pathName=os.path.join(outputpath, modelname))
    print >> sys.__stdout__, 'Writing .inp file'
    mdb.jobs[jobname].writeInput(consistencyChecking=OFF)

def loadLoadPointCsv(csvFilePath, modelName):
    loadData = []

    with open(csvFilePath, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            loadData.append(row)

    loadPoints = [0.0, 0.0, 0.0]
    for searchModel in loadData:
        if modelName.startswith(searchModel[0]):
            loadPoints[0] = float(searchModel[1])
            loadPoints[1] = float(searchModel[2])
            loadPoints[2] = float(searchModel[3])
    return loadPoints

def main():

    inp_list = []
    inp_list = getfiles(input_directory, ".inp")

    if inp_list:
        for i, current_file in enumerate(inp_list):
            current_model = current_file[:-4]
            # Import the next model in the folder
            mdb.ModelFromInputFile(name = current_model, inputFileName = os.path.join(input_directory, current_file))
            # Delete all models except the one just imported, and delete all present jobs
            cleanup(current_model)
            # Get the part and instance names from the imported model
            current_part, current_instance = getpart(current_model)
            # Delete all interactions present in the imported model
            deleteinteractions(current_model)
            # Create a new loading step
            #mdb.models[current_model].StaticStep(name=stepName, previous='Initial', nlgeom=OFF)
            mdb.models[current_model].StaticStep(name=stepName, previous='Initial', maxNumInc=100, initialInc=0.025, minInc=0.025, maxInc=0.025, nlgeom=ON)
            # Create an analytical rigid plate
            createAnalyticalPlate(current_model, analytical_plate_radius)
            # Instance the analytical rigid plate
            instancePart(current_model, 'platen')
            # Create the tie constraints within the model
            meshTies(current_model)
            # Create the datum surface along which the platen will be aligned and align it
            # Load the load position data from the csv file and translate the platen centre to this position
            loadPoints = loadLoadPointCsv(load_point_csv_path, current_model)
            alignPlaten(current_model, loadPoints)
            translatePlaten(current_model, loadPoints)
            # Create the encastre and platen displacement BCs
            applybcs(current_model, encastre_set, displacement)
            # Check for any materials with zero density, if found replace with 1 density
            adjust_matprops(current_model, yield_strain)
            # Create a job and save the reconfigured model as a .cae file
            saveinpcae(current_model, output_directory)

    else:
        print >> sys.__stdout__, 'There are no .inp files in the chosen directory.'

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
            # Delete all models except the one just imported, and delete all present jobs
            cleanup(current_model)
            changeMatProp(current_model)
        else:
            print >> sys.__stdout__, 'No Files in Dir'

main()

# Example script: sample_script.sh
#!/bin/bash
# Set current working directory
#$ -cwd -V
#Use current environment variables/ modules
#$ -V
#Request 4 hours of runtime
#$ -l h_rt=4:00:00
#use 6GB of memory
#$ -l h_vmem=2000M
#use 8 cores
#$ -pe smp 8
#Email at the beginning and end of the job
#$ -m be
#add module
module add abaqus/6.14
export LM_LICENSE_FILE=27004@abaqus-server1.LEEDS.AC.UK
#Run the executable 'myprogram' from the current working directory
abaqus cae nogui=setup_models_Yield.py && abaqus cae nogui=runAllModels.py && abaqus cae nogui=postProcess.py

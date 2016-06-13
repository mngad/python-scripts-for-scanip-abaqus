# Example script: sample_script.sh
#!/bin/bash
# Set current working directory
cd /nobackup/mngad/abaqusTest/
#Use current environment variables/ modules
#$ -V
#Request 4 hours of runtime
#$ -l h_rt=1:00:00
#use 6GB of memory
#$ -l h_vmem=6000M
#use 8 cores
#$ -pe smp 4
#Email at the beginning and end of the job
#$ -m be
#add module
module add abaqus/6.13
export LM_LICENSE_FILE=27004@abaqus-server1.LEEDS.AC.UK
#Run the executable 'myprogram' from the current working directory
abaqus cae nogui=setup_models_FOR_CEMENT.py && abaqus cae nogui=caeToStiffnessOutput_FOR_CEMENT_DENSITY_CHANGE.py

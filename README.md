# Python Files for model generation in ScanIP and ABAQUS

## caeToStiffnessOutput_FOR_CEMENT.py

Runs all previously set up cae files and returns txt files with the stiffness

## segment_FOR_CEMENT.py

ScanIP python script to segment CT scan into model - for use with augmented vertebrae

## segment_WITHOUT_CEMENT.py

ScanIP python script to segment CT scan into model - for use without augmented vertebrae

## setup_models_WITHOUT_CEMENT.py

Takes all .inp files along with positions in a .csv and sets up all boundary conditions and interactions for a 1 mm compression.

## setup_models_FOR_CEMENT.py

Takes all .inp files along with positions in a .csv and sets up all boundary conditions and interactions for a 1 mm compression. For augmented models.

## setup_models_FOR_CEMENT_WITH_INTERFACE.py

Takes all .inp files along with positions in a .csv and sets up all boundary conditions and interactions for a 1 mm compression. For augmented models with an interface layer.

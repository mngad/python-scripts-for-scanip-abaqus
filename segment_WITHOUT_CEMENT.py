from scanip_api import *
if InputDialog.AskYesNoQuestion('Align', 'Have you aligned the model?') == True:
    
    App.GetDocument().ResampleDataByPixelSpacing(1, 1, 1, Doc.PartialVolumeEffectInterpolation, Doc.PartialVolumeEffectInterpolation)
    
    # Select vertebrae mask & open and close it
    App.GetDocument().Threshold(20, 255, Doc.CreateNewMask, App.GetDocument().GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
    App.GetDocument().ApplyCloseFilter(Doc.TargetMask, 1, 1, 1, 0)
    App.GetDocument().ApplyOpenFilter(Doc.TargetMask, 1, 1, 1, 0)
    
    # Select both endcaps, open and close
    App.GetDocument().Threshold(10, 20, Doc.CreateNewMask, App.GetDocument().GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
    App.GetDocument().ApplyCloseFilter(Doc.TargetMask, 1, 1, 1, 0)
    App.GetDocument().ApplyOpenFilter(Doc.TargetMask, 1, 1, 1, 0)
    
    # duplicate endcaps to allow manual flood fill to separate the two
    App.GetDocument().GetActiveMask().Duplicate()
    
    # Rename all masks
   
    App.GetDocument().GetMaskByName("Mask 1").Activate()
    App.GetDocument().GetMaskByName("Mask 1").SetName("Vertebrae")
    App.GetDocument().GetMaskByName("Mask 2").Activate()
    App.GetDocument().GetMaskByName("Mask 2").SetName("Inferior_endcap")
    App.GetDocument().GetMaskByName("Copy of Mask 2").Activate()
    App.GetDocument().GetMaskByName("Copy of Mask 2").SetName("Superior_endcap")
  
    
    # Subtract masks from each other
   
    App.GetDocument().GetMaskByName("Inferior_endcap").Activate()
    App.GetDocument().GetActiveMask().SubtractWith(App.GetDocument().GetMaskByName("Vertebrae"), App.GetDocument().GetSliceIndices (Doc.OrientationYZ), Doc.OrientationYZ)
    App.GetDocument().GetMaskByName("Superior_endcap").Activate()
    App.GetDocument().GetActiveMask().SubtractWith(App.GetDocument().GetMaskByName("Vertebrae"), App.GetDocument().GetSliceIndices (Doc.OrientationYZ), Doc.OrientationYZ)
    App.GetDocument().GenerateFastPreview()

    # Messages to remind manual parts
    App.GetInstance().ShowMessage('Separate endcaps, crop and remove spinal canal cement')
else:
    App.GetInstance().ShowMessage('Align first')

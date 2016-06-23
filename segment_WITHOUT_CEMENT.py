from scanip_api import *
if InputDialog.AskYesNoQuestion('Align', 'Have you aligned the model?') == True:
    
    doc=App.GetDocument()
    
    #doc.ResampleDataByPixelSpacing(1, 1, 1, doc.PartialVolumeEffectInterpolation, doc.PartialVolumeEffectInterpolation)
    
    # Select vertebrae mask & open and close it
    doc.Threshold(20, 255, Doc.CreateNewMask, doc.GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
    doc.ApplyCloseFilter(Doc.TargetMask, 1, 1, 1, 0)
    doc.ApplyOpenFilter(Doc.TargetMask, 1, 1, 1, 0)
    
    # Select both endcaps, open and close
    doc.Threshold(10, 20, Doc.CreateNewMask, doc.GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
    doc.ApplyCloseFilter(Doc.TargetMask, 1, 1, 1, 0)
    doc.ApplyOpenFilter(Doc.TargetMask, 1, 1, 1, 0)
    
    # duplicate endcaps to allow manual flood fill to separate the two
    doc.GetActiveMask().Duplicate()
    
    # Rename all masks
   
    doc.GetMaskByName("Mask 1").Activate()
    doc.GetMaskByName("Mask 1").SetName("Vertebrae")
    doc.GetMaskByName("Mask 2").Activate()
    doc.GetMaskByName("Mask 2").SetName("Inferior_endcap")
    doc.GetMaskByName("Copy of Mask 2").Activate()
    doc.GetMaskByName("Copy of Mask 2").SetName("Superior_endcap")
  
    
    # Subtract masks from each other
   
    doc.GetMaskByName("Inferior_endcap").Activate()
    doc.GetActiveMask().SubtractWith(doc.GetMaskByName("Vertebrae"), doc.GetSliceIndices (Doc.OrientationYZ), Doc.OrientationYZ)
    doc.GetMaskByName("Superior_endcap").Activate()
    doc.GetActiveMask().SubtractWith(doc.GetMaskByName("Vertebrae"), doc.GetSliceIndices (Doc.OrientationYZ), Doc.OrientationYZ)
    doc.GenerateFastPreview()
    
    
    
    mask_vert = doc.GetMaskByName("Vertebrae")
    mask_inf = doc.GetMaskByName("Inferior_endcap")
    mask_sup = doc.GetMaskByName("Superior_endcap")
   
    feModel = doc.CreateFeModel()
    feModel.AddMask(mask_vert)
    feModel.AddMask(mask_inf)
    feModel.AddMask(mask_sup)

    feModel.SetExportType(Model.AbaqusVolume)
    feModel.SetUseGreyscaleValues(True)
    feModel.SetUseSmartMaskSmoothing(True)
    feModel.SetNumSmartMaskSmoothingIterations(20)
    App.GetDocument().SetActiveModel(App.GetDocument().GetModelByName("Model 1"))
    App.GetDocument().GetActiveModel().SetExportUsingAbsoluteCoordinates(False)
    App.GetDocument().GetActiveModel().SetMeshingAlgorithmType(Model.Grid)
    App.GetDocument().GetActiveModel().SetTargetMaxGridSize(Model.GridSize1x1)
	
	
    feModel.GetMaskPart(mask_inf).SetMaterial(HomogeneousMaterial(1, 2.45, 0.3, "INFERIOR_CAP_HMG"))
    feModel.GetMaskPart(mask_sup).SetMaterial(HomogeneousMaterial(1, 2.45, 0.3, "SUPERIOR_CAP_HMG"))
    #feModel.GetMaskPart(mask_vert).SetMaterial() # Set GS material?
    feModel.AddContactPair(feModel.GetMaskPart(mask_vert), feModel.GetMaskPart(mask_inf))
    feModel.AddContactPair(feModel.GetMaskPart(mask_vert), feModel.GetMaskPart(mask_sup))
    doc.ShrinkWrapData(Doc.TargetAllMasks, 5, 5, 5, 5, 0, 0)
    doc.CropData(0,doc.GetSliceCount(Doc.OrientationYZ),0,doc.GetSliceCount(Doc.OrientationZX),2,(doc.GetSliceCount(Doc.OrientationXY)-4))
    App.GetDocument().GetActiveModel().AddNodeSet(App.GetDocument().GetActiveModel().GetPartByName("Inferior_endcap"), Model.Zmin)
    App.GetDocument().GetActiveModel().AddSurfaceContact(App.GetDocument().GetActiveModel().GetPartByName("Superior_endcap"), Model.Zmax)

	
	
    
	#doc.CropData(0, 75, 0, 77, 1, 60)
    
    #feModel.AddContactPair(feModel.GetMaskPart(mask_sup), feModel.Zmax)
    #feModel.AddNodeSet(feModel.GetMaskPart(mask_inf), feModel.Zmin)

    App.GetDocument().GetMaskByName("Vertebrae").Activate()
    App.GetDocument().ApplyCavityFillFilter()
    App.GetDocument().GetActiveModel().SetExportUsingAbsoluteCoordinates(False)
    App.GetDocument().GetActiveModel().SetMeshingAlgorithmType(Model.Grid)
    App.GetDocument().GetActiveModel().SetEditAdvancedParametersManually(True)
    App.GetDocument().GetActiveModel().SetTargetMaxGridSize(Model.GridSize1x1)
    App.GetDocument().GetActiveModel().SetAdditionalMeshQualityImprovementQualityMetric(Model.InOutRatio)
    
	#remove gaps between end-caps and the vertebrae
    App.GetDocument().GetMaskByName("Vertebrae").Activate()
    App.GetDocument().GetActiveMask().UnionWith(App.GetDocument().GetMaskByName("Superior_endcap"), App.GetDocument().GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)
    App.GetDocument().ApplyCavityFillFilter()
    App.GetDocument().GetActiveMask().SubtractWith(App.GetDocument().GetMaskByName("Superior_endcap"), App.GetDocument().GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)
    App.GetDocument().GetMaskByName("Vertebrae").Activate()
    App.GetDocument().GetActiveMask().UnionWith(App.GetDocument().GetMaskByName("Inferior_endcap"), App.GetDocument().GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)
    App.GetDocument().ApplyCavityFillFilter()
    App.GetDocument().GetActiveMask().SubtractWith(App.GetDocument().GetMaskByName("Inferior_endcap"), App.GetDocument().GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)

    App.GetDocument().GetMaskByName("Superior_endcap").Activate()
    App.GetDocument().FloodFillFromActiveMask(35, 8, 54, False, Doc.Mode3D, Doc.ReplaceWithMask, App.GetDocument().GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
    App.GetDocument().GetMaskByName("Inferior_endcap").Activate()
    App.GetDocument().FloodFillFromActiveMask(35, 8, 1, False, Doc.Mode3D, Doc.ReplaceWithMask, App.GetDocument().GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)

    App.GetDocument().GetMaskByName("Vertebrae").Activate()
    App.GetDocument().ApplyCavityFillFilter()
	
	
    # Messages to remind manual parts
    App.GetInstance().ShowMessage('Separate endcaps, crop and remove spinal canal cement')
else:
    App.GetInstance().ShowMessage('Align first')
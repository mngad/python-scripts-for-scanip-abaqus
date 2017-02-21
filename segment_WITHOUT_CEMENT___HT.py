from scanip_api import *

if InputDialog.AskYesNoQuestion('Align', 'Have you aligned the model?') == True:

	doc=App.GetDocument()

	#downsample to 1x1x1
	#doc.ResampleDataByPixelSpacing(1, 1, 1, doc.PartialVolumeEffectInterpolation, doc.PartialVolumeEffectInterpolation)

	# Select vertebrae mask & open and close it
	doc.Threshold(17, 255, Doc.CreateNewMask, doc.GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
	doc.ApplyCloseFilter(Doc.TargetMask, 1, 1, 1, 0)
	#doc.ApplyOpenFilter(Doc.TargetMask, 1, 1, 1, 0) #no need for this

	# Select both endcaps, open and close
	doc.Threshold(10, 20, Doc.CreateNewMask, doc.GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
	doc.ApplyCloseFilter(Doc.TargetMask, 1, 1, 1, 0)
	doc.ApplyOpenFilter(Doc.TargetMask, 1, 1, 1, 0) #still need it here to remove extra "cement" around the top and bottom of the vertebra

	# duplicate endcaps to allow manual flood fill to separate the two
	doc.GetActiveMask().Duplicate()

	# Rename all masks
	doc.GetMaskByName("Mask 1").Activate()
	doc.GetMaskByName("Mask 1").SetName("Vertebra")
	doc.GetMaskByName("Mask 2").Activate()
	doc.GetMaskByName("Mask 2").SetName("Inferior_endcap")
	doc.GetMaskByName("Copy of Mask 2").Activate()
	doc.GetMaskByName("Copy of Mask 2").SetName("Superior_endcap")

	# Subtract masks from each other
	doc.GetMaskByName("Inferior_endcap").Activate()
	doc.GetActiveMask().SubtractWith(doc.GetMaskByName("Vertebra"), doc.GetSliceIndices (Doc.OrientationYZ), Doc.OrientationYZ)
	doc.GetMaskByName("Superior_endcap").Activate()
	doc.GetActiveMask().SubtractWith(doc.GetMaskByName("Vertebra"), doc.GetSliceIndices (Doc.OrientationYZ), Doc.OrientationYZ)
	doc.GenerateFastPreview()

	#define masks
	mask_vert = doc.GetMaskByName("Vertebra")
	mask_inf = doc.GetMaskByName("Inferior_endcap")
	mask_sup = doc.GetMaskByName("Superior_endcap")

	#create FE model and add masks
	feModel = doc.CreateFeModel()
	feModel.AddMask(mask_vert)
	feModel.AddMask(mask_inf)
	feModel.AddMask(mask_sup)

	#model properties
	feModel.SetExportType(Model.AbaqusVolume)
	feModel.SetUseGreyscaleValues(True)
	feModel.SetUseSmartMaskSmoothing(True)
	feModel.SetNumSmartMaskSmoothingIterations(20)
	doc.SetActiveModel(doc.GetModelByName("Model 1"))
	doc.GetActiveModel().SetExportUsingAbsoluteCoordinates(False)#sets local coordinate system
	doc.GetActiveModel().SetMeshingAlgorithmType(Model.Grid)
	doc.GetActiveModel().SetTargetMaxGridSize(Model.GridSize1x1)
	doc.GetActiveModel().SetExportUsingAbsoluteCoordinates(False)
	doc.GetActiveModel().SetEditAdvancedParametersManually(True)
	doc.GetActiveModel().SetAdditionalMeshQualityImprovementQualityMetric(Model.InOutRatio)

	#Set Material Properties
	feModel.GetMaskPart(mask_inf).SetMaterial(HomogeneousMaterial(1, 2.45, 0.3, "INFERIOR_CAP_HMG"))
	feModel.GetMaskPart(mask_sup).SetMaterial(HomogeneousMaterial(1, 2.45, 0.3, "SUPERIOR_CAP_HMG"))
	#feModel.GetMaskPart(mask_vert).SetMaterial() # Set GS material?

	#Add contacts between vertebra and end-caps
	feModel.AddContactPair(feModel.GetMaskPart(mask_vert), feModel.GetMaskPart(mask_inf))
	feModel.AddContactPair(feModel.GetMaskPart(mask_vert), feModel.GetMaskPart(mask_sup))

	#shrink wrap and crop to achieve parrallel surfaces
	#doc.ShrinkWrapData(Doc.TargetAllMasks, 5, 5, 5, 5, 0, 0)




	# add node sets and surface contacts for top and bottom layer
	doc.CropData(0,doc.GetSliceCount(Doc.OrientationYZ),0,doc.GetSliceCount(Doc.OrientationZX),2,(doc.GetSliceCount(Doc.OrientationXY)-4))
	doc.GetActiveModel().AddNodeSet(doc.GetActiveModel().GetPartByName("Inferior_endcap"), Model.Zmin)
	doc.GetActiveModel().AddSurfaceContact(doc.GetActiveModel().GetPartByName("Superior_endcap"), Model.Zmax)

	# remove gaps between end-caps and the vertebrae
	doc.GetMaskByName("Vertebra").Activate()
	doc.GetActiveMask().UnionWith(doc.GetMaskByName("Superior_endcap"), doc.GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)
	doc.ApplyCavityFillFilter()
	doc.GetActiveMask().SubtractWith(doc.GetMaskByName("Superior_endcap"), doc.GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)
	doc.GetMaskByName("Vertebra").Activate()
	doc.GetActiveMask().UnionWith(doc.GetMaskByName("Inferior_endcap"), doc.GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)
	doc.ApplyCavityFillFilter()
	doc.GetActiveMask().SubtractWith(doc.GetMaskByName("Inferior_endcap"), doc.GetSliceIndices (Doc.OrientationXY), Doc.OrientationXY)

	# Flood fill the two end-caps to separate them
	doc.GetMaskByName("Superior_endcap").Activate()
	doc.FloodFillFromActiveMask(57, 19, 32, False, Doc.Mode3D, Doc.ReplaceWithMask, doc.GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)
	doc.GetMaskByName("Inferior_endcap").Activate()
	doc.FloodFillFromActiveMask(57, 17, 5, False, Doc.Mode3D, Doc.ReplaceWithMask, doc.GetSliceIndices(Doc.OrientationYZ), Doc.OrientationYZ)

	# remove void from centre of vertebra
	doc.GetMaskByName("Vertebra").Activate()
	doc.ApplyCavityFillFilter()




	doc.GenerateFastPreview()
	# Messages to remind manual parts
	App.GetInstance().ShowMessage('Separate endcaps, crop and remove spinal canal cement')
else:
	App.GetInstance().ShowMessage('Align first')

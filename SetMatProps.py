from scanip_api import *
doc=App.GetDocument()



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
doc.SetActiveModel(doc.GetModelByName("Model 1"))
feModel = doc.GetModelByName("Model 1")
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
feModel.AddNodeSet(doc.GetActiveModel().GetPartByName("Inferior_endcap"), Model.Zmin)
feModel.AddSurfaceContact(doc.GetActiveModel().GetPartByName("Superior_endcap"), Model.Zmax)


import FWCore.ParameterSet.Config as cms
from DQMOffline.RecoB.bTagCombinedSVVariables_cff import *


# combinedSecondaryVertex jet tag computer configuration
bTagCombinedSVAnalysisBlock = cms.PSet(
    parameters = cms.PSet(
        categoryVariable = cms.string('vertexCategory'),
        categories = cms.VPSet(
            cms.PSet(                # all vertices
                combinedSVNoVertexVariables,
                combinedSVPseudoVertexVariables,
                combinedSVRecoVertexVariables
            ), 
            cms.PSet(                # reco vertex
                combinedSVNoVertexVariables,
                combinedSVPseudoVertexVariables,
                combinedSVRecoVertexVariables
            ), 
            cms.PSet(                # psuedo vertex
                combinedSVNoVertexVariables,
                combinedSVPseudoVertexVariables
            ), 
            cms.PSet(                # no vertex
                combinedSVNoVertexVariables
            )
        )
    )
)



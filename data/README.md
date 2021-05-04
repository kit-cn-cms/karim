# Scale factors and weights for CMS ttX analyses

The different scale factors and weights collected in this directory are summarized below. 
Some are official POG weights and scale factors which have been collected here for convenience. 
Some are privately produced weights and scale factors for MC-to-data corrections in specific analyses.


## b-tagging scale factors

Currently included are b-tagging scale factors for the deepJet tagger and its corresponding uncertainties.
The files contain fixed working point scale factors as well as iterative fit scale factors for the correction of the b-tagging shape (only use them if you are actually using the shape of the b-tagging distribution anywhere in your analysis).
The files are copied without changes from the [official POG TWiki pages](https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation).

|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | |
| legacy 2017 | [DeepFlavour_94XSF_V4_B_F.csv](https://twiki.cern.ch/twiki/pub/CMS/BtagRecommendation94X/DeepFlavour_94XSF_V4_B_F.csv) | `iterativefit`  |
| legacy 2018 | [DeepJet_102XSF_V2_JESreduced.csv](https://twiki.cern.ch/twiki/pub/CMS/BtagRecommendation102X/DeepJet_102XSF_V2_JESreduced.csv) | `iterativefit` |
|  |  |  |
| UL 2017 | | |
| | | |


These b-tagging SFs can be read with a dedicated class in `configs/weightModules.py`
```python
btaggingSFs = weightModules.BTaggingScaleFactors(FILE)

for jet in jets:
    sfs = btaggingSFs.getSFs(jetFlavor, abs(jetEta), jetPt, deepJetValue, jec)
    nominalSF = sfs.loc["central"] # nominal scale factor
    variedSF  = sfs.loc["hf_up"]   # example for varied SF value
```

The b-tagging scale factors are multiplicative, i.e. multiply each SF per jet to get the total SF for the event.
For the iterative fit scale factor it is important to note, that `cferr` variations are only applied to c-jets and all other uncertainties only to non-c-jets.
Apply the nominal scale factor for jets that do not match the criteria, i.e.
```python
for u in btagSF_uncs:
    # cferr only exists for c-jets
    if flav == 1:
        if "cferr" in u:
            uncs[u] *= sfs.loc[u]
        else:
            uncs[u] *= sfs.loc["central"]
    # for the others cferr does not exist
    else:
        if "cferr" in u:
            uncs[u] *= sfs.loc["central"]
        else:
            uncs[u] *= sfs.loc[u]

```
The b-tagging SF uncertainties should be normalized with `1./nominalSF` for easier application.

WIP: currently the fixed WP scale factors are not implemented properly - use with care

### b-tagging scale factor patches

As the application of the POG b-tagging scale factors has shown to change kinematic distributions like jet multiplicity, jet pT or HT private patches for these scale factors have been derived.
These patches are binned in nJets and HT of jets, separately for ttlf, ttcc, ttbb(5FS), ttbb(4FS), ttH and ttZ processes and are to be applied in addition to the b-tagging scale factors (and scale factor variations).
For events not matching any of the processes currently the ttlf patch values are used for simplicity.

The b-tagging SF patches can be read with a dedicated class in `configs/weightModules.py`
```python
sfPatch = weightModules.SFPatches(FILE)

patchValue = sfPatch.getPatchValue(sampleName, ttbarID, nJets, HTjets)
```

## Rate factors

Some uncertainty sources have separate nuisance parameters covering the rate change associated with the variation of the uncertainty source and the thereby associated shape changing effects.
To ensure that there is no double counting of these uncertainties, rate factors are applied to these uncertainty sources to normalize the rate contribution out of the varied distributions.
For this purpose privately produced rate factors are derived for 
- muR and muF matrix element scales
- ISR and FSR parton shower scales
- ME+PS matching scale (i.e. hdamp)
- pdf variations
- underlying event variations

Custom csv files are provided where rate factors for ttbar, ttbb(5FS), ttbb(4FS) and ttH samples are provided
These rate factors can be read with a dedicated class in `configs/weightModules.py`
```python
rateFactors = weightModules.RateFactors(FILE)
rf = rateFactors.getRF(sampleName, VARIATIONNAME)
```
These rate factors are to be applied on top of the variations.

WIP: hdamp, pdf and UE variations not yet validated

## Lepton Trigger scale factors

For electons and muons separate trigger scale factors are used. 
The muon trigger scale factors are provided by the POG as root files on the [official Muon POG TWiki pages](https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOG).
The electron trigger scale factors are derived as a part of the ttHbb analysis and are provided in [this gitlab repository](https://gitlab.cern.ch/ttH/reference/-/tree/master/scale_factors/triggers).
These root files has been converted to csv files with the scripts in `data/util` without changing the content.
The trigger scale factors can be read with a dedicated class in `configs/weightModules.py`

#### Electron Trigger SFs
|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | [SingleEG_JetHT_Trigger_Scale_Factors_ttHbb2017_v3.root](https://gitlab.cern.ch/ttH/reference/-/blob/master/scale_factors/triggers/SingleEG_JetHT_Trigger_Scale_Factors_ttHbb2017_v3.root) | `ele28_ht150_OR_ele32_ele_pt_ele_sceta` |
| legacy 2018 | [SingleEG_JetHT_Trigger_Scale_Factors_ttHbb2018_v3.root](https://gitlab.cern.ch/ttH/reference/-/blob/master/scale_factors/triggers/SingleEG_JetHT_Trigger_Scale_Factors_ttHbb2018_v3.root) | `ele28_ht150_OR_ele32_ele_pt_ele_sceta` |
|  |  |  |
| UL 2017 | | |
|  | |  |

```python
elTrigSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for el in electrons:
    trigSF = elTrigSFs.getSFs(elPt, elEtaSuperCluster)
    nominalSF = trigSF.loc["central"] # nominal scale factor
    variedSF  = trigSF.loc["up"] # example of varied scale factor
```

#### Muon Trigger SFs
|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | [EfficienciesAndSF_RunBtoF_Nov17Nov2017.root](http://kplee.web.cern.ch/kplee/TagProbe/94X/v20180202_MergingHighPtBins/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root) | `IsoMu27_PtEtaBins` |
| legacy 2018 | [EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root](https://gitlab.cern.ch/cms-muonPOG/MuonReferenceEfficiencies/blob/master/EfficienciesStudies/2018_trigger/EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root) (8950.82/pb)   [EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root](https://gitlab.cern.ch/cms-muonPOG/MuonReferenceEfficiencies/blob/master/EfficienciesStudies/2018_trigger/EfficienciesAndSF_2018Data_BeforeMuonHLTUpdate.root) (50789.75/pb)  | `IsoMu24_PtEtaBins` |
|  |  |  |
| UL 2017 | | |
|  | | |

```python
muTrigSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for mu in muons:
    trigSF = muTrigSFs.getSFs(muPt, abs(muEta))
    nominalSF = trigSF.loc["central"] # nominal scale factor
    variedSF  = trigSF.loc["up"] # example of varied scale factor
```


## Lepton ID/RECO/ISO scale factors

For electrons and muons separate official POG identification and reconstruction scale factors are used.
The POGs provide these scale factors as ROOT histograms on the [official EGamma POG TWiki pages](https://twiki.cern.ch/twiki/bin/view/CMS/EgammaRunIIRecommendations) and [official Muon POG TWiki pages](https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOG).
These root files has been converted to csv files with the scripts in `data/util` without changing the content.
The lepton scale factors can be read with a dedicated class in `configs/weightModules.py`

#### Electron ID SFs
|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | [2017_ElectronTight.root](https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/2017_ElectronTight.root) | `tightElectronID` |
| legacy 2018 | [2018_ElectronTight.root](https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/2018_ElectronTight.root) | `tightElectronID` |
|  |  |  |
| UL 2017 | | |
|  |  |  |

```python
elIDSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for el in electrons:
    idSF = elIDSFs.getSFs(elPt, elEtaSuperCluster)
    nominalSF = idSF.loc["central"] # nominal scale factor
    variedSF  = idSF.loc["up"] # example of varied scale factor
```

#### Muon ID SFs
|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | [RunBCDEF_SF_ID.root](https://twiki.cern.ch/twiki/pub/CMS/MuonReferenceEffs2017/RunBCDEF_SF_ID.root) | `NUM_TightID_DEN_genTracks_pt_abseta` |
| legacy 2018 | [RunABCD_SF_ID.root](https://gitlab.cern.ch/cms-muonPOG/muonefficiencies/-/blob/master/Run2/preUL/2018/2018_Jpsi/RunABCD_SF_ID.root) | `NUM_TightID_DEN_genTracks_pt_abseta` |
|  |  |  |
| UL 2017 | | |
|  |  |  |

```python
muIDSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for mu in muons:
    idSF = muIDSFs.getSFs(muPt, abs(muEta))
    nominalSF = idSF.loc["central"] # nominal scale factor
    variedSF  = idSF.loc["up"] # example of varied scale factor
```

#### Electron RECO SFs
|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | [egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root](https://twiki.cern.ch/twiki/pub/CMS/Egamma2017DataRecommendations/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root) | `electronReco` |
| legacy 2018 | [egammaEffi.txt_EGM2D_updatedAll.root](https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/egammaEffi.txt_EGM2D_updatedAll.root) | `electronReco` |
|  |  |  |
| UL 2017 | | |
|  |  |  |

```python
elRecoSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)
for el in electrons:
    recoSF = elRecoSFs.getSFs(elPt, elEtaSuperCluster)
    nominalSF = recoSF.loc["central"] # nominal scale factor
    variedSF  = recoSF.loc["up"] # example of varied scale factor
```

#### Muon ISO SFs
|data period | official SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | [RunBCDEF_SF_ISO.root](https://twiki.cern.ch/twiki/pub/CMS/MuonReferenceEffs2017/RunBCDEF_SF_ISO.root) | `NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta` |
| legacy 2018 | [RunABCD_SF_ISO.root](https://gitlab.cern.ch/cms-muonPOG/MuonReferenceEfficiencies/blob/master/EfficienciesStudies/2018/rootfiles/RunABCD_SF_ISO.root)| `NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta` |
|  |  |  |
| UL 2017 | | |
|  |  |  |

```python
muISOSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for mu in muons:
    isoSF = muISOSFs.getSFs(muPt, abs(muEta))
    nominalSF = isoSF.loc["central"] # nominal scale factor
    variedSF  = isoSF.loc["up"] # example of varied scale factor
```


## Pileup reweighting

Pileup weights are calculated as fractions between the pileup distribution measured in data and the number of true interaction distribution with which the MC samples are generated.
For this purpose the number of true interaction distribution can be taken from [this](https://github.com/cms-sw/cmssw/blob/CMSSW_12_0_X/SimGeneral/MixingModule/python/mix_2017_25ns_WinterMC_PUScenarioV1_PoissonOOTPU_cfi.py) CMSSW config or from the [miniAODHelper](https://github.com/cms-ttH/MiniAOD/tree/Legacy_2016_2017_2018_Devel/MiniAODHelper/data/puweights/MC).

To collect the PU density histograms for data you need the correct lumi JSON file which can be found via the [PdmV TWiki page](https://twiki.cern.ch/twiki/bin/view/CMS/PdmV) and also the central pileup json file which can be found on the [pileup TWiki page](https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData#Pileup_JSON_Files_For_Run_II).

The PU density histogram can then be created by executing
```
pileupCalc.py -i LUMIJSON --inputLumiJSON PUFILE --calcMode true --minBiasXsec 69200 --maxPileupBin 100 --numPileupBins 100 OUTFILE.root

```

This needs to be executed once with the nominal minimum bias cross section (69.2 mb) and one per 4.6% variation of this cross section (i.e. 66.017 mb for down and 72.383 mb for up).

The resulting four files can be combined into one pandas dataframe with the scripts in `data/util`.

| data period | pileup json | lumi json |
| -- | -- | -- |
| legacy 2016 | | | 
| legacy 2017 | | | 
| legacy 2018 | `/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt` | `/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt` | 
| | | |
| UL 2017 | | |


These pileup reweighting SFs can be read with a dedicated class in `configs/weightModules.py`
```python
pileupSFs = weightModules.PileupSFs(FILE)

nomSF  = pileupSFs.getSF(nTruePUInteractions, "central")
upSF   = pileupSFs.getSF(nTruePUInteractions, "up")
downSF = pileupSFs.getSF(nTruePUInteractions, "down")
```

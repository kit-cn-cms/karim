## Scalefactors and weights for CMS analyses

The different scale factors and weights collected in this directory are summarized below. 
Some are official POG weights and scale factors which have been collected here for convenience. 
Some are privately produced weights and scale factors for MC-to-data corrections in specific analyses.

### b-tagging scale factors

Currently included are b-tagging scale factors for the deepJet tagger and its corresponding uncertainties.
The files contain fixed working point scale factors as well as iterative fit scale factors for the correction of the b-tagging shape (only use them if you are actually using the shape of the b-tagging distribution anywhere in your analysis).
The files are copied without changes from the !(https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation)[official POG TWiki pages].

|data period | SF file |
| -- | -- |
| legacy 2016 | |
| legacy 2017 | !(https://twiki.cern.ch/twiki/pub/CMS/BtagRecommendation94X/DeepFlavour_94XSF_V4_B_F.csv)[DeepFlavour_94XSF_V4_B_F.csv] |
| legacy 2018 | |
|  |  |
| UL 2017 | | 
| -- | -- |


These b-tagging SFs can be read with a dedicated class in `configs/weightModules.py`
```python
btaggingSFs = weightModules.BTaggingScaleFactors(FILE)

for jet in jets:
    sfs = btaggingSFs.getSFs(jetFlavor, abs(jetEta), jetPt, deepJetValue)
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

patchValue = sfPatch.getPatchValue(sampleName, ttbbID, ttccID, nJets, HTjets)
```

### Rate factors

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

### Lepton Trigger scale factors

For electons and muons separate trigger scale factors are used. 
The muon trigger scale factors are provided by the POG as root files on the !(https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOG)[official Muon POG TWiki pages].
The electron trigger scale factors are derived as a part of the ttHbb analysis and are provided in !(https://gitlab.cern.ch/ttH/reference/-/tree/master/scale_factors/triggers)[this gitlab repository].
These root files has been converted to csv files with the scripts in `data/util` without changing the content.
The trigger scale factors can be read with a dedicated class in `configs/weightModules.py`

#### Electron Trigger SFs
|data period | SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | !(https://gitlab.cern.ch/ttH/reference/-/blob/master/scale_factors/triggers/SingleEG_JetHT_Trigger_Scale_Factors_ttHbb2017_v3.root)[SingleEG_JetHT_Trigger_Scale_Factors_ttHbb2017_v3.root ] | `ele28_ht150_OR_ele32_ele_pt_ele_sceta` |
| legacy 2018 | | |
|  |  |  |
| UL 2017 | | |
| -- | -- | -- |

```python
elTrigSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for el in electrons:
    trigSF = elTrigSFs.getSFs(elPt, elEtaSuperCluster)
    nominalSF = trigSF.loc["central"] # nominal scale factor
    variedSF  = trigSF.loc["up"] # example of varied scale factor
```

#### Muon Trigger SFs
|data period | SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | !(http://kplee.web.cern.ch/kplee/TagProbe/94X/v20180202_MergingHighPtBins/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root)[EfficienciesAndSF_RunBtoF_Nov17Nov2017.root] | `IsoMu27_PtEtaBins` |
| legacy 2018 | | |
|  |  |  |
| UL 2017 | | |
| -- | -- | -- |

```python
muTrigSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for mu in muons:
    trigSF = muTrigSFs.getSFs(muPt, abs(muEta))
    nominalSF = trigSF.loc["central"] # nominal scale factor
    variedSF  = trigSF.loc["up"] # example of varied scale factor
```


### Lepton ID/RECO/ISO scale factors

For electrons and muons separate official POG identification and reconstruction scale factors are used.
The POGs provide these scale factors as ROOT histograms on the !(https://twiki.cern.ch/twiki/bin/view/CMS/EgammaRunIIRecommendations)[official EGamma POG TWiki pages] and !(https://twiki.cern.ch/twiki/bin/view/CMS/MuonPOG)[official Muon POG TWiki pages].
These root files has been converted to csv files with the scripts in `data/util` without changing the content.
The lepton scale factors can be read with a dedicated class in `configs/weightModules.py`

#### Electron ID SFs
|data period | SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | !(https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/2017_ElectronTight.root)[2017_ElectronTight.root] | `tightElectronID` |
| legacy 2018 | | |
|  |  |  |
| UL 2017 | | |
| -- | -- | -- |

```python
elIDSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for el in electrons:
    idSF = elIDSFs.getSFs(elPt, elEtaSuperCluster)
    nominalSF = idSF.loc["central"] # nominal scale factor
    variedSF  = idSF.loc["up"] # example of varied scale factor
```

#### Muon ID SFs
|data period | SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | !(https://twiki.cern.ch/twiki/pub/CMS/MuonReferenceEffs2017/RunBCDEF_SF_ID.root)[RunBCDEF_SF_ID.root] | `NUM_TightID_DEN_genTracks_pt_abseta` |
| legacy 2018 | | |
|  |  |  |
| UL 2017 | | |
| -- | -- | -- |

```python
muIDSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for mu in muons:
    idSF = muIDSFs.getSFs(muPt, abs(muEta))
    nominalSF = idSF.loc["central"] # nominal scale factor
    variedSF  = idSF.loc["up"] # example of varied scale factor
```

#### Electron RECO SFs
|data period | SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | !(https://twiki.cern.ch/twiki/pub/CMS/Egamma2017DataRecommendations/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root)[egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root] | `electronReco` |
| legacy 2018 | | |
|  |  |  |
| UL 2017 | | |
| -- | -- | -- |

```python
elRecoSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)
for el in electrons:
    recoSF = elRecoSFs.getSFs(elPt, elEtaSuperCluster)
    nominalSF = recoSF.loc["central"] # nominal scale factor
    variedSF  = recoSF.loc["up"] # example of varied scale factor
```

#### Muon ISO SFs
|data period | SF file | SF name |
| -- | -- | -- |
| legacy 2016 | | |
| legacy 2017 | !(https://twiki.cern.ch/twiki/pub/CMS/MuonReferenceEffs2017/RunBCDEF_SF_ISO.root)[RunBCDEF_SF_ISO.root] | `NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta` |
| legacy 2018 | | |
|  |  |  |
| UL 2017 | | |
| -- | -- | -- |

```python
muISOSFs = weightModules.LeptonSFs(csv = FILE, sfName = SFNAME)

for mu in muons:
    isoSF = muISOSFs.getSFs(muPt, abs(muEta))
    nominalSF = isoSF.loc["central"] # nominal scale factor
    variedSF  = isoSF.loc["up"] # example of varied scale factor
```

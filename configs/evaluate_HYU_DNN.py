import numpy as np
import common
import pandas as pd
name = "addbb"
def get_naming():
    '''
    define name for this reconstruction
    '''
    return name

def get_jet_collection():
    ''' define name of jet collection to read '''
    return "Jet", "nJets_SYS"
#should be in the ntuple

def get_objects():
    '''
    define a list of objects considered for the reconstruction
    '''
    objects = [

        "b1",
        "b2"

        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [

        "E_SYS", 
        "Eta_SYS",
        "M_SYS",
        "Phi_SYS",
        "Pt_SYS",
        "btagValue_SYS"

        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''

    # from ntuple
    variables = [

        "nTagsM_SYS",               #nbjets_m
        "nJets_SYS",                #ngoodjets
        "HT_SYS",                   #Ht

        "Lep_Pt[0]",                #lepton_pt
        "Lep_Eta[0]",               #lepton_eta
        "Lep_Phi[0]",               #lepton_phi
        "Lep_M[0]",                 #lepton_m
        "Lep_E[0]",                 #lepton_m

        "MET_T1_Pt_SYS",            #MET_pt 
        "MET_T1_Phi_SYS",           #MET_phi

        "Jet_Pt_SYS[0]",            #jet1_pt
        "Jet_Eta_SYS[0]",           #jet1_eta
        "Jet_Phi_SYS[0]",           #jet1_phi
        "Jet_M_SYS[0]",             #jet1_m
        "Jet_E_SYS[0]",             #jet1_m
        "Jet_btagValue_SYS[0]",     #jet1_btag

        "Jet_Pt_SYS[1]",            #jet2_pt
        "Jet_Eta_SYS[1]",           #jet2_eta
        "Jet_Phi_SYS[1]",           #jet2_phi
        "Jet_M_SYS[1]",             #jet2_m
        "Jet_E_SYS[1]",             #jet1_m
        "Jet_btagValue_SYS[1]",     #jet2_btag

        "Jet_Pt_SYS[2]",            #jet3_pt
        "Jet_Eta_SYS[2]",           #jet3_eta
        "Jet_Phi_SYS[2]",           #jet3_phi
        "Jet_M_SYS[2]",             #jet3_m
        "Jet_E_SYS[2]",             #jet1_m
        "Jet_btagValue_SYS[2]",     #jet3_btag

        "Jet_Pt_SYS[3]",            #jet4_pt
        "Jet_Eta_SYS[3]",           #jet4_eta
        "Jet_Phi_SYS[3]",           #jet4_phi
        "Jet_M_SYS[3]",             #jet4_m
        "Jet_E_SYS[3]",             #jet1_m
        "Jet_btagValue_SYS[3]",     #jet4_btag

        ]
    return variables

def get_permutation_variables():
    '''
    list of all variables that are used for the different permutations of 2jets
    '''
    variables = [

        name+"_dEta",
        name+"_dPhi",
        name+"_M",
        name+"_dR_nuLep"

        ]
    return variables

def get_event_variables():
    '''
    list of all event variables that are used
    '''
    variables = [

        "Jet1lep_dR",     #dRlep1
        "Jet1nu_dR",      #dRnu1
        "Jet1lep_M",      #invmlep1
        "Jet2lep_dR",     #dRlep2
        "Jet2nu_dR",      #dRnu2
        "Jet2lep_M",      #invmlep2
        "Jet3lep_dR",     #dRlep3
        "Jet3nu_dR",      #dRnu3
        "Jet3lep_M",      #invmlep3
        "Jet4lep_dR",     #dRlep4
        "Jet4nu_dR",      #dRnu4
        "Jet4lep_M"       #invmlep4

        ]
    return variables + get_additional_variables()
 
'''
numerate the indices of the output nodes and the corresponding dijet combination
e.g. 0: "12" means the first output node corresponds to combination of the 1st and 2nd jets being the signal
'''
indices = {

    0: "12",
    1: "13",
    2: "14",
    3: "23",
    4: "24",
    5: "34"

        }

def get_output_indices():
    return indices

def get_input_variables():
    '''
    return an ordered list of all DNN input variables
    the order is important to assign the correct values to the DNN input nodes
    '''
    variables = []
    for v in get_permutation_variables():
        variables += [v.replace(name, name+indices[i]) for i in indices]

    evtVar = [

        "nTagsM_SYS",               #nbjets_m
        "nJets_SYS",                #ngoodjets
        "HT_SYS",                   #Ht

        "Lep_Pt[0]",                #lepton_pt
        "Lep_Eta[0]",               #lepton_eta
        "Lep_Phi[0]",               #lepton_phi
        "Lep_M[0]",                 #lepton_m

        "MET_T1_Pt_SYS",            #MET_pt 
        "MET_T1_Phi_SYS"            #MET_phi

    ]

    evtVar += variables
     
    jetVar = [

        "Jet_Pt_SYS[0]",            #jet1_pt
        "Jet_Eta_SYS[0]",           #jet1_eta
        "Jet_M_SYS[0]",             #jet1_m
        "Jet_btagValue_SYS[0]",     #jet1_btag
        "Jet1lep_dR",               #dRlep1
        "Jet1nu_dR",                #dRnu1
        "Jet1lep_M",                #invmlep1

        "Jet_Pt_SYS[1]",            #jet2_pt
        "Jet_Eta_SYS[1]",           #jet2_eta
        "Jet_M_SYS[1]",             #jet2_m
        "Jet_btagValue_SYS[1]",     #jet2_btag
        "Jet2lep_dR",               #dRlep2
        "Jet2nu_dR",                #dRnu2
        "Jet2lep_M",                #invmlep2

        "Jet_Pt_SYS[2]",            #jet3_pt
        "Jet_Eta_SYS[2]",           #jet3_eta
        "Jet_M_SYS[2]",             #jet3_m
        "Jet_btagValue_SYS[2]",     #jet3_btag
        "Jet3lep_dR",               #dRlep3
        "Jet3nu_dR",                #dRnu3
        "Jet3lep_M",                #invmlep3

        "Jet_Pt_SYS[3]",            #jet4_pt
        "Jet_Eta_SYS[3]",           #jet4_eta
        "Jet_M_SYS[3]",             #jet4_m
        "Jet_btagValue_SYS[3]",     #jet4_btag
        "Jet4lep_dR",               #dRlep4
        "Jet4nu_dR",                #dRnu4
        "Jet4lep_M"                 #invmlep4

        ]
    return evtVar, jetVar

def get_output_variables():
    '''
    get list of all variables to be written to the output ntuple
    '''
    variables = get_permutation_variables()
    variables+= [

        "nJets_SYS",
        "nTagsM_SYS",
        name+"_dR",

        ]
    return variables

debug=False
def get_permutations(df, ptMatrix, btagOrder):
    '''
    produce flat list for input of the DNN
    all the permutations that are based eother on pT or btagvalue ordering can be set here
    '''
    # first 4 entries in btagOrder list point to pT index of jets
    if debug: print("btagValue order", btagOrder)
    # consider btagOrder 0,1,2,3 jets 
    # then consider remaining jets
    remainingJets = btagOrder[4:]
    if debug: print("indices of remaining jets after cutting first four:", remainingJets)
    # sort them by pT
    pTOrder = sorted(remainingJets)
    if debug: print("pt indices of remaining jets: ", pTOrder)

    # define name of entries
    permutations = {
        # entry "01" for example here refers to jet with highest and second highest btag values
        # these are accesed via btagorder[0] and btagorder[1]
        # pT Order sorting is available for example: ptMatrix[btagOrder[0],pTOrder[1]]

        "12": ptMatrix[btagOrder[0],btagOrder[1]],
        "13": ptMatrix[btagOrder[0],btagOrder[2]],
        "14": ptMatrix[btagOrder[0],btagOrder[3]],
        "23": ptMatrix[btagOrder[1],btagOrder[2]],
        "24": ptMatrix[btagOrder[1],btagOrder[3]],
        "34": ptMatrix[btagOrder[2],btagOrder[3]]

        }
    
    if debug: print("values of the dict are the index in the dataframe of the corresponding permutation: ",permutations)

    # fill all of the values needed for output
    data = {}
    # loop over all these permutations
    for p in permutations:
        # get the entry at the corresponding index
        entry = df.iloc[permutations[p]]
        # loop over all the permutation variables
        for v in get_permutation_variables():
            # fill the entry in the data dictionary
            data[v.replace(name,name+p)] = entry[v]
    # also fill all the event shape variables that are needed
    for v in get_event_variables():
        data[v] = entry[v]
    
    #print(data)
    #print(get_event_variables())
    #print(get_input_variables())   

    # now return the permutations dictionary and a list of values for the DNN
    # the list of values will be returned as a list that should have the correct order of values
    #return permutations, np.array([data[v] for v in get_input_variables()])

    evtVar, jetVar = get_input_variables()
    # HYU convention:
    evtValues = np.array([data[v] for v in evtVar]).reshape(-1,33)
    jetValues = np.array([data[v] for v in jetVar]).reshape(-1,4,7)

    return permutations, [evtValues, jetValues]

def base_selection(event, syst = "nom"):
    return event.nLep == 1 and getattr(event, "nJets_"+syst) >= 6 and getattr(event, "nTagsM_"+syst) >= 4

def calculate_variables(df, ptMatrix, btagOrder, syst = "nom"):
    '''
    calculate additional variables needed
    '''

    # get vectors to build top quarks
    vectors = common.Vectors(df, name, ["b1", "b2"], jecDependent = True)

    # get add bb system
    vectors.add(["b1", "b2"], out = "addbb")

    # lepton
    vectors.initIndexedVector(df, "Lep", 0)
    # met
    vectors.addNeutrino(df, "MET_T1_Pt_SYS", "MET_T1_Phi_SYS", "Lep_0")

    # get lepton+met system
    vectors.add(["Lep_0", "nu"], out = "nuLep")
    df["nuLep_Pt"]  = vectors.get("nuLep", "Pt")
    df["nuLep_Eta"]  = vectors.get("nuLep", "Eta")
    df["nuLep_Phi"]  = vectors.get("nuLep", "Phi")
    df["nuLep_M"]  = vectors.get("nuLep", "M")

    # write ttbar variables to dataframe
    df[name+"_Pt"]  = vectors.get("addbb", "Pt")
    df[name+"_Eta"] = vectors.get("addbb", "Eta")
    df[name+"_M"]   = vectors.get("addbb", "M")
    df[name+"_E"]   = vectors.get("addbb", "E")
    
    df[name+"_dPhi"]  = common.get_dPhi(df[name+"_b1_Phi_SYS"].values, df[name+"_b2_Phi_SYS"].values)
    df[name+"_dEta"]  = abs(df[name+"_b1_Eta_SYS"].values - df[name+"_b2_Eta_SYS"].values)
    df[name+"_dR"]  = np.sqrt(df[name+"_dPhi"].values**2 + df[name+"_dEta"]**2)

    df[name+"_dR_nuLep"] = np.sqrt(
        common.get_dPhi(df[name+"_b1_Phi_SYS"].values, df["nuLep_Phi"].values)**2 + \
        abs(df[name+"_b1_Eta_SYS"].values - df["nuLep_Eta"].values)**2
        )

    vectors.initIndexedVector(df, "Jet", 0, suffix="_SYS")
    vectors.initIndexedVector(df, "Jet", 1, suffix="_SYS")
    vectors.initIndexedVector(df, "Jet", 2, suffix="_SYS")
    vectors.initIndexedVector(df, "Jet", 3, suffix="_SYS")

    vectors.add(["Jet_0", "Lep_0"], out = "Jet1lep")
    vectors.add(["Jet_1", "Lep_0"], out = "Jet2lep")
    vectors.add(["Jet_2", "Lep_0"], out = "Jet3lep")
    vectors.add(["Jet_3", "Lep_0"], out = "Jet4lep")

    df["Jet1lep_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[0]"].values, df["Lep_Phi[0]"].values)**2 + \
        abs(df["Jet_Eta_SYS[0]"].values - df["Lep_Eta[0]"].values)**2
        )
    df["Jet1nu_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[0]"].values, df["MET_T1_Phi_SYS"].values)**2 + \
        abs(df["Jet_Eta_SYS[0]"].values)**2
        )
    df["Jet2lep_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[1]"].values, df["Lep_Phi[0]"].values)**2 + \
        abs(df["Jet_Eta_SYS[1]"].values - df["Lep_Eta[0]"].values)**2
        )
    df["Jet2nu_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[1]"].values, df["MET_T1_Phi_SYS"].values)**2 + \
        abs(df["Jet_Eta_SYS[1]"].values)**2
        )
    df["Jet3lep_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[2]"].values, df["Lep_Phi[0]"].values)**2 + \
        abs(df["Jet_Eta_SYS[2]"].values - df["Lep_Eta[0]"].values)**2
        )
    df["Jet3nu_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[2]"].values, df["MET_T1_Phi_SYS"].values)**2 + \
        abs(df["Jet_Eta_SYS[2]"].values)**2
        )
    df["Jet4lep_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[3]"].values, df["Lep_Phi[0]"].values)**2 + \
        abs(df["Jet_Eta_SYS[3]"].values - df["Lep_Eta[0]"].values)**2
        )
    df["Jet4nu_dR"] = np.sqrt(
        common.get_dPhi(df["Jet_Phi_SYS[3]"].values, df["MET_T1_Phi_SYS"].values)**2 + \
        abs(df["Jet_Eta_SYS[3]"].values)**2
        )

    df["Jet1lep_M"] = vectors.get("Jet1lep", "M")
    df["Jet2lep_M"] = vectors.get("Jet2lep", "M")
    df["Jet3lep_M"] = vectors.get("Jet3lep", "M")
    df["Jet4lep_M"] = vectors.get("Jet4lep", "M")
  
    # generate flat list of data for the dnn
    permutations, data = get_permutations(df, ptMatrix, btagOrder)
    return permutations, data, df

def get_match_variables():
    ''' function not needed '''
    variables = [
        ]
    return variables

def get_random_index(df, bestIndex):
    ''' function not needed '''
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex

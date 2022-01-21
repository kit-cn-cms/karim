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
        "btagValue_SYS",
        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Lep_E[0]",
        "Lep_Eta[0]",
        "Lep_M[0]",
        "Lep_Phi[0]",
        "Lep_Pt[0]",

        "MET_T1_Phi_SYS",
        "MET_T1_Pt_SYS",

        "nJets_SYS",
        "nTagsM_SYS",
        "nTagsT_SYS",
        ]
    return variables

def get_permutation_variables():
    '''
    list of all variables that are used for the different permutations of 2jets
    '''
    variables = [
        name+"_Pt",
        name+"_Eta",
        name+"_M",
        name+"_E",
        name+"_dPhi",
        name+"_dEta",
        name+"_dR",
        name+"_b1Lep_dR"
        ]
    return variables

def get_event_variables():
    '''
    list of all event variables that are used
    '''
    variables = [
        "nJets_SYS",
        "nTagsM_SYS",
        ]
    return variables
    
'''
numerate the indices of the output nodes and the corresponding dijet combination
e.g. 0: "01" means the first output node corresponds to combination "01" being the signal
'''
indices = {
    0: "01",
    1: "02",
    2: "03",
    3: "04",
    4: "05",

    5: "12",
    6: "13",
    7: "14",
    8: "15",

    9: "23",
    10: "24",
    11: "25",

    12: "34",
    13: "35",

    14: "45",
        }
def get_output_indices():
    return indices

def get_input_variables():
    '''
    return an ordered list of all DNN input variables
    the order is important to assign the correct values to the DNN input nodes
    '''
    variables = []
    for i in indices:
        variables += [v.replace(name, name+indices[i]) for v in get_permutation_variables()]
    variables += get_event_variables()
    return variables

def get_output_variables():
    '''
    get list of all variables to be written to the output ntuple
    '''
    variables = get_permutation_variables()
    variables+= [
        "nJets_SYS",
        "nTagsM_SYS",
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
        "01": ptMatrix[btagOrder[0],btagOrder[1]],
        "02": ptMatrix[btagOrder[0],btagOrder[2]],
        "03": ptMatrix[btagOrder[0],btagOrder[3]],
        # entry "04" for example here refers to jet with highest btag value and jet with highest pt value that is not among the first four btagvalue jets
        "04": ptMatrix[btagOrder[0],pTOrder[0]],
        "05": ptMatrix[btagOrder[0],pTOrder[1]],

        "12": ptMatrix[btagOrder[1],btagOrder[2]],
        "13": ptMatrix[btagOrder[1],btagOrder[3]],
        "14": ptMatrix[btagOrder[1],pTOrder[0]],
        "15": ptMatrix[btagOrder[1],pTOrder[1]],

        "23": ptMatrix[btagOrder[2],btagOrder[3]],
        "24": ptMatrix[btagOrder[2],pTOrder[0]],
        "25": ptMatrix[btagOrder[2],pTOrder[1]],

        "34": ptMatrix[btagOrder[3],pTOrder[0]],
        "35": ptMatrix[btagOrder[3],pTOrder[1]],

        "45": ptMatrix[pTOrder[0],pTOrder[1]],
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
        
    # now return the permutations dictionary and a list of values for the DNN
    # the list of values will be returned as a list that should have the correct order of values
    return permutations, np.array([data[v] for v in get_input_variables()])


def base_selection(event, syst = "nom"):
    return getattr(event, "nJets_"+syst) >= 6 and getattr(event, "nTagsM_"+syst) >= 4

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
    #vectors.addNeutrino(df, "MET_T1_Pt_SYS", "MET_T1_Phi_SYS", "Lep_0")

    # write ttbar variables to dataframe
    df[name+"_Pt"]  = vectors.get("addbb", "Pt")
    df[name+"_Eta"] = vectors.get("addbb", "Eta")
    df[name+"_M"]   = vectors.get("addbb", "M")
    df[name+"_E"]   = vectors.get("addbb", "E")
    
    df[name+"_dPhi"]  = common.get_dPhi(df[name+"_b1_Phi_SYS"].values, df[name+"_b2_Phi_SYS"].values)
    df[name+"_dEta"]  = abs(df[name+"_b1_Eta_SYS"].values - df[name+"_b2_Eta_SYS"].values)
    df[name+"_dR"]  = np.sqrt(df[name+"_dPhi"].values**2 + df[name+"_dEta"]**2)

    df[name+"_b1Lep_dR"] = np.sqrt(
        common.get_dPhi(df[name+"_b1_Phi_SYS"].values, df["Lep_Phi[0]"].values)**2 + \
        abs(df[name+"_b1_Eta_SYS"].values - df["Lep_Eta[0]"].values)**2
        )

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

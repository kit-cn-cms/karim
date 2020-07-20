import common


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Evt_Run",   
        "Evt_Lumi",
        "Evt_ID",
        "Evt_JetIdx",
        "N_Jets",
        "N_BTagsM",
        "isTagged",
        "jetEnergy",
        "jetPt",
        "jetMass",
        "jetPhi",
        "jetEta",
        "jetCharge",
        "deepJetValue",
        "deepJet_CvsL",
        "deepJet_CvsB",
        "leptonPt",
        "leptonEta",
        "leptonPhi",
        "leptonE",
        "jetFlavor"

        ]
    return variables

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    return True



def calculate_variables(df):
    '''
    calculate additional variables
    '''
    return df

    df["jetFlavorTag_CvsB"] = df["jetFlavorTag_c"]/(df["jetFlavorTag_c"]+df["jetFlavotTag_b"])
    df["jetFlavorTag_CvsL"] = df["jetFlavorTag_c"]/(df["jetFlavorTag_c"]+df["jetFlavotTag_lf"])


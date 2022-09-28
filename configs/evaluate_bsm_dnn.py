import common


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "run",   
        "lumi",
        "event",
        "N_allJets_corr_nom",
        "N_taggedJets_corr_nom",
        ]
    return variables

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    sel_base = "((N_allJets_corr_nom>=2 and N_taggedJets_corr_nom>=1 and nPairs_corr==1) and (crossTrigMatch_corr == 1 or singleTrigMatch_corr == 1))"

    return sel_base

def calculate_variables(df):
    '''
    calculate additional variables
    '''
    return df


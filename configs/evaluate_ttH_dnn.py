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
        "N_Jets",
        "N_BTagsM"
        ]
    return variables

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    return event.N_Jets>=4 and event.Evt_MET >= 20.

def calculate_variables(df):
    '''
    calculate additional variables
    '''
    return df


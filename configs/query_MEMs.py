import common

name = "MEM"

def get_Mode():
    return "MEM"

def get_reco_naming():
    '''
    define name for this reconstruction
    '''
    return name


def get_objects():
    '''
    define a list of objects considered for the reconstruction
    '''
    objects = [
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi",
        "N_Jets",
        "N_BTagsM"
        ]
    return variables

def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''
    return df
def base_selection(event):
    return True


import common

name = "Reco"
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
        ]
    return variables



def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''
    return df


import common

name = "Reco"
def get_naming():
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

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    return event.N_Jets>=2


def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''
    return df



'''
for matching mode
'''
def get_match_variables():
    '''
    list of variables (usually dR variables) that should be checked for matches
    the matching threshold can be set via the -t argument
    '''
    variables = [
        ]
    return variables

def get_random_index(df, bestIndex):
    '''
    return a random index for the definition of the background
    the default implementation returns any index as long as it is not the correct assignment
    '''
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex


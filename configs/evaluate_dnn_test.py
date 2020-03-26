import common

variables = [
    
    ]

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    return variables

def add_variables(add_vars):
    variables += add_vars

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    return event.N_Jets>=4

def calculate_variables(df):
    '''
    calculate additional variables
    '''
    return df


def get_dnn_outputs():
    outputs = [
        "dnnOutput_ttH_node",
        "dnnOutput_ttmb_node",
        "dnnOutput_tt2b_node",
        "dnnOutput_ttcc_node",
        "dnnOutput_ttlf_node",
        "dnnOutput_tHq_node",
        "dnnOutput_tHW_node",
        ]
    return outputs
    
def get_dnn_predicted_class():
    varnames = [
        "dnn_predictedClass",
        ]
    return varnames

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
        "N_BTagsM",
        "TRF_weight_4j4b",
        "TRF_weight_4j3b",
        "mem_p"
        ]
    return variables

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    sel_singleel = (event.N_LooseMuons == 0 and event.N_TightElectrons == 1) and (event.Triggered_HLT_Ele28_eta2p1_WPTight_Gsf_HT150_vX == 1 or (event.Triggered_HLT_Ele32_WPTight_Gsf_L1DoubleEG_vX == 1 and event.Triggered_HLT_Ele32_WPTight_Gsf_2017SeedsX == 1))
    sel_singlemu = (event.N_LooseElectrons == 0 and event.N_TightMuons == 1) and event.Triggered_HLT_IsoMu27_vX

    return event.N_Jets>=4 and event.Evt_MET >= 20. and (sel_singleel or sel_singlemu)



def calculate_variables(df):
    '''
    calculate additional variables
    '''
    return df


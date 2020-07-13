import numpy as np
import common

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Evt_Odd",
        "N_Jets",
        "N_BTagsM",
        "Weight_XS",
        "Weight_btagSF",
        "Weight_GEN_nom",
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi"
        ]
    for i in range(11):
        variables += [
            "Jet_DeepCSV_b["+str(i)+"]",
            "Jet_DeepCSV_bb["+str(i)+"]",
            "Jet_DeepCSV_c["+str(i)+"]",
            "Jet_DeepCSV_udsg["+str(i)+"]",
            "Jet_DeepJet_b["+str(i)+"]",
            "Jet_DeepJet_bb["+str(i)+"]",
            "Jet_DeepJet_c["+str(i)+"]",
            "Jet_DeepJet_g["+str(i)+"]",
            "Jet_DeepJet_lepb["+str(i)+"]",
            "Jet_DeepJet_uds["+str(i)+"]",
            ]
    return variables

def base_selection(event):
    return event.N_Jets>=4

def calculate_variables(df):
    '''
    calculate additional variables needed
    '''
    for i in range(11):
        df["Jet_DeepCSV_CvsL_"+str(i)] = df["Jet_DeepCSV_c["+str(i)+"]"].values / \
            (df["Jet_DeepCSV_c["+str(i)+"]"].values + \
             df["Jet_DeepCSV_udsg["+str(i)+"]"].values + 1e-10)

        df["Jet_DeepCSV_CvsB_"+str(i)] = df["Jet_DeepCSV_c["+str(i)+"]"].values / \
            (df["Jet_DeepCSV_c["+str(i)+"]"].values + \
             df["Jet_DeepCSV_b["+str(i)+"]"].values + \
             df["Jet_DeepCSV_bb["+str(i)+"]"].values + 1e-10)


        df["Jet_DeepJet_CvsB_"+str(i)] = df["Jet_DeepJet_c["+str(i)+"]"].values / \
            (df["Jet_DeepJet_c["+str(i)+"]"].values + \
             df["Jet_DeepJet_b["+str(i)+"]"].values + \
             df["Jet_DeepJet_bb["+str(i)+"]"].values + \
             df["Jet_DeepJet_lepb["+str(i)+"]"].values + 1e-10)

        df["Jet_DeepJet_CvsL_"+str(i)] = df["Jet_DeepJet_c["+str(i)+"]"].values / \
            (df["Jet_DeepJet_c["+str(i)+"]"].values + \
             df["Jet_DeepJet_g["+str(i)+"]"].values + \
             df["Jet_DeepJet_uds["+str(i)+"]"].values + 1e-10)
    return df


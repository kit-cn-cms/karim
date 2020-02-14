from ROOT import TFile

def getEntries(filepath):
    '''
    get entries of rootfile
    '''
    f = TFile(filepath)
    t = f.Get("MVATree")
    entries = t.GetEntries()
    f.Close()
    return entries


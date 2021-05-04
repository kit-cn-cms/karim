from ROOT import TFile

def getEntries(filepath, treeName = "Events"):
    '''
    get entries of rootfile
    '''
    f = TFile(filepath)
    t = f.Get(treeName)
    entries = t.GetEntries()
    f.Close()
    return entries


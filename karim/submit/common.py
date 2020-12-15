from ROOT import TFile

def getEntries(filepath):
    '''
    get entries of rootfile
    '''
    print("loading filepath '{}'".format(filepath))
    f = TFile.Open(filepath)
    t = f.Get("Events")
    entries = t.GetEntries()
    f.Close()
    return entries


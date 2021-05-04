import pandas as pd

class RateFactors:
    '''
    read rate factors from csv files for various uncertainties
    '''
    def __init__(self, csv, sampleColumn = "sample", variationColumn = "variation", factorColumn = "final_weight_sl_analysis"):
        self.data = pd.read_csv(csv, index_col = [sampleColumn, variationColumn])
        self.factorColumn    = factorColumn
        
        self.samples    = self.data.index.unique(0).values
        self.variations = self.data.index.unique(1).values

        self.errors = 0

    def getRF(self, sample, variation):
        try:
            return self.data.loc[(sample, variation), self.factorColumn]
        except:
            if not sample in self.samples:
                if self.errors < 100: print("sample {} not in rateFactor file".format(sample))
                self.errors += 1
                return 1.
            if not variation in self.variations:
                if self.errors < 100: print("variation {} not in rateFactor file".format(variation))
                self.errors += 1
                return 1.


class BTaggingScaleFactors:
    '''
    read b-tagging sfs from csv files
    WIP: jes variations and fixedWP
    '''
    def __init__(self, csv, measurementType = "iterativefit", workingPoint = 3, wpName = "OperatingPoint", sysTypes = []):
        # load dataframe
        data = pd.read_csv(csv, index_col = ["measurementType", wpName, "sysType", "jetFlavor"], delimiter = ", ", engine = "python")
        data = data.sort_index()
        # select only the chosen type
        self.data = data.loc[(measurementType, workingPoint, )]

        # error book keeping
        self.errors = 0

    def removeUnusedSys(self, keep, jec = None):
        '''
        prune csv table to variations that are actually used
        improves runtime substantially
        '''
        data = self.data[self.data.index.get_level_values("sysType").isin(keep)]
        self.jecData = {}
        if not jec is None:
            for j in jec:
                self.jecData[j] = self.data[self.data.index.get_level_values("sysType").isin([j])]
        self.data = data

    def getSF(self, sys, flav, eta, pt, x):
        '''
        get exactly one scale factor value
        '''
        try:
            sfs = self.data.loc[(sys, flav)]
        except:
            if self.errors < 100: print("could not find sfs for {} and flavor {}".format(sys, flav))
            self.errors+=1
            return 1.

        # find sf bin
        func = sfs.loc[(sfs["etaMin"]<=eta) & (sfs["etaMax"]>eta) & (sfs["ptMin"]<=pt) & (sfs["ptMax"]>pt) & (sfs["discrMin"]<=x) & (sfs["discrMax"]>x)]
    
        # evaluate formula
        return eval(func["formula"].iloc[0])

    def getSFs(self, flav, eta, pt, x, jec = "nom"):
        '''
        get scale factors for one flavor, eta, pt and b-tag value combination
        '''
        if jec == "nom":
            # search jet flavor entries
            sfs = self.data[self.data.index.get_level_values("jetFlavor") == flav]
        else:
            sfs = self.jecData[jec][self.jecData[jec].index.get_level_values("jetFlavor") == flav]
        sfs.index = sfs.index.droplevel("jetFlavor")

        # find sf bin
        sfs = sfs.loc[(sfs["etaMin"]<=eta) & (sfs["etaMax"]>eta) & (sfs["ptMin"]<=pt) & (sfs["ptMax"]>pt) & (sfs["discrMin"]<=x) & (sfs["discrMax"]>x)]
    
        # evaulate formula
        return sfs["formula"].apply(eval, args = ({"x": x},))

class SFPatches:
    '''
    read patches for b-tagging scale factors from csv files
    WIP: current implementation hard coded to nJets/HT bins
    '''
    def __init__(self, csv, applyToMissing = "ttlf"):
        # read csv file
        self.data = pd.read_csv(csv, index_col = ["process"])

        # how are other events treated?
        self.applyToMissing = applyToMissing

        # error book keeping
        self.errors = 0

    def getPatchValue(self, sample, ttID, nJets, HT):
        if sample.startswith("ttH") or sample.startswith("TTH"):
            proc = "ttH"
        elif sample.startswith("TTZ"):
            proc = "ttZ"
        elif sample.startswith("TTbb"):
            proc = "ttbb"
        elif sample.startswith("TTTo"):
            if   ttID >= 50: proc = "ttbb_5FS"
            elif ttID >= 40: proc = "ttcc"
            else:            proc = "ttlf"
        else:
            if self.errors < 100:
                print("no dedicated SF found - applying {} instead".format(self.applyToMissing))
                self.errors+=1
            if not self.applyToMissing is None:
                proc = self.applyToMissing
            else:
                return 1.

        p = self.data.loc[(proc)]
        return p.loc[(p["jetsMin"]<=nJets) & (p["jetsMax"]>nJets) & (p["htMin"]<=HT) & (p["htMax"]>HT)]["factor"]


class LeptonSFs:
    '''
    read lepton scale factors from csv files
    '''
    def __init__(self, csv, sfName):
        # load dataframe
        data = pd.read_csv(csv, index_col = ["sfType", "sysType"])
        data = data.sort_index()

        # select only the chosen type
        self.data = data.loc[(sfName, )]

        # error book keeping
        self.errors = 0

    def getSFs(self, pt, eta):
        '''
        get scale factors for one pt and eta bin
        '''
        # find sf bin
        return self.data.loc[(self.data["ptMin"]<=pt) & (self.data["ptMax"]>pt) & (self.data["etaMin"]<=eta) & (self.data["etaMax"]>eta)]["factor"]

class PileupSFs:
    '''
    read pileup reweighting scale factors from csv files
    '''
    def __init__(self, csv):
        data = pd.read_csv(csv, index_col = ["nPU"])
        data = data.sort_index()
        
        self.data = data

    def getSF(self, pu, name = "central"):
        if pu > 98: pu = 98
        return self.data.loc[pu][name]

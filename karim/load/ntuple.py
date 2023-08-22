import ROOT
import os
import uproot as up


class InputFile(object):
    """
    Input file class based on uproot to be used with a 'with' statement
    """

    def __init__(self, fileName):
        """
        initialization
        """
        self.file_name = fileName

    def __enter__(self):
        """
        enter function to execute at the beginning of the with statement and returning the class instance
        """
        self.open_str = "{}".format(self.file_name)
        with up.open(self.open_str) as file:
            print("\nWill be loading file {}\n".format(self.open_str))
            print("File contents:")
            print(file.keys())
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        """
        exit function to execute at the end of the with statement e.g. to clean up
        """
        print("Closed {}".format(self.open_str))
        del self.open_str

    def load(self, load_object_name):
        """
        load function to open an object in the file with uproot
        """
        return up.open("{}:{}".format(self.open_str, load_object_name))


jecs = [
    "jes",
    "jesAbsolute_2018",
    "jesAbsolute_2017",
    "jesAbsolute_2016",
    "jesHF_2018",
    "jesHF_2017",
    "jesHF_2016",
    "jesEC2_2018",
    "jesEC2_2017",
    "jesEC2_2016",
    "jesRelativeBal",
    "jesHEMIssue",
    "jesBBEC1_2018",
    "jesBBEC1_2017",
    "jesBBEC1_2016",
    "jesRelativeSample_2018",
    "jesRelativeSample_2017",
    "jesRelativeSample_2016",
    "jesFlavorQCD",
    "jesBBEC1",
    "jesHF",
    "jesAbsolute",
    "jesEC2",
    "jesTotal",
    "jer",
    "jesHEMIssue",
    "unclustEn",
    "jer0",
    "jer1",
    "jer2",
    "jer3",
    "jer4",
    "jer5",
]
validSysts = ["nom"]
validSysts += [j + "Up" for j in jecs]
validSysts += [j + "Down" for j in jecs]


def getSystematics(tree):
    branches = tree.keys()
    # print(branches)
    postfix = []
    for b in branches:
        if not b.split("_")[-1].startswith("201"):
            postfix.append(b.split("_")[-1])
        else:
            postfix.append(b.split("_")[-2] + "_" + b.split("_")[-1])
    jecs = list(set(postfix))
    jecs = [j for j in jecs if j in validSysts]
    jecs = list(sorted(jecs))
    print("\tfound the following JECs in the input file")
    for j in jecs:
        print("\t{}".format(j))
    return jecs


class TreeIterator:
    """
    Iterator class to loop over a ROOT TTree based on uproot
    """

    def __init__(self, inputtree, branches=[]):
        """
        initialize iterator class
        """
        # tree object and desired branches
        self.tree = inputtree
        self.branches = branches

    def __iter__(self):
        """
        initialize iteration
        """
        # event counter for iterator
        self.idx = 0
        # number of processed events directly from returned output
        self.num_processed = 0
        # max number of events i.e. number of events in tree
        self.max = self.tree.num_entries
        # event step size of iterator i.e. one iteration corresponds to processing self.step events
        self.step = 50
        # time extrapolation scale
        self.scale = 100000
        # ToDo add branch address initialization?
        self.timer = ROOT.TStopwatch()
        self.timer.Start()
        return self

    def __next__(self):
        """
        iteration function
        """
        if self.idx % self.step == 0 and self.idx > 0:
            print("at event {}/{}".format(self.idx, self.max))
            print(
                "  time for {} events:  {:.1f} s".format(
                    self.step, self.timer.RealTime()
                )
            )
            print(
                "  estimated time for {} events: {:.0f} min".format(
                    self.scale, self.timer.RealTime() / self.step * self.scale / 60.0
                )
            )
            self.timer.Start()
        if self.idx < self.max:
            start = self.idx
            self.idx += self.step
            stop = self.idx
            return_array = self.tree.arrays(
                self.branches, entry_start=start, entry_stop=stop, library="ak"
            )
            self.num_processed += len(return_array)
            return return_array
        else:
            raise StopIteration

    def next(self):
        """
        manual iteration function
        """
        return self.__next__()


class OutputFile(object):
    """
    Class to write a ROOT file based on uproot to be used with a 'with' statement
    """

    def __init__(self, fileName, treeName="Events"):
        """
        initialization of outputfile class
        """
        self.file_name = fileName
        self.setSampleName()
        # self.file = ROOT.TFile(self.file, "RECREATE")
        self.tree_name = treeName  # ROOT.TTree(treeName,"KarimTree")
        print("\nwriting info to file {}\n".format(self.file_name))

    def __enter__(self):
        """
        enter function to execute at the beginning of the with statement and returning the class instance
        """
        self.open_str = "{}".format(self.file_name)
        print("\nWill be opening file {}\n".format(self.open_str))
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        """
        exit function to execute at the end of the with statement e.g. to clean up
        """
        print("Closed {}".format(self.open_str))
        del self.open_str

    def open(self):
        """
        open function to open a ROOT file with uproot
        """
        return up.recreate(self.open_str)

    def setSampleName(self):
        self.sample_name = os.path.basename(os.path.dirname(self.file_name))


class GenWeights:
    def __init__(self, treepath):
        samplepath = os.path.dirname(treepath)
        ntuplepath = os.path.dirname(samplepath)
        samplename = os.path.basename(samplepath)
        self.filename = os.path.join(ntuplepath, samplename + "_genWeights.root")
        if not os.path.exists(self.filename):
            print("sample does not have genWeights file")
            self.isInitialized = False
            return

        print("loading genWeight file {}".format(self.filename))

        self.file = ROOT.TFile.Open(self.filename)
        self.branches = [b.GetName() for b in self.file.GetListOfKeys()]

        self.getProcessFractions()
        self.setRateFactors()
        self.isInitialized = True

    def getProcessFractions(self):
        # extract gen weight branches
        genWeights = [b for b in self.branches if b.startswith("genWeight")]
        self.weightTypes = [b.replace("genWeight_", "") for b in genWeights]

        if not "incl" in self.weightTypes:
            print("ERROR: could not find 'incl' gen weight in genWeight file")
            sys.exit()

        self.genFractions = {}
        self.xsNorms = {}
        print("process fractions:")
        inclh = self.file.Get("genWeight_incl")
        for w in self.weightTypes:
            genh = self.file.Get("genWeight_" + w)
            self.genFractions[w] = (
                genh.GetMean()
                * genh.GetEntries()
                / (inclh.GetMean() * inclh.GetEntries())
            )
            # XS usually given in pb, lumi in fb-1
            # -> expect 1000 events for a XS of 1 [pb] in 1 [fb-1] of data if all events are selected
            # -> multiply with XS number in plotscript later on
            self.xsNorms[w] = 1000.0 / (genh.GetMean() * genh.GetEntries())
            print(
                "\t{}: {} (XS norm: {})".format(
                    w, self.genFractions[w], self.xsNorms[w]
                )
            )
        print("=" * 50)

    def setRateFactors(self):
        self.rateFactors = {}
        print("rateFactors:")
        for b in self.branches:
            h = self.file.Get(b)
            self.rateFactors[b] = h.GetMean()
            print("{}: {}".format(b, self.rateFactors[b]))
        print("=" * 50)

    def getRF(self, w):
        if not self.isInitialized:
            return 1.0
        if not w in self.rateFactors:
            sys.exit("could not access ratefactor {}".format(w))
        return self.rateFactors[w]

    def getXS(self, t="incl"):
        if not self.isInitialized:
            return 1.0
        if not t in self.xsNorms:
            sys.exit("could not access norm type {}".format(t))
        return self.xsNorms[t]

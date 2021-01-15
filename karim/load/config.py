import sys
import os
import importlib

class Config:
    def __init__(self, configpath, friendTrees, mode, assignment_method):
        # load config module
        dirname, basename = os.path.split(configpath)
        sys.path.append(dirname)
        config_name = os.path.splitext(basename)[0]
        config = importlib.import_module(config_name)
        print("\nimporting config:\n{}\n".format(configpath))

        self.additional_variables   = config.get_additional_variables()
        self.base_selection         = config.base_selection
        self.calculate_variables    = config.calculate_variables

        if mode == "Reconstruction":
            self.naming     = config.get_naming()
            self.objects    = config.get_objects()
            self.features   = config.get_features()

            self.template = "{name}_OBJECT_FEATURE".format(name = self.naming)

            print("name template:")
            print(self.template)
            print("list of objects for reconstruction:")
            print("\n".join(self.objects))
            print("list of features for reconstruction:")
            print("\n".join(self.features))
            
            self.additional_objects = config.get_additional_objects()
            if len(self.additional_objects) > 0:
                print("additional objects:")
                for order in self.additional_objects:
                    print("ordered by {}:".format(order))
                    print("\n".join(self.additional_objects[order]))

            self.def_sig_selection = {}
            self.def_background_selection = {}
            
        if mode == "Matching":
            self.naming     = config.get_naming()
            self.objects    = config.get_objects()
            self.features   = config.get_features()
            self.additional_objects = {}

            self.template = "{name}_OBJECT_FEATURE".format(name = self.naming)

            print("name template:")
            print(self.template)

            self.def_signal_selection = config.def_signal_selection()
            self.def_background_selection = config.def_background_selection()
            #self.get_random_index = config.get_random_index

            '''
            # previous version #
            self.match_variables  = config.get_match_variables()
            '''
            ##################################################################
            #  news  Lukas, 14.01.2021
            ##################################################################
            if assignment_method == "threshold-based":
                #print type(config.get_match_variables())
                if len(config.get_match_variables()) == 3:
                    self.match_variables = config.get_match_variables()[:-1]
                    print("list of variables to be matched:")
                    print("\n".join(self.match_variables))
                else:
                    print("\033[1;31mSomething is wrong with the list in match_variables.\033[0m")
                    print("\033[1;31mPlease check if the list contains exactly 3 variables (jet1, jet2, chi^2).\033[0m")
                    sys.exit()
            elif assignment_method == "chi2":
                if len(config.get_match_variables()) == 3:
                    self.match_variables = config.get_match_variables()[-1]
                    print("list of variables to be matched:")
                    print(self.match_variables)
                    print(type(self.match_variables))
                else:
                    print("\033[1;31mSomething is wrong with the list in match_variables.\033[0m")
                    print("\033[1;31mPlease check if the list contains exactly 3 variables (jet1, jet2, chi^2).\033[0m")
                    sys.exit()
            ##################################################################
            #print("list of variables to be matched:")
            #print("\n".join(self.match_variables))

        if mode == "Calculation":
            print("mode - calculation")
            self.set_branches = config.set_branches
            self.objects    = []
            self.features   = []
            self.naming = ""
            self.template = ""
    
        if mode == "Evaluation":
            print("mode - dnn evaluation")

        # friend trees
        self.friendTreeBasePaths = []
        if len(friendTrees) > 0:
            print("adding friend trees:")
            self.friendTreeBasePaths = friendTrees

    def getFriendTrees(self, filename):
        '''
        get correct friend tree files for one base filename
        the strucutre of ntuples is
        basepath/
        ----/sample/
        ----/----/file.root
        '''
        sampledir, treename = os.path.split(filename)
        basedir, samplename = os.path.split(sampledir)

        friendTrees = []
        for ft in self.friendTreeBasePaths:
            friendTrees.append("/".join([ft, samplename, treename]))

        return friendTrees

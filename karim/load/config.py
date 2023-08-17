import sys
import os
import importlib
import glob 

class Config:
    def __init__(self, configpath, friendTrees, mode):
        # load config module
        dirname, basename = os.path.split(configpath)
        sys.path.append(dirname)
        config_name = os.path.splitext(basename)[0]
        config = importlib.import_module(config_name)
        print("\nimporting config:\n{}\n".format(configpath))

        self.additional_variables   = config.get_additional_variables()
        self.base_selection         = config.base_selection
        self.calculate_variables    = config.calculate_variables
        if config.load_input_branches:
            self.load_input_branches = config.load_input_branches
        else:
            self.load_input_branches = self.loadInputBranches

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
            self.def_dnn_reco_selection = config.def_dnn_reco_selection()
            
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
            self.def_dnn_reco_selection = {}
            self.get_random_index = config.get_random_index
            self.match_variables  = config.get_match_variables()
            print("list of variables to be matched:")
            print("\n".join(self.match_variables))

        if mode == "Calculation":
            print("mode - calculation")
            self.set_branches = config.set_branches
            self.objects    = []
            self.features   = []
            self.naming     = ""
            self.template   = ""
 
        if mode == "Database":
            print("mode - database converter")
            self.run, self.lumi, self.evtid = config.get_db_ids()
            self.treename = config.get_db_tree()

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

    def getDataBase(self, filename, database):
        '''
        get correct database files for one sample
        the strucutre of databases is
        basepath/
        ----/sample/
        ----/----/DBFILE_db.root

        there have to be all events of this sample in 
        one file to function as a database.

        Additionally a file DBFILE_idx.h5 has to exists
        Where the event indices of the database are stored
        This can for example be created with the 
        scripts/create_idx_file.py script
        '''
        sampledir, treename = os.path.split(filename)
        basedir, samplename = os.path.split(sampledir)
    
        database_files = glob.glob(os.path.join(database, samplename, "*_db.root"))
        if len(database_files)!= 1: 
            sys.exit("more than one/no database files found at {}".format(
                os.path.join(database, samplename, "*_db.root")))
        db  = database_files[0]
        idx = db.replace("_db.root", "_idx.h5")
        if not os.path.exists(idx):
            sys.exit("index file does not exist {}".format(idx))
        return db, idx

    def loadInputBranches(self):
        return []

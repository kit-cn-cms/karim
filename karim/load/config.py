import sys
import os
import importlib

class Config:
    def __init__(self, configpath, mode):
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
            self.objects    = []
            self.features   = []
            self.naming = ""
            self.template = ""
    
        if mode == "Evaluation":
            self.dnn_output_variables = config.get_dnn_outputs()
            self.dnn_predicted_class  = config.get_dnn_predicted_class()   

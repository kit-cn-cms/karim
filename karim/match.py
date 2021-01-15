import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def match_jets(filename, configpath, friendTrees, n_bkg_combis, assignment_method, threshold, signal_only, outpath, apply_selection = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")


    bkg_combis = setNumberDijetCombis(n_bkg_combis)
    #print bkg_combis

    assign_method = def_assignment_method(assignment_method)

    #config = load.Config(configpath, friendTrees, "Matching")
    # new config style (with 4 arguments instead of 3)
    #   has to be taken into account for evaluation, calculation, reconstructian as well as for matching!!
    config = load.Config(configpath, friendTrees, "Matching", assign_method)

    # open input file
    with load.InputFile(filename, config.getFriendTrees(filename)) as ntuple:
    
        # load hypotheses module
        hypotheses = Hypotheses(config)

        # initialize hypotheses combinatorics
        hypotheses.initPermutations()

        first = True
        fillIdx = 0
        cutIdx = []
        # start loop over ntuple entries
        for i, event in enumerate(load.TreeIterator(ntuple)):
            entry, error = hypotheses.GetEntry(event, event.N_Jets)


            if first:
                # get list of all dataframe variables
                outputVariables = entry.columns.values
                outputVariables = np.append(outputVariables, config.naming+"_matchable")
                #print len(outputVariables)
                for v in outputVariables:
                    print(v)

                # setup empty array for event data storage
                outputSig = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))
                if not signal_only:
                    outputBkg = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables), bkg_combis))

                first = False

                # indices to fill basic variables regardless of matching status
                loIdxVars = hypotheses.nBaseVariables
                hiIdxVars = hypotheses.nAdditionalVariables


            if error:
                # for some reason no hypotheses are viable
                #   e.g. not enough jets
                if not apply_selection:
                    outputSig[fillIdx,:loIdxVars] = -99
                    outputSig[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                    outputSig[fillIdx,hiIdxVars:] = -99
                    if not signal_only:
                        outputBkg[fillIdx,:loIdxVars,0] = -99
                        #for i in range(bkg_combis):
                        outputBkg[fillIdx,loIdxVars:hiIdxVars,0] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                        outputBkg[fillIdx,hiIdxVars:,0] = -99
                        cutIdx.append(1)
                    fillIdx+=1
                continue

            # apply signal selection
            sig_selection = config.def_signal_selection
            entry_signal_selection = entry_selection(entry, sig_selection)
            # get best permutation
            # bestIndex = findBest(entry, threshold, config.match_variables)
            #bestIndex = findBest(entry_signal_selection, threshold, config.match_variables)
            bestIndex = findBest(entry_signal_selection, threshold, config.match_variables, assign_method)
            # fill -1 if no match was found
            if bestIndex == -1:
                if not apply_selection:
                    outputSig[fillIdx,:loIdxVars] = -1
                    outputSig[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                    outputSig[fillIdx,hiIdxVars:] = -1
                    if not signal_only:
                        outputBkg[fillIdx,:loIdxVars,0] = -1
                        #for i in range(bkg_combis):
                        outputBkg[fillIdx,loIdxVars:hiIdxVars,0] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                        outputBkg[fillIdx,hiIdxVars:,0] = -1
                        cutIdx.append(1)
            else:
                # randIndex = config.get_random_index(entry, bestIndex)
                outputSig[fillIdx,:-1] = entry.iloc[bestIndex].values
                outputSig[fillIdx, -1] = 1
                if not signal_only:
                    bkg_selection = config.def_background_selection
                    entry_background_selection = entry_selection(entry, bkg_selection)
                    #print entry_background_selection
                    #print entry_background_selection.shape[0]
                    fill = True
                    if entry_background_selection.shape[0] == 1:
                        if entry_background_selection.index[0] == bestIndex:
                            fill = False
                    if entry_background_selection.shape[0] == 0:
                        fill = False
                    if not fill:
                        if not apply_selection:
                            outputBkg[fillIdx,:loIdxVars,0] = -99
                            #for i in range(bkg_combis):
                            outputBkg[fillIdx,loIdxVars:hiIdxVars,0] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                            outputBkg[fillIdx,hiIdxVars:,0] = -99
                            cutIdx.append(1)
                    else:
                        randIndexList = get_random_index(entry_background_selection, bkg_combis, bestIndex)
                        for i in range(len(randIndexList)):
                            outputBkg[fillIdx,:-1,i] = entry.iloc[randIndexList[i]].values
                            outputBkg[fillIdx, -1,i] = 1
                        cutIdx.append(len(randIndexList))
                
            if fillIdx<=10:
                print("=== testevent ===")
                if not signal_only:
                    for name, sigval, bkgval in zip(
                        outputVariables, outputSig[fillIdx], outputBkg[fillIdx]):
                        print(name, sigval, bkgval)
                else:
                    for name, sigval in zip(outputVariables, outputSig[fillIdx]):
                        print(name, sigval)
                print("================="+"\n\n")

            fillIdx+=1

            #if fillIdx>=200:
            #	break


    # save information as h5 file
    #df = pd.DataFrame(outputData, columns = outputVariables)
    #df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    #del df            
    if apply_selection:
        print("events that fulfilled the selection {}/{}".format(fillIdx, len(outputSig)))
        outputSig = outputSig[:fillIdx]
        if not signal_only:
            outputBkg = outputBkg[:fillIdx]
            #print outputBkg


    # open output root file 
    sigpath = outpath
    if not signal_only:
        bkgpath = outpath.replace(".root","_bkg.root")

    with load.OutputFile(sigpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputSig:
            outfile.FillTree(event)

    if not signal_only:    
        with load.OutputFile(bkgpath) as outfile:
            # initialize branches
            outfile.SetBranches(outputVariables)
            # loop over events and fill tree
            for bkg_combinations,n in zip(outputBkg,cutIdx):
            	#print n
            	for j in range(n):
            		outfile.FillTree(bkg_combinations[:,j])

'''
def findBest(entry, threshold, match_variables):
    # print(list(entry.columns))
    # entry = entry.query("bbfromttbar_HadTopB_CSV>0.277")
    # entry = entry.query("bbfromttbar_LepTopB_CSV>0.277")
    # print(entry)
    # print(match_variables)
    for v in match_variables:
        entry = entry.query(v+"<="+threshold)

    bestIndex = -1
    if entry.shape[0]>=1:
        bestIndex =  entry.index.values[0]
    return bestIndex
'''
'''
#######################################################################
#  new findBest function
#######################################################################
def findBest(entry, threshold, match_variables):
    # idea: - save chi2 column of dataframe as new dataframe "entry"
    #       - for each line of the dataframe (aka each permutation of two jets of the event)
    #         check if chi2-value is the minimum of all the chi2-values
    #       - save line-index of the minimum chi2  =  bestIndex

    for chi2 in match_variables:
        chi2values = entry.loc[:,chi2]      # dataframe, only one column -> chi2-column
        print "chi2values:  ",chi2values

        chi2min = chi2values.min()
        print "chi2min:  ",chi2min
        chi2idxmin = chi2values.idxmin()
        print "chi2idxmin:  ",chi2idxmin

    bestIndex = -1
    if entry.shape[0] >= 1:
        bestIndex = chi2idxmin
    return bestIndex
'''


######################################################################

def def_assignment_method(assignment_method):

    #print assignment_method, type(assignment_method)

    assignment_method_name = ""
    if assignment_method is None:
        assignment_method_name = "threshold-based"
        print("\033[1;32mNo assignment method specified. Set jet-assignment method to threshold-based.\033[0m")
        return assignment_method_name
    elif assignment_method == "t":
        assignment_method_name = "threshold-based"
        print("\033[1;32mAssignment method for the jets is threshold-based.\033[0m")
        return assignment_method_name
    elif assignment_method == "c":
        assignment_method_name = "chi2"
        print("\033[1;32mAssignment method for the jets is chi^2-based.\033[0m")
        return assignment_method_name
    else:
        print("\033[1;31mNo valid assignment_method is given. Please enter c for chi^2 method, or t for threshold-based method, respectively.\033[0m")
        sys.exit()



#######################################################################
#  new findBest function, switch modi between chi2 and "usual" matching
#######################################################################
def findBest(entry, threshold, match_variables, assignment_method):
    # idea: - save chi2 column of dataframe as new dataframe "entry"
    #       - for each line of the dataframe (aka each permutation of two jets of the event)
    #         check if chi2-value is the minimum of all the chi2-values
    #       - save line-index of the minimum chi2  =  bestIndex

    if assignment_method == "threshold-based":
        for v in match_variables:
            entry = entry.query(v+"<="+threshold)

        bestIndex = -1
        if entry.shape[0]>=1:
            bestIndex =  entry.index.values[0]
        return bestIndex
    elif assignment_method == "chi2":
        for chi2 in [match_variables]:
            chi2values = entry.loc[:,chi2]    # dataframe, only one column -> chi2-column
            #print "chi2values:   ",chi2values
            chi2min = chi2values.min()
            #print "chi2min:   ",chi2min
            chi2idxmin = chi2values.idxmin()
            #print "chi2idxmin:   ",chi2idxmin

        bestIndex = -1
        if entry.shape[0] >= 1:
            bestIndex = chi2idxmin
        return bestIndex

########################################################################


def entry_selection(entry, selection):
    # print (sig_selection)
    for i in selection:
        entry = entry.query(i)
    return entry

# def signal_selection(entry, sig_selection):
#     # print (sig_selection)
#     for i in sig_selection:
#         entry = entry.query(i)
#     return entry

# def background_selection(entry, bkg_selection):
#     # print (bkg_selection)
#     for i in bkg_selection:
#         entry = entry.query(i)
#     return entry

'''
def get_random_index(df, bestIndex):
	# print(df)
	# print(df.shape[0])
	randomIndex = bestIndex
	while randomIndex==bestIndex:
		# randomIndex = np.random.randint(0,df.shape[0])
		randomIndex = df.index[np.random.randint(0,df.shape[0])]
	return randomIndex
'''


def get_random_index(df, bkg_combis, bestIndex):

    randomIndex = 0
    randomIndexList = []
    n_combis = bkg_combis    

    #maximum of bkg-combinations is maximum number of entries minus signal index (i.e. -1)
    if n_combis > df.shape[0]-1:
        n_combis = df.shape[0]-1
        #print '\nCaution!! Number of requested bkg-combis is bigger than the number of existing combinations!!\n'
        #print '\nSet number to maximum number n={}!!\n'.format(n_combis)

    # loop to generate a list of random indices (no double counting!)
    for i in range(n_combis):
        randomIndex = np.random.randint(0,df.shape[0])
        checkidx = True
        if randomIndex in randomIndexList:
            checkidx = False
        elif randomIndex == bestIndex:
        	checkidx = False

        while not checkidx:
            randomIndex = np.random.randint(0,df.shape[0])
            if randomIndex in randomIndexList:
                checkidx = False
            elif randomIndex == bestIndex:
            	checkidx = False
            else:
                checkidx = True

        #print type(df.index[randomIndex])
        randomIndexList.append(df.index[randomIndex])
        #print randomIndexList

    #print randomIndexList
    #print n_combis
    #print len(randomIndexList)
    return randomIndexList



###############################################################################
def setNumberDijetCombis(n_bkg_combis):
    '''
    Convert given n_bkg_combis string into integer.
    Check, if given string make sense.
    '''

    bkg_combis = 1
    if n_bkg_combis is None:
        bkg_combis = 1
        print("\033[1;31mNo number of di-jet combinations specified. Set number of considered random combinations to one.\033[0m")
        return bkg_combis

    while True:
	    try:
	        val = int(n_bkg_combis)
	        if int(n_bkg_combis) > 0:
	        	bkg_combis = val
	        	return bkg_combis
	        else:
	        	bkg_combis = 1
	        	print("\033[1;31mGiven number of di-jet combinations is negative or 0. Set number of considered combinations to 1.\033[0m")
	        	return bkg_combis

	        break;
	    except ValueError:
	    	print("No valid number of di-jet combinations given. Please enter an positive integer number.")
	    	sys.exit()
################################################################################




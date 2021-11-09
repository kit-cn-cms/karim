import numpy as np
from array import array
import os
import sys
from correctionlib import _core

filepath = os.path.abspath(__file__)
datapath = os.path.dirname(os.path.dirname(filepath))

import optparse
parser = optparse.OptionParser()
parser.add_option("-y", dest = "year", help ="era")
parser.add_option("--wp", dest = "wp", help = "WP")
(opts, args) = parser.parse_args()

sfDir = os.path.join(datapath, "UL_"+opts.year[2:])

btagSFjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "bjets.json"))
if opts.year == "2018":
    btagSF = btagSFjson["deepJet_106XUL18SF_wp"]
elif opts.year == "2017":
    btagSF = btagSFjson["deepJet_106XUL17SF_wp"]


sf_b = []
sf_b_up = []
sf_b_down = []
sf_c_up = []
sf_c_down = []
sf_b_mj = []
sf_b_up_mj = []
sf_b_down_mj = []
sf_c_up_mj = []
sf_c_down_mj = []
sf_l = []
sf_l_up = []
sf_l_down = []
wpDict = {"L": 0, "M": 1, "T": 2}
wp = wpDict[opts.wp]
pTvalues = np.arange(20., 1000., 1.)
for pT in pTvalues:
    sf_b.append(
        btagSF.evaluate("central", "comb", wp, 0, 0.1, pT))
    sf_b_up.append(
        btagSF.evaluate("up", "comb", wp, 0, 0.1, pT))
    sf_b_down.append(
        btagSF.evaluate("down", "comb", wp, 0, 0.1, pT))
    sf_c_up.append(
        btagSF.evaluate("up", "comb", wp, 1, 0.1, pT))
    sf_c_down.append(
        btagSF.evaluate("down", "comb", wp, 1, 0.1, pT))
    sf_b_mj.append(
        btagSF.evaluate("central", "mujets", wp, 0, 0.1, pT))
    sf_b_up_mj.append(
        btagSF.evaluate("up", "mujets", wp, 0, 0.1, pT))
    sf_b_down_mj.append(
        btagSF.evaluate("down", "mujets", wp, 0, 0.1, pT))
    sf_c_up_mj.append(
        btagSF.evaluate("up", "mujets", wp, 1, 0.1, pT))
    sf_c_down_mj.append(
        btagSF.evaluate("down", "mujets", wp, 1, 0.1, pT))
    sf_l.append(
        btagSF.evaluate("central", "incl", wp, 2, 0.1, pT))
    sf_l_up.append(
        btagSF.evaluate("up", "incl", wp, 2, 0.1, pT))
    sf_l_down.append(
        btagSF.evaluate("down", "incl", wp, 2, 0.1, pT))
    
import matplotlib.pyplot as plt

plt.title("WP: {} ({})".format(opts.wp, opts.year), loc = "right")
plt.title("CMS Simulation Preliminary", loc = "left")
plt.plot([0., 1000], [1., 1.], color = "black", linestyle = "-", markersize = 0)
#plt.plot(pTvalues, sf_b_mj, color = "blue",  label = "SF b (mujets)", linestyle = "-", linewidth = 2, markersize = 0)
#plt.fill_between(pTvalues, sf_b_down_mj, sf_b_up_mj, alpha = 0.4, color = "blue", label = "unc SFb (mujets)")
#plt.fill_between(pTvalues, sf_c_down_mj, sf_c_up_mj, alpha = 0.2, color = "blue", hatch = "x", label = "unc SFc (mujets)")
plt.plot(pTvalues, sf_l, color = "blue", label = "SF light", linestyle = "-", linewidth = 2, markersize = 0)
plt.fill_between(pTvalues, sf_l_down, sf_l_up, alpha = 0.2, color = "blue", label = "unc SFl (incl)")
plt.plot(pTvalues, sf_b, color = "red",  label = "SF b (comb)", linestyle = "-", linewidth = 2, markersize = 0)
plt.fill_between(pTvalues, sf_b_down, sf_b_up, alpha = 0.5, color = "red", label = "unc SFb (comb)")
plt.fill_between(pTvalues, sf_c_down, sf_c_up, alpha = 0.2, color = "red", hatch = "x", label = "unc SFc (comb)")
#plt.plot(pTvalues, sf_b, color = "blue", label = "SFb", linestyle = "-", linewidth = 2, markersize = 0)
plt.legend()
plt.grid(True)
plt.ylim((0.5,1.5))
plt.xlim((0.,1000.))
plt.ylabel("scale factor")
plt.xlabel("jet pT / GeV")
plt.savefig("btagSF_{}_{}.pdf".format(opts.year, opts.wp))



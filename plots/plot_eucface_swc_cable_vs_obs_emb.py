#!/usr/bin/env python

"""
Plot EucFACE soil moisture at observated dates

That's all folks.
"""

__author__ = "MU Mengyuan"
__version__ = "2019-10-06"
__changefrom__ = 'plot_eucface_swc_cable_vs_obs_obsved_dates-13-layer.py'

import os
import sys
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib import ticker
import datetime as dt
import netCDF4 as nc
from scipy.interpolate import griddata
import scipy.stats as stats
from sklearn.metrics import mean_squared_error
from plot_eucface_swc_cable_vs_obs_neo import *
from plot_eucface_swc_cable_vs_obs_tdr import *
from plot_eucface_swc_cable_vs_obs_obsved_dates import *

if __name__ == "__main__":

    layer = "31uni"
    '''
    cases = glob.glob(os.path.join("/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run_sen_31uni_2bch-mid-bot/outputs",\
                      "met_LAI_vrt_swilt-watr-ssat_SM_31uni_bch=4-2_fw-hie-exp_fix"))
    # bch-mid-bot 4. 2.
    '''

    cases = glob.glob(os.path.join("/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run_sen_31uni_5bch-top50-mid-bot/outputs",\
                      "met_LAI_vrt_swilt-watr-ssat_SM_31uni_bch=8-3-4_bch=6-3_fw-hie-exp_fix"))
    # 5bch-top50-mid-bot 8 3 4 6 3
    contour = False

    rings = ["amb"]#"R1","R2","R3","R4","R5","R6",,"ele"

    for case_name in cases:
        for ring in rings:
            fcable ="%s/EucFACE_%s_out.nc" % (case_name, ring)
            plot_profile(fcable, case_name, ring, contour, layer)
            plot_neo(fcable, case_name, ring, layer)
            plot_tdr(fcable, case_name, ring, layer)

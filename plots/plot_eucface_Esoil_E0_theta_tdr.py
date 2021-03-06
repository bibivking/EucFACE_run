#!/usr/bin/env python

"""
Plot EucFACE soil moisture at observated dates

That's all folks.
"""

__author__ = "MU Mengyuan"
__version__ = "2019-10-06"
__changefrom__ = 'plot_eucface_swc_cable_vs_obs.py'

import os
import sys
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

def main(fobs, fcable, case_name, hk, b, ring, layer, ep_type):

    tdr = pd.read_csv(fobs, usecols = ['Ring','Date','swc.tdr'])
    tdr['Date'] = pd.to_datetime(tdr['Date'],format="%Y-%m-%d",infer_datetime_format=False)
    tdr['Date'] = tdr['Date'] - pd.datetime(2011,12,31)
    tdr['Date'] = tdr['Date'].dt.days
    tdr = tdr.sort_values(by=['Date'])
    # divide neo into groups
    if ring == 'amb':
        subset = tdr[(tdr['Ring'].isin(['R2','R3','R6'])) & (tdr.Date > 366)]
    elif ring == 'ele':
        subset = tdr[(tdr['Ring'].isin(['R1','R4','R5'])) & (tdr.Date > 366)]
    else:
        subset = tdr[(tdr['Ring'].isin([ring]))  & (tdr.Date > 366)]

    subset = subset.groupby(by=["Date"]).mean()/100.
    subset['swc.tdr']   = subset['swc.tdr'].clip(lower=0.)
    subset['swc.tdr']   = subset['swc.tdr'].replace(0., float('nan'))
    subset['Esoil']     = np.zeros(len(subset))
    subset['Esoil'][1:] = (subset['swc.tdr'].values[1:] - subset['swc.tdr'].values[:-1])*(-500.)
    subset['Esoil']     = subset['Esoil'].clip(lower=0.)
    subset['Esoil']     = subset['Esoil'].replace(0., float('nan'))
    #subset = subset.xs('swc.tdr', axis=1, drop_level=True)
    print(subset)

# _________________________ CABLE ___________________________
    cable = nc.Dataset(fcable, 'r')
    Time  = nc.num2date(cable.variables['time'][:],cable.variables['time'].units)
    SoilMoist = pd.DataFrame(cable.variables['SoilMoist'][:,0,0,0], columns=['SoilMoist'])

    if layer == "6":
        SoilMoist['SoilMoist'] = cable.variables['SoilMoist'][:,0,0,0]
        '''
        SoilMoist['SoilMoist'] = ( cable.variables['SoilMoist'][:,0,0,0]*0.022 \
                                 + cable.variables['SoilMoist'][:,1,0,0]*0.058 \
                                 + cable.variables['SoilMoist'][:,2,0,0]*0.154 \
                                 + cable.variables['SoilMoist'][:,3,0,0]*(0.5-0.022-0.058-0.154) )/0.5
        '''
    elif layer == "13":
        SoilMoist['SoilMoist'] = ( cable.variables['SoilMoist'][:,0,0,0]*0.02 \
                                 + cable.variables['SoilMoist'][:,1,0,0]*0.05 \
                                 + cable.variables['SoilMoist'][:,2,0,0]*0.06 \
                                 + cable.variables['SoilMoist'][:,3,0,0]*0.13 \
                                 + cable.variables['SoilMoist'][:,3,0,0]*(0.5-0.02-0.05-0.06-0.13) )/0.5
    elif layer == "31uni":
        SoilMoist['SoilMoist'] = ( cable.variables['SoilMoist'][:,0,0,0]*0.15 \
                                 + cable.variables['SoilMoist'][:,1,0,0]*0.15 \
                                 + cable.variables['SoilMoist'][:,2,0,0]*0.15 \
                                 + cable.variables['SoilMoist'][:,3,0,0]*0.05 )/0.5
    elif layer == "31exp":
        SoilMoist['SoilMoist'] = ( cable.variables['SoilMoist'][:,0,0,0]*0.020440 \
                                 + cable.variables['SoilMoist'][:,1,0,0]*0.001759 \
                                 + cable.variables['SoilMoist'][:,2,0,0]*0.003957 \
                                 + cable.variables['SoilMoist'][:,3,0,0]*0.007035 \
                                 + cable.variables['SoilMoist'][:,4,0,0]*0.010993 \
                                 + cable.variables['SoilMoist'][:,5,0,0]*0.015829 \
                                 + cable.variables['SoilMoist'][:,6,0,0]*0.021546 \
                                 + cable.variables['SoilMoist'][:,7,0,0]*0.028141 \
                                 + cable.variables['SoilMoist'][:,8,0,0]*0.035616 \
                                 + cable.variables['SoilMoist'][:,9,0,0]*0.043971 \
                                 + cable.variables['SoilMoist'][:,10,0,0]*0.053205 \
                                 + cable.variables['SoilMoist'][:,11,0,0]*0.063318 \
                                 + cable.variables['SoilMoist'][:,12,0,0]*0.074311 \
                                 + cable.variables['SoilMoist'][:,13,0,0]*0.086183 \
                                 + cable.variables['SoilMoist'][:,14,0,0]*(0.5-0.466304))/0.5
    elif layer == "31para":
        SoilMoist['SoilMoist'] = ( cable.variables['SoilMoist'][:,0,0,0]*0.020440 \
                                 + cable.variables['SoilMoist'][:,1,0,0]*0.001759 \
                                 + cable.variables['SoilMoist'][:,2,0,0]*0.003957 \
                                 + cable.variables['SoilMoist'][:,3,0,0]*0.007035 \
                                 + cable.variables['SoilMoist'][:,4,0,0]*0.010993 \
                                 + cable.variables['SoilMoist'][:,5,0,0]*0.015829 \
                                 + cable.variables['SoilMoist'][:,6,0,0]*(0.5-0.420714))/0.5

    SoilMoist['dates'] = Time
    SoilMoist = SoilMoist.set_index('dates')
    SoilMoist = SoilMoist.resample("D").agg('mean')
    SoilMoist.index = SoilMoist.index - pd.datetime(2011,12,31)
    SoilMoist.index = SoilMoist.index.days
    SoilMoist = SoilMoist.sort_values(by=['dates'])

    ESoil = pd.DataFrame(cable.variables['ESoil'][:,0,0],columns=['ESoil'])
    ESoil = ESoil*1800.
    ESoil['dates'] = Time
    ESoil = ESoil.set_index('dates')
    ESoil = ESoil.resample("D").agg('sum')
    ESoil.index = ESoil.index - pd.datetime(2011,12,31)
    ESoil.index = ESoil.index.days
    print(ESoil)

    if ep_type == 'PotEvap':
        Ep = pd.DataFrame(cable.variables['PotEvap'][:,0,0],columns=['Ep'])
        Ep = Ep*1800.
        Ep['dates'] = Time
        Ep = Ep.set_index('dates')
        Ep = Ep.resample("D").agg('sum')
        Ep.index = Ep.index - pd.datetime(2011,12,31)
        Ep.index = Ep.index.days
        #print(Ep)
    elif ep_type == 'Rnet-G':
        Ep = pd.DataFrame(cable.variables['Rnet'][:,0,0]-cable.variables['Qg'][:,0,0],columns=['Ep'])
        Ep['dates'] = Time
        Ep = Ep.set_index('dates')
        Ep = Ep.resample("D").agg('mean')
        Ep.index = Ep.index - pd.datetime(2011,12,31)
        Ep.index = Ep.index.days
        print(Ep*86400/2454000)


    Rainf = pd.DataFrame(cable.variables['Rainf'][:,0,0],columns=['Rainf'])
    Rainf = Rainf*1800.
    Rainf['dates'] = Time
    Rainf = Rainf.set_index('dates')
    Rainf = Rainf.resample("D").agg('sum')
    Rainf.index = Rainf.index - pd.datetime(2011,12,31)
    Rainf.index = Rainf.index.days

    rain          = Rainf['Rainf'].loc[Rainf.index.isin(subset.index)]
    esoil         = ESoil['ESoil'].loc[ESoil.index.isin(subset.index)]
    ep            = Ep['Ep'].loc[Ep.index.isin(subset.index)]
    soilmoist     = SoilMoist['SoilMoist'].loc[SoilMoist.index.isin(subset.index)]
    esoil_tdr     = subset['Esoil'].loc[subset.index.isin(SoilMoist.index)]
    soilmoist_tdr = subset['swc.tdr'].loc[subset.index.isin(SoilMoist.index)]

    # exclude tdr soilmoisture < 0 or tdr esoil < 0
    mask      = np.any([np.isnan(soilmoist_tdr), np.isnan(esoil_tdr)],axis=0)
    print(mask)
    rain      = rain[mask == False]
    esoil     = esoil[mask == False]
    ep        = ep[mask == False]
    soilmoist = soilmoist[mask == False]
    esoil_tdr = esoil_tdr[mask == False]
    soilmoist_tdr = soilmoist_tdr[mask == False]
    print("any(rain>0.)")
    print(np.any(rain>0.))

    # exclude rainday and the after two days of rain
    mask      = np.ones((len(rain)), dtype=bool)
    print(rain)
    if rain.values[0] > 0. :
        mask[0] = False
    if rain.values[0] > 0. or rain.values[1] > 0.:
        mask[1] = False
    for i in np.arange(2,len(rain)):
        if rain.values[i] > 0. or rain.values[i-1] > 0. or rain.values[i-2] > 0. :
            mask[i] = False
    rain      = rain[mask == True]
    esoil     = esoil[mask == True]
    ep        = ep[mask == True]
    soilmoist = soilmoist[mask == True]
    esoil_tdr = esoil_tdr[mask == True]
    soilmoist_tdr = soilmoist_tdr[mask == True]
    print("any(rain>0.)")
    print(np.any(rain>0.))

    # exclude the days Rnet < 0.
    ep   = ep.clip(lower=0.)
    ep   = ep.replace(0., float('nan'))
    mask = np.isnan(ep)

    esoil     = esoil[mask == False]
    ep        = ep[mask == False]
    soilmoist = soilmoist[mask == False]
    esoil_tdr = esoil_tdr[mask == False]
    soilmoist_tdr = soilmoist_tdr[mask == False]

    if ep_type == 'PotEvap':
        rate      = esoil/ep
        rate_tdr  = esoil_tdr/ep
    elif ep_type == 'Rnet-G':
        rate      = esoil/(ep*86400/2454000)
        rate_tdr  = esoil_tdr/(ep*86400/2454000)



    print("-------------------------------------------------")
    print(np.any(esoil < 0.))
    print(np.any(ep < 0.))
    print(np.any(soilmoist < 0.))
    print(np.any(esoil_tdr < 0.))
    print(np.any(soilmoist_tdr < 0.))

    print(esoil)
    print(ep)
    print(soilmoist)
    print(esoil_tdr)
    print(soilmoist_tdr)
    print(rate)
    print(rate_tdr)
    print("-------------------------------------------------")


# ____________________ Plot obs _______________________
    fig = plt.figure(figsize=[15,10])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color'] = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor'] = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    ax1 = fig.add_subplot(111)

    ax1.scatter(soilmoist, rate, s=2, marker='o', c='orange')
    ax1.scatter(soilmoist_tdr, rate_tdr, s=2, marker='o', c='green')
    ax1.set_xlim(0.,1.)
    ax1.set_ylim(-0.1,1.)

    fig.savefig("EucFACE_Esoil_E0_theta_%s_%s_hk=%s_b=%s_%s.png" \
                % (ep_type, case_name, hk, b, ring),\
                 bbox_inches='tight', pad_inches=0.1)
if __name__ == "__main__":

    layer =  "6"

    cases = ["ctl_met_LAI_vrt_SM_swilt-watr_hyds-bch"]
    # 6
    # ["met_LAI_sand","met_LAI_clay","met_LAI_silt"\
    #  "ctl_met_LAI", "ctl_met_LAI_vrt", "ctl_met_LAI_vrt_SM",\
    #  "ctl_met_LAI_vrt_SM_swilt-watr", "ctl_met_LAI_vrt_SM_swilt-watr_Hvrd",\
    #  "ctl_met_LAI_vrt_SM_swilt-watr_Or-Off","default-met_only"]
    # 31para
    #["ctl_met_LAI_vrt_SM_swilt-watr_31para"]
    # 31exp
    #["ctl_met_LAI_vrt_SM_swilt-watr_31exp"]
    # 31uni
    #  ["ctl_met_LAI_vrt_SM_31uni","ctl_met_LAI_vrt_SM_swilt-watr_31uni",\
    #   "ctl_met_LAI_vrt_SM_swilt-watr_31uni_root-uni",\
    #   "ctl_met_LAI_vrt_SM_swilt-watr_31uni_root-log10"]

    ep_type = 'Rnet-G'
    #"PotEvap"
    rings = ["amb"]#["R1","R2","R3","R4","R5","R6","amb","ele"]
    hyds_value = [1e3,1e2,1e1,1.,1e-1,1e-2,1e-3,1e-4,1e-5,1e-6]
    bch_value  = np.arange(1.,11.,1.)
    for hk in hyds_value:
        for b in bch_value:
            for case_name in cases:
                for ring in rings:
                    fobs = "/srv/ccrc/data25/z5218916/cable/EucFACE/Eucface_data/swc_average_above_the_depth/swc_tdr.csv"
                    fcable ="/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/%s/EucFACE_hyds=%s_bch=%s_%s_out.nc" \
                            % (case_name,str(hk),str(b), ring)
                    main(fobs, fcable, case_name, str(hk),str(b), ring, layer,ep_type)

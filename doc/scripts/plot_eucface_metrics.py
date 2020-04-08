#!/usr/bin/env python

"""
Calculate metrics for every simulations,

Include functions :
    calc_metrics
    plotting
    annual_value
    plot_r_rmse

"""

__author__ = "MU Mengyuan"
__version__ = "2020-03-25"

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
from scipy.interpolate import interp1d
import scipy.stats as stats
from sklearn.metrics import mean_squared_error
from plot_eucface_get_var import *

def calc_metrics(fcable, case_name, ring, layer):

    plt.rc('font', family='Helvetica')

    subs_Esoil = read_obs_esoil(ring)
    print(len(subs_Esoil))
    subs_Trans = read_obs_trans(ring)
    print(len(subs_Trans))
    subs_tdr   = read_obs_swc_tdr(ring)
    print(len(subs_tdr))
    subs_neo   = read_obs_neo_top_mid_bot(ring)
    print(len(subs_neo))
    subs_cable = read_ET_SM_top_mid_bot(fcable, ring, layer)
    print(len(subs_cable))

    # unify dates
    Esoil_obs   = subs_Esoil['obs'].loc[subs_Esoil.index.isin(subs_cable.index)]
    Esoil_cable = subs_cable["ESoil"].loc[subs_cable.index.isin(subs_Esoil.index)]
    Trans_obs   = subs_Trans['obs'].loc[subs_Trans.index.isin(subs_cable.index)]
    Trans_cable = subs_cable["TVeg"].loc[subs_cable.index.isin(subs_Trans.index)]

    #mask           = np.any([np.isnan(Esoil_obs), ],axis=0)

    Esoil_cable    = Esoil_cable[np.isnan(Esoil_obs) == False]
    Trans_cable    = Trans_cable[np.isnan(Trans_obs) == False]
    Esoil_obs      = Esoil_obs[np.isnan(Esoil_obs) == False]
    Trans_obs      = Trans_obs[np.isnan(Trans_obs) == False]

    print(np.any(np.isnan(Esoil_obs)))
    print(np.any(np.isnan(Trans_obs)))
    print(np.any(np.isnan(Esoil_cable)))
    print(np.any(np.isnan(Trans_cable)))

    SM_25cm_obs   = subs_tdr["obs"].loc[subs_tdr.index.isin(subs_cable.index)]
    SM_25cm_cable = subs_cable["SM_25cm"].loc[subs_cable.index.isin(subs_tdr.index)]

    mask           = np.isnan(SM_25cm_obs)
    SM_25cm_obs     = SM_25cm_obs[mask == False]
    SM_25cm_cable   = SM_25cm_cable[mask == False]

    SM_15m_obs  = subs_neo["SM_15m"].loc[subs_neo.index.isin(subs_cable.index)]
    SM_15m_cable= subs_cable["SM_15m"].loc[subs_cable.index.isin(subs_neo.index)]

    mask           = np.isnan(SM_15m_obs)
    SM_15m_obs     = SM_15m_obs[mask == False]
    SM_15m_cable   = SM_15m_cable[mask == False]

    SM_all_obs  = subs_neo["SM_all"].loc[subs_neo.index.isin(subs_cable.index)]
    SM_all_cable= subs_cable["SM_all"].loc[subs_cable.index.isin(subs_neo.index)]

    mask           = np.isnan(SM_all_obs)
    SM_all_obs     = SM_all_obs[mask == False]
    SM_all_cable   = SM_all_cable[mask == False]

    SM_top_obs  = subs_neo["SM_top"].loc[subs_neo.index.isin(subs_cable.index)]
    SM_top_cable= subs_cable["SM_top"].loc[subs_cable.index.isin(subs_neo.index)]

    mask           = np.isnan(SM_top_obs)
    SM_top_obs     = SM_top_obs[mask == False]
    SM_top_cable   = SM_top_cable[mask == False]

    SM_mid_obs  = subs_neo["SM_mid"].loc[subs_neo.index.isin(subs_cable.index)]
    SM_mid_cable= subs_cable["SM_mid"].loc[subs_cable.index.isin(subs_neo.index)]

    mask           = np.isnan(SM_mid_obs)
    SM_mid_obs     = SM_mid_obs[mask == False]
    SM_mid_cable   = SM_mid_cable[mask == False]

    SM_bot_obs  = subs_neo["SM_bot"].loc[subs_neo.index.isin(subs_cable.index)]
    SM_bot_cable= subs_cable["SM_bot"].loc[subs_cable.index.isin(subs_neo.index)]

    mask          = np.isnan(SM_bot_obs)
    SM_bot_obs    = SM_bot_obs[mask == False]
    SM_bot_cable  = SM_bot_cable[mask == False]

    WA_all_obs    = subs_neo["WA_all"].loc[subs_neo.index.isin(subs_cable.index)]
    WA_all_cable  = subs_cable["WA_all"].loc[subs_cable.index.isin(subs_neo.index)]

    mask          = np.isnan(WA_all_obs)
    WA_all_obs    = WA_all_obs[mask == False]
    WA_all_cable  = WA_all_cable[mask == False]

    Esoil_r   = stats.pearsonr(Esoil_obs, Esoil_cable)[0]
    Esoil_MSE = mean_squared_error(Esoil_obs, Esoil_cable)

    Trans_r   = stats.pearsonr(Trans_obs, Trans_cable)[0]
    Trans_MSE = mean_squared_error(Trans_obs, Trans_cable)

    #Esoil_Trans_r   = stats.pearsonr(Esoil_obs/Trans_obs,Esoil_cable/Trans_cable)[0]
    #Esoil_Trans_MSE = mean_squared_error(Esoil_obs/Trans_obs,Esoil_cable/Trans_cable)
    SM_25cm_r       = stats.pearsonr(SM_25cm_obs.values, SM_25cm_cable.values)[0]
    SM_25cm_MSE     = mean_squared_error(SM_25cm_obs, SM_25cm_cable)
    SM_15m_r        = stats.pearsonr(SM_15m_obs, SM_15m_cable)[0]
    SM_15m_MSE      = mean_squared_error(SM_15m_obs, SM_15m_cable)
    SM_all_r        = stats.pearsonr(SM_all_obs, SM_all_cable)[0]
    SM_all_MSE      = mean_squared_error(SM_all_obs, SM_all_cable)
    SM_top_r        = stats.pearsonr(SM_top_obs, SM_top_cable)[0]
    SM_top_MSE      = mean_squared_error(SM_top_obs, SM_top_cable)
    SM_mid_r        = stats.pearsonr(SM_mid_obs, SM_mid_cable)[0]
    SM_mid_MSE      = mean_squared_error(SM_mid_obs, SM_mid_cable)
    SM_bot_r        = stats.pearsonr(SM_bot_obs, SM_bot_cable)[0]
    SM_bot_MSE      = mean_squared_error(SM_bot_obs, SM_bot_cable)
    WA_all_r        = stats.pearsonr(WA_all_obs, WA_all_cable)[0]
    WA_all_MSE      = mean_squared_error(WA_all_obs, WA_all_cable)
    # Esoil_Trans_r,  Esoil_Trans_MSE,
    return Esoil_r,   Trans_r,      SM_25cm_r,   SM_15m_r,   SM_all_r,   SM_bot_r,   WA_all_r, \
           Esoil_MSE, Trans_MSE,  SM_25cm_MSE, SM_15m_MSE, SM_all_MSE, SM_bot_MSE, WA_all_MSE;

def plotting(metrics,ring):

    fig = plt.figure(figsize=[15,10])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    #plt.rc('font', family='Helvetica')
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

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    width = 1.
    im1 = ax1.imshow(metrics[:,0:8], interpolation='nearest')
    fig.colorbar(im1, ax=ax1)

    im2 = ax2.imshow(metrics[:,8:15], interpolation='nearest')
    fig.colorbar(im2, ax=ax2)


    fig.savefig("EucFACE_metrics_%s.png" % (ring), bbox_inches='tight', pad_inches=0.1)

def annual_value(fcable, case_name, ring, layer):

    """
    calculate annual water budget items, energy flux and soil status
    """

    if layer == "6":
        zse = [ 0.022, 0.058, 0.154, 0.409, 1.085, 2.872 ]
    elif layer == "31uni":
        zse = [ 0.15,  0.15,  0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  \
                0.15,  0.15,  0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  \
                0.15,  0.15,  0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  \
                0.15 ]
    total_year = 7

    cable = nc.Dataset(fcable, 'r')

    step_2_sec = 30.*60.
    umol_2_gC  = 12.0107 * 1.0E-6

    df              = pd.DataFrame(cable.variables['Rainf'][:,0,0]*step_2_sec, columns=['Rainf']) # 'Rainfall+snowfall'
    df['Evap']      = cable.variables['Evap'][:,0,0]*step_2_sec   # 'Total evaporation'
    df['TVeg']      = cable.variables['TVeg'][:,0,0]*step_2_sec   # 'Vegetation transpiration'
    df['ESoil']     = cable.variables['ESoil'][:,0,0]*step_2_sec  # 'evaporation from soil'
    df['ECanop']    = cable.variables['ECanop'][:,0,0]*step_2_sec # 'Wet canopy evaporation'
    df['Qs']        = cable.variables['Qs'][:,0,0]*step_2_sec     # 'Surface runoff'
    df['Qsb']       = cable.variables['Qsb'][:,0,0]*step_2_sec    # 'Subsurface runoff'
    df['Qrecharge'] = cable.variables['Qrecharge'][:,0,0]*step_2_sec
    df['GPP']       = cable.variables['GPP'][:,0,0]*step_2_sec*umol_2_gC

    status              = pd.DataFrame(cable.variables['Qle'][:,0,0] , columns=['Qle'])   # 'Surface latent heat flux'
    status['Qh']        = cable.variables['Qh'][:,0,0]    # 'Surface sensible heat flux'
    status['Qg']        = cable.variables['Qg'][:,0,0]    # 'Surface ground heat flux'

    if layer == "6":

        status['SoilMoist_top']  = (  cable.variables['SoilMoist'][:,0,0,0]*0.022 \
                                    + cable.variables['SoilMoist'][:,1,0,0]*0.058\
                                    + cable.variables['SoilMoist'][:,2,0,0]*0.154 \
                                    + cable.variables['SoilMoist'][:,3,0,0]*(0.3-0.022-0.058-0.154) )/0.3
        status['SoilMoist_mid']  = (  cable.variables['SoilMoist'][:,3,0,0]*0.343 \
                                    + cable.variables['SoilMoist'][:,4,0,0]*(1.2-0.343) )/1.2
        status['SoilMoist_bot']  = (  cable.variables['SoilMoist'][:,4,0,0]*(1.085-(1.2-0.343)) \
                                    + cable.variables['SoilMoist'][:,5,0,0]*2.872)/(4.6-1.5)

        status['SoilMoist_all'] = cable.variables['SoilMoist'][:,0,0,0]*zse[0]
        for i in np.arange(1,6):
            status['SoilMoist_all'] = status['SoilMoist_all'] + cable.variables['SoilMoist'][:,i,0,0]*zse[i]
        status['SoilMoist_all'] = status['SoilMoist_all']/sum(zse)

        status['SoilTemp_top']  = (   cable.variables['SoilTemp'][:,0,0,0]*0.022 \
                                    + cable.variables['SoilTemp'][:,1,0,0]*0.058\
                                    + cable.variables['SoilTemp'][:,2,0,0]*0.154 \
                                    + cable.variables['SoilTemp'][:,3,0,0]*(0.3-0.022-0.058-0.154) )/0.3\
                                  - 273.15
        status['SoilTemp_mid']  = (   cable.variables['SoilTemp'][:,3,0,0]*0.343 \
                                    + cable.variables['SoilTemp'][:,4,0,0]*(1.2-0.343) )/1.2\
                                  - 273.15
        status['SoilTemp_bot']  = (   cable.variables['SoilTemp'][:,4,0,0]*(1.085-(1.2-0.343)) \
                                    + cable.variables['SoilTemp'][:,5,0,0]*2.872)/(4.6-1.5) \
                                  - 273.15
        status['SoilTemp_all']  = cable.variables['SoilTemp'][:,0,0,0]*zse[0]
        for i in np.arange(1,6):
            status['SoilTemp_all']  = status['SoilTemp_all']  + cable.variables['SoilTemp'][:,i,0,0]*zse[i]
        status['SoilTemp_all']  = status['SoilTemp_all']/sum(zse) - 273.15

    elif layer == "31uni":

        status['SoilMoist_top']     = ( cable.variables['SoilMoist'][:,0,0,0]*0.15 \
                                      + cable.variables['SoilMoist'][:,1,0,0]*0.15 )/0.3

        status['SoilMoist_mid']     = cable.variables['SoilMoist'][:,2,0,0]*0.15
        for i in np.arange(3,10):
            status['SoilMoist_mid'] = status['SoilMoist_mid'] + cable.variables['SoilMoist'][:,i,0,0]*0.15
        status['SoilMoist_mid']     = status['SoilMoist_mid'] /(1.5-0.3)

        status['SoilMoist_bot']     = cable.variables['SoilMoist'][:,10,0,0]*0.15
        for i in np.arange(11,30):
            status['SoilMoist_bot'] = status['SoilMoist_bot'] + cable.variables['SoilMoist'][:,i,0,0]*0.15
        status['SoilMoist_bot']     = (status['SoilMoist_bot'] + cable.variables['SoilMoist'][:,30,0,0]*0.1)/(4.6-1.5)

        status['SoilMoist_all']     = cable.variables['SoilMoist'][:,30,0,0]*0.1
        for i in np.arange(0,30):
            status['SoilMoist_all'] = status['SoilMoist_all'] + cable.variables['SoilMoist'][:,i,0,0]*zse[i]
        status['SoilMoist_all']     = status['SoilMoist_all']/4.6

        status['SoilTemp_top']      = ( cable.variables['SoilTemp'][:,0,0,0]*0.15 \
                                      + cable.variables['SoilTemp'][:,1,0,0]*0.15 )/0.3 \
                                      - 273.15
        status['SoilTemp_mid']  = cable.variables['SoilTemp'][:,2,0,0]*0.15
        for i in np.arange(3,10):
            status['SoilTemp_mid']  = status['SoilTemp_mid']  + cable.variables['SoilTemp'][:,i,0,0]*0.15
        status['SoilTemp_mid']    = status['SoilTemp_mid'] /(1.5-0.3) - 273.15

        status['SoilTemp_bot']   = cable.variables['SoilTemp'][:,10,0,0]*0.15
        for i in np.arange(11,30):
            status['SoilTemp_bot']   = status['SoilTemp_bot'] + cable.variables['SoilTemp'][:,i,0,0]*0.15
        status['SoilTemp_bot']   = (status['SoilTemp_bot'] + cable.variables['SoilTemp'][:,30,0,0]*0.1)/(4.6-1.5)\
                                    - 273.15

        status['SoilTemp_all']  = cable.variables['SoilTemp'][:,30,0,0]*0.1
        for i in np.arange(0,30):
            status['SoilTemp_all']  = status['SoilTemp_all']  + cable.variables['SoilTemp'][:,i,0,0]*zse[i]
        status['SoilTemp_all']     = status['SoilTemp_all']/4.6 - 273.15


    df['dates']     = nc.num2date(cable.variables['time'][:], cable.variables['time'].units)
    df              = df.set_index('dates')
    df              = df.resample("Y").agg('sum')

    status['dates']   = nc.num2date(cable.variables['time'][:], cable.variables['time'].units)
    status            = status.set_index('dates')
    status            = status.resample("Y").agg('mean')

    # multi-year average
    df     = df.iloc[:,:].mean(axis=0)
    status = status.iloc[:,:].mean(axis=0)

    annual = np.zeros(20)
    for i in np.arange(20):
        if i <= 8:
            annual[i] = df.iloc[i]
        else:
            annual[i] = status.iloc[i-9]

    return annual;

def plot_r_rmse(metrics,ring):

    fig = plt.figure(figsize=[15,15])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 8
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

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    labels = ["Esoil", "Trans", "Esoil/Trans", "SM_25cm", "SM_top", "SM_mid", "SM_bot", "WA_all"]

    x = np.linspace(2.,7.,11) #np.linspace(-10.,5.,31)
    for i in np.arange(0,8):
        labels[i]
        ax1.plot(x, metrics[:,i],label=labels[i] )
    for i in np.arange(11,15):#(8,15):
        labels[i-8]
        ax2.plot(x, metrics[:,i],label=labels[i-8])
    ax1.legend()
    ax1.set_title("r")
    ax2.legend()
    ax2.set_title("MSE")

    fig.savefig("EucFACE_metrics_%s.png" % (ring), bbox_inches='tight', pad_inches=0.1)
    np.savetxt("EucFACE_metrics_%s.csv" % (ring), metrics, delimiter=",")

def stat_obs(fcables, ring):

    '''
    statistics of ET observation
    '''

    # ===== Obs   =====
    subs_Esoil = read_obs_esoil(ring)
    subs_Trans = read_obs_trans(ring)

    print("=== observation ===")
    print(len(subs_Esoil[subs_Esoil.index < 732]['obs']))
    print(len(subs_Trans[subs_Trans.index < 732]['obs']))
    print(np.nanmean( subs_Esoil[subs_Esoil.index < 732]['obs'].values) )
    print(np.nanmean( subs_Trans[subs_Trans.index < 732]['obs'].values) )

    # ===== CABLE =====
    for fcable in fcables:
        TVeg       = read_cable_var(fcable, 'TVeg')
        ESoil      = read_cable_var(fcable, 'ESoil')

        print("=== %s ===" % fcable.split("/")[-2])
        print(np.nanmean( ESoil['cable'][:365].values) )
        print(np.nanmean( TVeg['cable'][:365].values) )


if __name__ == "__main__":

    cases_6 = [
            "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_6",
            "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_6_litter"
              ]
    cases_31= [
            "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_31uni_litter",
            "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_hydsx1_x10_31uni_litter",
            "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_hydsx1_x10_31uni_litter_Hvrd",
            "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_hydsx1_x10_31uni_litter_hie-exp"
              ]

    rings  = ["amb"]#["R1","R2","R3","R4","R5","R6","amb","ele"]
    metrics= np.zeros((len(cases_6)+len(cases_31),14))
    annual = np.zeros((len(cases_6)+len(cases_31),20))
    for ring in rings:
        layer =  "6"
        for i,case_name in enumerate(cases_6):
            print(i)
            print(case_name)
            fcable ="%s/EucFACE_%s_out.nc" % (case_name, ring)
            metrics[i,:] = calc_metrics(fcable, case_name, ring, layer)
            annual[i,:]  = annual_value(fcable, case_name, ring, layer)
        print("i = %s" % str(i))
        j = i
        layer =  "31uni"
        for i,case_name in enumerate(cases_31):
            print(case_name)
            fcable ="%s/EucFACE_%s_out.nc" % (case_name, ring)
            metrics[i+j+1,:] = calc_metrics(fcable, case_name, ring, layer)
            annual[i+j+1,:]  = annual_value(fcable, case_name, ring, layer)
        #print(metrics)
        plotting(metrics,ring)
        #metrics.to_csv("EucFACE_amb_%slayers_%s_gw_on_or_on.csv" %(layers, case_name))
        np.savetxt("./csv/EucFACE_metrics_%s.csv" % (ring), metrics, delimiter=",")
        np.savetxt("./csv/EucFACE_annual_%s.csv" % (ring), annual, delimiter=",")


    '''
    ring  = "amb"
    #sen_values = np.linspace(-10.,5.,31)
    sen_values = ["2","25","3","35","4","45","5","55","6","65","7"]
    metrics= np.zeros((len(sen_values),16))
    annual = np.zeros((len(sen_values),19))

    layer =  "31uni"
    for i,sen_value in enumerate(sen_values):
        #fcable = "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run_sen_31uni_bch-hyds-30cm/outputs/met_LAI_vrt_swilt-watr-ssat_SM_31uni_hyds^0-%s_litter/EucFACE_amb_out.nc" % str(sen_value).replace('.', '')
        fcable = "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run_sen_31uni_bch-hyds-30cm/outputs/met_LAI_vrt_swilt-watr-ssat_SM_31uni_hyds^0-%s_litter/EucFACE_amb_out.nc" % sen_value

        print(fcable)
        metrics[i,:] = calc_metrics(fcable, sen_value, ring, layer)
        annual[i,:]  = annual_value(fcable, sen_value, ring, layer)
    plot_r_rmse(metrics,ring)
    np.savetxt("EucFACE_annual_%s.csv" % (ring), annual, delimiter=",")
    '''

    '''
    for statistics of ET observation
    '''
    # fcables = [ "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_6/EucFACE_amb_out.nc",
    #             "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_6_litter/EucFACE_amb_out.nc",
    #             "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_31uni_litter/EucFACE_amb_out.nc",
    #             "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_hydsx1_x10_31uni_litter/EucFACE_amb_out.nc",
    #             "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_hydsx1_x10_31uni_litter_Hvrd/EucFACE_amb_out.nc",
    #             "/srv/ccrc/data25/z5218916/cable/EucFACE/EucFACE_run/outputs/met_LAI_vrt_swilt-watr-ssat_SM_hydsx1_x10_31uni_litter_hie-exp/EucFACE_amb_out.nc"]
    #
    # stat_obs(fcables, 'amb')

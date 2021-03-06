#!/usr/bin/env python

"""
draw drought plots

Include functions :

    plot_EF_SM
    plot_Fwsoil_Trans
    plot_Rain_Fwsoil_Trans
    plot_Fwsoil_boxplot
    plot_fwsoil_SM
    plot_fwsoil_boxplot_SM
    plot_Fwsoil_days_bar
    plot_Rain_Fwsoil_Trans_Esoil_EF_SM

"""
__author__ = "MU Mengyuan"
__version__ = "2020-03-19"

import os
import sys
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
import datetime as dt
import netCDF4 as nc
import scipy.stats as stats
import seaborn as sns
from matplotlib import cm
from matplotlib import ticker
from scipy.interpolate import griddata
from sklearn.metrics import mean_squared_error
from plot_eucface_get_var import *

def plot_EF_SM(fstd, fhvrd, fexp, fwatpot, ring, layer):

    lh1 = read_cable_var(fstd, "Qle")
    lh2 = read_cable_var(fhvrd, "Qle")
    lh3 = read_cable_var(fexp, "Qle")
    lh4 = read_cable_var(fwatpot, "Qle")

    r1 = read_cable_var(fstd, "Qh") + read_cable_var(fstd, "Qle")
    r2 = read_cable_var(fhvrd, "Qh") + read_cable_var(fhvrd, "Qle")
    r3 = read_cable_var(fexp, "Qh") + read_cable_var(fexp, "Qle")
    r4 = read_cable_var(fwatpot, "Qh") + read_cable_var(fwatpot, "Qle")

    r1["cable"] = np.where(r1["cable"].values < 1., lh1['cable'].values, r1["cable"].values)
    r2["cable"] = np.where(r2["cable"].values < 1., lh2['cable'].values, r2["cable"].values)
    r3["cable"] = np.where(r3["cable"].values < 1., lh3['cable'].values, r3["cable"].values)
    r4["cable"] = np.where(r4["cable"].values < 1., lh4['cable'].values, r4["cable"].values)

    EF1 = pd.DataFrame(lh1['cable'].values/r1['cable'].values, columns=['EF'])
    EF1["Date"] = lh1.index
    EF1 = EF1.set_index('Date')
    EF1["EF"]= np.where(EF1["EF"].values> 10.0, 10., EF1["EF"].values)

    EF2 = pd.DataFrame(lh2['cable'].values/r2['cable'].values, columns=['EF'])
    EF2["Date"] = lh2.index
    EF2 = EF2.set_index('Date')
    EF2["EF"]= np.where(EF2["EF"].values> 10.0, 10., EF2["EF"].values)

    EF3 = pd.DataFrame(lh3['cable'].values/r3['cable'].values, columns=['EF'])
    EF3["Date"] = lh3.index
    EF3 = EF3.set_index('Date')
    EF3["EF"]= np.where(EF3["EF"].values> 10.0, 10., EF3["EF"].values)

    EF4 = pd.DataFrame(lh4['cable'].values/r4['cable'].values, columns=['EF'])
    EF4["Date"] = lh4.index
    EF4 = EF4.set_index('Date')
    EF4["EF"]= np.where(EF4["EF"].values> 10.0, 10., EF4["EF"].values)

    sm1 = read_SM_top_mid_bot(fstd, ring, layer)
    #print(sm1)
    sm2 = read_SM_top_mid_bot(fhvrd, ring, layer)
    sm3 = read_SM_top_mid_bot(fexp, ring, layer)
    sm4 = read_SM_top_mid_bot(fwatpot, ring, "6")

    fig = plt.figure(figsize=[15,17])

    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 12
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

    ax1  = fig.add_subplot(511)
    ax2  = fig.add_subplot(512)
    ax3  = fig.add_subplot(513)
    ax4  = fig.add_subplot(514)
    ax5  = fig.add_subplot(515)

    day_start = 1828
    x    = lh1.index[lh1.index >= day_start]
    width= 1.
    print(EF1['EF'])
    ax1.plot(x, EF1['EF'][lh1.index >= day_start],   c="orange", lw=1.0, ls="-", label="β-std")#.rolling(window=30).mean()
    ax1.plot(x, EF2['EF'][lh1.index >= day_start],   c="blue", lw=1.0, ls="-", label="β-hvrd")
    ax1.plot(x, EF3['EF'][lh1.index >= day_start],   c="green", lw=1.0, ls="-", label="β-exp")
    ax1.plot(x, EF4['EF'][lh1.index >= day_start],   c="red", lw=1.0, ls="-", label="Ctl-β-std")
    print("-------------------")
    print(sm1['SM_top'])
    print(lh1)
    ax2.plot(x, sm1['SM_top'][lh1.index >= day_start],   c="orange", lw=1.0, ls="-", label="β-std")#.rolling(window=30).mean()
    ax2.plot(x, sm2['SM_top'][lh1.index >= day_start],   c="blue", lw=1.0, ls="-", label="β-hvrd")
    ax2.plot(x, sm3['SM_top'][lh1.index >= day_start],   c="green", lw=1.0, ls="-", label="β-exp")
    ax2.plot(x, sm4['SM_top'][lh1.index >= day_start],   c="red", lw=1.0, ls="-", label="Ctl-β-std")
    #
    # ax3.plot(x, sm1['SM_mid'][lh1.index >= day_start],   c="orange", lw=1.0, ls="-", label="β-std")#.rolling(window=30).mean()
    # ax3.plot(x, sm2['SM_mid'][lh1.index >= day_start],   c="blue", lw=1.0, ls="-", label="β-hvrd")
    # ax3.plot(x, sm3['SM_mid'][lh1.index >= day_start],   c="green", lw=1.0, ls="-", label="β-exp")
    # ax3.plot(x, sm4['SM_mid'][lh1.index >= day_start],   c="red", lw=1.0, ls="-", label="Ctl-β-std")
    #
    # ax4.plot(x, sm1['SM_bot'][lh1.index >= day_start],   c="orange", lw=1.0, ls="-", label="β-std")#.rolling(window=30).mean()
    # ax4.plot(x, sm2['SM_bot'][lh1.index >= day_start],   c="blue", lw=1.0, ls="-", label="β-hvrd")
    # ax4.plot(x, sm3['SM_bot'][lh1.index >= day_start],   c="green", lw=1.0, ls="-", label="β-exp")
    # ax4.plot(x, sm4['SM_bot'][lh1.index >= day_start],   c="red", lw=1.0, ls="-", label="Ctl-β-std")

    ax5.plot(x, sm1['SM_all'][lh1.index >= day_start],   c="orange", lw=1.0, ls="-", label="β-std")#.rolling(window=30).mean()
    ax5.plot(x, sm2['SM_all'][lh1.index >= day_start],   c="blue", lw=1.0, ls="-", label="β-hvrd")
    ax5.plot(x, sm3['SM_all'][lh1.index >= day_start],   c="green", lw=1.0, ls="-", label="β-exp")
    ax5.plot(x, sm4['SM_all'][lh1.index >= day_start],   c="red", lw=1.0, ls="-", label="Ctl-β-std")

    cleaner_dates = ["2013","2014","2015","2016","2017","2018","2019"]
    xtickslocs    = [367,732,1097,1462,1828,2193,2558]

    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set(xticks=xtickslocs, xticklabels=cleaner_dates) ####
    ax1.yaxis.tick_left()
    ax1.yaxis.set_label_position("left")
    ax1.set_ylabel("Evaporative Fraction (-)")
    ax1.axis('tight')
    #ax1.set_ylim(0.,120.)
    #ax1.set_xlim(367,2739)#,1098)
    ax1.set_xlim(day_start,2739)

    plt.setp(ax2.get_xticklabels(), visible=False)
    ax2.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax2.set_ylabel("Top soil moisture  (m$3$ m$-3$)")
    ax2.axis('tight')
    ax2.set_ylim(0.,0.4)
    #ax2.set_xlim(367,2739)#,1098)
    ax2.set_xlim(day_start,2739)

    plt.setp(ax3.get_xticklabels(), visible=False)
    ax3.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax3.set_ylabel("Middle soil moisture  (m$3$ m$-3$)")
    ax3.axis('tight')
    ax3.set_ylim(0.,0.4)
    #ax3.set_xlim(367,2739)#,1098)
    ax3.set_xlim(day_start,2739)

    plt.setp(ax4.get_xticklabels(), visible=False)
    ax4.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax4.set_ylabel("Bottom soil moisture  (m$3$ m$-3$)")
    ax4.axis('tight')
    ax4.set_ylim(0.,0.4)
    #ax4.set_xlim(367,2739)#,1098)
    ax4.set_xlim(day_start,2739)

    plt.setp(ax5.get_xticklabels(), visible=True)
    ax5.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax5.set_ylabel("soil moisture  (m$3$ m$-3$)")
    ax5.axis('tight')
    ax5.set_ylim(0.,0.4)
    #ax5.set_xlim(367,2739)#,1098)
    ax5.set_xlim(day_start,2739)
    ax5.legend()

    fig.savefig("./plots/EucFACE_EF_SM" , bbox_inches='tight', pad_inches=0.1)

def plot_Fwsoil_Trans(fcables, ring, case_labels):

    subs_Trans = read_obs_trans(ring)

    fig = plt.figure(figsize=[10,8])

    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 14
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

    ax1  = fig.add_subplot(211)
    ax2  = fig.add_subplot(212)
    #day_start = 1828
    cleaner_dates = ["2013","2014","2015","2016","2017","2018","2019"]
    xtickslocs    = [367,732,1097,1462,1828,2193,2558]

    colors = ["pink","orange","blue","green"]
    case_sum = len(case_labels)

    ax2.plot(subs_Trans.index, subs_Trans['obs'].rolling(window=10).mean(),  c='red', label="Obs")#,edgecolors="red", s = 4., marker='o')#.rolling(window=30).sum()
    #scatter
    for case_num in np.arange(case_sum):
        fw    = read_cable_var(fcables[case_num], "Fwsoil")
        Trans = read_cable_var(fcables[case_num], "TVeg")

        x    = fw.index

        ax1.plot(x, fw['cable'].rolling(window=10).mean(),   c=colors[case_num], lw=1.0, ls="-", label=case_labels[case_num])#.rolling(window=30).mean()
        ax2.plot(x, Trans['cable'].rolling(window=10).mean(), c=colors[case_num], lw=1.0, ls="-", label=case_labels[case_num])

    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax1.set_ylabel("β")
    ax1.axis('tight')
    ax1.set_ylim(0.,1.1)
    ax1.set_xlim(367,978)
    #ax1.legend()

    plt.setp(ax2.get_xticklabels(), visible=True)
    ax2.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax2.set_ylabel("Transpiration (mm d$^{-1}$)")
    ax2.axis('tight')
    ax2.set_ylim(0.,3.)
    ax2.set_xlim(367,978)#(367,1098)
    ax2.legend()
    fig.savefig("./plots/EucFACE_Fwsoil_Trans-Martin" , bbox_inches='tight', pad_inches=0.1)

def plot_Rain_Fwsoil_Trans(fstd, fhvrd, fexp, fwatpot, ring):

    Rain= read_cable_var(fstd, "Rainf")

    fw1 = read_cable_var(fstd, "Fwsoil")
    fw2 = read_cable_var(fhvrd, "Fwsoil")
    fw3 = read_cable_var(fexp, "Fwsoil")
    fw4 = read_cable_var(fwatpot, "Fwsoil")

    t1 = read_cable_var(fstd, "TVeg")
    t2 = read_cable_var(fhvrd, "TVeg")
    t3 = read_cable_var(fexp, "TVeg")
    t4 = read_cable_var(fwatpot, "TVeg")

    fig = plt.figure(figsize=[15,10])

    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 12
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

    ax1  = fig.add_subplot(311)
    ax2  = fig.add_subplot(312)
    ax3  = fig.add_subplot(313)

    day_start = 1828
    x    = Rain.index[Rain.index >= day_start]
    width= 1.

    ax1.plot(x, Rain['cable'][Rain.index >= day_start].rolling(window=30).sum(), width, color='royalblue', label='Obs') # bar   .cumsum()

    ax2.plot(x, fw1['cable'][fw1.index >= day_start].rolling(window=30).mean(),   c="orange", lw=1.0, ls="-", label="β-std")#.rolling(window=30).mean()
    ax2.plot(x, fw2['cable'][fw2.index >= day_start].rolling(window=30).mean(),   c="blue", lw=1.0, ls="-", label="β-hvrd")
    ax2.plot(x, fw3['cable'][fw3.index >= day_start].rolling(window=30).mean(),   c="green", lw=1.0, ls="-", label="β-exp")
    ax2.plot(x, fw4['cable'][fw4.index >= day_start].rolling(window=30).mean(),   c="red", lw=1.0, ls="-", label="β-watpot")

    ax3.plot(x, t1['cable'][t1.index >= day_start].rolling(window=30).sum(),   c="orange", lw=1.0, ls="-", label="β-std")
    ax3.plot(x, t2['cable'][t2.index >= day_start].rolling(window=30).sum(),   c="blue", lw=1.0, ls="-", label="β-hvrd")
    ax3.plot(x, t3['cable'][t3.index >= day_start].rolling(window=30).sum(),   c="green", lw=1.0, ls="-", label="β-exp")
    ax3.plot(x, t4['cable'][t4.index >= day_start].rolling(window=30).sum(),   c="red", lw=1.0, ls="-", label="β-watpot")

    cleaner_dates = ["2013","2014","2015","2016","2017","2018","2019"]
    xtickslocs    = [367,732,1097,1462,1828,2193,2558]

    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set(xticks=xtickslocs, xticklabels=cleaner_dates) ####
    ax1.yaxis.tick_left()
    ax1.yaxis.set_label_position("left")
    ax1.set_ylabel("Rainfall (mm mon$^{-1}$)")
    ax1.axis('tight')
    #ax1.set_ylim(0.,120.)
    #ax1.set_xlim(367,2739)#,1098)
    ax1.set_xlim(day_start,2739)

    plt.setp(ax2.get_xticklabels(), visible=False)
    ax2.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax2.set_ylabel("β")
    ax2.axis('tight')
    ax2.set_ylim(0.,1.1)
    #ax2.set_xlim(367,2739)#,1098)
    ax2.set_xlim(day_start,2739)
    ax2.legend()

    plt.setp(ax3.get_xticklabels(), visible=True)
    ax3.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax3.set_ylabel("Transpiration ($mm$ $mon^{-1}$)")
    ax3.axis('tight')
    #ax3.set_ylim(0.,2.5)
    #ax3.set_ylim(0.,1000.)
    #ax3.set_xlim(367,2739)#,1098)
    ax3.set_xlim(day_start,2739)
    ax3.legend()
    fig.savefig("./plots/EucFACE_Rain_Fwsoil_Trans" , bbox_inches='tight', pad_inches=0.1)

def plot_Fwsoil_boxplot(fcables, case_labels):

    """
    box-whisker of fwsoil
    """

    day_start_drought = 1828 # first day of 2017
    day_start_all     = 367  # first day of 2013
    day_end           = 2558 # first day of 2019

    day_drought  = day_end - day_start_drought + 1
    day_all      = day_end - day_start_all + 1
    case_sum     = len(fcables)
    fw           = pd.DataFrame(np.zeros((day_drought+day_all)*case_sum),columns=['fwsoil'])
    fw['year']   = [''] * ((day_drought+day_all)*case_sum)
    fw['exp']    = [''] * ((day_drought+day_all)*case_sum)

    s = 0

    for case_num in np.arange(case_sum):

        cable = nc.Dataset(fcables[case_num], 'r')
        Time  = nc.num2date(cable.variables['time'][:],cable.variables['time'].units)

        Fwsoil          = pd.DataFrame(cable.variables['Fwsoil'][:,0,0],columns=['fwsoil'])
        Fwsoil['dates'] = Time
        Fwsoil          = Fwsoil.set_index('dates')
        Fwsoil          = Fwsoil.resample("D").agg('mean')
        Fwsoil.index    = Fwsoil.index - pd.datetime(2011,12,31)
        Fwsoil.index    = Fwsoil.index.days

        e  = s+day_drought
        print(Fwsoil[np.all([Fwsoil.index >= day_start_drought, Fwsoil.index <=day_end],axis=0)]['fwsoil'].values)
        print(fw['year'].iloc[s:e] )
        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_drought, Fwsoil.index <=day_end],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['drought'] * day_drought
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_drought
        s  = e
        e  = s+day_all
        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_all, Fwsoil.index <=day_end],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['all'] * day_all
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_all
        s  =  e

    print(fw)

    fig = plt.figure(figsize=[12,9])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 14
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

    ax  = fig.add_subplot(111)

    #ax.boxplot(Qle, widths = 0.4, showfliers=False)# c=colors[case_num], label=case_labels[case_num])

    # define outlier properties
    flierprops = dict(marker='o', markersize=3, markerfacecolor="black")
    ax = sns.boxplot(x="exp", y="fwsoil", hue="year", data=fw, palette="Set2",
                     order=case_labels, flierprops=flierprops, width=0.6,
                     hue_order=['drought','all'])

    ax.set_ylabel("β")
    ax.set_xlabel("simulations")
    ax.axis('tight')
    #ax1.set_xlim(date[0],date[-1])
    ax.set_ylim(0.,1.1)
    #ax.axhline(y=np.median(fw[np.all([fw.year=='drought',fw.exp=='Ctl'],axis=0)]['fwsoil'].values) , ls="--")
    ax.axhline(y=np.mean(fw[np.all([fw.year=='drought',fw.exp=='Ctl'],axis=0)]['fwsoil'].values) , ls="--")

    plt.legend()#loc="upper right"

    fig.savefig("./plots/EucFACE_Fwsoil_boxplot" , bbox_inches='tight', pad_inches=0.1)

def plot_fwsoil_SM( fcables, layers, case_labels, ring):

    fig = plt.figure(figsize=[12,9])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 14
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

    ax = fig.add_subplot(111)
    colors = cm.tab20(np.linspace(0,1,len(case_labels)))
    #rainbow nipy_spectral Set1
    for case_num in np.arange(len(fcables)):
        SM  = read_cable_SM(fcables[case_num], layers[case_num])
        fw  = read_cable_var(fcables[case_num], "Fwsoil")
        print(SM)
        if layers[case_num] == "6":
            sm =(  SM.iloc[:,0]*0.022 + SM.iloc[:,1]*0.058 \
                 + SM.iloc[:,2]*0.154 + SM.iloc[:,3]*0.409 \
                 + SM.iloc[:,4]*(1.5-0.022-0.058-0.154-0.409) )/1.5
        elif layers[case_num] == "31uni":
            sm = SM.iloc[:,0:10].mean(axis = 1)

        ax.scatter(sm, fw,  s=3., marker='o', c=colors[case_num],label=case_labels[case_num])

    ax.set_xlim(0.1,0.45)
    ax.set_ylim(0.,1.1)
    ax.set_ylabel("β (-)")
    ax.set_xlabel("volumetric water content in top 1.5 m (m3/m3)")
    ax.legend(numpoints=1, loc='lower right')

    fig.savefig("./plots/EucFACE_fwsoil_vs_SM_%s.png" % ring , bbox_inches='tight', pad_inches=0.1)

def plot_Rain_Fwsoil_Trans_Esoil_EF_SM( fcables, case_labels, layers, ring):

    # ======================= Plot setting ============================
    fig = plt.figure(figsize=[13,17.5])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.1)

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']  = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')

    # choose colormap
    colors = cm.Set2(np.arange(0,len(case_labels)))
    #colors = cm.Set3(np.arange(2,len(case_labels)+2)) # Set3
    #colors = ['tomato','silver','lime','turquoise','fuchsia','teal','green','pink']

    ax1  = fig.add_subplot(511)
    ax2  = fig.add_subplot(512)
    ax3  = fig.add_subplot(513)
    ax4  = fig.add_subplot(514)
    ax5  = fig.add_subplot(515)

    #cleaner_dates = ["2013","2014","2015","2016","2017","2018","2019","2020"]
    #xtickslocs    = [367,      732,  1097,  1462,  1828,  2193,  2558,  2923]

    #cleaner_dates = ["Jul 2017","Jan 2018","Jul 2018", "Jan 2019", "Jul 2019"]
    #xtickslocs    = [      2009,      2193,      2374,       2558,       2739]
    #day_start     = 367 #2009
    #day_end       = 2923 #2739

    cleaner_dates = ["Oct 2017","Jan 2018","Apr 2018", "Jul 2018", "Oct 2018"]
    xtickslocs    = [      2101,      2193,      2283,       2374,       2466]
    day_start = 2101 # 2017-10-1
    day_end   = 2467 # 2018-10-1

    day_start_smooth = day_start - 30
    case_sum = len(fcables)

    for case_num in np.arange(case_sum):

        Rain  = read_cable_var(fcables[case_num], "Rainf")
        fw    = read_cable_var(fcables[case_num], "Fwsoil")
        Trans = read_cable_var(fcables[case_num], "TVeg")
        Esoil = read_cable_var(fcables[case_num], "ESoil")
        Qle   = read_cable_var(fcables[case_num], "Qle")
        Rnet  = read_cable_var(fcables[case_num], "Qh") + \
                read_cable_var(fcables[case_num], "Qle")

        Rnet = np.where(Rnet["cable"].values < 5., Qle['cable'].values, Rnet["cable"].values)

        EF   = pd.DataFrame(Qle['cable'].values/Rnet, columns=['EF'])
        EF["Date"] = Qle.index
        EF   = EF.set_index('Date')
        #mean_val = np.where(np.any([EF1["EF"].values> 1.0, EF1["EF"].values< 0.0], axis=0), float('nan'), EF1["EF"].values)
        #EF["EF"]= np.where(EF["EF"].values> 10.0, 10., EF["EF"].values)

        sm = read_SM_top_mid_bot(fcables[case_num], ring, layers[case_num])

        x        = fw.index[fw.index >= day_start]
        x_smooth = fw.index[fw.index >= day_start_smooth]

        ax1.plot(x_smooth, sm['SM_15m'][Qle.index >= day_start_smooth].rolling(window=30).mean(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)#.rolling(window=30).mean()
                # .rolling(window=30).mean()
        ax2.plot(x_smooth, fw['cable'][fw.index >= day_start_smooth].rolling(window=30).mean(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num])#.rolling(window=30).mean()
        ax3.plot(x_smooth, Trans['cable'][Trans.index >= day_start_smooth].rolling(window=30).sum(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)
        ax4.plot(x_smooth, Esoil['cable'][Esoil.index >= day_start_smooth].rolling(window=30).sum(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)
        ax5.plot(x_smooth, EF['EF'][Qle.index >= day_start_smooth].rolling(window=30).mean(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)#.rolling(window=30).mean()

    ax6  = ax1.twinx()
    ax6.set_ylabel('P (mm d$^{-1}$)')
    ax6.bar(x_smooth, -Rain['cable'][Rain.index >= day_start_smooth].values,  1.,
            color='gray', alpha = 0.5, label='Rainfall') # 'royalblue'
    ax6.set_ylim(-60.,0)
    y_ticks      = [-60,-50,-40,-30,-20,-10,0.]
    y_ticklabels = ['60','50','40','30','20','10','0']
    ax6.set_yticks(y_ticks)
    ax6.set_yticklabels(y_ticklabels)
    ax6.get_xaxis().set_visible(False)

    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set(xticks=xtickslocs, xticklabels=cleaner_dates) ####
    ax1.axis('tight')
    ax1.set_ylim(0.,0.55)
    ax1.set_xlim(day_start,day_end)
    ax1.set_ylabel('VWC in 1.5m (m$^{3}$ m$^{-3}$)')
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax2.get_xticklabels(), visible=False)
    ax2.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax2.set_ylabel("β")
    ax2.axis('tight')
    ax2.set_ylim(0.,1.18)
    #ax2.set_xlim(367,2739)#,1098)
    ax2.legend(numpoints=1, loc='best', frameon=False) #'upper right'
    ax2.set_xlim(day_start,day_end)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax3.get_xticklabels(), visible=False)
    ax3.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax3.set_ylabel("T (mm mon$^{-1}$)")
    ax3.axis('tight')
    ax3.set_ylim(0.,70.)
    ax3.set_xlim(day_start,day_end)
    ax3.text(0.02, 0.95, '(c)', transform=ax3.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax4.get_xticklabels(), visible=False)
    ax4.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax4.set_ylabel("Es (mm mon$^{-1}$)")
    ax4.axis('tight')
    ax4.set_ylim(0.,40.)
    ax4.set_xlim(day_start,day_end)
    ax4.text(0.02, 0.95, '(d)', transform=ax4.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax5.get_xticklabels(), visible=True)
    ax5.set(xticks=xtickslocs, xticklabels=cleaner_dates) ####
    #ax5.yaxis.tick_left()
    #ax5.yaxis.set_label_position("left")
    ax5.set_ylabel("EF")
    ax5.axis('tight')
    ax5.set_ylim(0.,2.)
    ax5.set_xlim(day_start,day_end)
    ax5.text(0.02, 0.95, '(e)', transform=ax5.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    fig.savefig("./plots/EucFACE_Rain_Fwsoil_Trans_EF_SM" , bbox_inches='tight', pad_inches=0.1)

def plot_fwsoil_boxplot_SM( fcables, case_labels, layers, ring):

    """
    box-whisker of fwsoil + fwsoil vs SM
    """

    # ======================= Plot setting ============================
    fig = plt.figure(figsize=[12,4])
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(wspace=0.12)

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14
    plt.rcParams["legend.markerscale"] = 3.0

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']  = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')

    # choose colormap
    #colors = cm.tab20(np.linspace(0,1,len(case_labels))) # Set3
    #colors = cm.Set3(np.arange(2,len(case_labels)+2)) # Set3
    colors = cm.Set2(np.arange(0,len(case_labels)))
    #colors = ['tomato','silver','lime','turquoise','fuchsia','teal','green','pink']


    #print(colors)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # ========================= box-whisker of fwsoil============================
    #day_start_drought = 2193 # first day of 2018
    #day_end_drought   = 2558 # first day of 2019
    day_start_drought = 2101 # 2017-10-1
    day_end_drought   = 2466 # 2018-10-1

    day_start_all     = 367  # first day of 2013
    day_end           = 2923 # first day of 2020

    day_drought  = day_end_drought - day_start_drought + 1
    day_all      = day_end - day_start_all + 1
    case_sum     = len(fcables)
    fw           = pd.DataFrame(np.zeros((day_drought+day_all)*case_sum),columns=['fwsoil'])
    fw['year']   = [''] * ((day_drought+day_all)*case_sum)
    fw['exp']    = [''] * ((day_drought+day_all)*case_sum)

    s = 0

    for case_num in np.arange(case_sum):

        cable = nc.Dataset(fcables[case_num], 'r')
        Time  = nc.num2date(cable.variables['time'][:],cable.variables['time'].units)

        Fwsoil          = pd.DataFrame(cable.variables['Fwsoil'][:,0,0],columns=['fwsoil'])
        Fwsoil['dates'] = Time
        Fwsoil          = Fwsoil.set_index('dates')
        Fwsoil          = Fwsoil.resample("D").agg('mean')
        Fwsoil.index    = Fwsoil.index - pd.datetime(2011,12,31)
        Fwsoil.index    = Fwsoil.index.days

        e  = s+day_drought

        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_drought,
                                 Fwsoil.index <=day_end_drought],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['drought'] * day_drought
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_drought
        s  = e
        e  = s+day_all
        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_all,
                                 Fwsoil.index <=day_end],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['all'] * day_all
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_all
        s  =  e

    # define outlier properties
    #flierprops = dict(marker='o', markersize=3, markerfacecolor="black") flierprops=flierprops,

    # boxplot
    #ax1.boxplot(Qle, widths = 0.4, showfliers=False)# c=colors[case_num], label=case_labels[case_num])

    # seaborn
    #sns.color_palette("Set2", 8)
    sns.boxplot(x="exp", y="fwsoil", hue="year", data=fw, palette="Set2",
                order=case_labels,  width=0.7, hue_order=['drought','all'],
                ax=ax1, showfliers=False, color=almost_black)

    ax1.set_ylabel("β")
    ax1.set_xlabel("")
    ax1.axis('tight')
    #ax1.set_xlim(date[0],date[-1])
    ax1.set_ylim(0.,1.05)
    #ax1.axhline(y=np.median(fw[np.all([fw.year=='drought',fw.exp=='Ctl'],axis=0)]['fwsoil'].values),
    #            c=almost_black, ls="--")
    ax1.axhline(y=np.mean(fw[np.all([fw.year=='drought',fw.exp=='Ctl'],axis=0)]['fwsoil'].values),
                c=almost_black, ls="--")
    ax1.legend(loc='best', frameon=False)
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=14, verticalalignment='top', bbox=props)
    #plt.legend(loc='best', frameon=False)#loc="upper right"


    # ============================= boxplot ===================================

    for case_num in np.arange(len(fcables)):
        SM  = read_cable_SM(fcables[case_num], layers[case_num])
        fw  = read_cable_var(fcables[case_num], "Fwsoil")
        print(SM)
        if layers[case_num] == "6":
            sm =(  SM.iloc[:,0]*0.022 + SM.iloc[:,1]*0.058 \
                 + SM.iloc[:,2]*0.154 + SM.iloc[:,3]*0.409 \
                 + SM.iloc[:,4]*(1.5-0.022-0.058-0.154-0.409) )/1.5
        elif layers[case_num] == "31uni":
            sm = SM.iloc[:,0:10].mean(axis = 1)

        ax2.scatter(sm, fw,  s=1., marker='o', alpha=1., c=colors[case_num],label=case_labels[case_num])

    ax2.set_xlim(0.08,0.405)
    ax2.set_ylim(0.0,1.05)
    #ax2.set_ylabel("β")
    ax2.set_xlabel("VWC in 1.5m (m$^{3}$ m$^{-3}$)")
    ax2.legend(numpoints=1, loc='lower right', frameon=False)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top', bbox=props)
    #plt.setp(ax2.get_yticklabels(), visible=False)

    fig.savefig("./plots/EucFACE_Fwsoil_boxplot_SM" , bbox_inches='tight', pad_inches=0.1)

def plot_Fwsoil_days_bar(fcables, case_labels):
    """
    Calculate from beta figure two metrics: #1 over only drought periods and
    #2 over whole length of run. Calculate number of days where the average
    beta is below 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1. Then plot a simple
    bar chart with the results for each experiment.
    """

    # ======================= Plot setting ============================
    fig = plt.figure(figsize=[12,4])
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(wspace=0.12)

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']  = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')

    # choose colormap
    #colors = cm.tab20(np.linspace(0,1,len(case_labels))) # Set3
    #colors = cm.Set3(np.arange(2,len(case_labels)+2)) # Set3
    colors = cm.Set2(np.arange(0,len(case_labels)))
    #colors = ['tomato','silver','lime','turquoise','fuchsia','teal','green','pink']

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    case_sum   = len(fcables)
    intval     = np.arange(0.8,0.0,-0.1)
    intval_sum = len(intval)

    # start from 2013-1-1
    #day_start_drought  = 1826 # first day of 2018
    #day_end_drought    = 2191 # first day of 2019
    day_start_drought  = 2101 - 367 # 2017-10-1
    day_end_drought    = 2466 - 367 # 2018-10-1
    tot_year_drought   = 1 #6

    day_start          = 0    # first day of 2013
    day_end            = 2556 # first day of 2020
    tot_year           = 7

    offset             = 0.5
    fw_days            = np.zeros([case_sum,intval_sum])
    fw_days_drought    = np.zeros([case_sum,intval_sum])

    for case_num in np.arange(case_sum):
        print(fcables[case_num])
        fw = read_cable_var(fcables[case_num], "Fwsoil")

        for intval_num in np.arange(intval_sum):
            tmp1 = np.where(fw.values[day_start:day_end] <= intval[intval_num], 1., 0.)
            fw_days[case_num, intval_num] = sum(tmp1)/tot_year

            tmp2 = np.where(fw.values[day_start_drought:day_end_drought] <= intval[intval_num], 1., 0.)
            fw_days_drought[case_num, intval_num] = sum(tmp2)/tot_year_drought

    x      = np.arange(intval_sum)
    width  = 1./(case_sum+2.)

    for case_num in np.arange(case_sum):
        offset = (case_num+1+0.5)*width
        ax1.bar(x + offset, fw_days_drought[case_num,:], width, color=colors[case_num], label=case_labels[case_num])
        ax2.bar(x + offset, fw_days[case_num,:], width, color=colors[case_num], label=case_labels[case_num])

    cleaner_dates = [ "0.8","0.7","0.6","0.5","0.4","0.3","0.2","0.1"]
    xtickslocs    = [   0.5,  1.5,  2.5,  3.5,  4.5,  5.5,  6.5,  7.5]


    #plt.setp(ax.get_xticklabels(), visible=True)
    ax1.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    #ax1.set_title("2018 Drought")
    ax1.set_ylabel("days per year")
    ax1.set_xlabel("β")
    ax1.axis('tight')
    ax1.set_ylim(0,360)
    ax1.set_xlim(-0.1,7)
    ax1.legend( loc='best', frameon=False) #'upper right'
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    ax2.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax2.set_xlabel("β")
    ax2.axis('tight')
    ax2.set_ylim(0,360)
    ax2.set_xlim(-0.1,7)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    fig.savefig("./plots/EucFACE_Fwsoil_days" , bbox_inches='tight', pad_inches=0.1)

def plot_Rain_Fwsoil_Trans_Esoil_SH_SM( fcables, case_labels, layers, ring):

    # ======================= Plot setting ============================
    fig = plt.figure(figsize=[13,17.5])
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.1)

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']  = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')

    # choose colormap
    colors = cm.tab20(np.arange(0,len(case_labels)))
    #colors = cm.Set3(np.arange(2,len(case_labels)+2)) # Set3
    #colors = ['tomato','silver','lime','turquoise','fuchsia','teal','green','pink']

    ax1  = fig.add_subplot(511)
    ax2  = fig.add_subplot(512)
    ax3  = fig.add_subplot(513)
    ax4  = fig.add_subplot(514)
    ax5  = fig.add_subplot(515)

    #cleaner_dates = ["2013","2014","2015","2016","2017","2018","2019","2020"]
    #xtickslocs    = [367,      732,  1097,  1462,  1828,  2193,  2558,  2923]

    #cleaner_dates = ["Jul 2017","Jan 2018","Jul 2018", "Jan 2019", "Jul 2019"]
    #xtickslocs    = [      2009,      2193,      2374,       2558,       2739]
    #day_start     = 367 #2009
    #day_end       = 2923 #2739

    cleaner_dates = ["Oct 2017","Jan 2018","Apr 2018", "Jul 2018", "Oct 2018"]
    xtickslocs    = [      2101,      2193,      2283,       2374,       2466]
    day_start = 2101 # 2017-10-1
    day_end   = 2467 # 2018-10-1

    day_start_smooth = day_start - 30
    case_sum = len(fcables)


    # read obs soil moisture at top 1.5 m
    subs_neo   = read_obs_neo_top_mid_bot(ring)

    for case_num in np.arange(case_sum):

        Rain  = read_cable_var(fcables[case_num], "Rainf")
        fw    = read_cable_var(fcables[case_num], "Fwsoil")
        Trans = read_cable_var(fcables[case_num], "TVeg")
        Esoil = read_cable_var(fcables[case_num], "ESoil")
        Qle   = read_cable_var(fcables[case_num], "Qle")
        Qh    = read_cable_var(fcables[case_num], "Qh")

        sm = read_SM_top_mid_bot(fcables[case_num], ring, layers[case_num])

        x        = fw.index[fw.index >= day_start]
        x_smooth = fw.index[fw.index >= day_start_smooth]

        if case_num == 0:
            print(subs_neo[subs_neo.index >= day_start].index)
            print(subs_neo["SM_15m"][subs_neo.index >= day_start])
            ax1.scatter(subs_neo[subs_neo.index >= day_start].index, subs_neo["SM_15m"][subs_neo.index >= day_start],
                        marker='o', c='',edgecolors='blue', s = 6., label="Obs")

        ax1.plot(x_smooth, sm['SM_15m'][Qle.index >= day_start_smooth].rolling(window=30).mean(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)#.rolling(window=30).mean()
                # .rolling(window=30).mean()
        ax2.plot(x_smooth, Trans['cable'][Trans.index >= day_start_smooth].rolling(window=30).sum(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)
        ax3.plot(x_smooth, fw['cable'][fw.index >= day_start_smooth].rolling(window=30).mean(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num])#.rolling(window=30).mean()
        ax4.plot(x_smooth, Esoil['cable'][Esoil.index >= day_start_smooth].rolling(window=30).sum(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)
        ax5.plot(x_smooth, Qh['cable'][Qle.index >= day_start_smooth].rolling(window=30).mean(),
                c=colors[case_num], lw=1.5, ls="-", label=case_labels[case_num], alpha=1.)#.rolling(window=30).mean()

    ax6  = ax1.twinx()
    ax6.set_ylabel('$P$ (mm d$^{-1}$)')
    ax6.bar(x_smooth, -Rain['cable'][Rain.index >= day_start_smooth].values,  1.,
            color='gray', alpha = 0.5, label='Rainfall') # 'royalblue'
    ax6.set_ylim(-60.,0)
    y_ticks      = [-60,-50,-40,-30,-20,-10,0.]
    y_ticklabels = ['60','50','40','30','20','10','0']
    ax6.set_yticks(y_ticks)
    ax6.set_yticklabels(y_ticklabels)
    ax6.get_xaxis().set_visible(False)

    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set(xticks=xtickslocs, xticklabels=cleaner_dates) ####
    ax1.axis('tight')
    ax1.set_ylim(0.05,0.35)
    ax1.set_xlim(day_start,day_end)
    ax1.set_ylabel('$θ$$_{1.5m}$ (m$^{3}$ m$^{-3}$)')
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax2.get_xticklabels(), visible=False)
    ax2.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax2.set_ylabel("$E_{tr}$ (mm mon$^{-1}$)")
    ax2.axis('tight')
    ax2.legend(numpoints=1, ncol=3, loc='best', frameon=False) #'upper right'
    ax2.set_ylim(0.,70.)
    ax2.set_xlim(day_start,day_end)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax3.get_xticklabels(), visible=False)
    ax3.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax3.set_ylabel("$β$")
    ax3.axis('tight')
    ax3.set_ylim(0.,1.18)
    #ax3.set_xlim(367,2739)#,1098)
    ax3.set_xlim(day_start,day_end)
    ax3.text(0.02, 0.95, '(c)', transform=ax3.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax4.get_xticklabels(), visible=False)
    ax4.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax4.set_ylabel("$E_{s}$ (mm mon$^{-1}$)")
    ax4.axis('tight')
    ax4.set_ylim(0.,50.)
    ax4.set_xlim(day_start,day_end)
    ax4.text(0.02, 0.95, '(d)', transform=ax4.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    plt.setp(ax5.get_xticklabels(), visible=True)
    ax5.set(xticks=xtickslocs, xticklabels=cleaner_dates) ####
    #ax5.yaxis.tick_left()
    #ax5.yaxis.set_label_position("left")
    ax5.set_ylabel("$Q_{H}$ (W m$^{-2}$)")
    ax5.axis('tight')
    ax5.set_ylim(-20.,100.)
    ax5.set_xlim(day_start,day_end)
    ax5.text(0.02, 0.95, '(e)', transform=ax5.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    fig.savefig("./plots/EucFACE_Rain_Fwsoil_Trans_SH_SM" , bbox_inches='tight', pad_inches=0.1)

def plot_fwsoil_boxplot_SM_days_bar( fcables, case_labels, layers, ring):

    """
    (a) box-whisker of fwsoil
    (b) fwsoil vs SM
    (c) Calculate from beta figure two metrics: #1 over only drought periods and
        #2 over whole length of run. Calculate number of days where the average
        beta is below 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1. Then plot a simple
        bar chart with the results for each experiment.
    """

    # ======================= Plot setting ============================
    fig = plt.figure(figsize=[10,14])
    fig.subplots_adjust(hspace=0.20)
    fig.subplots_adjust(wspace=0.12)

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14
    plt.rcParams["legend.markerscale"] = 3.0

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']  = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')

    # choose colormap
    #colors = cm.Set2(np.arange(0,len(case_labels)))

    #print(colors)
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    # ========================= box-whisker of fwsoil============================
    day_start_drought = 2101 # 2017-10-1
    day_end_drought   = 2466 # 2018-10-1

    day_start_all     = 367  # first day of 2013
    day_end           = 2923 # first day of 2020

    day_drought  = day_end_drought - day_start_drought + 1
    day_all      = day_end - day_start_all + 1
    case_sum     = len(fcables)
    fw           = pd.DataFrame(np.zeros((day_drought+day_all)*case_sum),columns=['fwsoil'])
    fw['year']   = [''] * ((day_drought+day_all)*case_sum)
    fw['exp']    = [''] * ((day_drought+day_all)*case_sum)

    s = 0

    for case_num in np.arange(case_sum):

        cable = nc.Dataset(fcables[case_num], 'r')
        Time  = nc.num2date(cable.variables['time'][:],cable.variables['time'].units)

        Fwsoil          = pd.DataFrame(cable.variables['Fwsoil'][:,0,0],columns=['fwsoil'])
        Fwsoil['dates'] = Time
        Fwsoil          = Fwsoil.set_index('dates')
        Fwsoil          = Fwsoil.resample("D").agg('mean')
        Fwsoil.index    = Fwsoil.index - pd.datetime(2011,12,31)
        Fwsoil.index    = Fwsoil.index.days

        e  = s+day_drought

        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_drought,
                                 Fwsoil.index <=day_end_drought],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['drought'] * day_drought
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_drought
        s  = e
        e  = s+day_all
        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_all,
                                 Fwsoil.index <=day_end],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['all'] * day_all
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_all
        s  =  e

    # seaborn
    #sns.color_palette("Set2", 8)
    #flatui = ["orange", "dodgerblue"]
    #aaa = sns.set_palette(flatui)
    sns.boxplot(x="exp", y="fwsoil", hue="year", data=fw, palette="BrBG",
                order=case_labels,  width=0.7, hue_order=['drought','all'],
                ax=ax1, showfliers=False, color=almost_black) # palette="Set2",

    ax1.set_ylabel("$β$")
    ax1.set_xlabel("")
    ax1.axis('tight')
    ax1.set_ylim(0.,1.1)
    ax1.axhline(y=np.mean(fw[np.all([fw.year=='drought',fw.exp=='Ctl'],axis=0)]['fwsoil'].values),
                c=almost_black, ls="--")
    ax1.legend(loc='best', frameon=False)
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    print("***********************")
    print("median of beta-exp is %f" % np.median(fw[np.all([fw.year=='drought',fw.exp=='β-exp'],axis=0)]['fwsoil'].values))
    print("median of Hi-Res-2 is %f" % np.median(fw[np.all([fw.year=='drought',fw.exp=='Hi-Res-2'],axis=0)]['fwsoil'].values))
    print("median of Opt is %f" % np.median(fw[np.all([fw.year=='drought',fw.exp=='Opt'],axis=0)]['fwsoil'].values))
    print("median of beta-exp is %f" % np.median(fw[np.all([fw.year=='drought',fw.exp=='β-exp'],axis=0)]['fwsoil'].values))
    print("median of Hi-Res-2 is %f" % np.median(fw[np.all([fw.year=='drought',fw.exp=='Hi-Res-2'],axis=0)]['fwsoil'].values))
    print("median of Opt is %f" % np.median(fw[np.all([fw.year=='drought',fw.exp=='Opt'],axis=0)]['fwsoil'].values))
    print("***********************")

    #colors = cm.Set3(np.arange(0,len(case_labels)))
    colors = cm.tab20(np.arange(0,len(case_labels)))
    # ============================= boxplot ===================================
    for case_num in np.arange(len(fcables)):
        SM  = read_cable_SM(fcables[case_num], layers[case_num])
        fw  = read_cable_var(fcables[case_num], "Fwsoil")
        print(SM)

        # theta_1.5m : using root zone soil moisture
        if layers[case_num] == "6":
            sm =(  SM.iloc[:,0]*0.022 + SM.iloc[:,1]*0.058 \
                 + SM.iloc[:,2]*0.154 + SM.iloc[:,3]*0.409 \
                 + SM.iloc[:,4]*(1.5-0.022-0.058-0.154-0.409) )/1.5
        elif layers[case_num] == "31uni":
            sm = SM.iloc[:,0:10].mean(axis = 1)

        # theta_all : using whole soil column soil moisture
        # if layers[case_num] == "6":
        #     sm =(  SM.iloc[:,0]*0.022 + SM.iloc[:,1]*0.058 \
        #          + SM.iloc[:,2]*0.154 + SM.iloc[:,3]*0.409 \
        #          + SM.iloc[:,4]*1.085 + SM.iloc[:,5]*2.872 )/4.6
        # elif layers[case_num] == "31uni":
        #     sm = SM.iloc[:,:].mean(axis = 1)

        ax2.scatter(sm, fw,  s=1., marker='o', alpha=0.45, c=colors[case_num],label=case_labels[case_num])

    ax2.set_xlim(0.08,0.405)
    ax2.set_ylim(0.0,1.05)
    ax2.set_ylabel("$β$")
    ax2.set_xlabel("$θ$$_{1.5m}$ (m$^{3}$ m$^{-3}$)")
    #ax2.set_xlabel("$θ$ (m$^{3}$ m$^{-3}$)")
    #ax2.legend(numpoints=1, loc='lower right', frameon=False)
    ax2.legend(numpoints=1, loc='best', frameon=False)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top', bbox=props)
    #plt.setp(ax2.get_yticklabels(), visible=False)

    # ============================= days bar ===================================
    intval     = np.arange(0.8,0.0,-0.1)
    intval_sum = len(intval)

    # start from 2013-1-1
    day_start_drought  = 2101 - 367 # 2017-10-1
    day_end_drought    = 2466 - 367 # 2018-10-1
    tot_year_drought   = 1 #6

    offset             = 0.5
    fw_days_drought    = np.zeros([case_sum,intval_sum])

    for case_num in np.arange(case_sum):
        print(fcables[case_num])
        fw = read_cable_var(fcables[case_num], "Fwsoil")

        for intval_num in np.arange(intval_sum):
            tmp2 = np.where(fw.values[day_start_drought:day_end_drought] <= intval[intval_num], 1., 0.)
            fw_days_drought[case_num, intval_num] = sum(tmp2)/tot_year_drought

    x      = np.arange(intval_sum)
    width  = 1./(case_sum+2.)

    for case_num in np.arange(case_sum):
        offset = (case_num+1+0.5)*width
        ax3.bar(x + offset, fw_days_drought[case_num,:], width, color=colors[case_num], label=case_labels[case_num])

    cleaner_dates = [ "0.8","0.7","0.6","0.5","0.4","0.3","0.2","0.1"]
    xtickslocs    = [   0.5,  1.5,  2.5,  3.5,  4.5,  5.5,  6.5,  7.5]

    ax3.set(xticks=xtickslocs, xticklabels=cleaner_dates)
    ax3.set_ylabel("Days per year")
    ax3.set_xlabel("$β$")
    ax3.axis('tight')
    ax3.set_ylim(0,390)
    ax3.set_xlim(-0.1,7)
    ax3.legend( loc='best', ncol=2, frameon=False) #'upper right'
    ax3.text(0.02, 0.95, '(c)', transform=ax3.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    fig.savefig("./plots/EucFACE_Fwsoil_boxplot_SM_days" , bbox_inches='tight', pad_inches=0.1)

def plot_fwsoil_boxplot_SM( fcables, case_labels, layers, ring):

    """
    (a) box-whisker of fwsoil
    (b) fwsoil vs SM
    """

    # ======================= Plot setting ============================
    fig = plt.figure(figsize=[10,11])
    fig.subplots_adjust(hspace=0.20)
    fig.subplots_adjust(wspace=0.12)

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14
    plt.rcParams["legend.markerscale"] = 3.0

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']  = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')

    # choose colormap
    #colors = cm.Set2(np.arange(0,len(case_labels)))

    #print(colors)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    # ========================= box-whisker of fwsoil============================
    day_start_drought = 2101 # 2017-10-1
    day_end_drought   = 2466 # 2018-10-1

    day_start_all     = 367  # first day of 2013
    day_end           = 2923 # first day of 2020

    day_drought  = day_end_drought - day_start_drought + 1
    day_all      = day_end - day_start_all + 1
    case_sum     = len(fcables)
    fw           = pd.DataFrame(np.zeros((day_drought+day_all)*case_sum),columns=['fwsoil'])
    fw['year']   = [''] * ((day_drought+day_all)*case_sum)
    fw['exp']    = [''] * ((day_drought+day_all)*case_sum)

    s = 0

    for case_num in np.arange(case_sum):

        cable = nc.Dataset(fcables[case_num], 'r')
        Time  = nc.num2date(cable.variables['time'][:],cable.variables['time'].units)

        Fwsoil          = pd.DataFrame(cable.variables['Fwsoil'][:,0,0],columns=['fwsoil'])
        Fwsoil['dates'] = Time
        Fwsoil          = Fwsoil.set_index('dates')
        Fwsoil          = Fwsoil.resample("D").agg('mean')
        Fwsoil.index    = Fwsoil.index - pd.datetime(2011,12,31)
        Fwsoil.index    = Fwsoil.index.days

        e  = s+day_drought

        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_drought,
                                 Fwsoil.index <=day_end_drought],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['drought'] * day_drought
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_drought
        s  = e
        e  = s+day_all
        fw['fwsoil'].iloc[s:e] = Fwsoil[np.all([Fwsoil.index >= day_start_all,
                                 Fwsoil.index <=day_end],axis=0)]['fwsoil'].values
        fw['year'].iloc[s:e]   = ['all'] * day_all
        fw['exp'].iloc[s:e]    = [ case_labels[case_num]] * day_all
        s  =  e

    # seaborn
    #sns.color_palette("Set2", 8)
    #flatui = ["orange", "dodgerblue"]
    #aaa = sns.set_palette(flatui)
    sns.boxplot(x="exp", y="fwsoil", hue="year", data=fw, palette="BrBG",
                order=case_labels,  width=0.7, hue_order=['drought','all'],
                ax=ax1, showfliers=False, color=almost_black) # palette="Set2",

    ax1.set_ylabel("$β$")
    ax1.set_xlabel("")
    ax1.axis('tight')
    ax1.set_ylim(0.,1.1)
    ax1.axhline(y=np.mean(fw[np.all([fw.year=='drought',fw.exp=='Ctl'],axis=0)]['fwsoil'].values),
                c=almost_black, ls="--")
    ax1.legend(loc='best', frameon=False)
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=14, verticalalignment='top', bbox=props)

    print("***********************")
    # case_labels = ["Ctl", "Sres", "Watr", "Hi-Res-1", "Hi-Res-2", "Opt",  "β-hvrd",  "β-exp" ]
    print("median of Ctl is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='Ctl'],axis=0)]['fwsoil'].values))
    print("median of Sres is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='Sres'],axis=0)]['fwsoil'].values))
    print("median of Watr is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='Watr'],axis=0)]['fwsoil'].values))
    print("median of Hi-Res-1 is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='Hi-Res-1'],axis=0)]['fwsoil'].values))
    print("median of Hi-Res-2 is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='Hi-Res-2'],axis=0)]['fwsoil'].values))
    print("median of Opt is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='Opt'],axis=0)]['fwsoil'].values))
    print("median of β-hvrd is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='β-hvrd'],axis=0)]['fwsoil'].values))
    print("median of β-exp is %f" % np.median(fw[np.all([fw.year=='all',fw.exp=='β-exp'],axis=0)]['fwsoil'].values))
    print("***********************")

    #colors = cm.Set3(np.arange(0,len(case_labels)))
    colors = cm.tab20(np.arange(0,len(case_labels)))
    # ============================= boxplot ===================================
    for case_num in np.arange(len(fcables)):
        SM  = read_cable_SM(fcables[case_num], layers[case_num])
        fw  = read_cable_var(fcables[case_num], "Fwsoil")
        # print(SM)

        # theta_1.5m : using root zone soil moisture
        if layers[case_num] == "6":
            sm =(  SM.iloc[:,0]*0.022 + SM.iloc[:,1]*0.058 \
                 + SM.iloc[:,2]*0.154 + SM.iloc[:,3]*0.409 \
                 + SM.iloc[:,4]*(1.5-0.022-0.058-0.154-0.409) )/1.5
        elif layers[case_num] == "31uni":
            sm = SM.iloc[:,0:10].mean(axis = 1)

        # theta_all : using whole soil column soil moisture
        # if layers[case_num] == "6":
        #     sm =(  SM.iloc[:,0]*0.022 + SM.iloc[:,1]*0.058 \
        #          + SM.iloc[:,2]*0.154 + SM.iloc[:,3]*0.409 \
        #          + SM.iloc[:,4]*1.085 + SM.iloc[:,5]*2.872 )/4.6
        # elif layers[case_num] == "31uni":
        #     sm = SM.iloc[:,:].mean(axis = 1)

        ax2.scatter(sm, fw,  s=1., marker='o', alpha=0.45, c=colors[case_num],label=case_labels[case_num])

    ax2.set_xlim(0.08,0.405)
    ax2.set_ylim(0.0,1.05)
    ax2.set_ylabel("$β$")
    ax2.set_xlabel("$θ$$_{1.5m}$ (m$^{3}$ m$^{-3}$)")
    #ax2.set_xlabel("$θ$ (m$^{3}$ m$^{-3}$)")
    #ax2.legend(numpoints=1, loc='lower right', frameon=False)
    ax2.legend(numpoints=1, loc='best', frameon=False)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=14, verticalalignment='top', bbox=props)
    #plt.setp(ax2.get_yticklabels(), visible=False)

    fig.savefig("./plots/EucFACE_Fwsoil_boxplot_SM" , bbox_inches='tight', pad_inches=0.1)

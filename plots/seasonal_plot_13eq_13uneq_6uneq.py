#!/usr/bin/env python

"""
Plot visual benchmark (average seasonal cycle) of old vs new model runs.

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (18.10.2017)"
__email__ = "mdekauwe@gmail.com"

import netCDF4 as nc
import matplotlib.pyplot as plt
import sys
import datetime as dt
import pandas as pd
import numpy as np
from matplotlib.ticker import FixedLocator
import os

def main(uneq13_fname, eq13_fname,uneq6_fname):

    df_a = read_cable_file(uneq13_fname)
    df_a = resample_to_seasonal_cycle(df_a)
    df_e = read_cable_file(eq13_fname)
    df_e = resample_to_seasonal_cycle(df_e)
    df_s = read_cable_file(uneq6_fname)
    df_s = resample_to_seasonal_cycle(df_s)

    fig = plt.figure(figsize=(8,6))
    fig.subplots_adjust(hspace=0.3)
    fig.subplots_adjust(wspace=0.2)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['font.size'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

    ax1 = fig.add_subplot(3,2,1)
    ax2 = fig.add_subplot(3,2,2)
    ax3 = fig.add_subplot(3,2,3)
    ax4 = fig.add_subplot(3,2,4)
    ax5 = fig.add_subplot(3,2,5)
    ax6 = fig.add_subplot(3,2,6)

    axes = [ax1, ax2, ax3, ax4, ax5, ax6]
    vars = ["GPP", "CO2air", "Qle", "LAI", "TVeg", "ESoil"]
    for a, v in zip(axes, vars):
        a.plot(df_a.month, df_a[v], c="blue", lw=2.0, ls="-", label="uneq13")
        a.plot(df_e.month, df_e[v], c="red", lw=2.0, ls="-", label="eq13")
        a.plot(df_s.month, df_s[v], c="green", lw=2.0, ls="-", label="uneq6")

    labels = ["GPP (g C m$^{-2}$ d$^{-1}$)", \
              "CO$_2$ ($\mathrm{\mu}$mol mol$^{-1}$)",\
              "Qle (W m$^{-2}$)", "LAI (m$^{2}$ m$^{-2}$)",\
              "TVeg (mm d$^{-1}$)", "Esoil (mm d$^{-1}$)"]
    for a, l in zip(axes, labels):
        a.set_title(l, fontsize=12)

    xtickagaes_minor = FixedLocator([2, 3, 4, 5, 7, 8, 9, 10, 11])
    for i,a in enumerate(axes):
        a.set_xticks([1, 6, 12])
        if i != 1:
            a.set_ylim(ymin=0)
        a.xaxis.set_minor_locator(xtickagaes_minor)
        a.set_xticklabels(['Jan', 'Jun', 'Dec'])
        if i < 4:
            plt.setp(a.get_xticklabels(), visible=False)
    ax1.legend(numpoints=1, loc="best")


    plot_fname = "seasonal_plot_gw_on_uneq-eq-13-6.png"
    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    fig.savefig(os.path.join(plot_dir, plot_fname), bbox_inches='tight',
                pad_inches=0.1)


def read_cable_file(fname):

    f = nc.Dataset(fname)
    time = nc.num2date(f.variables['time'][:],
                        f.variables['time'].units)
    df = pd.DataFrame(f.variables['GPP'][:,0,0], columns=['GPP'])
    df['Qle'] = f.variables['Qle'][:,0,0]
    df['LAI'] = f.variables['LAI'][:,0,0]
    df['TVeg'] = f.variables['TVeg'][:,0,0]
    df['ESoil'] = f.variables['ESoil'][:,0,0]
    df['CO2air'] = f.variables['CO2air'][:,0]

    df['dates'] = time
    df = df.set_index('dates')

    return df

def resample_to_seasonal_cycle(df, OBS=False):

    UMOL_TO_MOL = 1E-6
    MOL_C_TO_GRAMS_C = 12.0
    SEC_2_DAY = 86400.

    # umol/m2/s -> g/C/d
    df['GPP'] *= UMOL_TO_MOL * MOL_C_TO_GRAMS_C * SEC_2_DAY

    # kg/m2/s -> mm/d
    df['TVeg'] *= SEC_2_DAY
    df['ESoil'] *= SEC_2_DAY

    method = {'GPP':'mean', 'CO2air':'mean', 'Qle':'mean', 'LAI':'mean',
              'TVeg':'mean', 'ESoil':'mean'}
    df = df.resample("M").agg(method).groupby(lambda x: x.month).mean()
    df['month'] = np.arange(1,13)

    return df

if __name__ == "__main__":

    uneq13_fname = "/short/w35/mm3972/cable/runs/EucFACE/EucFACE_run/outputs/type_elev_para_ununi/13layers/unequal/gw_on_or_off/EucFACE_amb_out.nc"
    eq13_fname = "/short/w35/mm3972/cable/runs/EucFACE/EucFACE_run/outputs/type_elev_para_ununi/13layers/equal/gw_on_or_off/EucFACE_amb_out.nc"
    uneq6_fname = "/short/w35/mm3972/cable/runs/EucFACE/EucFACE_run/outputs/type_elev_para_ununi/6layers/using_type_elev_para_writen_in_met/gw_on_or_off/EucFACE_amb_out.nc"
    main(uneq13_fname, eq13_fname,uneq6_fname)

#!/usr/bin/env python

"""
Run CABLE for the EucFACE site and gather some specific outputs about direct
and diffuse fracs and direct and diffuse GPP for Jim and Dushan

That's all folks.
"""

'''
modifications:
1. add bulk density to calculate cnsd
2. divide soil/buld density for amb and ele
3. adding Cosby uni Cosby multi HC_SWC
4. add option for single ring
5. add soil fraction interpolation methods
6. add option for soil layers - done
'''

__author__    = "Martin De Kauwe"
__developer__ = "MU Mengyuan"

import os
import sys
import glob
import pandas as pd
import numpy as np
import netCDF4 as nc
import datetime
from scipy.interpolate import interp1d
from scipy.interpolate import griddata

def main(met_fname, lai_fname, swc_fname, stx_fname, out_fname, PTF, soil_frac, layer_num, ring=ring):

    DEG_2_KELVIN = 273.15
    SW_2_PAR = 2.3
    PAR_2_SW = 1.0 / SW_2_PAR
    HLFHR_2_SEC = 1.0 / 1800.

    df = pd.read_csv(met_fname)

    ndim = 1
    nsoil= layer_num
    n_timesteps = len(df)
    times = []
    secs = 0.0
    for i in range(n_timesteps):
        times.append(secs)
        secs += 1800.

    # create file and write global attributes
    f = nc.Dataset(out_fname, 'w', format='NETCDF4')
    f.description = 'EucFACE met data, created by MU Mengyuan'
    f.history = "Created by: %s" % (os.path.basename(__file__))
    f.creation_date = "%s" % (datetime.datetime.now())

    # set dimensions
    f.createDimension('time', None)
    f.createDimension('z', ndim)
    f.createDimension('y', ndim)
    f.createDimension('x', ndim)
    f.createDimension('soil_depth', nsoil)
    f.Conventions = "CF-1.0"

    # create variables
    time = f.createVariable('time', 'f8', ('time',))
    time.units = "seconds since 2013-01-01 00:00:00"
    time.long_name = "time"
    time.calendar = "standard"

    z = f.createVariable('z', 'f8', ('z',))
    z.long_name = "z"
    z.long_name = "z dimension"

    y = f.createVariable('y', 'f8', ('y',))
    y.long_name = "y"
    y.long_name = "y dimension"

    x = f.createVariable('x', 'f8', ('x',))
    x.long_name = "x"
    x.long_name = "x dimension"

    soil_depth = f.createVariable('soil_depth', 'f4', ('soil_depth',))
    soil_depth.long_name = "soil_depth"

    latitude = f.createVariable('latitude', 'f4', ('y', 'x',))
    latitude.units = "degrees_north"
    latitude.missing_value = -9999.
    latitude.long_name = "Latitude"

    longitude = f.createVariable('longitude', 'f4', ('y', 'x',))
    longitude.units = "degrees_east"
    longitude.missing_value = -9999.
    longitude.long_name = "Longitude"

    SWdown = f.createVariable('SWdown', 'f4', ('time', 'y', 'x',))
    SWdown.units = "W/m^2"
    SWdown.missing_value = -9999.
    SWdown.long_name = "Surface incident shortwave radiation"
    SWdown.CF_name = "surface_downwelling_shortwave_flux_in_air"

    Tair = f.createVariable('Tair', 'f4', ('time', 'z', 'y', 'x',))
    Tair.units = "K"
    Tair.missing_value = -9999.
    Tair.long_name = "Near surface air temperature"
    Tair.CF_name = "surface_temperature"

    Rainf = f.createVariable('Rainf', 'f4', ('time', 'y', 'x',))
    Rainf.units = "mm/s"
    Rainf.missing_value = -9999.
    Rainf.long_name = "Rainfall rate"
    Rainf.CF_name = "precipitation_flux"

    Qair = f.createVariable('Qair', 'f4', ('time', 'z', 'y', 'x',))
    Qair.units = "kg/kg"
    Qair.missing_value = -9999.
    Qair.long_name = "Near surface specific humidity"
    Qair.CF_name = "surface_specific_humidity"

    Wind = f.createVariable('Wind', 'f4', ('time', 'z', 'y', 'x',))
    Wind.units = "m/s"
    Wind.missing_value = -9999.
    Wind.long_name = "Scalar windspeed" ;
    Wind.CF_name = "wind_speed"

    PSurf = f.createVariable('PSurf', 'f4', ('time', 'y', 'x',))
    PSurf.units = "Pa"
    PSurf.missing_value = -9999.
    PSurf.long_name = "Surface air pressure"
    PSurf.CF_name = "surface_air_pressure"

    LWdown = f.createVariable('LWdown', 'f4', ('time', 'y', 'x',))
    LWdown.units = "W/m^2"
    LWdown.missing_value = -9999.
    LWdown.long_name = "Surface incident longwave radiation"
    LWdown.CF_name = "surface_downwelling_longwave_flux_in_air"

    CO2 = f.createVariable('CO2air', 'f4', ('time', 'z', 'y', 'x',))
    CO2.units = "ppm"
    CO2.missing_value = -9999.
    CO2.long_name = ""
    CO2.CF_name = ""

    LAI = f.createVariable('LAI', 'f4', ('time', 'y', 'x'))
    LAI.setncatts({'long_name': u"Leaf Area Index",})

    vcmax = f.createVariable('vcmax', 'f4', ('y', 'x'))
    ejmax = f.createVariable('ejmax', 'f4', ('y', 'x'))
    g1 = f.createVariable('g1', 'f4', ('y', 'x'))
    hc = f.createVariable('hc', 'f4', ('y', 'x'))

    elevation = f.createVariable('elevation', 'f4', ('y', 'x',))
    elevation.units = "m" ;
    elevation.missing_value = -9999.
    elevation.long_name = "Site elevation above sea level" ;

    za = f.createVariable('za', 'f4', ('y', 'x',))
    za.units = "m"
    za.missing_value = -9999.
    za.long_name = "level of lowest atmospheric model layer"

########## add hydrological parameters ###########
    # 2-Dimension variables
    # slope = 0.004(maximum)
    # sfc   = 0.265 (m3/m3)
    # swilt = 0.115 (m3/m3)
    iveg = f.createVariable('iveg', 'f4', ('y', 'x',))
    iveg.long_name = "vegetation type"
    iveg.units = "-"
    iveg.missing_value = -9999.0

    sand = f.createVariable('sand', 'f4', ('y', 'x',))
    sand.units = "-"
    sand.missing_value = -1.0

    clay = f.createVariable('clay', 'f4', ('y', 'x',))
    clay.units = "-"
    clay.missing_value = -1.0

    silt = f.createVariable('silt', 'f4', ('y', 'x',))
    silt.units = "-"
    silt.missing_value = -1.0

    rhosoil = f.createVariable('rhosoil', 'f4', ('y', 'x',))
    rhosoil.units = "kg m-3"
    rhosoil.long_name = "soil density"
    rhosoil.missing_value = -9999.0

    bch  = f.createVariable('bch', 'f4', ('y', 'x',))
    bch.units = "-"
    bch.long_name = "C and H B"
    bch.missing_value = -9999.0

    hyds = f.createVariable('hyds', 'f4', ('y', 'x',))
    hyds.units = "m s-1"
    hyds.long_name = "hydraulic conductivity at saturation"
    hyds.missing_value = -9999.0

    sucs = f.createVariable('sucs', 'f4', ('y', 'x',))
    sucs.units = "m"
    sucs.long_name = "matric potential at saturation"
    sucs.missing_value = -9999.0

    ssat = f.createVariable('ssat', 'f4', ('y', 'x',))
    ssat.units = "m3 m-3"
    ssat.long_name = "volumetric water content at saturation"
    ssat.missing_value = -9999.0

    swilt= f.createVariable('swilt', 'f4', ('y', 'x',))
    swilt.units = "m3 m-3"
    swilt.long_name = "wilting point"
    swilt.missing_value = -9999.0

    sfc  = f.createVariable('sfc', 'f4', ('y', 'x',))
    sfc.units = "m3 m-3"
    sfc.long_name = "field capcacity"
    sfc.missing_value = -9999.0

    css  = f.createVariable('css', 'f4', ('y', 'x',))
    css.units = "kJ kg-1 K-1"
    css.long_name = "soil specific heat capacity"
    css.missing_value = -9999.0

    cnsd = f.createVariable('cnsd', 'f4', ('y', 'x',))
    cnsd.units = "W m-1 K-1"
    cnsd.long_name = "thermal conductivity of dry soil"
    cnsd.missing_value = -9999.0

    # 3-Dimension variables
    sand_vec = f.createVariable('sand_vec', 'f4', ('soil_depth', 'y', 'x',))
    sand_vec.units = "-"
    sand_vec.missing_value = -1.0

    clay_vec = f.createVariable('clay_vec', 'f4', ('soil_depth', 'y', 'x',))
    clay_vec.units = "-"
    clay_vec.missing_value = -1.0

    silt_vec = f.createVariable('silt_vec', 'f4', ('soil_depth', 'y', 'x',))
    silt_vec.units = "-"
    silt_vec.missing_value = -1.0

    org_vec  = f.createVariable('org_vec', 'f4', ('soil_depth', 'y', 'x',))
    org_vec.units = "-"
    org_vec.missing_value = -1.0

    rhosoil_vec = f.createVariable('rhosoil_vec', 'f4', ('soil_depth', 'y', 'x',))
    rhosoil_vec.units = "kg m-3"
    rhosoil_vec.long_name = "soil density"
    rhosoil_vec.missing_value = -9999.0

    bch_vec  = f.createVariable('bch_vec', 'f4', ('soil_depth', 'y', 'x',))
    bch_vec.units = "-"
    bch_vec.long_name = "C and H B"
    bch_vec.missing_value = -9999.0

    hyds_vec = f.createVariable('hyds_vec', 'f4', ('soil_depth', 'y', 'x',))
    hyds_vec.units = "mm s-1"
    hyds_vec.long_name = "hydraulic conductivity at saturation"
    hyds_vec.missing_value = -9999.0

    sucs_vec = f.createVariable('sucs_vec', 'f4', ('soil_depth', 'y', 'x',))
    sucs_vec.units = "m"
    sucs_vec.long_name = "matric potential at saturation"
    sucs_vec.missing_value = -9999.0

    ssat_vec = f.createVariable('ssat_vec', 'f4', ('soil_depth', 'y', 'x',))
    ssat_vec.units = "m3 m-3"
    ssat_vec.long_name = "volumetric water content at saturation"
    ssat_vec.missing_value = -9999.0

    swilt_vec= f.createVariable('swilt_vec', 'f4', ('soil_depth', 'y', 'x',))
    swilt_vec.units = "m3 m-3"
    swilt_vec.long_name = "wilting point"
    swilt_vec.missing_value = -9999.0

    sfc_vec  = f.createVariable('sfc_vec', 'f4', ('soil_depth', 'y', 'x',))
    sfc_vec.units = "m3 m-3"
    sfc_vec.long_name = "field capcacity"
    sfc_vec.missing_value = -9999.0

    css_vec  = f.createVariable('css_vec', 'f4', ('soil_depth', 'y', 'x',))
    css_vec.units = "kJ kg-1 K-1"
    css_vec.long_name = "soil specific heat capacity"
    css_vec.missing_value = -9999.0

    cnsd_vec = f.createVariable('cnsd_vec', 'f4', ('soil_depth', 'y', 'x',))
    cnsd_vec.units = "W m-1 K-1"
    cnsd_vec.long_name = "thermal conductivity of dry soil"
    cnsd_vec.missing_value = -9999.0

    watr = f.createVariable('watr', 'f4', ('soil_depth', 'y', 'x',))
    watr.units = "m3 m-3"
    watr.long_name = "residual water content of the soil"
    watr.missing_value = -9999.0

    SoilMoist = f.createVariable('SoilMoist', 'f4', ('soil_depth', 'y', 'x',))
    SoilMoist.units = "m3 m-3"
    SoilMoist.long_name = "soil moisture (water+ice)"
    SoilMoist.missing_value = -9999.0

    """
    Parameters based on param_vec:

            2D: sand, silt, clay, organic, sucs, ssat, rhosoil, bch, hyds,
                cnsd (thermal conductivity of dry soil, W/m/K), css (soil specific heat capacity, kJ/kg/K)

    Aquifer Parameters copied from bottom soil layer:
            "Sy", "permeability"

    Parameters read from gridinfo file:

           2D:  "slope_std", "Albedo", "albedo2", "elevation_std", "drainage_density",
                "drainage_dist",  "permeability_std",
                "dtb" (is there an observation)
                "soil_color" (relate to soil type?)
           3D:  "SnowDepth", "patchfrac",
           4D:  "SoilTemp"
    """

    # write data to file
    x[:] = ndim
    y[:] = ndim
    z[:] = ndim

    soil_depth[:] = np.arange(0,nsoil,1)
    time[:] = times
    latitude[:]  = -33.617778 # Ellsworth 2017, NCC
    longitude[:] = 150.740278 # Ellsworth 2017, NCC

    SWdown[:,0,0] = (df.PAR.values * PAR_2_SW).reshape(n_timesteps, ndim, ndim)
    Tair[:,0,0,0] = (df.TAIR.values + DEG_2_KELVIN).reshape(n_timesteps,
                                                            ndim, ndim, ndim)
    df.PPT *= HLFHR_2_SEC
    Rainf[:,0,0] = df.PPT.values.reshape(n_timesteps, ndim, ndim)
    qa_vals = convert_rh_to_qair(df.RH.values, df.TAIR.values, df.PRESS.values)
    Qair[:,0,0,0] = qa_vals.reshape(n_timesteps, ndim, ndim, ndim)
    Wind[:,0,0,0] = df.WIND.values.reshape(n_timesteps, ndim, ndim, ndim)
    PSurf[:,0,0] = df.PRESS.values.reshape(n_timesteps, ndim, ndim)
    lw = estimate_lwdown(df.TAIR.values + DEG_2_KELVIN, df.RH.values)
    LWdown[:,0,0] = lw.reshape(n_timesteps, ndim, ndim)
    if ring in ["amb","R2","R3","R6"]:
        CO2[:,0,0] = df["Ca.A"].values.reshape(n_timesteps, ndim, ndim, ndim)
        vcmax[:] = 86.1425919e-6
        ejmax[:] = 138.4595736e-6
    elif ring in ["ele","R1","R4","R5"]:
        CO2[:,0,0] = df["Ca.E"].values.reshape(n_timesteps, ndim, ndim, ndim)
        vcmax[:] = 81.70591263e-6
        ejmax[:] = 135.8062907e-6
    elevation[:] = 23.0 # Ellsworth 2017, NCC
    LAI[:,0,0] = interpolate_lai(lai_fname, ring)

    #df.lai.values.reshape(n_timesteps, ndim, ndim)
    g1[:] = 3.8
    hc[:] = 20.
    za[:] = 20.0 + 2.0

# read hydraulic parameters:
    iveg[:]       = 2
    if layer_num == "6":
        depth_mid     = [ 1.1 ,   5.1,  15.7,  43.85, 118.55, 316.4]
        soil_depth[:] = [0.011, 0.051, 0.157, 0.4385, 1.1855, 3.164]
        zse_vec       = [0.022, 0.058, 0.154, 0.409, 1.085, 2.872]
        org_vec[:,0,0]= [0.0102,0.0102,0.0025,0.0025, 0.0025,0.0025]
    elif layer_num == "13":
        depth_mid     = [1,4.5,10.,19.5,41,71,101,131,161,191,221,273.5,386]
        soil_depth[:] = [0.01,0.045,0.10,0.195,0.41,0.71,1.01,1.31,1.61,1.91,2.21,2.735,3.86]
        zse_vec       = [0.02, 0.05, 0.06, 0.13, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.75, 1.50]
        org_vec[:,0,0]= [0.0102,0.0102,0.0102,0.0025,0.0025,0.0025,0.0025,0.0025,\
                         0.0025,0.0025,0.0025,0.0025,0.0025]
    elif layer_num == "31":
        depth_mid     = [ 7.5,   22.5 , 37.5 , 52.5 , 67.5 , 82.5 , 97.5 , \
                         112.5, 127.5, 142.5, 157.5, 172.5, 187.5, 202.5, \
                         217.5, 232.5, 247.5, 262.5, 277.5, 292.5, 307.5, \
                         322.5, 337.5, 352.5, 367.5, 382.5, 397.5, 412.5, \
                         427.5, 442.5, 457.5 ]
        soil_depth[:] = [ 0.075, 0.225 , 0.375 , 0.525 , 0.675 , 0.825 , 0.975 , \
                          1.125, 1.275, 1.425, 1.575, 1.725, 1.875, 2.025, \
                          2.175, 2.325, 2.475, 2.625, 2.775, 2.925, 3.075, \
                          3.225, 3.375, 3.525, 3.675, 3.825, 3.975, 4.125, \
                          4.275, 4.425, 4.575 ]
        zse_vec       = [ 0.15,  0.15,  0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  \
                          0.15,  0.15,  0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  \
                          0.15,  0.15,  0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  \
                          0.15 ]
        org_vec[:,0,0]= [ 0.0102, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025,\
                          0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025,\
                          0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025,\
                          0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025,\
                          0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025,\
                          0.0025]

    sand_vec[:,0,0]   = np.zeros(nsoil)
    silt_vec[:,0,0]   = np.zeros(nsoil)
    clay_vec[:,0,0]   = np.zeros(nsoil)
    rhosoil_vec[:,0,0]= np.zeros(nsoil)
    hyds_vec[:,0,0]   = np.zeros(nsoil)
    bch_vec[:,0,0]    = np.zeros(nsoil)
    sucs_vec[:,0,0]   = np.zeros(nsoil)
    ssat_vec[:,0,0]   = np.zeros(nsoil)
    watr[:,0,0]       = np.zeros(nsoil)
    swilt_vec[:,0,0]  = np.zeros(nsoil)
    sfc_vec[:,0,0]    = np.zeros(nsoil)
    css_vec[:,0,0]    = np.zeros(nsoil)
    cnsd_vec[:,0,0]   = np.zeros(nsoil)
    SoilMoist[:,0,0]  = np.zeros(nsoil)

    bulk_density      = np.zeros(nsoil)
    sand_vec[:,0,0],silt_vec[:,0,0],clay_vec[:,0,0] = calc_soil_frac(stx_fname, ring, nsoil, depth_mid, soil_frac)
    rhosoil_vec[:,0,0],bulk_density = estimate_rhosoil_vec(swc_fname, depth_mid, ring, soil_frac)
    SoilMoist[:,0,0]  = init_soil_moisture(swc_fname, depth_mid, ring, soil_frac)
    print(rhosoil_vec)
    print(bulk_density)

    psi_tmp  = 2550000.0
    print("good")
    if PTF == 'Campbell_Cosby_multi_Python':
        for i in np.arange(0,nsoil,1):
            css_vec[i]  = (1.0-org_vec[i]) * ( 850*(1.0 - sand_vec[i] - clay_vec[i]) + \
                            865.0*clay_vec[i] + 750.0*sand_vec[i] ) + org_vec[i]*950.0
            hyds_vec[i] = (1.0-org_vec[i]) * 0.00706 * ( 10.0 ** (-0.60 + 1.26*sand_vec[i] - 0.64*clay_vec[i]) )\
                          + org_vec[i]*10**(-4)
            bch_vec[i]  = (1.0-org_vec[i]) * ( 3.1 + 15.4*clay_vec[i] - 0.3*sand_vec[i]) + org_vec[i]*3.0
            watr[i]     = (1.0-org_vec[i]) * ( 0.02 + 0.018*clay_vec[i] ) + org_vec[i]*0.15
            ssat_vec[i] = (1.0-org_vec[i]) * ( 0.505 - 0.142*sand_vec[i] - 0.037*clay_vec[i]) \
                          + org_vec[i]*0.6
            sfc_vec[i]   = (ssat_vec[i] - watr[i]) * ( 1.157407 * 10**(-6) / hyds_vec[i])** \
                          (1.0 / (2.0*bch_vec[i] + 3.0) ) + watr[i]
            sst_tmp  = 1.0 - max(min(ssat_vec[i], 0.85), 0.15)
            cnsd_vec[i]  = (1.0-org_vec[i]) * ( 0.135*sst_tmp + 0.0239/sst_tmp )  /  \
                            (1.0 - 0.947*sst_tmp) + org_vec[i]*0.05
            sucs_vec[i] = (1.0-org_vec[i]) * 10.0 * 10.0**( 1.54 - 0.95*sand_vec[i] + 0.63*silt_vec[i] ) \
                            + org_vec[i]*10.3
            swilt_vec[i] = (ssat_vec[i] - watr[i]) * ( (psi_tmp/sucs_vec[i]) ** (-1.0/bch_vec[i]) ) \
                           + watr[i]
            sucs_vec[i] = sucs_vec[i]/1000. # cannot put it before swilt_vec calculation, it will cause error
                                            # comment out *(-1.0) then waterbal can be closed, because CABLE expect the positive sucs_vec input,
                                            # for global sucs_vec in cable is soil%sucs_vec  = 1000._r_2 * ( abs('sucs_vec') / abs(insucs) ),
                                            # thus the negetive value in surface forcing data is transfer into positve value...
    else:
        if PTF == 'Campbell_Cosby_univariate':
            for i in np.arange(0,nsoil,1):
                hyds_vec[i] = (1.0-org_vec[i]) * ( 0.0070556 * 10.0**( -0.884 + 1.53*sand_vec[i] )) \
                              + org_vec[i]*10**(-4)
                sucs_vec[i] = (1.0-org_vec[i]) * ( 10.0 * 10.0**( 1.88 -1.31*sand_vec[i] ))\
                              + org_vec[i]*10.3
                bch_vec[i]  = (1.0-org_vec[i]) * ( 2.91 + 15.9*clay_vec[i] ) \
                              + org_vec[i]*2.91
                ssat_vec[i] = (1.0-org_vec[i]) * ( min( 0.489, max( 0.1, 0.489 - 0.126*sand_vec[i] ))) \
                              + org_vec[i]*0.9
                watr[i]     = (1.0-org_vec[i]) * ( 0.02 + 0.018*clay_vec[i] ) \
                              + org_vec[i]*0.1
        elif PTF == 'Campbell_Cosby_multivariate':
            for i in np.arange(0,nsoil,1):
                hyds_vec[i] = (1.0-org_vec[i]) * ( 0.00706*(10.0**(-0.60 + 1.26*sand_vec[i] - 0.64*clay_vec[i] ))) \
                              + org_vec[i]*10**(-4)
                sucs_vec[i] = (1.0-org_vec[i]) * ( 10.0 * 10.0**(1.54 - 0.95*sand_vec[i] + 0.63*silt_vec[i] )) \
                              + org_vec[i]*10.3
                bch_vec[i]  = (1.0-org_vec[i]) * ( 3.1 + 15.7 *clay_vec[i] - 0.3*sand_vec[i] ) \
                              + org_vec[i]*2.91
                # 15.4 -> 15.7, because in Cosby 1980 is 15.7
                ssat_vec[i] = (1.0-org_vec[i]) * ( 0.505 - 0.142*sand_vec[i] - 0.037*clay_vec[i] ) \
                              + org_vec[i]*0.9
                watr[i]     = (1.0-org_vec[i]) * ( 0.02 + 0.018*clay_vec[i] ) \
                              + org_vec[i]*0.1
        elif PTF == 'Campbell_HC_SWC':
            for i in np.arange(0,nsoil,1):
                sucs_vec[i] = 10.0*10.0**( -4.9840 + 5.0923*sand_vec[i] + 15.752*silt_vec[i]\
                              + 0.12409*bulk_density[i] - 16.400*org_vec[i] - 21.767*(silt_vec[i]**2.0)\
                              + 14.382*(silt_vec[i]**3.0) + 8.0407*(clay_vec[i]**2.0) + 44.067*(org_vec[i]**2.0) )
                print("we did sucs")
                bch_vec[i]  = 10.0**(0.84669 + 0.46806*sand_vec[i] - 0.92464*silt_vec[i] \
                              + 0.45428*bulk_density[i] +4.9792*org_vec[i] - 3.2947*(sand_vec[i]**2.0)\
                              + 1.6891*(sand_vec[i]**3.0) - 11.225*(org_vec[i]**3.0) )
                print("we did bch")
                ssat_vec[i] = 0.23460 + 0.46614*sand_vec[i] + 0.88163*silt_vec[i] \
                              + 0.64339*clay_vec[i] - 0.30282*bulk_density[i] \
                              + 0.17976*(sand_vec[i]**2.0) - 0.31346*(silt_vec[i]**2.0)
                print("we did ssat")
                hyds_vec[i] = (1.0-org_vec[i]) * ( 0.00706*(10.0**(-0.60 + 1.26*sand_vec[i] - 0.64*clay_vec[i] ))) \
                              + org_vec[i]*10**(-4)
                print("we did hyds")
                # In CABLE for HC_SWC is hyds_vec[i] = 0.00706*(10.0**(-0.60 + 1.26*sand_vec[i]+ -0.64*clay_vec[i] ))
                watr[i]     = 0.0
        print("well done")
        for i in np.arange(0,nsoil,1):
            swilt_vec[i] = (ssat_vec[i]-watr[i]) * (psi_tmp/sucs_vec[i])**(-1.0/bch_vec[i])+watr[i]
            sfc_vec[i]   = (1.157407 * 10**(-6) / hyds_vec[i])**(1.0/(2.0*bch_vec[i]+3.0)) \
                           *(ssat_vec[i]-watr[i]) + watr[i]
            swilt_vec[i] = min(0.95*sfc_vec[i],swilt_vec[i])
            ssat_bounded = min(0.8, max(0.1, ssat_vec[i] ))
            cnsd_vec[i]  = (1.0-org_vec[i]) * (( 0.135*(1.0-ssat_bounded)) + (64.7/rhosoil_vec[i]))\
                           / (1.0 - 0.947*(1.0-ssat_bounded)) + org_vec[i]*0.1
            css_vec[i]   = (1.0-org_vec[i]) * max( 910.6479*silt_vec[i] + 916.4438 * clay_vec[i] + 740.7491*sand_vec[i], 800.0)\
                           + org_vec[i]*4000.0
            sucs_vec[i] = sucs_vec[i]/1000.
    print("all are good")
    sand[:,0] = thickness_weighted_average(sand_vec)
    silt[:,0] = thickness_weighted_average(silt_vec)
    clay[:,0] = thickness_weighted_average(clay_vec)
    rhosoil[:,0] = thickness_weighted_average(rhosoil_vec)
    css[:,0] = thickness_weighted_average(css_vec)
    hyds[:,0] = thickness_weighted_average(hyds_vec)
    hyds[:,0] = hyds[:,0]/1000.
    bch[:,0]  = thickness_weighted_average(bch_vec)
    ssat[:,0] = thickness_weighted_average(ssat_vec)
    sfc[:,0] = thickness_weighted_average(sfc_vec)
    cnsd[:,0] = thickness_weighted_average(cnsd_vec)
    sucs[:,0] = thickness_weighted_average(sucs_vec)
    swilt[:,0] = thickness_weighted_average(swilt_vec)

    f.close()

def calc_soil_frac(stx_fname, ring, nsoil, depth_mid, soil_frac):
    """
    interpolate the observated sand,silt,clay to pointed depth
    """
    soil_texture = pd.read_csv(stx_fname, usecols = ['Ring','Depth_interval_cm','Sand_%','Silt_%','Clay_%'])
    soil_texture['Depth'] = np.zeros(len(soil_texture))
    soil_texture['Depth_top'] = np.zeros(len(soil_texture))
    soil_texture['Depth_bot'] = np.zeros(len(soil_texture))

    for i in np.arange(0,len(soil_texture),1):
        index = soil_texture['Depth_interval_cm'].values[i].index('-')
        soil_texture['Depth'].iloc[i] = (float(soil_texture['Depth_interval_cm'].values[i][:index]) \
                                        + float(soil_texture['Depth_interval_cm'].values[i][index+1:]))/2.
        soil_texture['Depth_top'].iloc[i] = float(soil_texture['Depth_interval_cm'].values[i][:index])
        soil_texture['Depth_bot'].iloc[i] = float(soil_texture['Depth_interval_cm'].values[i][index+1:])

    if ring == 'amb':
        subset = soil_texture[soil_texture['Ring'].isin(['R2','R3','R6'])]
    elif ring == 'ele':
        subset = soil_texture[soil_texture['Ring'].isin(['R1','R4','R5'])]
    else:
        subset = soil_texture[soil_texture['Ring'].isin([ring])]

    subset = subset.groupby(by=["Depth"]).mean()
    Sand_calu = interp1d(subset.index, subset['Sand_%'].values, kind = soil_frac, \
                fill_value=(subset['Sand_%'].values[0],subset['Sand_%'].values[-1]), \
                bounds_error=False)
    sand_calu = Sand_calu(depth_mid)/100.

    Silt_calu = interp1d(subset.index, subset['Silt_%'].values, kind = soil_frac, \
                fill_value=(subset['Silt_%'].values[0],subset['Silt_%'].values[-1]), \
                bounds_error=False)
    silt_calu = Silt_calu(depth_mid)/100.

    Clay_calu = interp1d(subset.index, subset['Clay_%'].values, kind = soil_frac, \
                fill_value=(subset['Clay_%'].values[0],subset['Clay_%'].values[-1]), \
                bounds_error=False)
    clay_calu = Clay_calu(depth_mid)/100.

    return sand_calu, silt_calu, clay_calu;

def estimate_rhosoil_vec(swc_fname, depth_mid, ring, soil_frac):
    """
    get Bulk.den
    """
    neo = pd.read_csv(swc_fname, usecols = ['Ring','Depth','Date','Bulk.den'])
    if ring == 'amb':
        subset = neo[neo['Ring'].isin(['R2','R3','R6'])]
    elif ring == 'ele':
        subset = neo[neo['Ring'].isin(['R1','R4','R5'])]
    else:
        subset = neo[neo['Ring'].isin([ring])]
    bulk_den = subset.groupby(by=['Depth']).mean()['Bulk.den']
    f = interp1d(bulk_den.index, bulk_den.values, kind = soil_frac, \
             fill_value=(bulk_den.values[0],bulk_den.values[-1]), bounds_error=False) # fill_value='extrapolate'
    Bulk_den_kg_m = f(depth_mid)*1000. # units: kg m-3
    Bulk_den_g_cm = f(depth_mid)      # units: g cm-3
    return Bulk_den_kg_m, Bulk_den_g_cm

def init_soil_moisture(swc_fname, depth_mid, ring, soil_frac):

    neo = pd.read_csv(swc_fname, usecols = ['Ring','Depth','Date','VWC'])
    neo['Date'] = pd.to_datetime(neo['Date'],format="%d/%m/%y",infer_datetime_format=False)
    neo['Date'] = neo['Date'] - pd.datetime(2012,12,31)
    neo['Date'] = neo['Date'].dt.days
    neo = neo.sort_values(by=['Date','Depth'])

    if ring == 'amb':
        subset = neo[neo['Ring'].isin(['R2','R3','R6'])]
    elif ring == 'ele':
        subset = neo[neo['Ring'].isin(['R1','R4','R5'])]
    else:
        subset = neo[neo['Ring'].isin([ring])]

    neo_mean = subset.groupby(by=["Depth","Date"]).mean()
    neo_mean = neo_mean.xs('VWC', axis=1, drop_level=True)
    date_start = pd.datetime(2012,12,1) - pd.datetime(2012,12,31)
    date_end   = pd.datetime(2013,1,31) - pd.datetime(2012,12,31)
    date_start = date_start.days
    date_end   = date_end.days
    x     = np.concatenate((neo_mean[(25)].index.values,               \
                            neo_mean.index.get_level_values(1).values, \
                            neo_mean[(450)].index.values ))              # time
    y     = np.concatenate(([0]*len(neo_mean[(25)]),                   \
                            neo_mean.index.get_level_values(0).values, \
                           [460]*len(neo_mean[(25)])    ))
    value = np.concatenate((neo_mean[(25)].values, neo_mean.values, neo_mean[(450)].values))
    X     = np.arange(date_start,date_end,1) # 2012-4-30 to 2019-5-11
    Y     = depth_mid
    grid_X, grid_Y = np.meshgrid(X,Y)
    print(grid_X.shape)
    # interpolate
    grid_data = griddata((x, y) , value, (grid_X, grid_Y), method=soil_frac)

    return grid_data[:,30]/100.

def convert_rh_to_qair(rh, tair, press):
    """
    Converts relative humidity to specific humidity (kg/kg)

    Params:
    -------
    tair : float
        deg C
    press : float
        pa
    rh : float
        %
    """

    # Sat vapour pressure in Pa
    esat = calc_esat(tair)

    # Specific humidity at saturation:
    ws = 0.622 * esat / (press - esat)

    # specific humidity
    qair = (rh / 100.0) * ws

    return qair

def calc_esat(tair):
    """
    Calculates saturation vapour pressure

    Params:
    -------
    tair : float
        deg C

    Reference:
    ----------
    * Jones (1992) Plants and microclimate: A quantitative approach to
    environmental plant physiology, p110
    """

    esat = 613.75 * np.exp(17.502 * tair / (240.97 + tair))

    return esat


def estimate_lwdown(tairK, rh):
    """
    Synthesises downward longwave radiation based on Tair RH

    Reference:
    ----------
    * Abramowitz et al. (2012), Geophysical Research Letters, 39, L04808

    """
    zeroC = 273.15

    sat_vapress = 611.2 * np.exp(17.67 * ((tairK - zeroC) / (tairK - 29.65)))
    vapress = np.maximum(5.0, rh) / 100. * sat_vapress
    lw_down = 2.648 * tairK + 0.0346 * vapress - 474.0

    return lw_down

def interpolate_lai(lai_fname, ring):
    """
    """
    df_lai = pd.read_csv(lai_fname, usecols = ['ring','Date','LAIsmooth']) # daily data
    if ring == "amb":
        subset = df_lai[df_lai['ring'].isin(['2','3','6'])]
    elif ring == "ele":
        subset = df_lai[df_lai['ring'].isin(['1','4','5'])]
    else:
        subset = df_lai[df_lai['ring'].isin([ring[-1]])] #???
    subset = subset.groupby(by=["Date"])['LAIsmooth'].mean()

    tmp = pd.DataFrame(subset.values, columns=['LAI'])
    tmp['month'] = subset.values
    tmp['day']   = subset.values
    for i in np.arange(0,len(tmp['LAI']),1):
        tmp['month'][i] = subset.index[i][5:7]
        tmp['day'][i]   = subset.index[i][8:10]
    tmp = tmp.groupby(by=['month','day'])['LAI'].mean()

    rate = subset[-1]/tmp[(4)][(27)]

    day_len_1 = (pd.datetime(2019,7,1) - pd.datetime(2012,12,31)).days
    day_len_2 = (pd.datetime(2018,4,27) - pd.datetime(2012,12,31)).days
    day_len_3 = (pd.datetime(2013,1,1) - pd.datetime(2012,10,26)).days
    day_len_4 = (pd.datetime(2019,1,1) - pd.datetime(2013,1,1)).days
    day_len_5 = (pd.datetime(2019,2,28) - pd.datetime(2012,12,31)).days

    lai = pd.DataFrame(np.arange(np.datetime64('2013-01-01','D'),\
            np.datetime64('2019-07-02','D')), columns=['date'])
    lai['LAI'] = np.zeros(day_len_1)
    lai['LAI'][:day_len_2]          = subset[day_len_3:].values # 2013,1,1 - 2018,4,27
    lai['LAI'][day_len_2:day_len_4] = tmp.values[118:]*rate # 2018,4,28-2018,12,31
    lai['LAI'][day_len_4:day_len_5] = tmp.values[:59]*rate # 2019,1,1-2019,2,28
    lai['LAI'][day_len_5:]          = tmp.values[60:183]*rate # 2019,3,1-2019,7,1

    date = lai['date'] - np.datetime64('2013-01-01T00:00:00')
    lai['Date']  = np.zeros(len(lai))
    for i in np.arange(0,len(lai),1):
        lai['Date'][i] = date.iloc[i].total_seconds()
    grid_x = np.arange(0.,204940800.,1800)

    LAI_interp = np.interp(grid_x, lai['Date'].values, lai['LAI'].values)

    return LAI_interp

def thickness_weighted_average(var, layer_num, zse_vec):
    VAR     = 0.0
    for i in np.arange(0,layer_num,1):
        VAR += var[i]*zse_vec[i]
    VAR = VAR/sum(zse_vec)

    return VAR

if __name__ == "__main__":

    met_fname = "/srv/ccrc/data25/z5218916/data/Eucface_data/met_July2019/eucMet_gap_filled.csv"
    lai_fname = "/srv/ccrc/data25/z5218916/data/Eucface_data/met_July2019/eucLAI.csv"
    swc_fname = "/srv/ccrc/data25/z5218916/data/Eucface_data/swc_at_depth/FACE_P0018_RA_NEUTRON_20120430-20190510_L1.csv"
    stx_fname = "/srv/ccrc/data25/z5218916/data/Eucface_data/soil_texture/FACE_P0018_RA_SOILTEXT_L2_20120501.csv"

    PTF = "Campbell_Cosby_multivariate"
    soil_frac = "nearest" # "linear"
    layer_num = "6":

    for ring in ["R1","R2","R3","R4","R5","R6","amb", "ele"]:
        out_fname = "EucFACE_met_%s.nc" % (ring)
        main(met_fname, lai_fname, swc_fname, stx_fname, out_fname, PTF, soil_frac, layer_num, ring=ring)
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import netCDF4

def get_espresso_temp(time,lat,lon,depth) :    
    #according to doppio model structure , data is from 2009-10-12 to 2017-1-1
    url=get_url(time)
    nc=netCDF4.Dataset(url).variables
    #first find the index of the grid 
    lons=nc['lon_rho'][:]
    lats=nc['lat_rho'][:]
    temp=nc['temp']
    #second find the index of time
    if time<=datetime(2013,5,18):
        espresso_time=nc['ocean_time']
    else:
        espresso_time=nc['time']
    itime = netCDF4.date2index(time,espresso_time,select='nearest')
    index = nearest_point_index2(lon,lat,lons,lats) 
    espresso_depth=nc['h'][index[0][0]][index[1][0]]
    if depth >espresso_depth:# case of bottom
        S_coordinate=1
    else:
        S_coordinate=float(depth)/float(espresso_depth)
    if 0<=S_coordinate<1:
       espresso_temp=temp[itime,35-int(S_coordinate/1.1611635),index[0][0],index[1][0]]# because there are 1.1611635 between each layer
    else:
       espresso_temp=temp[itime][0][index[0][0]][index[1][0]]
    
    return espresso_temp

def get_url(time):
    # hours = int((endtime-starttime).total_seconds()/60/60) # get total hours
    # time_r = datetime(year=2006,month=1,day=9,hour=1,minute=0)
    if (time- datetime(2013,5,18)).total_seconds()/3600>25:
        #url_oceantime = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/hidden/2006_da/his?ocean_time'
        #url_oceantime = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2013_da/his_Best/ESPRESSO_Real-Time_v2_History_Best_Available_best.ncd?time'
        url_oceantime = 'http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best?time[0:1:31931]'
        oceantime = netCDF4.Dataset(url_oceantime).variables['time'][:]    #if url2006, ocean_time.
        t1 = (time - datetime(2013,5,18)).total_seconds()/3600 # for url2006 it's 2006,01,01; for url2013, it's 2013,05,18, and needed to be devide with 3600
        index1 = closest_num(t1, oceantime)
        # url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2006_da/his?h[0:1:81][0:1:129],s_rho[0:1:35],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],mask_rho[0:1:81][0:1:129],u[{0}:1:{1}][0:1:35][0:1:81][0:1:128],v[{0}:1:{1}][0:1:35][0:1:80][0:1:129]'
        #url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/hidden/2006_da/his?s_rho[0:1:35],h[0:1:81][0:1:129],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],temp[{0}:1:{1}][0:1:35][0:1:81][0:1:129],ocean_time'
        #url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2013_da/his_Best/ESPRESSO_Real-Time_v2_History_Best_Available_best.ncd?h[0:1:81][0:1:129],s_rho[0:1:35],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],temp[{0}:1:{1}][0:1:35][0:1:81][0:1:129],time' 
        url = 'http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best?s_rho[0:1:35],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],time[0:1:32387],h[0:1:81][0:1:129],temp[0:1:32387][0:1:35][0:1:81][0:1:129]'
        url = url.format(index1)
    else :
        #url_oceantime = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/hidden/2006_da/his?ocean_time'
        url_oceantime='http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2009_da/his?ocean_time'#[0:1:19145]
        oceantime = netCDF4.Dataset(url_oceantime).variables['ocean_time'][:]    #if url2006, ocean_time.
        t1 = (time - datetime(2006,1,1)).total_seconds() # for url2006 it's 2006,01,01; for url2013, it's 2013,05,18, and needed to be devide with 3600
        index1 = closest_num(t1, oceantime)
        #print 'index1' ,index1
        #url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/hidden/2006_da/his?s_rho[0:1:35],h[0:1:81][0:1:129],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],temp[{0}:1:{1}][0:1:35][0:1:81][0:1:129],ocean_time'
        url='http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2009_da/his?s_rho[0:1:35],h[0:1:81][0:1:129],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],ocean_time[0:1:19145],temp[0:1:19145][0:1:35][0:1:81][0:1:129]'
        url = url.format(index1)
    return url

def nearest_point_index2(lon, lat, lons, lats):
    d = dist(lon, lat, lons ,lats)
    min_dist = np.min(d)
    index = np.where(d==min_dist)
    return index
def dist(lon1, lat1, lon2, lat2):
    R = 6371.004
    lon1, lat1 = angle_conversion(lon1), angle_conversion(lat1)
    lon2, lat2 = angle_conversion(lon2), angle_conversion(lat2)
    l = R*np.arccos(np.cos(lat1)*np.cos(lat2)*np.cos(lon1-lon2)+\
                        np.sin(lat1)*np.sin(lat2))
    return l
def angle_conversion(a):
    a = np.array(a)
    return a/180*np.pi     

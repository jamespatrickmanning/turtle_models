# testing the "get_doppio" function
# found another one called get_doppio_test.py which has different method not using "fitting"
from datetime import datetime as dt
from datetime import timedelta
import datetime
from dateutil import parser
import pandas as pd
import pytz
import glob
import numpy as np
import netCDF4
import zlconversions as zl # Lei Zhao's module


def doppio_coordinate(lat,lon):
    f1=-0.8777722604596849*lat-lon-23.507489034447012>=0
    f2=-1.072648270137022*lat-40.60872567829448-lon<=0
    f3=1.752828434063416*lat-131.70051451008493-lon>=0
    f4=1.6986954871237598*lat-lon-144.67649951783605<=0
    if f1 and f2 and f3 and f4:
        return True
    else:
        return False

def fitting(point,lat,lon):
#represent the value of matrix
    ISum = 0.0
    X1Sum = 0.0
    X2Sum = 0.0
    X1_2Sum = 0.0
    X1X2Sum = 0.0
    X2_2Sum = 0.0
    YSum = 0.0
    X1YSum = 0.0
    X2YSum = 0.0

    for i in range(0,len(point)):
        
        x1i=point[i][0]
        x2i=point[i][1]
        yi=point[i][2]

        ISum = ISum+1
        X1Sum = X1Sum+x1i
        X2Sum = X2Sum+x2i
        X1_2Sum = X1_2Sum+x1i**2
        X1X2Sum = X1X2Sum+x1i*x2i
        X2_2Sum = X2_2Sum+x2i**2
        YSum = YSum+yi
        X1YSum = X1YSum+x1i*yi
        X2YSum = X2YSum+x2i*yi

#  matrix operations
# _mat1 is the mat1 inverse matrix
    m1=[[ISum,X1Sum,X2Sum],[X1Sum,X1_2Sum,X1X2Sum],[X2Sum,X1X2Sum,X2_2Sum]]
    mat1 = np.matrix(m1)
    m2=[[YSum],[X1YSum],[X2YSum]]
    mat2 = np.matrix(m2)
    _mat1 =mat1.getI()
    mat3 = _mat1*mat2

# use list to get the matrix data
    m3=mat3.tolist()
    a0 = m3[0][0]
    a1 = m3[1][0]
    a2 = m3[2][0]
    y = a0+a1*lat+a2*lon

    return y
def get_doppio(lat=0,lon=0,depth=99999,time='2018-11-12 12:00:00'):
    """
    notice:
        the format of time is like "%Y-%m-%d %H:%M:%S"
        the default depth is under the bottom depth
    the module only output the temperature of point location
    """
    import datetime
    date_time=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') # transform time format
    if (date_time -datetime.datetime(2017,11,1,0,0,0)).total_seconds()<0:
        point_temp=''
        print('the date can\'t be earlier than 2017-11-1')
        return point_temp
    for i in range(0,7): # look back 7 hours for data
        url_time=(date_time-datetime.timedelta(hours=i)).strftime('%Y-%m-%d')#
        url=zl.get_doppio_url(url_time)
        nc=netCDF4.Dataset(url)
        lons=nc.variables['lon_rho'][:]
        lats=nc.variables['lat_rho'][:]
        temp=nc.variables['temp']
        doppio_time=nc.variables['time']
        doppio_depth=nc.variables['h'][:]
        min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
        min_diff_index=0
        
        for i in range(1,157): # 6.5 days and 24
            diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
            if diff_time<min_diff_time:
                min_diff_time=diff_time
                min_diff_index=i
                
        min_distance=zl.dist(lat1=lat,lon1=lon,lat2=lats[0][0],lon2=lons[0][0])
        index_1,index_2=0,0
        for i in range(len(lons)):
            for j in range(len(lons[i])):
                if min_distance>zl.dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j]):
                    min_distance=zl.dist(lat1=lat,lon1=lon,lat2=lats[i][j],lon2=lons[i][j])
                    index_1=i
                    index_2=j
        if depth==99999:# case of bottom
            S_coordinate=1
        else:
            S_coordinate=float(depth)/float(doppio_depth[index_1][index_2])
        if 0<=S_coordinate<1:
            point_temp=temp[min_diff_index][39-int(S_coordinate/0.025)][index_1][index_2]# because there are 0.025 between each later
        elif S_coordinate==1:
            point_temp=temp[min_diff_index][0][index_1][index_2]
        else:
            return 9999
        if np.isnan(point_temp):
            continue
        if min_diff_time<datetime.timedelta(hours=1):
            break
    return point_temp

def get_doppio1(lat=0,lon=0,depth='bottom',time='2018-11-12 12:00:00',fortype='temperature'):
    """
    notice:
        the format of time is like "%Y-%m-%d %H:%M:%S" this time is utctime  or it can also be datetime
        the depth is under the bottom depth
    the module only output the temperature of point location
    if fortype ='temperature',only return temperature, else return temperature and depth
    """
    if not doppio_coordinate(lat,lon):
        print('the lat and lon out of range in doppio')
        return np.nan,np.nan
    if type(time)==str:
        date_time=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') # transform time format
    elif type(time)==datetime.datetime:
        date_time=time
    else:
        print('check the type of input time in get_doppio')
    for m in range(0,1):
        try:
            url_time=(date_time-datetime.timedelta(days=m)).strftime('%Y-%m-%d')#
            url=zl.get_doppio_url(url_time)
            #get the data 
            nc=netCDF4.Dataset(url)
            lons=nc.variables['lon_rho'][:]
            lats=nc.variables['lat_rho'][:]
            doppio_time=nc.variables['time']
            doppio_rho=nc.variables['s_rho']
            doppio_temp=nc.variables['temp']
            doppio_h=nc.variables['h']
        except:
            print('error',date_time)
            continue
        min_diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[0]))-date_time)
        min_diff_index=0
        for i in range(1,len(doppio_time)):
            diff_time=abs(datetime.datetime(2017,11,1,0,0,0)+datetime.timedelta(hours=int(doppio_time[i]))-date_time)
            if diff_time<min_diff_time:
                min_diff_time=diff_time
                min_diff_index=i
        #calculate the min,second small and third small distance and index
        target_distance=zl.dist(lat1=lats[0][0],lon1=lons[0][0],lat2=lats[0][1],lon2=lons[0][1])
        index_1,index_2=zl.find_nd(target=target_distance,lat=lat,lon=lon,lats=lats,lons=lons)

        #calculate the optimal layer index
        layer_index=0  #specify the initial layer index
        #print (depth)
        if depth!='bottom':
            #h_distance=depth+doppio_rho[0]*doppio_h[index_1,index_2]  #specify the initial distanc of high
            h_distance=doppio_h[index_1,index_2]# bottom depth
            for i in range(len(doppio_rho)):
                #if abs(depth+doppio_rho[0]*doppio_h[index_1,index_2])<=h_distance:
                if depth<abs(doppio_rho[i])*doppio_h[index_1,index_2]:
                    #h_distance=depth+doppio_rho[i]*doppio_h[index_1,index_2]
                    layer_index=i
                if depth>doppio_h[index_1,index_2]:
                    print ("the depth is out of the depth of bottom:"+str(doppio_h[index_1,index_2]))
                    break
        if index_1==0:
            index_1=1
        if index_1==len(lats)-1:
            index_1=len(lats)-2
        if index_2==0:
            index_2=1
        if index_2==len(lats[0])-1:
            index_2=len(lats[0])-2
        while True:
            point=[[lats[index_1][index_2],lons[index_1][index_2],doppio_temp[min_diff_index,layer_index,index_1,index_2]],\
            [lats[index_1-1][index_2],lons[index_1-1][index_2],doppio_temp[min_diff_index,layer_index,(index_1-1),index_2]],\
            [lats[index_1+1][index_2],lons[index_1+1][index_2],doppio_temp[min_diff_index,layer_index,(index_1+1),index_2]],\
            [lats[index_1][index_2-1],lons[index_1][index_2-1],doppio_temp[min_diff_index,layer_index,index_1,(index_2-1)]],\
            [lats[index_1][index_2+1],lons[index_1][index_2+1],doppio_temp[min_diff_index,layer_index,index_1,(index_2+1)]]]
            break
        point_temp=fitting(point,lat,lon)
        if np.isnan(point_temp):
            continue
        if min_diff_time<datetime.timedelta(hours=1):
            break
    if fortype=='temperature':
        return point_temp
    else:
        return point_temp,doppio_h[index_1,index_2]
#
'''
#HARDCODES ##########
lat,lon=37.09133148,-75.18039703# mid Cape Cod Bay
time='2018-06-23 00:00:00' # mid-August
depth=4#'bottom'
# main
model_temp=get_doppio(lat,lon,depth=depth,time=time)
print (model_temp)
'''
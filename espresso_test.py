import netCDF4
import numpy as np
from datetime import datetime
import get_espresso_model
#get the same temp no matter what the depth
#the data duration offunction 'get_espresso_temp1' from 2009-10-12 to 2017-1-1
#the data duration offunction 'get_espresso_temp' from 2009-10-12 to 2013-5-18
time= datetime(2012,3,5)
lat,lon= 39 , -70
depth = 20

temp1 = get_espresso_temp1(time,lat,lon,depth)
temp2 = get_espresso_temp(time,lat,lon,depth)
print(temp1)
print(temp2)
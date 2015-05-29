# -*- coding: utf-8 -*-
"""
Created on Thu May 28 12:36:55 2015

@author: jpeacock-pr
"""
#==============================================================================
#     IMPORTS
#==============================================================================
import mtpy.usgs.zen as zen
from cStringIO import StringIO
import sys
import os
import time
#==============================================================================
#     VAIRABLES
#==============================================================================

copy_dir = r"c:\MT"
station = 'mb001'
copy_date = None

#==============================================================================
# this should capture all the print statements from zen
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

#==============================================================================
st = time.time()
#--> Copy data from files
if copy_date is None:
    zen.copy_from_sd(station, save_path=copy_dir)
else:
    zen.copy_from_sd(station, save_path=copy_dir, copy_date=copy_date,
                     copy_type='after')

#--> process data
station_dir = os.path.join(copy_dir, station) 
with Capturing() as output:
    z2edi = zen.Z3D_to_edi(station_dir)
    z2edi.birrp_exe = r"c:\MinGW32-xy\Peacock\birrp52\birrp52_3pcs6e9pts.exe"
    z2edi.coil_cal_path = r"c:\MT\Ant_calibrations"
    try:
        rp = z2edi.process_data(df_list=[256])
    except zen.mtex.MTpyError_inputarguments:
        print '==> Data not good!! Did not produce a proper .edi file' 
        et = time.time()
        print '--> took {0} seconds'.format(et-st)

#--> write log file
log_fid = open(os.path.join(station_dir, 'Processing.log'), 'w')
log_fid.write('\n'.join(output))
log_fid.close()

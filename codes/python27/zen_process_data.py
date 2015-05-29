# -*- coding: utf-8 -*-
"""
Created on Thu May 28 12:36:55 2015

This code will down load Z3D files from a Zen that is in SD Mode, 
convert the Z3D files to ascii format, then process them for each
sampling rate using Alan Chave's BIRRP code.  The outputs are then
converted to .edi files and plotted.

You need 2 things to run this code:
    * mtpy --> a Python package for MT and can be found at
	           https://github.com/geophysics/mtpy
    * BIRRP executable --> you can get this from Alan Chave at WHOI if you are 
                	          using it for non-commercial projects.
                           
..note:: This code is quite specific to my setup, so let me know what doesn't 
         work for you so I can generalize it.

@author: jpeacock
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
def compute_mt_response(survey_dir, station='mt000', copy_date=None, 
                        birrp_exe=r"c:\MinGW32-xy\Peacock\birrp52\birrp52_3pcs6e9pts.exe", 
                        ant_calibrations=r"c:\MT\Ant_calibrations",
                        process_df_list=[256]):
    """
    This code will down load Z3D files from a Zen that is in SD Mode, 
    convert the Z3D files to ascii format, then process them for each
    sampling rate using Alan Chave's BIRRP code.  The outputs are then
    converted to .edi files and plotted.
    
    You need 2 things to run this code:
        * mtpy --> a Python package for MT and can be found at
    	           https://github.com/geophysics/mtpy
        * BIRRP executable --> you can get this from Alan Chave at WHOI 
                               if you are using it for non-commercial projects.
                               
    ..note:: This code is quite specific to my setup, so let me know what
             doesn't work for you so I can generalize it.
    
    Arguments
    ----------------
        **survey_dir** : string
                         full path to the directory where you are storing 
                         the station data.  ie. /home/MT/Survey_00
                         
        **station** : string
                      name of the station you are down loading.
                      *default* is 'mt000'
                      
        **copy_date** : string
                        copy all files on and after this date
                        format is YYYY-MM-DD
                        *default* is None, which copies all files on the SD
                        cards.
                                  
        **birrp_exe** : string
                        full path to the BIRRP executable on your machine
                        *default* is the location on my machine
        
        **ant_calibrations** : string
                               full path to a folder that contains the coil
                               calibration data.  These must be in seperate
                               .csv files for each coil named by corresponding
                               coil name. If you're coil is 2884, then you
                               need a calibration file named Ant2884_cal.csv
                               in which the data is freq,real,imaginary 
                               
        **process_df_list** : list
                              list of sampling rates to process
                              
                               
    Returns
    -----------------
        **rp_plot** : mtpy.imaging.plotnresponses object
                      ploting object of data, if you want to change how the
                      output is plot change the attributes of rp_plot
                      
    Outputs
    -----------------
        **copy_from_sd.log** : file
                               contains information on how files were copied
                               from the SD cards.
                               
        **processing.log** : file
                             a log file of how the program ran
        
        **survey_dir/station/TS** : directory
                                   contains the time series data in .ascii 
                                   format
                                   
        **survey_dir/station/TS/BF** : directory
                                       contains the processing results from
                                       BIRRP for each sampling rate in the
                                       data in subsequent directories
                             
        **survey_dir/station/TS/station.cfg** : file
                                                configuration file of the
                                                station parameters
                                                
        
                             
    Example
    ------------------------
        >>> import zen_processing_data as zpd
        >>> zpd.compute_mt_response(r"/home/mt/survey_00", 
                                    station='mt010',
                                    copy_date='2015-05-22',
                                    birrp_exe=r"/home/bin/birrp52.exe",
                                    ant_calibrations=r"/home/ant_calibrations",
                                    process_df_list=[1024, 256])
    """
                        
    station_dir = os.path.join(survey_dir, station)
               
    st = time.time()
    #--> Copy data from files
    try:
        if copy_date is None:
            zen.copy_from_sd(station, save_path=survey_dir)
        else:
            zen.copy_from_sd(station, save_path=survey_dir, 
                             copy_date=copy_date, copy_type='after')
    except IOError:
        print 'No files copied from SD cards'
        print 'Looking in  {0} for Z3D files'.format(station_dir)
    
    #--> process data
     
    with Capturing() as output:
        z2edi = zen.Z3D_to_edi(station_dir)
        z2edi.birrp_exe = birrp_exe
        z2edi.coil_cal_path = ant_calibrations
        try:
            rp = z2edi.process_data(df_list=process_df_list)
        except zen.mtex.MTpyError_inputarguments:
            print '==> Data not good!! Did not produce a proper .edi file' 
            et = time.time()
            print '--> took {0} seconds'.format(et-st)
    
    #--> write log file
    log_fid = open(os.path.join(station_dir, 'Processing.log'), 'w')
    log_fid.write('\n'.join(output))
    log_fid.close()
    
    return rp

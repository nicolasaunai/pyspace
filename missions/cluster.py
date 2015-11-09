

import datetime as dtime
import numpy as np
import requests
import urllib
import dateutil.parser
import pandas as pd
from scipy.constants import k as kB



def csa_orbit_url(date):

    if isinstance(date,str):
        thedate = dateutil.parser.parse(date).date()
    else:
        thedate=date

    url='http://www.cluster.rl.ac.uk/csdsweb/ORBP1/CL_QL_ORB2_'
    ymj = dtime.datetime.strftime(thedate, "%Y%m%d")
    urltot = url+ymj+'.gif'
    tmp = thedate
    while requests.get(urltot).status_code == 404 :
        tmp = tmp - dtime.timedelta(days=1)
        ymj = dtime.datetime.strftime(tmp, "%Y%m%d")
        urltot = url +ymj+ '.gif'

    return urltot






def csa_orbit_img(date):

    url = csa_orbit_url(date)
    ymj = dtime.datetime.strftime(date, "%Y%m%d")
    urllib.urlretrieve (url, 'orbit_%s.png' % (ymj))
    return 'orbit_%s.png' % (ymj)






def GetHIA(fcdf):

    n           = fcdf['density__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:]
    t           = fcdf['time_tags__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:]
    Vgse        = fcdf['velocity_gse__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:]
    Tpara       = fcdf['temp_par__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:]
    Tperp       = fcdf['temp_perp__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:]
    V           = np.sqrt(Vgse[:,0]**2 + Vgse[:,1]**2 + Vgse[:,2]**2)
    datanp      = np.zeros((n.size,4))
    datanp[:,0] = n
    datanp[:,1] = V
    datanp[:,2] = Tpara*1e6*kB/1.6e-19
    datanp[:,3] = Tperp*1e6*kB/1.6e-19
    data        = pd.DataFrame(data=datanp, index=t, columns=['n','V','Tpara','Tperp'])

    return data





def GetFGM(fcdf):
    t = fcdf['time_tags__C1_CP_FGM_SPIN'][:]
    B = fcdf['B_mag__C1_CP_FGM_SPIN'][:]
    data = pd.DataFrame(data=B, index=t, columns=['B'])
    return data



def GetPitchAngle(fcdf):

    tpa   = fcdf['time_tags__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:]
    df    = fcdf['Differential_Particle_Flux__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:]
    E     = fcdf['energy_table__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:]
    pitch = fcdf['pitch_angle__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:]

    return (tpa, E, pitch, df)

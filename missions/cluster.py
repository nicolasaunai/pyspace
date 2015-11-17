

import datetime as dtime
import numpy as np
import requests
import urllib
import dateutil.parser
import pandas as pd
from scipy.constants import k as kB
import spacepy.pycdf as pycdf






def csa_orbit_url(date):
    """
    build a URL for orbit images on CSA website

    This function returns the url for the orbit image
    on the CSA website, at the desired date.

    parameters:

        date : string or datetime object
    """

    if isinstance(date,str):
        thedate = dateutil.parser.parse(date).date()
    else:
        thedate=date

    # build the url for the specified date
    # and decrement days ir error 404 arises and
    # until 200 comes.

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
    """
    download an orbit image at the specified date
    parameter:
        date : string or datetime
    """

    url = csa_orbit_url(date)
    ymj = dtime.datetime.strftime(date, "%Y%m%d")
    urllib.urlretrieve (url, 'orbit_%s.png' % (ymj))

    return 'orbit_%s.png' % (ymj)






def GetHIA(filename):

    """
    get data from HIA cdf filename

    returns a Pandas DataFrame with data extracted from
    a specified CDF file.
    """

    print filename
    fcdf        = pycdf.CDF(filename)

    n           = fcdf['density__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:].copy()
    t           = fcdf['time_tags__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:].copy()
    Vgse        = fcdf['velocity_gse__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:].copy()
    Tpara       = fcdf['temp_par__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:].copy()
    Tperp       = fcdf['temp_perp__C1_CP_CIS-HIA_ONBOARD_MOMENTS'][:].copy()
    V           = np.sqrt(Vgse[:,0]**2 + Vgse[:,1]**2 + Vgse[:,2]**2)
    datanp      = np.zeros((n.size,4))
    datanp[:,0] = n
    datanp[:,1] = V
    datanp[:,2] = Tpara*1e6*kB/1.6e-19
    datanp[:,3] = Tperp*1e6*kB/1.6e-19
    data        = pd.DataFrame(data=datanp, index=t, columns=['n','V','Tpara','Tperp'])
    fcdf.close()

    return data





def GetFGM(filename):

    fcdf = pycdf.CDF(filename)

    t = fcdf['time_tags__C1_CP_FGM_SPIN'][:].copy()
    B = fcdf['B_mag__C1_CP_FGM_SPIN'][:].copy()
    data = pd.DataFrame(data=B, index=t, columns=['B'])
    fcdf.close()
    return data



def GetPitchAngle(filename):

    fcdf  = pycdf.CDF(filename)

    tpa   = fcdf['time_tags__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:].copy()
    df    = fcdf['Differential_Particle_Flux__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:].copy()
    E     = fcdf['energy_table__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:].copy()
    pitch = fcdf['pitch_angle__C1_CP_CIS-HIA_PAD_HS_MAG_IONS_PF'][:].copy()

    fcdf.close()

    return (tpa, E, pitch, df)






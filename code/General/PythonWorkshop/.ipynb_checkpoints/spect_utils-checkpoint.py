import numpy as np

from astropy.wcs import WCS
from astropy.io import fits

def read_spec(filename):
    '''Read a UVES spectrum from the ESO pipeline

    Parameters
    ----------
    filename : string
       name of the fits file with the data

    Returns
    -------
    wavelength : np.ndarray
        wavelength (in Ang)
    flux : np.ndarray
        flux (in erg/s/cm**2)
    date_obs : string
        time of observation
    '''
    sp = fits.open(filename)
    header = sp[0].header

    wcs = WCS(header)
    #make index array
    index = np.arange(header['NAXIS1'])

    wavelength = wcs.wcs_pix2world(index[:,np.newaxis], 0)
    wavelength = wavelength.flatten()
    flux = sp[0].data

    date_obs = header['Date-OBS']
    return wavelength, flux, date_obs
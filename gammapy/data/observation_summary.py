# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
from astropy.units import Quantity
from astropy.coordinates import SkyCoord, Angle

from .observation import ObservationTable

__all__ = [
    'ObservationTableSummary',
]

class ObservationTableSummary(object):
    """Observation table summary.

    Class allowing to summarize informations conatained in 
    Observation index table (`~gammapy.data.ObservationTable`)

    Parameters:
    -----------
    obs_table:  `~gammapy.data.ObservationTable`
        Observation index table
    target_pos: `~astropy.coordinates.SkyCoord`
        Target position
    """

    def __init__(self, obs_table, target_pos=None):
        self.obs_table = obs_table
        self.target_pos = target_pos

    @property
    def _offset(self):
        """
        Compute offsets of the different observations
        
        Returns
        -------
        vector : `~numpy.array`
            Offsets
        """
        pnt_pos = SkyCoord(self.obs_table['RA_PNT'],
                           self.obs_table['DEC_PNT'],
                           unit='deg')

        offset = pnt_pos.separation(self.target_pos)
        
        return offset.degree
    
    def plot_zenith_distribution(self, ax=None, bins=None):
        """
        Construct the zenith distribution of the observations
        
        Parameters
        ----------
        ax : `~matplolib.axes`, optional
            Axis
        bins : integer
            number of bins, optional
        range : `range`
            range of the x axis, optional

        Returns
        --------
        ax : `~matplolib.axes`
            Axis
        """
        import matplotlib.pyplot as plt
        ax = plt.gca() if ax is None else ax

        zenith = self.obs_table['ZEN_PNT']

        if bins is None:
            bins = np.linspace(0, zenith.max() + 5, 30)

        ax.hist(zenith, bins=bins)
        ax.set_title('Zenith distribution')
        ax.set_xlabel('Zenith (Deg)')
        ax.set_ylabel('#Entries')
        
        return ax

    def plot_offset_distribution(self, ax=None, bins=None):
        """
        Construct the offset distribution of the observations
        
        Parameters
        ----------
        ax : `~matplolib.axes`, optional
            Axis
        bins : integer
            number of bins, optional

        Returns
        -------
        ax : `~matplolib.axes`
            Axis
        """
        import matplotlib.pyplot as plt
        ax = plt.gca() if ax is None else ax
        
        offset = self._offset

        if bins is None:
            bins = np.linspace(0, offset.max()+0.5, 10)
        ax.hist(offset, bins=bins)
        ax.set_title('Offset distribution')
        ax.set_xlabel('Offset (Deg)')
        ax.set_ylabel('#Entries')
        
        return ax

    def __str__(self):
        """Summary report"""
        ss = '*** Observation summary ***\n'
        ss += 'Target position: {}\n'.format(self.target_pos)
        
        ss += 'Number of observations: {}\n'.format(len(self.obs_table))
        
        livetime = Quantity(sum(self.obs_table['LIVETIME']), 'second')
        ss += 'Livetime: {:.2f}\n'.format(livetime.to('hour'))
        zenith = self.obs_table['ZEN_PNT']
        ss += 'Zenith angle: (mean={:.2f}, std={:.2f})\n'.format(zenith.mean(),
                                                                 zenith.std())    
        offset = self._offset
        ss += 'Offset: (mean={:.2f}, std={:.2f})\n'.format(offset.mean(),
                                                           offset.std())  
        
        return ss

    def show_in_browser(self):
        """Make HTML file and images in tmp dir, open in browser"""
        raise NotImplementedError

# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
from . import SkyRegionList, PixRegionList, PixCircleRegion
from astropy.coordinates import Angle

__all__ = [
    'find_reflected_regions',
]


def find_reflected_regions(region, center, exclusion_mask,
                           angle_increment=None, min_distance=None):
    """Find reflected regions.

    Converts to pixel coordinates internally

    Parameters
    ----------
    region : `~gammapy.region.Region`
        Region
    center : `~astropy.coordinates.SkyCoord`
        Rotation point
    exclusion_mask : `~gammapy.region.ExclusionMask`
        Exlusion mask
    angle_increment : `~astropy.coordinates.Angle`
        Rotation angle for each step
    min_dinstance : `~astropy.coordinates.Angle`
        Minimal distance from input region

    Returns
    -------
    regions : `~gammapy.region.SkyRegionList`
        Reflected regions list
    """
    
    if angle_increment is None:
        angle_increment = Angle('0.1 rad')
    if min_distance is None:
        min_distance = Angle('0 rad')
    
    reflected_regions_pix = PixRegionList()
    wcs = exclusion_mask.wcs
    pix_region = region.to_pixel(wcs)
    val = center.to_pixel(wcs, origin=1)
    pix_center = (float(val[0]), float(val[1]))
    offset = pix_region.offset(pix_center)
    angle = pix_region.angle(pix_center)    
    min_ang = Angle(2 * pix_region.radius / offset , 'rad')
    max_angle = angle + Angle('360deg') - min_ang - min_distance

    curr_angle = angle + min_ang + min_distance
    found_region = False
    while curr_angle < max_angle:
        test_pos = _compute_xy(pix_center, offset, curr_angle)
        test_reg = PixCircleRegion(test_pos, pix_region.radius)
        if not test_reg.is_inside_exclusion(exclusion_mask):
            reflected_regions_pix.append(test_reg)
            curr_angle = curr_angle + min_ang
        else:
            curr_angle = curr_angle + angle_increment
     
    reflected_regions = reflected_regions_pix.to_sky(wcs)
    return reflected_regions

def _compute_xy(pix_center, offset, angle):
    """Compute x, y position for a given position angle and offset"""
    dx = offset * np.sin(angle)
    dy = offset * np.cos(angle)
    x = pix_center[0] + dx
    y = pix_center[1] + dy
    return (x, y)

   

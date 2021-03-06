# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
from numpy.testing.utils import assert_allclose, assert_equal
from astropy.convolution import Gaussian2DKernel
from ...utils.testing import requires_dependency, requires_data
from ...detect import compute_ts_map
from ...datasets import load_poisson_stats_image
from ...image import SkyImage, SkyImageCollection

@requires_dependency('scipy')
@requires_dependency('skimage')
@requires_data('gammapy-extra')
def test_compute_ts_map(tmpdir):
    """Minimal test of compute_ts_map"""
    filenames = load_poisson_stats_image(extra_info=True, return_filenames=True)
    data = SkyImageCollection()
    data.counts = SkyImage.read(filenames['counts'])
    data.background = SkyImage.read(filenames['background'])
    data.exposure = SkyImage.read(filenames['exposure'])

    kernel = Gaussian2DKernel(2.5)
    for _, func in zip(['counts', 'background', 'exposure'], [np.nansum, np.nansum, np.mean]):
        data[_] = data[_].downsample(2, func)

    result = compute_ts_map(data.counts, data.background, data.exposure, kernel,
                            method='leastsq iter')
    for name, order in zip(['ts', 'amplitude', 'niter'], [2, 5, 0]):
        result[name].data = np.nan_to_num(result[name].data)
        result[name] = result[name].upsample(2, order=order)

    assert_allclose(1705.840212274973, result.ts.data[99, 99], rtol=1e-3)
    assert_allclose([[99], [99]], np.where(result.ts.data == result.ts.data.max()))
    assert_allclose(3, result.niter.data[99, 99])
    assert_allclose(1.0227934338735763e-09, result.amplitude.data[99, 99], rtol=1e-3)


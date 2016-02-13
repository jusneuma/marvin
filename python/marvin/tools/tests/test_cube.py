#!/usr/bin/env python

import os
import unittest
from marvin.tools.cube import Cube
from marvin.tools.core import MarvinError
from marvin import config


class TestCube(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.outver = 'v1_5_1'
        cls.filename = os.path.join(os.getenv('MANGA_SPECTRO_REDUX'), cls.outver, '8485/stack/manga-8485-1901-LOGCUBE.fits.gz')
        cls.mangaid = '1-209232'
        cls.plate = 8485
        cls.plateifu = '8485-1901'
        cls.ra = 232.544703894
        cls.dec = 48.6902009334
        config.drpver = cls.outver

        cls.cubeFromFile = Cube(filename=cls.filename)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cube_loadfail(self):
        with self.assertRaises(AssertionError) as cm:
            Cube()
        self.assertIn('Enter filename, plateifu, or mangaid!',
                      str(cm.exception))

    def test_cube_load_from_local_file_by_filename_success(self):
        cube = Cube(filename=self.filename)
        self.assertIsNotNone(cube)
        self.assertEqual(self.filename, cube.filename)

    def test_cube_load_from_local_file_by_filename_fail(self):
        self.filename = 'not_a_filename.fits'
        self.assertRaises(MarvinError, lambda: Cube(filename=self.filename))
        # errMsg = '{0} does not exist. Please provide full file path.'.format(self.filename)
        # with self.assertRaises(FileNotFoundError) as cm:
        #     Cube(filename=self.filename)
        # self.assertIn(errMsg, cm.exception.args)

    def test_cube_load_from_local_database_success(self):
        """does not work yet"""
        cube = Cube(mangaid=self.mangaid)
        self.assertIsNotNone(cube)
        self.assertEqual(self.mangaid, cube.mangaid)
        self.assertEqual(self.plate, cube.plate)
        self.assertEqual(self.dec, cube.dec)
        self.assertEqual(self.ra, cube.ra)

    def _test_getSpectrum(self, cube, idx, expect, **kwargs):
        """Convenience method to test getSpectrum."""

        spectrum = cube.getSpectrum(**kwargs)
        self.assertAlmostEqual(spectrum[idx], expect, places=5)

    def _test_getSpectrum_raise_exception(self, message, excType=AssertionError, **kwargs):
        """Convenience method to test exceptions raised by getSpectrum."""

        with self.assertRaises(excType) as ee:
            self.cubeFromFile.getSpectrum(**kwargs)

        self.assertIn(message, str(ee.exception))

    def test_getSpectrum_inputs(self):
        """Tests exceptions when getSpectrum gets inappropriate inputs."""

        self._test_getSpectrum_raise_exception(
            'Either use (x, y) or (ra, dec)', x=1, ra=1)

        self._test_getSpectrum_raise_exception(
            'Either use (x, y) or (ra, dec)', x=1, dec=1, ra=1)

        self._test_getSpectrum_raise_exception('Specify both x and y', x=1)

        self._test_getSpectrum_raise_exception('Specify both ra and dec', ra=1)

        self._test_getSpectrum_raise_exception(
            'You need to specify either (x, y) or (ra, dec)',
            excType=ValueError)

    def test_getSpectrum_outside_cube(self):
        """Tests getSpectrum when the input coords are outside the cube."""

        for xTest, yTest in [(-50, 1), (50, 1), (1, -50), (1, 50)]:
            self._test_getSpectrum_raise_exception(
                'pixel coordinates outside cube', x=xTest, y=yTest)

        for raTest, decTest in [(1., 1.), (100, 60),
                                (232.546383, 1.), (1., 48.6883954)]:
            self._test_getSpectrum_raise_exception(
                'pixel coordinates outside cube', ra=raTest, dec=decTest)

    def test_getSpectrum_file_flux_x_y(self):
        """Tests getSpectrum from a file cube with x, y inputs."""
        # TODO: check that the expected value is correct.

        expect = -0.10531016
        self._test_getSpectrum(self.cubeFromFile, 10, expect, x=10, y=5)

    def test_getSpectrum_file_flux_ra_dec(self):
        """Tests getSpectrum from a file cube with ra, dec inputs."""
        # TODO: check that the expected value is correct.

        expect = 0.017929086
        self._test_getSpectrum(self.cubeFromFile, 3000, expect,
                               ra=232.546383, dec=48.6883954)


if __name__ == '__main__':
    # set to 1 for the usual '...F..' style output, or 2 for more verbose output.
    verbosity = 2
    unittest.main(verbosity=verbosity)

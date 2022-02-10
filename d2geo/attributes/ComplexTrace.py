# -*- coding: utf-8 -*-
"""
Complex Trace Attributes for Seismic Data

@author: Braden Fitz-Gerald
@email: braden.fitzgerald@gmail.com

"""

# Import Libraries
import dask.array as da
import numpy as np

try:
    import cupy as cp
    import cusignal
    USE_CUPY = True
except Exception:
    USE_CUPY = False

from . import util
from .Base import BaseAttributes
from .SignalProcess import SignalProcess as sp


class ComplexAttributes(BaseAttributes):
    """
    Description
    -----------
    Class object containing methods for computing complex trace attributes
    from 3D seismic data.

    Methods
    -------
    hilbert_transform
    envelope
    instantaneous_phase
    cosine_instantaneous_phase
    relative_amplitude_change
    instantaneous_frequency
    instantaneous_bandwidth
    dominant_frequency
    frequency_change
    sweetness
    quality_factor
    response_phase
    response_frequency
    response_amplitude
    apparent_polarity
    """
    def __init__(self, use_cuda=False):
        """
        Description
        -----------
        Constructor of complex attribute class.

        Keywork Arguments
        ----------
        use_cuda : Boolean, variable to set CUDA usage
        """
        super().__init__(use_cuda=use_cuda)

    def hilbert_transform(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Hilbert Transform of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        kernel = (1, 1, 25)
        darray, chunks_init = self.create_array(darray, kernel,
                                                preview=preview)
        if USE_CUPY and self._use_cuda:
            analytical_trace = darray.map_blocks(cusignal.hilbert,
                                                 dtype=darray.dtype)
        else:
            analytical_trace = darray.map_blocks(util.hilbert,
                                                 dtype=darray.dtype)
        result = util.trim_dask_array(analytical_trace, kernel)

        return(result)

    def envelope(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Envelope of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        kernel = (1, 1, 25)
        darray, chunks_init = self.create_array(darray, kernel,
                                                preview=preview)
        if USE_CUPY and self._use_cuda:
            analytical_trace = darray.map_blocks(cusignal.hilbert,
                                                 dtype=darray.dtype)
        else:
            analytical_trace = darray.map_blocks(util.hilbert,
                                                 dtype=darray.dtype)
        result = da.absolute(analytical_trace)
        result = util.trim_dask_array(result, kernel)

        return(result)

    def instantaneous_phase(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Instantaneous Phase of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        kernel = (1, 1, 25)
        darray, chunks_init = self.create_array(darray, kernel,
                                                preview=preview)
        if USE_CUPY and self._use_cuda:
            analytical_trace = darray.map_blocks(cusignal.hilbert,
                                                 dtype=darray.dtype)
        else:
            analytical_trace = darray.map_blocks(util.hilbert,
                                                 dtype=darray.dtype)
        result = da.rad2deg(da.angle(analytical_trace))
        result = util.trim_dask_array(result, kernel)

        return(result)

    def cosine_instantaneous_phase(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Cose of Instantaneous Phase of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)
        phase = self.instantaneous_phase(darray)
        result = da.rad2deg(da.angle(phase))

        return(result)

    def relative_amplitude_change(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Relative Amplitude Change of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray)
        env_prime = sp(self._use_cuda).first_derivative(env, axis=-1)
        result = env_prime / env
        result = da.clip(result, -1, 1)

        return(result)

    def amplitude_acceleration(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Amplitude Acceleration of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)
        rac = self.relative_amplitude_change(darray)
        result = sp(self._use_cuda).first_derivative(rac, axis=-1)

        return(result)

    def instantaneous_frequency(self, darray, sample_rate=4, preview=None):
        """
        Description
        -----------
        Compute the Instantaneous Frequency of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        sample_rate : Number, sample rate in milliseconds (ms)
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)

        fs = 1000 / sample_rate
        phase = self.instantaneous_phase(darray)
        phase = da.deg2rad(phase)
        if USE_CUPY and self._use_cuda:
            phase = phase.map_blocks(cp.unwrap, dtype=darray.dtype)
        else:
            phase = phase.map_blocks(np.unwrap, dtype=darray.dtype)
        phase_prime = sp(self._use_cuda).first_derivative(phase, axis=-1)
        result = da.absolute((phase_prime / (2.0 * np.pi) * fs))

        return(result)

    def instantaneous_bandwidth(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Instantaneous Bandwidth of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)
        rac = self.relative_amplitude_change(darray)
        result = da.absolute(rac) / (2.0 * np.pi)

        return(result)

    def dominant_frequency(self, darray, sample_rate=4, preview=None):
        """
        Description
        -----------
        Compute the Dominant Frequency of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        sample_rate : Number, sample rate in milliseconds (ms)
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)
        inst_freq = self.instantaneous_frequency(darray, sample_rate)
        inst_band = self.instantaneous_bandwidth(darray)
        result = da.hypot(inst_freq, inst_band)

        return(result)

    def frequency_change(self, darray, sample_rate=4, preview=None):
        """
        Description
        -----------
        Compute the Frequency Change of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        sample_rate : Number, sample rate in milliseconds (ms)
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)
        inst_freq = self.instantaneous_frequency(darray, sample_rate)
        result = sp(self._use_cuda).first_derivative(inst_freq, axis=-1)

        return(result)

    def sweetness(self, darray, sample_rate=4, preview=None):
        """
        Description
        -----------
        Compute the Sweetness of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        sample_rate : Number, sample rate in milliseconds (ms)
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        def func(chunk):
            chunk[chunk < 5] = 5
            return(chunk)

        darray, chunks_init = self.create_array(darray, preview=preview)
        inst_freq = self.instantaneous_frequency(darray, sample_rate)
        inst_freq = inst_freq.map_blocks(func, dtype=darray.dtype)
        env = self.envelope(darray)

        result = env / inst_freq

        return(result)

    def quality_factor(self, darray, sample_rate=4, preview=None):
        """
        Description
        -----------
        Compute the Quality Factor of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        sample_rate : Number, sample rate in milliseconds (ms)
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        darray, chunks_init = self.create_array(darray, preview=preview)

        inst_freq = self.instantaneous_frequency(darray, sample_rate)
        rac = self.relative_amplitude_change(darray)

        result = (np.pi * inst_freq) / rac

        return(result)

    def response_phase(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Response Phase of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        def operation(chunk1, chunk2, chunk3):
            out = np.zeros(chunk1.shape)
            for i, j in np.ndindex(out.shape[:-1]):
                ints = np.unique(chunk3[i, j, :])
                for ii in ints:
                    idx = np.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk2[i, j, peak]

            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray)
        phase = self.instantaneous_phase(darray)
        troughs = env.map_blocks(util.local_events, comparator=np.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, phase, troughs,
                               dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)

    def response_frequency(self, darray, sample_rate=4, preview=None):
        """
        Description
        -----------
        Compute the Response Frequency of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        sample_rate : Number, sample rate in milliseconds (ms)
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        def operation(chunk1, chunk2, chunk3):
            out = np.zeros(chunk1.shape)
            for i, j in np.ndindex(out.shape[:-1]):
                ints = np.unique(chunk3[i, j, :])
                for ii in ints:
                    idx = np.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk2[i, j, peak]

            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray)
        inst_freq = self.instantaneous_frequency(darray, sample_rate)
        troughs = env.map_blocks(util.local_events, comparator=np.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, inst_freq, troughs,
                               dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)

    def response_amplitude(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Response Amplitude of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """

        def operation(chunk1, chunk2, chunk3):
            out = np.zeros(chunk1.shape)
            for i, j in np.ndindex(out.shape[:-1]):
                ints = np.unique(chunk3[i, j, :])

                for ii in ints:
                    idx = np.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk2[i, j, peak]

            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray)
        troughs = env.map_blocks(util.local_events, comparator=np.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, darray, troughs,
                               dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)

    def apparent_polarity(self, darray, preview=None):
        """
        Description
        -----------
        Compute the Apparent Polarity of the input data

        Parameters
        ----------
        darray : Array-like, acceptable inputs include Numpy, HDF5, or Dask
            Arrays

        Keywork Arguments
        -----------------
        preview : str, enables or disables preview mode and specifies direction
            Acceptable inputs are (None, 'inline', 'xline', 'z')
            Optimizes chunk size in different orientations to facilitate rapid
            screening of algorithm output

        Returns
        -------
        result : Dask Array
        """
        def operation(chunk1, chunk2, chunk3):
            out = np.zeros(chunk1.shape)
            for i, j in np.ndindex(out.shape[:-1]):
                ints = np.unique(chunk3[i, j, :])

                for ii in ints:
                    idx = np.where(chunk3[i, j, :] == ii)[0]
                    peak = idx[chunk1[i, j, idx].argmax()]
                    out[i, j, idx] = chunk1[i, j, peak] * np.sign(chunk2[i, j,
                                                                         peak])

            return(out)

        darray, chunks_init = self.create_array(darray, preview=preview)
        env = self.envelope(darray)
        troughs = env.map_blocks(util.local_events, comparator=np.less,
                                 dtype=darray.dtype)
        troughs = troughs.cumsum(axis=-1)
        result = da.map_blocks(operation, env, darray, troughs,
                               dtype=darray.dtype)
        result[da.isnan(result)] = 0

        return(result)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Filterbank simulation
# Author: Daniel Estevez
# GNU Radio version: 3.10.12.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import numpy as np
import threading




class filterbank_simulation(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Filterbank simulation", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 187.5e6 / 64
        self.noise_amplitude = noise_amplitude = 1
        self.tone_cn0 = tone_cn0 = 20
        self.nfft = nfft = 2**20
        self.n_int = n_int = 51
        self.n0 = n0 = noise_amplitude**2 / samp_rate
        self.tone_amplitude = tone_amplitude = np.sqrt(10**(tone_cn0 / 10) * n0)
        self.time_resampling = time_resampling = 100
        self.sec_per_int = sec_per_int = nfft * n_int / samp_rate
        self.hz_per_bin = hz_per_bin = samp_rate / nfft
        self.drift_rate = drift_rate = 10
        self.drift_duration = drift_duration = 400

        ##################################################
        # Blocks
        ##################################################

        self.fft_vxx_0 = fft.fft_vcc(nfft, True, [], True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, nfft)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(n_int, nfft)
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, (round(samp_rate * 300)))
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*nfft, 'spectrum_output.f32', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(nfft)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 0.5e6, (np.sqrt(10**(tone_cn0 / 10) * n0)), 0, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amplitude, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_head_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_hz_per_bin(self.samp_rate / self.nfft)
        self.set_n0(self.noise_amplitude**2 / self.samp_rate)
        self.set_sec_per_int(self.nfft * self.n_int / self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_head_0.set_length((round(self.samp_rate * 300)))

    def get_noise_amplitude(self):
        return self.noise_amplitude

    def set_noise_amplitude(self, noise_amplitude):
        self.noise_amplitude = noise_amplitude
        self.set_n0(self.noise_amplitude**2 / self.samp_rate)
        self.analog_noise_source_x_0.set_amplitude(self.noise_amplitude)

    def get_tone_cn0(self):
        return self.tone_cn0

    def set_tone_cn0(self, tone_cn0):
        self.tone_cn0 = tone_cn0
        self.set_tone_amplitude(np.sqrt(10**(self.tone_cn0 / 10) * self.n0))
        self.analog_sig_source_x_0.set_amplitude((np.sqrt(10**(self.tone_cn0 / 10) * self.n0)))

    def get_nfft(self):
        return self.nfft

    def set_nfft(self, nfft):
        self.nfft = nfft
        self.set_hz_per_bin(self.samp_rate / self.nfft)
        self.set_sec_per_int(self.nfft * self.n_int / self.samp_rate)

    def get_n_int(self):
        return self.n_int

    def set_n_int(self, n_int):
        self.n_int = n_int
        self.set_sec_per_int(self.nfft * self.n_int / self.samp_rate)

    def get_n0(self):
        return self.n0

    def set_n0(self, n0):
        self.n0 = n0
        self.set_tone_amplitude(np.sqrt(10**(self.tone_cn0 / 10) * self.n0))
        self.analog_sig_source_x_0.set_amplitude((np.sqrt(10**(self.tone_cn0 / 10) * self.n0)))

    def get_tone_amplitude(self):
        return self.tone_amplitude

    def set_tone_amplitude(self, tone_amplitude):
        self.tone_amplitude = tone_amplitude

    def get_time_resampling(self):
        return self.time_resampling

    def set_time_resampling(self, time_resampling):
        self.time_resampling = time_resampling

    def get_sec_per_int(self):
        return self.sec_per_int

    def set_sec_per_int(self, sec_per_int):
        self.sec_per_int = sec_per_int

    def get_hz_per_bin(self):
        return self.hz_per_bin

    def set_hz_per_bin(self, hz_per_bin):
        self.hz_per_bin = hz_per_bin

    def get_drift_rate(self):
        return self.drift_rate

    def set_drift_rate(self, drift_rate):
        self.drift_rate = drift_rate

    def get_drift_duration(self):
        return self.drift_duration

    def set_drift_duration(self, drift_duration):
        self.drift_duration = drift_duration




def main(top_block_cls=filterbank_simulation, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    tb.wait()


if __name__ == '__main__':
    main()

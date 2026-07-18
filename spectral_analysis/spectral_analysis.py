#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.filter import pfb
import numpy as np
import sip
import threading



class spectral_analysis(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "spectral_analysis")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.noise_amplitude = noise_amplitude = 1
        self.tone_cn0 = tone_cn0 = 60
        self.nfft = nfft = 4096
        self.n0 = n0 = noise_amplitude**2 / samp_rate
        self.integration_length_seconds = integration_length_seconds = 1
        self.broadband_cn0 = broadband_cn0 = 60
        self.tone_freq = tone_freq = 200e3
        self.tone_amplitude = tone_amplitude = np.sqrt(10**(tone_cn0 / 10) * n0)
        self.number_integrations = number_integrations = round(samp_rate / nfft * integration_length_seconds)
        self.noise_bandwidth = noise_bandwidth = 150e3
        self.broadband_freq = broadband_freq = (-300e3)
        self.broadband_amplitude = broadband_amplitude = np.sqrt(10**(broadband_cn0 / 10) * n0)

        ##################################################
        # Blocks
        ##################################################

        self._tone_freq_tool_bar = Qt.QToolBar(self)
        self._tone_freq_tool_bar.addWidget(Qt.QLabel("Tone Frequency (Hz)" + ": "))
        self._tone_freq_line_edit = Qt.QLineEdit(str(self.tone_freq))
        self._tone_freq_tool_bar.addWidget(self._tone_freq_line_edit)
        self._tone_freq_line_edit.editingFinished.connect(
            lambda: self.set_tone_freq(eng_notation.str_to_num(str(self._tone_freq_line_edit.text()))))
        self.top_layout.addWidget(self._tone_freq_tool_bar)
        self._noise_bandwidth_tool_bar = Qt.QToolBar(self)
        self._noise_bandwidth_tool_bar.addWidget(Qt.QLabel("Noise Bandwidth (Hz)" + ": "))
        self._noise_bandwidth_line_edit = Qt.QLineEdit(str(self.noise_bandwidth))
        self._noise_bandwidth_tool_bar.addWidget(self._noise_bandwidth_line_edit)
        self._noise_bandwidth_line_edit.editingFinished.connect(
            lambda: self.set_noise_bandwidth(eng_notation.str_to_num(str(self._noise_bandwidth_line_edit.text()))))
        self.top_layout.addWidget(self._noise_bandwidth_tool_bar)
        self._noise_amplitude_tool_bar = Qt.QToolBar(self)
        self._noise_amplitude_tool_bar.addWidget(Qt.QLabel("Noise Amplitude" + ": "))
        self._noise_amplitude_line_edit = Qt.QLineEdit(str(self.noise_amplitude))
        self._noise_amplitude_tool_bar.addWidget(self._noise_amplitude_line_edit)
        self._noise_amplitude_line_edit.editingFinished.connect(
            lambda: self.set_noise_amplitude(eng_notation.str_to_num(str(self._noise_amplitude_line_edit.text()))))
        self.top_layout.addWidget(self._noise_amplitude_tool_bar)
        self._broadband_freq_tool_bar = Qt.QToolBar(self)
        self._broadband_freq_tool_bar.addWidget(Qt.QLabel("Broadband Frequency (Hz)" + ": "))
        self._broadband_freq_line_edit = Qt.QLineEdit(str(self.broadband_freq))
        self._broadband_freq_tool_bar.addWidget(self._broadband_freq_line_edit)
        self._broadband_freq_line_edit.editingFinished.connect(
            lambda: self.set_broadband_freq(eng_notation.str_to_num(str(self._broadband_freq_line_edit.text()))))
        self.top_layout.addWidget(self._broadband_freq_tool_bar)
        self._tone_cn0_tool_bar = Qt.QToolBar(self)
        self._tone_cn0_tool_bar.addWidget(Qt.QLabel("Tone CN0 (dB)" + ": "))
        self._tone_cn0_line_edit = Qt.QLineEdit(str(self.tone_cn0))
        self._tone_cn0_tool_bar.addWidget(self._tone_cn0_line_edit)
        self._tone_cn0_line_edit.editingFinished.connect(
            lambda: self.set_tone_cn0(eng_notation.str_to_num(str(self._tone_cn0_line_edit.text()))))
        self.top_layout.addWidget(self._tone_cn0_tool_bar)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            nfft,
            (-samp_rate / 2),
            (samp_rate / nfft),
            "x-Axis",
            "y-Axis",
            "",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis((-50), 90)
        self.qtgui_vector_sink_f_0.enable_autoscale(True)
        self.qtgui_vector_sink_f_0.enable_grid(False)
        self.qtgui_vector_sink_f_0.set_x_axis_units("")
        self.qtgui_vector_sink_f_0.set_y_axis_units("")
        self.qtgui_vector_sink_f_0.set_ref_level(0)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
            (samp_rate / noise_bandwidth),
            taps=None,
            flt_size=32,
            atten=100)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        self.fft_vxx_0 = fft.fft_vcc(nfft, True, window.rectangular(nfft), True, 1)
        self._broadband_cn0_tool_bar = Qt.QToolBar(self)
        self._broadband_cn0_tool_bar.addWidget(Qt.QLabel("Broadband (Noise) CN0 (dB)" + ": "))
        self._broadband_cn0_line_edit = Qt.QLineEdit(str(self.broadband_cn0))
        self._broadband_cn0_tool_bar.addWidget(self._broadband_cn0_line_edit)
        self._broadband_cn0_line_edit.editingFinished.connect(
            lambda: self.set_broadband_cn0(eng_notation.str_to_num(str(self._broadband_cn0_line_edit.text()))))
        self.top_layout.addWidget(self._broadband_cn0_tool_bar)
        self.blocks_throttle2_1 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, nfft)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*nfft, 100)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, nfft, 0)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(number_integrations, nfft)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(nfft)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, broadband_freq, 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, tone_freq, tone_amplitude, 0, 0)
        self.analog_noise_source_x_1 = analog.noise_source_c(analog.GR_GAUSSIAN, broadband_amplitude, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amplitude, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_noise_source_x_1, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle2_1, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_throttle2_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.blocks_multiply_xx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "spectral_analysis")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_n0(self.noise_amplitude**2 / self.samp_rate)
        self.set_number_integrations(round(self.samp_rate / self.nfft * self.integration_length_seconds))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.blocks_throttle2_1.set_sample_rate(self.samp_rate)
        self.pfb_arb_resampler_xxx_0.set_rate((self.samp_rate / self.noise_bandwidth))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_vector_sink_f_0.set_x_axis((-self.samp_rate / 2), (self.samp_rate / self.nfft))

    def get_noise_amplitude(self):
        return self.noise_amplitude

    def set_noise_amplitude(self, noise_amplitude):
        self.noise_amplitude = noise_amplitude
        self.set_n0(self.noise_amplitude**2 / self.samp_rate)
        Qt.QMetaObject.invokeMethod(self._noise_amplitude_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.noise_amplitude)))
        self.analog_noise_source_x_0.set_amplitude(self.noise_amplitude)

    def get_tone_cn0(self):
        return self.tone_cn0

    def set_tone_cn0(self, tone_cn0):
        self.tone_cn0 = tone_cn0
        self.set_tone_amplitude(np.sqrt(10**(self.tone_cn0 / 10) * self.n0))
        Qt.QMetaObject.invokeMethod(self._tone_cn0_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.tone_cn0)))

    def get_nfft(self):
        return self.nfft

    def set_nfft(self, nfft):
        self.nfft = nfft
        self.set_number_integrations(round(self.samp_rate / self.nfft * self.integration_length_seconds))
        self.fft_vxx_0.set_window(window.rectangular(self.nfft))
        self.qtgui_vector_sink_f_0.set_x_axis((-self.samp_rate / 2), (self.samp_rate / self.nfft))

    def get_n0(self):
        return self.n0

    def set_n0(self, n0):
        self.n0 = n0
        self.set_broadband_amplitude(np.sqrt(10**(self.broadband_cn0 / 10) * self.n0))
        self.set_tone_amplitude(np.sqrt(10**(self.tone_cn0 / 10) * self.n0))

    def get_integration_length_seconds(self):
        return self.integration_length_seconds

    def set_integration_length_seconds(self, integration_length_seconds):
        self.integration_length_seconds = integration_length_seconds
        self.set_number_integrations(round(self.samp_rate / self.nfft * self.integration_length_seconds))

    def get_broadband_cn0(self):
        return self.broadband_cn0

    def set_broadband_cn0(self, broadband_cn0):
        self.broadband_cn0 = broadband_cn0
        self.set_broadband_amplitude(np.sqrt(10**(self.broadband_cn0 / 10) * self.n0))
        Qt.QMetaObject.invokeMethod(self._broadband_cn0_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.broadband_cn0)))

    def get_tone_freq(self):
        return self.tone_freq

    def set_tone_freq(self, tone_freq):
        self.tone_freq = tone_freq
        Qt.QMetaObject.invokeMethod(self._tone_freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.tone_freq)))
        self.analog_sig_source_x_0.set_frequency(self.tone_freq)

    def get_tone_amplitude(self):
        return self.tone_amplitude

    def set_tone_amplitude(self, tone_amplitude):
        self.tone_amplitude = tone_amplitude
        self.analog_sig_source_x_0.set_amplitude(self.tone_amplitude)

    def get_number_integrations(self):
        return self.number_integrations

    def set_number_integrations(self, number_integrations):
        self.number_integrations = number_integrations

    def get_noise_bandwidth(self):
        return self.noise_bandwidth

    def set_noise_bandwidth(self, noise_bandwidth):
        self.noise_bandwidth = noise_bandwidth
        Qt.QMetaObject.invokeMethod(self._noise_bandwidth_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.noise_bandwidth)))
        self.pfb_arb_resampler_xxx_0.set_rate((self.samp_rate / self.noise_bandwidth))

    def get_broadband_freq(self):
        return self.broadband_freq

    def set_broadband_freq(self, broadband_freq):
        self.broadband_freq = broadband_freq
        Qt.QMetaObject.invokeMethod(self._broadband_freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.broadband_freq)))
        self.analog_sig_source_x_1.set_frequency(self.broadband_freq)

    def get_broadband_amplitude(self):
        return self.broadband_amplitude

    def set_broadband_amplitude(self, broadband_amplitude):
        self.broadband_amplitude = broadband_amplitude
        self.analog_noise_source_x_1.set_amplitude(self.broadband_amplitude)




def main(top_block_cls=spectral_analysis, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: alecp
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
import math
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import soapy
import numpy as np
import sip
import threading



class fm_broadcast(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "fm_broadcast")

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
        self.tune_freq = tune_freq = 300e3
        self.samp_rate = samp_rate = 3.2e6
        self.rf_gain = rf_gain = 30
        self.recording_duration = recording_duration = 10
        self.freq = freq = 98.8e6
        self.fm_station = fm_station = 99.1e6
        self.decimation = decimation = 10
        self.audio_gain = audio_gain = .01

        ##################################################
        # Blocks
        ##################################################

        self._tune_freq_tool_bar = Qt.QToolBar(self)
        self._tune_freq_tool_bar.addWidget(Qt.QLabel("Tune Frequency (Hz)" + ": "))
        self._tune_freq_line_edit = Qt.QLineEdit(str(self.tune_freq))
        self._tune_freq_tool_bar.addWidget(self._tune_freq_line_edit)
        self._tune_freq_line_edit.editingFinished.connect(
            lambda: self.set_tune_freq(eng_notation.str_to_num(str(self._tune_freq_line_edit.text()))))
        self.top_layout.addWidget(self._tune_freq_tool_bar)
        self._rf_gain_tool_bar = Qt.QToolBar(self)
        self._rf_gain_tool_bar.addWidget(Qt.QLabel("RF Gain" + ": "))
        self._rf_gain_line_edit = Qt.QLineEdit(str(self.rf_gain))
        self._rf_gain_tool_bar.addWidget(self._rf_gain_line_edit)
        self._rf_gain_line_edit.editingFinished.connect(
            lambda: self.set_rf_gain(eng_notation.str_to_num(str(self._rf_gain_line_edit.text()))))
        self.top_layout.addWidget(self._rf_gain_tool_bar)
        # Create the options list
        self._fm_station_options = [99100000.0, 99900000.0, 102900000.0, 101100000.0]
        # Create the labels list
        self._fm_station_labels = ['Country', 'Pop', 'Hip-Hop', 'Not Sure']
        # Create the combo box
        # Create the radio buttons
        self._fm_station_group_box = Qt.QGroupBox("FM Station" + ": ")
        self._fm_station_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._fm_station_button_group = variable_chooser_button_group()
        self._fm_station_group_box.setLayout(self._fm_station_box)
        for i, _label in enumerate(self._fm_station_labels):
            radio_button = Qt.QRadioButton(_label)
            self._fm_station_box.addWidget(radio_button)
            self._fm_station_button_group.addButton(radio_button, i)
        self._fm_station_callback = lambda i: Qt.QMetaObject.invokeMethod(self._fm_station_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._fm_station_options.index(i)))
        self._fm_station_callback(self.fm_station)
        self._fm_station_button_group.buttonClicked[int].connect(
            lambda i: self.set_fm_station(self._fm_station_options[i]))
        self.top_layout.addWidget(self._fm_station_group_box)
        self._audio_gain_tool_bar = Qt.QToolBar(self)
        self._audio_gain_tool_bar.addWidget(Qt.QLabel("Audio Gain" + ": "))
        self._audio_gain_line_edit = Qt.QLineEdit(str(self.audio_gain))
        self._audio_gain_tool_bar.addWidget(self._audio_gain_line_edit)
        self._audio_gain_line_edit.editingFinished.connect(
            lambda: self.set_audio_gain(eng_notation.str_to_num(str(self._audio_gain_line_edit.text()))))
        self.top_layout.addWidget(self._audio_gain_tool_bar)
        self.soapy_custom_source_0 = None
        dev = 'driver=' + 'lime'
        stream_args = ''
        tune_args = ['']
        settings = ['']
        self.soapy_custom_source_0 = soapy.source(dev, "fc32",
                                  1, '',
                                  stream_args, tune_args, settings)
        self.soapy_custom_source_0.set_sample_rate(0, samp_rate)
        self.soapy_custom_source_0.set_bandwidth(0, 0)
        self.soapy_custom_source_0.set_antenna(0, 'LNAW')
        self.soapy_custom_source_0.set_frequency(0, (fm_station - (tune_freq)))
        self.soapy_custom_source_0.set_frequency_correction(0, 0)
        self.soapy_custom_source_0.set_gain_mode(0, False)
        self.soapy_custom_source_0.set_gain(0, rf_gain)
        self.soapy_custom_source_0.set_dc_offset_mode(0, True)
        self.soapy_custom_source_0.set_dc_offset(0, 0)
        self.soapy_custom_source_0.set_iq_balance(0, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=3,
                decimation=20,
                taps=[],
                fractional_bw=0)
        self.qtgui_freq_sink_x_2 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            (samp_rate / decimation), #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_2.set_update_time(0.10)
        self.qtgui_freq_sink_x_2.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_2.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_2.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_2.enable_autoscale(False)
        self.qtgui_freq_sink_x_2.enable_grid(False)
        self.qtgui_freq_sink_x_2.set_fft_average(1.0)
        self.qtgui_freq_sink_x_2.enable_axis_labels(True)
        self.qtgui_freq_sink_x_2.enable_control_panel(False)
        self.qtgui_freq_sink_x_2.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_2.set_plot_pos_half(not True)

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
                self.qtgui_freq_sink_x_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_2.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_2.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_2.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_2.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_2_win = sip.wrapinstance(self.qtgui_freq_sink_x_2.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_2_win)
        self._freq_tool_bar = Qt.QToolBar(self)
        self._freq_tool_bar.addWidget(Qt.QLabel("RF Frequency" + ": "))
        self._freq_line_edit = Qt.QLineEdit(str(self.freq))
        self._freq_tool_bar.addWidget(self._freq_line_edit)
        self._freq_line_edit.editingFinished.connect(
            lambda: self.set_freq(eng_notation.str_to_num(str(self._freq_line_edit.text()))))
        self.top_layout.addWidget(self._freq_tool_bar)
        self.filter_fft_low_pass_filter_1 = filter.fft_filter_fff(1, firdes.low_pass(1, 48e3, 18e3, 500, window.WIN_HAMMING, 6.76), 1)
        self.filter_fft_low_pass_filter_0 = filter.fft_filter_ccc(decimation, firdes.low_pass(1, samp_rate, 100e3, 25e3, window.WIN_HAMMING, 6.76), 1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(audio_gain)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, tune_freq, 1, 0, 0)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.filter_fft_low_pass_filter_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.filter_fft_low_pass_filter_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.filter_fft_low_pass_filter_1, 0), (self.qtgui_freq_sink_x_2, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.filter_fft_low_pass_filter_1, 0))
        self.connect((self.soapy_custom_source_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "fm_broadcast")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_tune_freq(self):
        return self.tune_freq

    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        Qt.QMetaObject.invokeMethod(self._tune_freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.tune_freq)))
        self.analog_sig_source_x_0.set_frequency(self.tune_freq)
        self.soapy_custom_source_0.set_frequency(0, (self.fm_station - (self.tune_freq)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 100e3, 25e3, window.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink_x_2.set_frequency_range(0, (self.samp_rate / self.decimation))

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        Qt.QMetaObject.invokeMethod(self._rf_gain_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.rf_gain)))
        self.soapy_custom_source_0.set_gain(0, self.rf_gain)

    def get_recording_duration(self):
        return self.recording_duration

    def set_recording_duration(self, recording_duration):
        self.recording_duration = recording_duration

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        Qt.QMetaObject.invokeMethod(self._freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq)))

    def get_fm_station(self):
        return self.fm_station

    def set_fm_station(self, fm_station):
        self.fm_station = fm_station
        self._fm_station_callback(self.fm_station)
        self.soapy_custom_source_0.set_frequency(0, (self.fm_station - (self.tune_freq)))

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.qtgui_freq_sink_x_2.set_frequency_range(0, (self.samp_rate / self.decimation))

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        Qt.QMetaObject.invokeMethod(self._audio_gain_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.audio_gain)))
        self.blocks_multiply_const_vxx_0.set_k(self.audio_gain)




def main(top_block_cls=fm_broadcast, options=None):

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

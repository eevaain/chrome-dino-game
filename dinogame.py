import pyautogui
from time import sleep
from pynput.keyboard import Key, Controller
from os import system as sys
from datetime import datetime
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
import utils  # imports a python file called utils.py (custom functions)

#Code adapted from https://github.com/NeuroTechX/bci-workshop/tree/master/python

class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3

BUFFER_LENGTH = 5              
EPOCH_LENGTH = 1                                               
OVERLAP_LENGTH = 0.5
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
INDEX_CHANNEL = [1]
      

print('Looking for an EEG stream...')
streams = resolve_byprop('type', 'EEG', timeout=2)
# print(streams)
if len(streams) == 0:
     raise RuntimeError('Unable to find EEG stream.')

print('Start acquiring data')
inlet = StreamInlet(streams[0], max_chunklen=12)
# print(inlet)


info = inlet.info()
description = info.desc()
# print(info)
# print(description)

fs = int(info.nominal_srate())
# print(fs) 

eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
# print(eeg_buffer)
filter_state = None  # for use with the notch filter
# print(filter_state)
n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) / SHIFT_LENGTH + 1))
# print(n_win_test) # = 9
band_buffer = np.zeros((n_win_test, 4))
# print(band_buffer)

keyboard = Controller()
# print(keyboard)
# print('Press Ctrl-C in the console to break the while loop.')


while True:
    eeg_data, timestamp = inlet.pull_chunk(timeout=1, max_samples=int(SHIFT_LENGTH * fs))
    # print(eeg_data) #(Holy shit thats alot of data)
    ch_data = np.array(eeg_data)[:, INDEX_CHANNEL] #extracts index ch annel column from all rows
    # print(ch_data)
    eeg_buffer, filter_state = utils.update_buffer(eeg_buffer, ch_data, notch=True, filter_state=filter_state)
    # print(eeg_buffer)
    # print(filter_state)
    data_epoch = utils.get_last_data(eeg_buffer, EPOCH_LENGTH * fs)
    # print(data_epoch)
    band_powers = utils.compute_band_powers(data_epoch, fs)
    # print(band_powers)
    band_buffer, _ = utils.update_buffer(band_buffer, np.asarray([band_powers]))
    # print(band_buffer)
    smooth_band_powers = np.mean(band_buffer, axis=0)
    # print(smooth_band_powers)
    print('Delta: ', band_powers[Band.Delta],
    ' Theta: ', band_powers[Band.Theta],
    ' Alpha: ', band_powers[Band.Alpha],
    ' Beta: ', band_powers[Band.Beta])

    if  band_powers[Band.Alpha] > 1.15:
        print('blink')
        pyautogui.press('space')   



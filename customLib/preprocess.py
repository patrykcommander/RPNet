import numpy as np
from customLib.load_wfdb import *
#from customLib.peak_detection import detect_my_peaks

def add_padding(signal: np.ndarray, kernel_length: int):

    n_padding = int(kernel_length/2)
    new_signal = np.zeros((signal.shape[0] + 2*n_padding))
    new_signal[n_padding:-n_padding] = signal

    # fill in the padding with boundary values
    new_signal[:n_padding] = signal[0]
    new_signal[-n_padding:] = signal[-1]

    return new_signal   

def myConv1D(signal: np.ndarray, kernel_length: int, padding='same'):
    weights = np.ones(kernel_length)
    weights /= kernel_length                # weights for smoothening the signal
    output = []

    if padding == 'same':                   # add padding
        signal = add_padding(signal, kernel_length)

    n_samples = signal.shape[0]
    index = int(kernel_length/2)

    for i in range(index, n_samples-index):
        start = i-index
        stop = start+kernel_length
        part = signal[start : stop]
        step = np.matmul(part, weights)
        output.append(step)  
    
    return np.array(output)

def norm_min_max(signal, lower, upper):
    signal_std = (signal - signal.min(axis=0)) / (signal.max(axis=0) - signal.min(axis=0))
    signal_scaled = signal_std * (upper - lower) + lower
    return signal_scaled

def stationary(signal):
    return np.diff(signal)

def split_signal(signal, start=0, window_in_seconds=10, fs=250, overlap_factor=0.1):
    window_size = int(fs * window_in_seconds)
    overlap = int(window_size * overlap_factor)
    step = window_size - overlap
    ecg_windows = []
    
    while start + window_size <= len(signal):
        signal_slice = signal[start:start+window_size]
        ecg_windows.append(signal_slice)
        start += step

    return ecg_windows

def _calc_hrv(peaks_time):
    RRI = np.diff(peaks_time)
    SDNN = np.std(RRI)
    return RRI, SDNN


""" def calculate_hrv(signal: np.array, fs: int, threshold=0.3):
    peaks_indices = detect_my_peaks(signal=signal, threshold=threshold)
    peaks_time = np.array([x * 1000/fs for x in peaks_indices])
    RRI, SDNN = _calc_hrv(peaks_time)
    return peaks_indices, RRI, SDNN """


def downsample_ecg(ecg_list, original_fs, target_fs):
    downsampled_ecg_list = []

    for ecg in ecg_list:
        downsampling_factor = int(original_fs / target_fs)

        downsampled_ecg = ecg[::downsampling_factor]
        downsampled_ecg_list.append(downsampled_ecg)

    return downsampled_ecg_list

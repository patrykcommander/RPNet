import matplotlib.pyplot as plt
import numpy as np 

def draw_plot(plot_index: int, signal_slice: np.ndarray, fs: int, r_peaks=None, HRV=None):
    n_samples = len(signal_slice)
    time_vector = [x * 1/fs for x in range(n_samples)]

    plt.figure(plot_index)
    if HRV != None and isinstance(HRV, (int, float)):
        plt.title("HRV: {:.3f}".format(HRV))
    plt.plot(time_vector, signal_slice, 'r-')

    if isinstance(r_peaks, (np.ndarray)) and len(r_peaks > 0):
        r_peaks_time = [x * 1/fs for x in r_peaks]
        plt.plot(r_peaks_time, signal_slice[r_peaks], 'bx')

    plt.grid()
    plt.show()


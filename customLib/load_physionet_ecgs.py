import os
import warnings
import numpy as np
import wfdb
from tqdm import tqdm
from customLib.config import *
from customLib.preprocess import split_signal, expand_labels

def load_physionet_ecgs(path: str, annotation_file_extension="atr", force_new=True, window_in_seconds=5, expand=True):
  preprocessed_path = os.path.join(path, "preprocessed")

  # if files already exist, read them
  if force_new == False:
    if os.path.exists(os.path.join(preprocessed_path, "x.npy")):
      x = np.load(os.path.join(preprocessed_path, "x.npy"))
      y = np.load(os.path.join(preprocessed_path, "y.npy"))

      return x, y
    else:
      print("Files not found. Preprocessing...")
  
  if not os.path.exists(preprocessed_path):
    os.mkdir(preprocessed_path)

  # Get all file names of the recordings / annotations
  fileNames = [ x.split(".")[0] for x in os.listdir(path) if x.endswith(annotation_file_extension) ]

  filteredFileNames = []

  # the aim of the original function was to exclude records with '/' in annotation symbols like in paper DOI: 10.1109/TIM.2023.3241997
  if path.find("mitdb")!= -1: 
    for fileName in fileNames:
      filePath = os.path.join(path, fileName)
      annotation = wfdb.rdann(filePath, annotation_file_extension)
      annotationSymbols = annotation.symbol
      if '/' not in annotationSymbols:
        filteredFileNames.append(fileName)
      else:
        print(f"Dropping recording {fileName}")

    fileNames = filteredFileNames
    filteredFileNames = None

  if path.find("apnea-ecg")!= -1: # records c05 and c06 are the same
    fileNames.remove("c05")

  x = None
  y = None

  for i, fileName in tqdm(enumerate(fileNames), total=len(fileNames)):
    filePath = os.path.join(path, fileName)

    try:
      record = wfdb.rdrecord(filePath)
    except Exception as e:
      print(e, "File: ", fileName, ". Respiratory data.")
      continue

    annotation = wfdb.rdann(filePath, annotation_file_extension)
    annotation = np.unique(annotation.sample[np.in1d(annotation.symbol, ['N', 'L', 'R', 'B', 'A', 'a', 'J', 'S', 'V', 'r', 'F', 'e', 'j', 'n', 'E', 'f', 'Q', '?'])])

    r_peaks = np.zeros(shape=(record.sig_len,), dtype=int)
    r_peaks[annotation] = 1

    n_sig = record.n_sig
    sampling_rate = record.fs
    print("ECGs sampling rate: ", sampling_rate)

    for sig in range(n_sig): # depends on the number of channels (mit-bih has 2, apnea-ecg has 1)
      ecg = record.p_signal[:,sig]

      ecg_windows = split_signal(signal=ecg, window_in_seconds=window_in_seconds, fs=sampling_rate, normalize=True, overlap_factor=0.0)

      invalid_ecg_indices = {i for i, x in enumerate(ecg_windows) if isinstance(x, int)}
      valid_ecg_windows = [ecg_window for i, ecg_window in enumerate(ecg_windows) if i not in invalid_ecg_indices]

      annotation_windows = split_signal(signal=r_peaks, window_in_seconds=window_in_seconds, fs=sampling_rate, overlap_factor=0.0)
      valid_annotation_windows = [annotation_window for i, annotation_window in enumerate(annotation_windows) if i not in invalid_ecg_indices]

      if expand: # like in paper DOI: 10.1109/TIM.2023. - expanding R-peaks labels for easier learning
        annotation_windows = expand_labels(valid_annotation_windows, fileName=str(fileName))

      if x is None:
        x = np.array(valid_ecg_windows)
        y = np.array(valid_annotation_windows)
      else:
        try:
          x = np.concatenate((x, np.array(valid_ecg_windows)))
          y = np.concatenate((y, np.array(valid_annotation_windows)))
        except:
          raise Exception('Invalid shape of ECG or Annotation windows. Ensure they have the correct shape -> (-1, sampling_rate * window_in_seconds).')

  np.save(file=(preprocessed_path + "\\x.npy"), arr=x)
  np.save(file=(preprocessed_path + "\\y.npy"), arr=y)

  return (x,y)

if __name__ == "__main__":
  load_physionet_ecgs()
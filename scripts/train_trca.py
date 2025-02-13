import numpy as np
from scipy.stats import pearsonr
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
import pandas as pd
import mne
from sklearn.metrics import confusion_matrix, accuracy_score
from brainda.algorithms.utils.model_selection import (
    set_random_seeds, 
    generate_loo_indices, match_loo_indices)
from brainda.algorithms.decomposition import (
    FBTRCA, FBTDCA, FBSCCA, FBECCA, FBDSP,
    generate_filterbank, generate_cca_references)
from collections import OrderedDict
from sklearn.pipeline import clone
from sklearn.metrics import balanced_accuracy_score
from tqdm import tqdm
import sys, time
from matplotlib.colors import LogNorm
import os, pickle
import argparse

parser = argparse.ArgumentParser(description='Train TRCA model')

folder_path = 'data/cyton8_alternating-vep_32-class_1.2s/sub-01/ses-01/'
model_save_dir = 'cache/'
model_name = 'FBTRCA_model.pkl'
# folder_path = '../data/cyton8_alternating-vep_32-class_1.5s/sub-01/ses-01/'
sampling_rate = 250

# List all the run files in the folder
run_files = [f for f in os.listdir(folder_path) if f.startswith('eeg-trials_2-per-class_run-') and f.endswith('.npy')]

# Initialize a list to store the reverted EEG trials
reverted_eeg_trials_list = []

# Process each run file
for run_file in run_files:
    # Extract the run number from the file name
    run_number = int(run_file.split('-')[-1].split('.')[0])
    
    # Load the EEG trials for the current run
    eeg_trials = np.load(os.path.join(folder_path, run_file))

    # Apply the band-pass filter using mne.filter.filter_data
    # eeg_trials = mne.filter.filter_data(eeg_trials, sfreq=sampling_rate, l_freq=1, h_freq=49, verbose=0, method='fir', fir_design='firwin', filter_length='auto')
    # print(f"Shape of eeg_trials after filtering for run {run_number}: {eeg_trials.shape}")
    
    # Check the shape of eeg_trials
    # print(f"Shape of eeg_trials for run {run_number}: {eeg_trials.shape}")
    
    # Create the original indices
    original_indices = np.arange(eeg_trials.shape[0])
    
    # Shuffle the indices using the run number as the random seed
    np.random.seed(run_number)
    shuffled_indices = np.random.permutation(eeg_trials.shape[0])
    
    # Revert the shuffling
    reverted_eeg_trials = np.empty_like(eeg_trials)
    reverted_eeg_trials[shuffled_indices] = eeg_trials
    
    # Reshape the reverted EEG trials to (2, 32, 8, 350)
    reverted_eeg_trials = reverted_eeg_trials.reshape(2, 32, 8, 350)
    # reverted_eeg_trials = reverted_eeg_trials.reshape(2, 32, 8, 425)
    
    # Add the reverted EEG trials to the list
    reverted_eeg_trials_list.append(reverted_eeg_trials)

# Combine all the reverted EEG trials
combined_eeg_trials = np.concatenate(reverted_eeg_trials_list, axis=0)

print("Combined shape:", combined_eeg_trials.shape)

def run_fbtrca(eeg, target_by_trial, target_tab, duration=1, onset_delay=42,srate=300, ensamble=True, return_prob=False,return_template_xcorr=False, return_matching_xcorr=False, print_acc=False):
    eeg = np.copy(eeg)
    np.random.seed(64)
    np.random.shuffle(eeg)
    n_trials = eeg.shape[0]
    classes = range(32)
    n_classes = len(classes)
    y = np.array([list(target_tab.values())] * n_trials).T.reshape(-1)
    eeg_temp = eeg[:n_trials,classes,:,onset_delay:]
    X = eeg_temp.swapaxes(0,1).reshape(-1,*eeg_temp.shape[2:])


    # freq_targets = np.array(target_by_trial)[0,:,0]
    # phase_targets = np.array(target_by_trial)[0,:,1]
    # n_harmonics = 5
    n_bands = 3
    # Yf = generate_cca_references(
    #     freq_targets, srate, duration, 
    #     phases=phase_targets, 
    #     n_harmonics=n_harmonics)
    wp = [[8*i, 90] for i in range(1, n_bands+1)]
    ws = [[8*i-2, 95] for i in range(1, n_bands+1)]
    filterbank = generate_filterbank(
        wp, ws, srate, order=4, rp=1)
    filterweights = np.arange(1, len(filterbank)+1)**(-1.25) + 0.25
    set_random_seeds(64)
    l = 5
    models = OrderedDict([
        ('fbtrca', FBTRCA(
            filterbank, filterweights=filterweights,ensemble=ensamble)),
    ])
    events = []
    for j_class in classes:
        events.extend([str(target_by_trial[i_trial][j_class]) for i_trial in range(n_trials)])
    events = np.array(events)
    subjects = ['1'] * (n_classes*n_trials)
    meta = pd.DataFrame(data=np.array([subjects,events]).T, columns=["subject", "event"])
    set_random_seeds(42)
    loo_indices = generate_loo_indices(meta)

    for model_name in models:
        if model_name == 'fbtdca':
            filterX, filterY = np.copy(X[..., :int(srate*duration)+l]), np.copy(y)
        else:
            filterX, filterY = np.copy(X[..., :int(srate*duration)]), np.copy(y)
        
        filterX = filterX - np.mean(filterX, axis=-1, keepdims=True)

        n_loo = len(loo_indices['1'][events[0]])
        prob_matrices=np.zeros((n_loo,n_classes,n_classes))
        txcorr_matrices=np.zeros((n_loo,n_classes,n_classes))
        mxcorr_matrices=np.zeros((n_loo,n_classes,n_classes))
        loo_accs = []
        testYs = []
        pred_labelss = []
        for k in range(n_loo):
            train_ind, validate_ind, test_ind = match_loo_indices(
                k, meta, loo_indices)
            train_ind = np.concatenate([train_ind, validate_ind])

            trainX, trainY = filterX[train_ind], filterY[train_ind]
            testX, testY = filterX[test_ind], filterY[test_ind]

            model = clone(models[model_name]).fit(
                trainX, trainY,
                # Yf=Yf
            )
            if return_template_xcorr:
                templates = np.copy(model.estimators_[0].templates_)
                U = np.copy(model.estimators_[0].Us_)[:, :, :model.n_components]
                U = np.concatenate(U, axis=-1)
                new_templates=np.zeros((templates.shape[0],templates.shape[0]*templates.shape[2]))
                for i_template, template in enumerate(templates):
                    new_templates[i_template] = np.reshape((U.T@template),(-1))
                templates = np.copy(new_templates)
                for i in range(n_classes):
                    for j in range(n_classes):
                        a1 = templates[i]
                        a2 = templates[j]
                        txcorr_matrices[k,i,j] = pearsonr(a1,a2)[0]
            if return_matching_xcorr:
                templates = np.copy(model.estimators_[0].templates_)
                U = np.copy(model.estimators_[0].Us_)[:, :, :model.n_components]
                U = np.concatenate(U, axis=-1)
                eegX = model.transform_filterbank(np.copy(testX))[0]
                new_templates=np.zeros((templates.shape[0],templates.shape[0]*templates.shape[2]))
                new_eegX = np.zeros((eegX.shape[0],eegX.shape[0]*eegX.shape[2]))
                for i_template, template in enumerate(templates):
                    new_templates[i_template] = np.reshape((U.T@template),(-1))
                templates = np.copy(new_templates)
                for i_x, x in enumerate(eegX):
                    new_eegX[i_x] = np.reshape((U.T@x),(-1))
                eegX = np.copy(new_eegX)
                for i in range(n_classes):
                    for j in range(n_classes):
                        a1 = templates[i]
                        a2 = eegX[j]
                        mxcorr_matrices[k,i,j] = pearsonr(a1,a2)[0]
            if return_prob:
                prob_matrices[k] = model.transform(testX)
            pred_labels = model.predict(testX)
            # print(testX.shape)
            loo_accs.append(
                balanced_accuracy_score(testY, pred_labels))
            pred_labelss.extend(pred_labels)
            testYs.extend(testY)
    if print_acc:
        print("Model:{} LOO Acc:{:.2f}".format(model_name, np.mean(loo_accs)))
    if return_template_xcorr:
        return txcorr_matrices, accuracy_score(testYs, pred_labelss), model
    if return_matching_xcorr:
        return mxcorr_matrices, accuracy_score(testYs, pred_labelss), model
    if return_prob:
        return prob_matrices, accuracy_score(testYs, pred_labelss)
    return confusion_matrix(testYs, pred_labelss, normalize='true'), accuracy_score(testYs, pred_labelss), model

def run_fbtdca(eeg, target_by_trial, target_tab, duration=1.0, onset_delay=42,srate=300, return_prob=True):
    eeg = np.copy(eeg)
    np.random.seed(64)
    np.random.shuffle(eeg)
    n_trials = eeg.shape[0]
    classes = range(32)
    n_classes = len(classes)
    prob_matrix=np.zeros((n_classes,n_classes))
    y = np.array([list(target_tab.values())] * n_trials).T.reshape(-1)
    eeg_temp = eeg[:n_trials,classes,:,onset_delay:]
    X = eeg_temp.swapaxes(0,1).reshape(-1,*eeg_temp.shape[2:])


    freq_targets = np.array(target_by_trial)[0,:,0]
    phase_targets = np.array(target_by_trial)[0,:,1]
    n_harmonics = 5
    n_bands = 3
    Yf = generate_cca_references(
        freq_targets, srate, duration, 
        phases=phase_targets, 
        n_harmonics=n_harmonics)
    wp = [[8*i, 90] for i in range(1, n_bands+1)]
    ws = [[8*i-2, 95] for i in range(1, n_bands+1)]
    filterbank = generate_filterbank(
        wp, ws, srate, order=4, rp=1)
    filterweights = np.arange(1, len(filterbank)+1)**(-1.25) + 0.25
    set_random_seeds(64)
    l = 5
    models = OrderedDict([
        ('fbtdca', FBTDCA(
                filterbank, l, n_components=8, 
                filterweights=filterweights)),
    ])
    events = []
    for j_class in classes:
        events.extend([str(target_by_trial[i_trial][j_class]) for i_trial in range(n_trials)])
    events = np.array(events)
    subjects = ['1'] * (n_classes*n_trials)
    meta = pd.DataFrame(data=np.array([subjects,events]).T, columns=["subject", "event"])
    set_random_seeds(42)
    loo_indices = generate_loo_indices(meta)

    for model_name in models:
        if model_name == 'fbtdca':
            filterX, filterY = np.copy(X[..., :int(srate*duration)+l]), np.copy(y)
        else:
            filterX, filterY = np.copy(X[..., :int(srate*duration)]), np.copy(y)
        
        filterX = filterX - np.mean(filterX, axis=-1, keepdims=True)

        n_loo = len(loo_indices['1'][events[0]])
        loo_accs = []
        testYs = []
        pred_labelss = []
        for k in range(n_loo):
            train_ind, validate_ind, test_ind = match_loo_indices(
                k, meta, loo_indices)
            train_ind = np.concatenate([train_ind, validate_ind])

            trainX, trainY = filterX[train_ind], filterY[train_ind]
            testX, testY = filterX[test_ind], filterY[test_ind]

            model = clone(models[model_name]).fit(
                trainX, trainY,
                Yf=Yf
            )
            if return_prob:
                prob_matrix+=model.transform(testX)
            pred_labels = model.predict(testX)
            loo_accs.append(
                balanced_accuracy_score(testY, pred_labels))
            pred_labelss.extend(pred_labels)
            testYs.extend(testY)
        
    if return_prob:
        return prob_matrix, accuracy_score(testYs, pred_labelss)
    return confusion_matrix(testYs, pred_labelss, normalize='true'), accuracy_score(testYs, pred_labelss)

stimulus_classes = [(8, 0), (8, 0.5), (8, 1), (8, 1.5),
                        (9, 0), (9, 0.5), (9, 1), (9, 1.5),
                        (10, 0), (10, 0.5), (10, 1), (10, 1.5),
                        (11, 0), (11, 0.5), (11, 1), (11, 1.5),
                        (12, 0), (12, 0.5), (12, 1), (12, 1.5),
                        (13, 0), (13, 0.5), (13, 1), (13, 1.5),
                        (14, 0), (14, 0.5), (14, 1), (14, 1.5),
                        (15, 0), (15, 0.5), (15, 1), (15, 1.5), ]

target_tab = {tuple(map(float, cls)): idx for idx, cls in enumerate(stimulus_classes)}
target_by_trial = [stimulus_classes] * 99

# Define the sampling rate and baseline duration
sampling_rate = 250
baseline_duration = 0.2
baseline_samples = int(baseline_duration * sampling_rate)

# Calculate the baseline average for each trial and each channel
baseline_average = np.mean(combined_eeg_trials[:, :, :, :baseline_samples], axis=3, keepdims=True)

# Subtract the baseline average from the entire trial
baseline_corrected_eeg_trials = combined_eeg_trials - baseline_average

# Crop the trials to exclude the baseline period
# cropped_eeg_trials = baseline_corrected_eeg_trials[:, :, :, baseline_samples:]
cropped_eeg_trials = combined_eeg_trials[:, :, :, baseline_samples:]

cm, acc, model = run_fbtrca(cropped_eeg_trials, target_by_trial, target_tab, duration=1.2, onset_delay=0,ensamble=True,print_acc=True, srate=250)
# cm, acc, model = run_fbtrca(cropped_eeg_trials, target_by_trial, target_tab, duration=1.5, onset_delay=0,ensamble=True,print_acc=True, srate=250)
# cm, acc = run_fbtdca(cropped_eeg_trials, target_by_trial, target_tab, duration=1.15, onset_delay=0, srate=250)
# cm, acc = run_fbtdca(cropped_eeg_trials, target_by_trial, target_tab, duration=1.45, onset_delay=0, srate=250)


os.makedirs(model_save_dir, exist_ok=True)
with open(model_save_dir + model_name, 'wb') as f:
    pickle.dump(model, f)
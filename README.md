# OpenVEP

## Setup for Windows 11
```
pip install virtualenv
virtualenv pyenv --python=3.11.9
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
pyenv\Scripts\activate
(Install "Desktop development with C++" workload: https://visualstudio.microsoft.com/visual-cpp-build-tools/)
pip install -r requirements.txt
git clone https://github.com/TBC-TJU/brainda.git
cd brainda
pip install -r requirements.txt 
pip install -e .
```
All of the Python packages would be installed into the folder `pyenv/`, so they can be easily removed by simply deleting the folder. When you need to install additional packages, you can activate the virtual environment by running `pyenv\Scripts\activate` and then install the packages using `pip install`. If you want to deactivate the virtual environment, you can run `deactivate`. You may need administrator access to be able to run `pip install -r requirements.txt` successfully.

## Using the VEP Speller
```
python run_vep.py
python scripts/train_trca.py
(change the run number in run_vep.py)
```
Repeat the above steps to run the VEP speller multiple times until you get the desired results. For the Cyton EEG cap, you can expect the accuracy to be around 0.6 after the first 2 runs and around 0.7 after 4 runs.
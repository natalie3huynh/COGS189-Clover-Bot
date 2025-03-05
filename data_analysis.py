import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

array = np.load('/Users/nataliehuynh/practice_web/data/eeg-trials_2-per-class_run-2.npy')
print(array)


trial_index = 0  # Change this to visualize different trials
plt.figure(figsize=(10, 6))
sns.heatmap(array[trial_index], cmap="coolwarm", center=0)
plt.xlabel("Time Points")
plt.ylabel("Channels")
plt.title(f"EEG Data - Trial {trial_index}")
plt.show()

# # Select a specific slice (e.g., the first trial)
# data_slice = data[0]  # This will select the first 8x350 matrix

# # Plot one of the 350-length vectors
# plt.plot(data_slice[0])  # Plot the first 350-length vector
# plt.xlabel('Index')
# plt.ylabel('Value')
# plt.title('Plot of Selected Data Slice')
# plt.show()

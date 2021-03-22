# -*- coding: utf-8 -*-
"""Music_Transformer_TMIDI_RPR_Edition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RYtCQbSBDZfWLbPi1DhxjtbxTLnsGgli

# Super Piano 3: Google Music Transformer Reproduction

## Generating Music with Long-Term structure

## Powered by TMIDI 2.0. RPR Processors
## https://github.com/asigalov61/tegridy-tools

### Based on 2019 ICLR paper by Cheng-Zhi Anna Huang, Google Brain and Damon Gwinn's code/repo https://github.com/gwinndr/MusicTransformer-Pytorch

###Setup Environment and Dependencies. Check GPU.
"""

#@title Check if GPU (driver) is avaiiable (you do not want to run this on CPU, trust me)
!nvcc --version
!nvidia-smi

#@title Clone/Install all dependencies
!git clone https://github.com/asigalov61/MusicTransformer-Pytorch
!git clone https://github.com/asigalov61/tegridy-tools
!cp /content/tegridy-tools/tegridy-tools/TMIDI.py /content/MusicTransformer-Pytorch

!pip install tqdm
!pip install progress
!pip install pretty-midi
!pip install pypianoroll
!pip install matplotlib
!pip install librosa
!pip install scipy
!pip install pillow
!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio
!pip install mir_eval
!cp /usr/share/sounds/sf2/FluidR3_GM.sf2 /content/font.sf2

# Commented out IPython magic to ensure Python compatibility.
#@title Import all needed modules
# %cd /content/tegridy-tools/tegridy-tools/
import TMIDI
# %cd /content/

import numpy as np
import pickle
import os
import sys
import math
import random

import pickle
import sys

from abc import ABC, abstractmethod
import pretty_midi as pyd
from pretty_midi import Note
from pprint import pprint

# For plotting
import pypianoroll
from pypianoroll import Multitrack, Track
import matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline
import mir_eval.display
import librosa
import librosa.display

# For rendering output audio
import pretty_midi
from midi2audio import FluidSynth
from google.colab import output
from IPython.display import display, Javascript, HTML, Audio

"""# Process your own custom MIDI DataSet"""

# Commented out IPython magic to ensure Python compatibility.
#@title Upload your custom MIDI DataSet to created "dataset/e_piano/custom_midis" folder through this cell or manually through any other means. You can also use the dataset below.
from google.colab import files
# %cd '/content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis'
uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

# Commented out IPython magic to ensure Python compatibility.
#@title Tegridy Piano Dataset (~230 Modern Piano MIDIs)
# %cd /content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis
!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Tegridy-Piano-CC-BY-NC-SA.zip'
!unzip -j 'Tegridy-Piano-CC-BY-NC-SA.zip'
!rm Tegridy-Piano-CC-BY-NC-SA.zip

# Commented out IPython magic to ensure Python compatibility.
#@title MAESTRO 3.0 MIDI dataset
# %cd /content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis
!wget 'https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip'
!unzip -j 'maestro-v3.0.0-midi.zip'
!rm maestro-v3.0.0-midi.zip

# Commented out IPython magic to ensure Python compatibility.
#@title Tegridy Piano Transformer Dataset dataset
# %cd /content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis
!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Tegridy-Piano-Transformer-Dataset-CC-BY-NC-SA.zip'
!unzip -j 'Tegridy-Piano-Transformer-Dataset-CC-BY-NC-SA.zip'
!rm Tegridy-Piano-Transformer-Dataset-CC-BY-NC-SA.zip

# Commented out IPython magic to ensure Python compatibility.
#@title Syntethic Tegridy Piano Dataset dataset
# %cd /content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis
!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Synthetic-Tegridy-Piano-MIDI-Dataset-CC-BY-NC-SA.zip'
!unzip 'Synthetic-Tegridy-Piano-MIDI-Dataset-CC-BY-NC-SA.zip'
!rm Synthetic-Tegridy-Piano-MIDI-Dataset-CC-BY-NC-SA.zip

"""For now, we are going to split the dataset by random into "test"/"val" dirs which is not ideal. So feel free to modify the code to your liking to achieve better training results with this implementation."""

#@title Declare Notes Representation (RPR) processor and helper functions

'''
This is the data processing script
============
It will allow you to quickly process the MIDI Files into the Google Magenta's music representation 
    as like [Music Transformer](https://magenta.tensorflow.org/music-transformer) 
            [Performance RNN](https://magenta.tensorflow.org/performance-rnn).

'''

total = 0
def process_midi(path):
    global total
    data = pyd.PrettyMIDI(path)
    main_notes = []
    acc_notes = []
    for ins in data.instruments:
        acc_notes.extend(ins.notes)
    for i in range(len(main_notes)):
        main_notes[i].start = round(main_notes[i].start,2)
        main_notes[i].end = round(main_notes[i].end,2)
    for i in range(len(acc_notes)):
        acc_notes[i].start = round(acc_notes[i].start,2)
        acc_notes[i].end = round(acc_notes[i].end,2)
    main_notes.sort(key = lambda x:x.start)
    acc_notes.sort(key = lambda x:x.start)
    mpr = MidiEventProcessor()
    repr_seq = mpr.encode(acc_notes)
    total += len(repr_seq)
    print('Converted file:', path)
    print('Total INTs count:', len(repr_seq))
    print('=' * 70)
    return repr_seq

def process_all_midis(midi_root, save_dir):
    save_py = []
    midi_paths = [d for d in os.listdir(midi_root)]
    i = 0
    out_fmt = '{}-{}.data'
    for path in midi_paths:
        pprint(path)
        filename = midi_root + path
        try:
            data = process_midi(filename)
        except KeyboardInterrupt:
            print(' Abort')
            return
        except EOFError:
            print('EOF Error')
            return
        save_py.append(data)
    # pprint(save_py, compact=True)    
    save_py = np.array(save_py, dtype='object')
    print('=' * 70)
    print('Total number of converted MIDIs:', save_py.size)
    print('Total INTs count:', total)
    np.save(save_dir + 'notes_representations.npy', save_py)

# Commented out IPython magic to ensure Python compatibility.
#@title Process your custom MIDI DataSet :)
# %cd /content/
import TMIDI

# %cd /content/MusicTransformer-Pytorch

import os
import random

# %cd '/content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis'

custom_MIDI_DataSet_dir = '/content/MusicTransformer-Pytorch/dataset/e_piano/custom_midis'

train_dir = '/content/MusicTransformer-Pytorch/dataset/e_piano/train' # split_type = 0
test_dir = '/content/MusicTransformer-Pytorch/dataset/e_piano/test' # split_type = 1  
val_dir = '/content/MusicTransformer-Pytorch/dataset/e_piano/val' # split_type = 2

total_count = 0
train_count = 0
val_count   = 0
test_count  = 0

f_ext = '.pickle'
fileList = os.listdir(custom_MIDI_DataSet_dir)
for file in fileList:
     # we gonna split by a random selection for now
    
    split = random.randint(1, 2)
    if (split == 0):
         o_file = os.path.join(train_dir, file+f_ext)
         train_count += 1

    elif (split == 2):
         o_file0 = os.path.join(train_dir, file+f_ext)
         train_count += 1
         o_file = os.path.join(val_dir, file+f_ext)
         val_count += 1

    elif (split == 1):
         o_file0 = os.path.join(train_dir, file+f_ext)
         train_count += 1
         o_file = os.path.join(test_dir, file+f_ext)
         test_count += 1
    
    try:
      
      prepped = process_midi(file)

      o_stream = open(o_file0, "wb")
      pickle.dump(prepped, o_stream)
      o_stream.close()

      o_stream = open(o_file, "wb")
      pickle.dump(prepped, o_stream)
      o_stream.close()
   
      print(file)
      print(o_file)
      print('Coverted!')

    except KeyboardInterrupt: 
      raise   
    except:
      print('Bad file. Skipping...', file)
      continue

print('Done')
print("Num Train:", train_count)
print("Num Val:", val_count)
print("Num Test:", test_count)
print("Total Count:", train_count)

# %cd /content/MusicTransformer-Pytorch

"""#Train the Model"""

# Commented out IPython magic to ensure Python compatibility.
#@title Activate Tensorboard Graphs/Stats to monitor/evaluate model perfomance during and after training runs
# Load the TensorBoard notebook extension
# %reload_ext tensorboard
import tensorflow as tf
import datetime, os
# %tensorboard --logdir /content/MusicTransformer-Pytorch/rpr

#@title Start to Train the Model
batch_size = 4 #@param {type:"slider", min:2, max:64, step:2}
number_of_training_epochs = 600 #@param {type:"slider", min:10, max:600, step:10}
maximum_output_MIDI_sequence = 2048 #@param {type:"slider", min:0, max:8192, step:128}
!python3 train.py -output_dir rpr --rpr -batch_size=$batch_size -epochs=$number_of_training_epochs -max_sequence=$maximum_output_MIDI_sequence #-n_layers -num_heads -d_model -dim_feedforward

#@title Re-Start Training from a certain checkpoint and epoch
batch_size = 4 #@param {type:"slider", min:2, max:16, step:2}
number_of_training_epochs = 400 #@param {type:"slider", min:10, max:600, step:10}
maximum_output_MIDI_sequence = 2048 #@param {type:"slider", min:128, max:8192, step:128}
saved_checkpoint_full_path = "/content/MusicTransformer-Pytorch/rpr/weights/epoch_0145.pickle" #@param {type:"string"}
continue_epoch_number = 145 #@param {type:"integer"}

!python3 train.py -output_dir rpr --rpr -batch_size=$batch_size -epochs=$number_of_training_epochs -max_sequence=$maximum_output_MIDI_sequence -continue_weights $saved_checkpoint_full_path -continue_epoch $continue_epoch_number #-n_layers -num_heads -d_model -dim_feedforward

"""###Evaluate the resulted models"""

#@title Graph the results
import argparse
import os
import csv
import math
import matplotlib.pyplot as plt

RESULTS_FILE = "results.csv"
EPOCH_IDX = 0
LR_IDX = 1
EVAL_LOSS_IDX = 4
EVAL_ACC_IDX = 5

SPLITTER = '?'


def graph_results(input_dirs="/content/MusicTransformer-Pytorch/rpr/results", output_dir=None, model_names=None, epoch_start=0, epoch_end=None):
    """
    ----------
    Author: Damon Gwinn
    ----------
    Graphs model training and evaluation data
    ----------
    """

    input_dirs = input_dirs.split(SPLITTER)

    if(model_names is not None):
        model_names = model_names.split(SPLITTER)
        if(len(model_names) != len(input_dirs)):
            print("Error: len(model_names) != len(input_dirs)")
            return

    #Initialize Loss and Accuracy arrays
    loss_arrs = []
    accuracy_arrs = []
    epoch_counts = []
    lrs = []

    for input_dir in input_dirs:
        loss_arr = []
        accuracy_arr = []
        epoch_count = []
        lr_arr = []

        f = os.path.join(input_dir, RESULTS_FILE)
        with open(f, "r") as i_stream:
            reader = csv.reader(i_stream)
            next(reader)

            lines = [line for line in reader]

        if(epoch_end is None):
            epoch_end = math.inf

        epoch_start = max(epoch_start, 0)
        epoch_start = min(epoch_start, epoch_end)

        for line in lines:
            epoch = line[EPOCH_IDX]
            lr = line[LR_IDX]
            accuracy = line[EVAL_ACC_IDX]
            loss = line[EVAL_LOSS_IDX]

            if(int(epoch) >= epoch_start and int(epoch) < epoch_end):
                accuracy_arr.append(float(accuracy))
                loss_arr.append(float(loss))
                epoch_count.append(int(epoch))
                lr_arr.append(float(lr))

        loss_arrs.append(loss_arr)
        accuracy_arrs.append(accuracy_arr)
        epoch_counts.append(epoch_count)
        lrs.append(lr_arr)

    if(output_dir is not None):
        try:
            os.mkdir(output_dir)
        except OSError:
            print ("Creation of the directory %s failed" % output_dir)
        else:
            print ("Successfully created the directory %s" % output_dir)

    ##### LOSS #####
    for i in range(len(loss_arrs)):
        if(model_names is None):
            name = None
        else:
            name = model_names[i]

        #Create and save plots to output folder
        plt.plot(epoch_counts[i], loss_arrs[i], label=name)
        plt.title("Loss Results")
        plt.ylabel('Loss (Cross Entropy)')
        plt.xlabel('Epochs')
        fig1 = plt.gcf()

    plt.legend(loc="upper left")

    if(output_dir is not None):
        fig1.savefig(os.path.join(output_dir, 'loss_graph.png'))

    plt.show()

    ##### ACCURACY #####
    for i in range(len(accuracy_arrs)):
        if(model_names is None):
            name = None
        else:
            name = model_names[i]

        #Create and save plots to output folder
        plt.plot(epoch_counts[i], accuracy_arrs[i], label=name)
        plt.title("Accuracy Results")
        plt.ylabel('Accuracy')
        plt.xlabel('Epochs')
        fig2 = plt.gcf()

    plt.legend(loc="upper left")

    if(output_dir is not None):
        fig2.savefig(os.path.join(output_dir, 'accuracy_graph.png'))

    plt.show()

    ##### LR #####
    for i in range(len(lrs)):
        if(model_names is None):
            name = None
        else:
            name = model_names[i]

        #Create and save plots to output folder
        plt.plot(epoch_counts[i], lrs[i], label=name)
        plt.title("Learn Rate Results")
        plt.ylabel('Learn Rate')
        plt.xlabel('Epochs')
        fig2 = plt.gcf()

    plt.legend(loc="upper left")

    if(output_dir is not None):
        fig2.savefig(os.path.join(output_dir, 'lr_graph.png'))

    plt.show()
graph_results('/content/MusicTransformer-Pytorch/rpr/results', model_names='rpr')

"""To have the model continue your custom MIDI enter the following into the custom_MIDI field below:

-primer_file '/content/some_dir/some_seed_midi.mid'

For example: -primer_file '/content/MusicTransformer-Pytorch/seed.mid'

# Generate and Explore the output :)
"""

# Commented out IPython magic to ensure Python compatibility.
#@title Generate, Plot, Graph, Save, Download, and Render the resulting output
number_of_tokens_to_generate = 2000 #@param {type:"slider", min:1, max:4096, step:1}
priming_sequence_length = 1 #@param {type:"slider", min:1, max:100, step:1}
maximum_possible_output_sequence = 2048 #@param {type:"slider", min:0, max:4096, step:8}
select_model = "/content/MusicTransformer-Pytorch/rpr/results/best_loss_weights.pickle" #@param ["/content/MusicTransformer-Pytorch/rpr/results/best_acc_weights.pickle", "/content/MusicTransformer-Pytorch/rpr/results/best_loss_weights.pickle"]
custom_MIDI = "" #@param {type:"string"}
# %cd /content/MusicTransformer-Pytorch
#import processor
#from processor import encode_midi, decode_midi

!python generate_TMIDI.py --rpr -output_dir output -model_weights=$select_model -target_seq_length=$number_of_tokens_to_generate -num_prime=$priming_sequence_length -max_sequence=$maximum_possible_output_sequence $custom_MIDI

print('Successfully exported the output to output folder. To primer.mid and rand.mid')

# set the src and play
#FluidSynth("/content/font.sf2").midi_to_audio('/content/MusicTransformer-Pytorch/output/rand.mid', '/content/MusicTransformer-Pytorch/output/output.wav')

#from google.colab import files
#files.download('/content/MusicTransformer-Pytorch/output/rand.mid')
#files.download('/content/MusicTransformer-Pytorch/output/primer.mid')

#Audio('/content/MusicTransformer-Pytorch/output/output.wav')

# Commented out IPython magic to ensure Python compatibility.
#@title Plot and Graph the Output :)
graphs_length_inches = 14 #@param {type:"slider", min:0, max:20, step:1}
notes_graph_height = 10 #@param {type:"slider", min:0, max:20, step:1}
highest_displayed_pitch = 92 #@param {type:"slider", min:1, max:128, step:1}
lowest_displayed_pitch = 24 #@param {type:"slider", min:1, max:128, step:1}
piano_roll_color_map = "Blues"

import librosa
import numpy as np
import pretty_midi
import pypianoroll
from pypianoroll import Multitrack, Track
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('SVG')
# For plotting
import mir_eval.display
import librosa.display
# %matplotlib inline


midi_data = pretty_midi.PrettyMIDI('/content/MusicTransformer-Pytorch/output/rand.mid')

def plot_piano_roll(pm, start_pitch, end_pitch, fs=100):
    # Use librosa's specshow function for displaying the piano roll
    librosa.display.specshow(pm.get_piano_roll(fs)[start_pitch:end_pitch],
                             hop_length=1, sr=fs, x_axis='time', y_axis='cqt_note',
                             fmin=pretty_midi.note_number_to_hz(start_pitch))



# Plot the output
fname = '/content/MusicTransformer-Pytorch/output/rand'
plt.figure(figsize=(graphs_length_inches, notes_graph_height))
ax2 = plot_piano_roll(midi_data, int(lowest_displayed_pitch), int(highest_displayed_pitch))

plt.show(block=False)
FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)
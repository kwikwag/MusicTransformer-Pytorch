import argparse

from .constants import SEPERATOR

# parse_train_args
def parse_train_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-input_dir", type=str, default="./dataset/e_piano", help="Folder of preprocessed and pickled midi files")
    parser.add_argument("-output_dir", type=str, default="./saved_models", help="Folder to save model weights. Saves one every epoch")
    parser.add_argument("-weight_modulus", type=int, default=1, help="How often to save epoch weights (ex: value of 10 means save every 10 epochs)")

    parser.add_argument("-lr", type=float, default=None, help="Constant learn rate. Leave as None for a custom scheduler.")
    parser.add_argument("-batch_size", type=int, default=2, help="Batch size to use")
    parser.add_argument("-epochs", type=int, default=100, help="Number of epochs to use")

    parser.add_argument("-max_sequence", type=int, default=2048, help="Maximum midi sequence to consider")
    parser.add_argument("-n_layers", type=int, default=6, help="Number of decoder layers to use")
    parser.add_argument("-num_heads", type=int, default=8, help="Number of heads to use for multi-head attention")
    parser.add_argument("-d_model", type=int, default=512, help="Dimension of the model (output dim of embedding layers, etc.)")

    parser.add_argument("-dim_feedforward", type=int, default=2048, help="Dimension of the feedforward layer")

    parser.add_argument("-dropout", type=float, default=0.1, help="Dropout rate")

    return parser.parse_args()

# print_train_args
def print_train_args(args):
    print(SEPERATOR)
    print("input_dir:", args.input_dir)
    print("output_dir:", args.output_dir)
    print("weight_modulus:", args.weight_modulus)
    print("")
    print("lr:", args.lr)
    print("batch_size:", args.batch_size)
    print("epochs:", args.epochs)
    print("")
    print("max_sequence:", args.max_sequence)
    print("n_layers:", args.n_layers)
    print("num_heads:", args.num_heads)
    print("d_model:", args.d_model)
    print("")
    print("dim_feedforward:", args.dim_feedforward)
    # print("feedforward_activation:", args.feedforward_activation)
    print("dropout:", args.dropout)
    print(SEPERATOR)
    print("")

# parse_eval_args
def parse_eval_args():
    parser.add_argument("-dataset_dir", type=str, default="./dataset/e_piano", help="Folder of preprocessed and pickled midi files")
    parser.add_argument("-model_weights", type=str, default="./saved_models/model.pickle", help="Pickled model weights file saved with torch.save and model.state_dict()")

    parser.add_argument("-batch_size", type=int, default=2, help="Batch size to use")

    parser.add_argument("-max_sequence", type=int, default=2048, help="Maximum midi sequence to consider")
    parser.add_argument("-n_layers", type=int, default=6, help="Number of decoder layers to use")
    parser.add_argument("-num_heads", type=int, default=8, help="Number of heads to use for multi-head attention")
    parser.add_argument("-d_model", type=int, default=512, help="Dimension of the model (output dim of embedding layers, etc.)")

    parser.add_argument("-dim_feedforward", type=int, default=2048, help="Dimension of the feedforward layer")

# print_eval_args
def print_eval_args(args):
    print(SEPERATOR)
    print("dataset_dir:", args.dataset_dir)
    print("model_weights:", args.model_weights)
    print("")
    print("batch_size:", args.batch_size)
    print("")
    print("max_sequence:", args.max_sequence)
    print("n_layers:", args.n_layers)
    print("num_heads:", args.num_heads)
    print("d_model:", args.d_model)
    print("")
    print("dim_feedforward:", args.dim_feedforward)
    print(SEPERATOR)
    print("")

# parse_generate_args
def parse_generate_args(args):
    parser.add_argument("-midi_primer", type=str, default="./dataset/e_piano/test/MIDI-Unprocessed_01_R1_2006_01-09_ORIG_MID--AUDIO_01_R1_2006_02_Track02_wav.midi.pickle", help="Midi file to prime the generator with")
    parser.add_argument("-output_dir", type=str, default="./gen", help="Folder to write generated midi to")

    parser.add_argument("-num_prime", type=int, default=25, help="Amount of messages to prime the generator with")
    parser.add_argument("-model_weights", type=str, default="./saved_models/model.pickle", help="Pickled model weights file saved with torch.save and model.state_dict()")

    parser.add_argument("-max_sequence", type=int, default=2048, help="Maximum midi sequence to consider")
    parser.add_argument("-n_layers", type=int, default=6, help="Number of decoder layers to use")
    parser.add_argument("-num_heads", type=int, default=8, help="Number of heads to use for multi-head attention")
    parser.add_argument("-d_model", type=int, default=512, help="Dimension of the model (output dim of embedding layers, etc.)")

    parser.add_argument("-dim_feedforward", type=int, default=2048, help="Dimension of the feedforward layer")

# print_generate_args
def print_generate_args(args):
    print(SEPERATOR)
    print("midi_primer:", args.midi_primer)
    print("output_dir:", args.output_dir)
    print("")
    print("num_prime:", args.num_prime)
    print("model_weights:", args.model_weights)
    print("")
    print("max_sequence:", args.max_sequence)
    print("n_layers:", args.n_layers)
    print("num_heads:", args.num_heads)
    print("d_model:", args.d_model)
    print("")
    print("dim_feedforward:", args.dim_feedforward)
    print(SEPERATOR)
    print("")

# write_model_params
def write_model_params(args, output_file):
    o_stream = open(output_file, "w")

    o_stream.write("lr: " + str(args.lr) + "\n")
    o_stream.write("batch_size: " + str(args.batch_size) + "\n")
    o_stream.write("max_sequence: " + str(args.max_sequence) + "\n")
    o_stream.write("n_layers: " + str(args.n_layers) + "\n")
    o_stream.write("num_heads: " + str(args.num_heads) + "\n")
    o_stream.write("d_model: " + str(args.d_model) + "\n")
    o_stream.write("dim_feedforward: " + str(args.dim_feedforward) + "\n")
    o_stream.write("dropout: " + str(args.dropout) + "\n")

    o_stream.close()
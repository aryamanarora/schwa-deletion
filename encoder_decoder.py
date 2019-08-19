from keras.models import Model
from keras.layers import Input, LSTM, Dense
import numpy as np

batch_size = 128  # Batch size for training.
epochs = 50  # Number of epochs to train for.
latent_dim = 256  # Latent dimensionality of the encoding space.
num_samples = 30000  # Number of samples to train on.
# Path to the data txt file on disk.
data_path = 'data/extra_large_unicode.csv'


def main(reuse):
    # Vectorize the data.
    hindis = []
    translits = []
    input_characters = set()
    target_characters = set()
    with open(data_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    for line in lines[1 : min(num_samples, len(lines) - 1)]:
        print(line)
        hindi, translit = line.split(',')
        # \t and \n are delimiters
        translit = '\t' + translit + '\n'
        hindis.append(hindi)
        translits.append(translit)
        for char in hindi:
            if char not in input_characters:
                input_characters.add(char)
        for char in translit:
            if char not in target_characters:
                target_characters.add(char)

    input_characters = sorted(list(input_characters))
    target_characters = sorted(list(target_characters))
    num_encoder_tokens = len(input_characters)
    num_decoder_tokens = len(target_characters)
    max_encoder_seq_length = max([len(txt) for txt in hindis])
    max_decoder_seq_length = max([len(txt) for txt in translits])

    print('Number of samples:', len(hindis))
    print('Number of unique input tokens:', num_encoder_tokens)
    print('Number of unique output tokens:', num_decoder_tokens)
    print('Max sequence length for inputs:', max_encoder_seq_length)
    print('Max sequence length for outputs:', max_decoder_seq_length)

    input_token_index = dict(
        [(char, i) for i, char in enumerate(input_characters)])
    target_token_index = dict(
        [(char, i) for i, char in enumerate(target_characters)])

    encoder_input_data = np.zeros(
        (len(hindis), max_encoder_seq_length, num_encoder_tokens),
        dtype='float32')
    decoder_input_data = np.zeros(
        (len(hindis), max_decoder_seq_length, num_decoder_tokens),
        dtype='float32')
    decoder_target_data = np.zeros(
        (len(hindis), max_decoder_seq_length, num_decoder_tokens),
        dtype='float32')

    for i, (hindi, translit) in enumerate(zip(hindis, translits)):
        for t, char in enumerate(hindi):
            encoder_input_data[i, t, input_token_index[char]] = 1.
        for t, char in enumerate(translit):
            # decoder_target_data is ahead of decoder_input_data by one timestep
            decoder_input_data[i, t, target_token_index[char]] = 1.
            if t > 0:
                # decoder_target_data will be ahead by one timestep
                # and will not include the start character.
                decoder_target_data[i, t - 1, target_token_index[char]] = 1.

    # Define an input sequence and process it.
    encoder_inputs = Input(shape=(None, num_encoder_tokens))
    encoder = LSTM(latent_dim, return_state=True)
    encoder_outputs, state_h, state_c = encoder(encoder_inputs)
    # We discard `encoder_outputs` and only keep the states.
    encoder_states = [state_h, state_c]

    # Set up the decoder, using `encoder_states` as initial state.
    decoder_inputs = Input(shape=(None, num_decoder_tokens))
    # We set up our decoder to return full output sequences,
    # and to return internal states as well. We don't use the
    # return states in the training model, but we will use them in inference.
    decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                        initial_state=encoder_states)
    decoder_dense = Dense(num_decoder_tokens, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    # Define the model that will turn
    # `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

    if reuse:
        model.load_weights('s2s.h5')
    else:
        # Run training
        model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
        model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
                batch_size=batch_size,
                epochs=epochs,
                validation_split=0.2)
        # Save model
        model.save('s2s.h5')

    # Next: inference mode (sampling).
    # Here's the drill:
    # 1) encode input and retrieve initial decoder state
    # 2) run one step of decoder with this initial state
    # and a "start of sequence" token as target.
    # Output will be the next target token
    # 3) Repeat with the current target token and current states

    # Define sampling models
    encoder_model = Model(encoder_inputs, encoder_states)

    decoder_state_input_h = Input(shape=(latent_dim,))
    decoder_state_input_c = Input(shape=(latent_dim,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_inputs, initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_outputs = decoder_dense(decoder_outputs)
    decoder_model = Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs] + decoder_states)

    # Reverse-lookup token index to decode sequences back to
    # something readable.
    reverse_input_char_index = dict(
        (i, char) for char, i in input_token_index.items())
    reverse_target_char_index = dict(
        (i, char) for char, i in target_token_index.items())

    def decode_sequence(input_seq):
        # Encode the input as state vectors.
        states_value = encoder_model.predict(input_seq)

        # Generate empty target sequence of length 1.
        target_seq = np.zeros((1, 1, num_decoder_tokens))
        # Populate the first character of target sequence with the start character.
        target_seq[0, 0, target_token_index['\t']] = 1.

        # Sampling loop for a batch of sequences
        # (to simplify, here we assume a batch of size 1).
        stop_condition = False
        decoded_sentence = ''
        while not stop_condition:
            output_tokens, h, c = decoder_model.predict(
                [target_seq] + states_value)

            # Sample a token
            sampled_token_index = np.argmax(output_tokens[0, -1, :])
            sampled_char = reverse_target_char_index[sampled_token_index]
            decoded_sentence += sampled_char

            # Exit condition: either hit max length
            # or find stop character.
            if (sampled_char == '\n' or
            len(decoded_sentence) > max_decoder_seq_length):
                stop_condition = True

            # Update the target sequence (of length 1).
            target_seq = np.zeros((1, 1, num_decoder_tokens))
            target_seq[0, 0, sampled_token_index] = 1.

            # Update states
            states_value = [h, c]

        return decoded_sentence

    for seq_index in range(1):
        # Take one sequence (part of the training set)
        # for trying out decoding.
        input_seq = encoder_input_data[seq_index: seq_index + 1]
        print(input_seq)
        decoded_sentence = decode_sequence(input_seq)
        print('-')
        print('Input sentence:', hindis[seq_index])
        print('Decoded sentence:', decoded_sentence)
    
    while True:
        hindi_t = input()
        encoder_input_data_t = np.zeros(
            (1, max_encoder_seq_length, num_encoder_tokens),
            dtype='float32')
        print(encoder_input_data_t)
        for t, char in enumerate(hindi_t):
            encoder_input_data_t[0, t, input_token_index[char]] = 1.
        decoded_sentence = decode_sequence(encoder_input_data_t)
        print('-')
        print('Decoded sentence:', decoded_sentence)
        



if __name__ == '__main__':
    main(True)

# ओव्वो
# [[[0. 0. 0. ... 0. 0. 0.]
# [0. 0. 0. ... 0. 0. 0.]
# [0. 0. 0. ... 0. 0. 0.]
# ...
# [0. 0. 0. ... 0. 0. 0.]
# [0. 0. 0. ... 0. 0. 0.]
# [0. 0. 0. ... 0. 0. 0.]]]
# -
# Decoded sentence: ovvo

# रेडियोएक्टिव
# [[[0. 0. 0. ... 0. 0. 0.]
#   [0. 0. 0. ... 0. 0. 0.]
#   [0. 0. 0. ... 0. 0. 0.]
#   ...
#   [0. 0. 0. ... 0. 0. 0.]
#   [0. 0. 0. ... 0. 0. 0.]
#   [0. 0. 0. ... 0. 0. 0.]]]
# -
# Decoded sentence: ḍheriyokṛ
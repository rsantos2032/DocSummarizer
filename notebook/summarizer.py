import pickle
import re
import warnings

import contractions
import numpy as np
import opendatasets as od
import pandas as pd
import tensorflow as tf
import tensorflow.keras.backend as K
from attention import AttentionLayer
from nltk.corpus import stopwords
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import (
    LSTM,
    Bidirectional,
    Concatenate,
    Dense,
    Embedding,
    Input,
    TimeDistributed,
)
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

pd.set_option("display.max_colwidth", 200)
warnings.filterwarnings("ignore")

def clean_text(text, summary=False):
    new_text = text.lower()
    new_text = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', new_text) # Removes text inside (), [], {}
    new_text = re.sub(r'\b(?:https?://)?(?:www\.)?\S+\.com\b', '', new_text) # Removes URLs
    new_text = re.sub(r'[\n\t]', '', new_text) # New lines and tabs
    new_text = ' '.join([contractions.fix(w) for w in new_text.split(' ')]) # Fixes contractions
    new_text = re.sub(r'[^\w\s]', ' ', new_text) # Remove non-words
    new_text = re.sub(r'\b\w*[^\w\s]+\w*\b', '', new_text) # Remove symbols from words
    new_text = re.sub(r'[^a-zA-z]', ' ', new_text) # Keeps all English alphabet characters
    stop_words = set(stopwords.words('english'))
    if not summary:
        new_text = [w for w in new_text.split() if not w in stop_words] # Removing stop words from non abstract text
    else:
        new_text = new_text.split()
    new_text = [w for w in new_text if len(w) > 1] # Removing remaining words with only 1 character
    return (' '.join(new_text)).strip() 

def common_words_tokenizer(tokenizer, training_data, threshold=10):
    total_count = len(tokenizer.word_counts.items())
    rare_count = sum(int(i) < threshold for i in tokenizer.word_counts.values())
    tokenizer = Tokenizer(num_words=(total_count-rare_count))
    tokenizer.fit_on_texts(list(training_data))
    return tokenizer
    
def sequence_pad(tokenizer, data, maxlen):
    seq = tokenizer.texts_to_sequences(list(data))
    pad = pad_sequences(seq, maxlen=maxlen, padding='post')
    return pad

def prep_keras_input(X, y):
    return [X, y[:, :-1]], y.reshape(y.shape[0], y.shape[1], 1)[:, 1:]

od.download('https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail', data_dir='./data/')
np.random.seed(128)
total_rows = 287113
skip_size = int(total_rows * 0.8)
skip_sample = np.random.choice(range(1, total_rows+1), size=skip_size, replace=False).tolist()

train_df = pd.read_csv('./data/newspaper-text-summarization-cnn-dailymail/cnn_dailymail/train.csv', skiprows=skip_sample)
validation_df = pd.read_csv('./data/newspaper-text-summarization-cnn-dailymail/cnn_dailymail/validation.csv')
test_df = pd.read_csv('./data/newspaper-text-summarization-cnn-dailymail/cnn_dailymail/test.csv')

df = pd.concat([train_df, validation_df, test_df], keys=['train', 'validation', 'test'], ignore_index=False)
df['cleaned_article'] = df['article'].apply(lambda x: clean_text(x))
df['cleaned_highlights'] = df['highlights'].apply(lambda x: f'<SOS> {clean_text(x, summary=True)} <EOS>')

train_df_cleaned, validation_df_cleaned, test_df_cleaned = df.xs('train'), df.xs('validation'), df.xs('test')
max_article_len = 350
max_highlights_len = 48

X_tokenizer = Tokenizer()
X_tokenizer.fit_on_texts(list(train_df_cleaned['cleaned_article']))
X_tokenizer = common_words_tokenizer(X_tokenizer, train_df_cleaned['cleaned_article'])
X_train = sequence_pad(X_tokenizer, train_df_cleaned['cleaned_article'], max_article_len)

y_tokenizer = Tokenizer()
y_tokenizer.fit_on_texts(list(train_df_cleaned['cleaned_highlights']))
y_tokenizer = common_words_tokenizer(y_tokenizer, train_df_cleaned['cleaned_highlights'])
y_train = sequence_pad(y_tokenizer, train_df_cleaned['cleaned_highlights'], max_highlights_len)

with open("../models/X_tokenizer.pickle", "wb") as handle:
    pickle.dump(X_tokenizer, handle)
    
with open("../models/y_tokenizer.pickle", "wb") as handle:
    pickle.dump(y_tokenizer, handle)
    
X_vocab = X_tokenizer.num_words + 1
y_vocab = y_tokenizer.num_words + 1

K.clear_session()

embed_dim = 90
latent_dim = 150

# Encoder
encoder_input = Input(shape=(max_article_len, ))
encoder_embed = Embedding(X_vocab, embed_dim, trainable=True)(encoder_input)
encoder_bidirectional = Bidirectional(LSTM(75, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4))
encoder_output_bi, forward_h, backward_h, forward_c, backward_c = encoder_bidirectional(encoder_embed)
state_h = Concatenate(axis=-1)([forward_h, backward_h])
state_c = Concatenate(axis=-1)([forward_c, backward_c])
encoder_lstm1 = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4)
encoder_output1, state_h1, state_c1 = encoder_lstm1(encoder_output_bi, initial_state=[state_h, state_c])
# encoder_output1, state_h1, state_c1 = encoder_lstm1(encoder_embed)
encoder_lstm2 = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4)
encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1)
encoder_lstm3 = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4)
encoder_output3, state_h3, state_c3 = encoder_lstm3(encoder_output2)

# Decoder
decoder_input = Input(shape=(None, ))
decoder_embed = Embedding(y_vocab, embed_dim, trainable=True)(decoder_input)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4)
decoder_output, _, _ = decoder_lstm(decoder_embed, initial_state=[state_h3, state_c3])

# Attention
attention = AttentionLayer()
attention_output, _ = attention([encoder_output3, decoder_output])

# Concatenate Attention with LSTM Output
concatenate = Concatenate(axis=-1)([decoder_output, attention_output])
decoder_dense = TimeDistributed(Dense(y_vocab, activation='softmax'))
decoder_output = decoder_dense(concatenate)

model = Model([encoder_input, decoder_input], decoder_output)
print(model.summary())

model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
early_stop = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=2)
X_val = sequence_pad(X_tokenizer, validation_df_cleaned['cleaned_article'], max_article_len)
y_val = sequence_pad(y_tokenizer, validation_df_cleaned['cleaned_highlights'], max_highlights_len)

X_train_k, y_train_k = prep_keras_input(X_train, y_train)
X_val_k, y_val_k = prep_keras_input(X_val, y_val)

history = model.fit(X_train_k, y_train_k, batch_size=128, epochs=15, validation_data=(X_val_k, y_val_k), callbacks=[early_stop], verbose=1)
model.save('../models/model.h5')
model.save_weights('../models/model_weights.h5')



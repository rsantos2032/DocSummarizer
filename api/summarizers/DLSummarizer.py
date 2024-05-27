import pickle
import re

import contractions
import nltk
import numpy as np
from nltk.corpus import stopwords
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from .attention import AttentionLayer


class DLSummarizer:
    def __init__(self) -> None:
        self.X_tokenizer = None
        self.y_tokenizer = None
        
        self.encoder_model = load_model('./models/encoder_model.h5')
        self.decoder_model = load_model('./models/decoder_model.h5', custom_objects={'AttentionLayer': AttentionLayer})
        
        with open('./models/X_tokenizer.pickle', 'rb') as handle:
            self.X_tokenizer = pickle.load(handle)
            
        with open('./models/y_tokenizer.pickle', 'rb') as handle:
            self.y_tokenizer = pickle.load(handle)
            
        self.reverse_target_word_index = self.y_tokenizer.index_word
        self.reverse_source_word_index = self.X_tokenizer.index_word
        self.target_word_index = self.y_tokenizer.word_index
            
    def sequence_pad(self, tokenizer, data, maxlen=350):
        seq = tokenizer.texts_to_sequences(list(data))
        pad = pad_sequences(seq, maxlen=maxlen, padding='post')
        return pad
    
    def sequence_decoder(self, input_seq):
        encode_out, encode_h, encode_c = self.encoder_model.predict(input_seq, verbose=0)
        target_seq = np.zeros((1, 1))
        
        target_seq[0, 0] = self.target_word_index['sostok']
        
        stop_condition = False
        decoded_sentence = ''
        
        while not stop_condition:
            output_tokens, h, c = self.decoder_model.predict([target_seq] + [encode_out, encode_h, encode_c], verbose=0)
            
            sample_token_idx = np.argmax(output_tokens[0, -1, :])
            sampled_token = self.reverse_target_word_index[sample_token_idx]
            
            if sampled_token != 'eostok':
                decoded_sentence += ' ' + sampled_token
            
            if sampled_token == 'eostok' or len(decoded_sentence.split()) >= 47:
                stop_condition = True
                
            target_seq = np.zeros((1, 1))
            target_seq[0, 0] = sample_token_idx
            
            encode_h, encode_c = h, c
        return decoded_sentence
            
    def clean_text(self, text):
        new_text = text.lower()
        new_text = re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', new_text) # Removes text inside (), [], {}
        new_text = re.sub(r'\b(?:https?://)?(?:www\.)?\S+\.com\b', '', new_text) # Removes URLs
        new_text = re.sub(r'[\n\t]', '', new_text) # New lines and tabs
        new_text = ' '.join([contractions.fix(w) for w in new_text.split(' ')]) # Fixes contractions
        new_text = re.sub(r'[^\w\s]', ' ', new_text) # Remove non-words
        new_text = re.sub(r'\b\w*[^\w\s]+\w*\b', '', new_text) # Remove symbols from words
        new_text = re.sub(r'[^a-zA-z]', ' ', new_text) # Keeps all English alphabet characters
        stop_words = set(stopwords.words('english'))
        new_text = [w for w in new_text.split() if not w in stop_words] # Removing stop words from non abstract text
        new_text = [w for w in new_text if len(w) > 1] # Removing remaining words with only 1 character
        return (' '.join(new_text)).strip() 
    
    def summarize(self, text):
        cleaned_text = self.clean_text(text)
        pad_text = self.sequence_pad(self.X_tokenizer, f"sostok {cleaned_text} eostok")
        summarized_text = self.sequence_decoder(pad_text[0].reshape(1, 350))
        return summarized_text

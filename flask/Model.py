import nltk
import docx2txt
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
import pymorphy2
import torch
import pickle
import re
import numpy as np
import pandas as pd


from  mlp_model import MLPModel

class CustomUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        if name == 'MLPModel':
            from mlp_model import MLPModel
            return MLPModel
        return super().find_class(module, name)


class Model():
    def __init__(self):
        nltk.download('stopwords')
        self.STOPWORDS = set(stopwords.words('russian'))
        self.model = MLPModel(300, 39)
        self.model = CustomUnpickler(open("model.p", "rb")).load()
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.lemmatizer = pymorphy2.MorphAnalyzer()
        self.vectorizer = pickle.load(open("vectorizer.p", "rb"))
        self.selector = pickle.load(open("selector.p", "rb"))

    def init_data(self, filename,  root='.'):

        df = pd.DataFrame(columns=['text', 'label'])
        for row in docx2txt.process(filename).split('{')[1::2]:
            row_data = row.split('}')
            npa_label = row_data[0]
            try:
                npa_text = row_data[1]  # там всего пару таких строчек, чтобы не кидало ошибку на не юникод символах
            except:
                print('Файл содержит недопустимые символы, которые обработаны не будут.')
                continue
            df.loc[len(df.index)] = [npa_text, npa_label]
        return df

    def tokenize_text(self, text, min_word_length=1):
        text = text.lower()
        text = re.sub(r'http\S+', '', text)
        text = BeautifulSoup(text, 'lxml').get_text()
        text = self.tokenizer.tokenize(text)
        return [token for token in text if len(token) > min_word_length]

    def delete_stopwords(self, tokens):
        return ' '.join(list(filter(lambda token: token not in self.STOPWORDS, tokens)))

    def lemmatizing(self, tokens):
        return [self.lemmatizer.parse(token)[0].normal_form for token in tokens]

    def clean_data(self, text):
        tokens = self.tokenize_text(text)
        tokens = self.lemmatizing(tokens)
        return self.delete_stopwords(tokens)

    def process_text(self, name):
        data = self.init_data(name)
        paragraphs = data.text.copy()
        data.text = data.text.apply(self.clean_data)
        rows_count = data.shape[0]
        doc_metrics = np.zeros(39)
        rows_main_class_data = []
        rows_all_classes_data = []
        for row in data.text:
            X = self.vectorizer.transform([row])
            X = self.selector.transform(X).astype('float32')
            X = torch.FloatTensor(X.toarray())
            X_classes = self.model.forward(X)
            X_main_class = {torch.argmax(self.model.forward(X)).item() + 1: torch.max(self.model.forward(X)).item()}
            X_all_classes = {torch.argmax(self.model.forward(X)).item() + 1: self.model.forward(X).detach().numpy()[0]}
            rows_main_class_data.append(X_main_class)
            rows_all_classes_data.append(X_all_classes)
            doc_metrics += X_classes.detach().numpy()[0]
        doc_metrics /= rows_count

        return list(zip(paragraphs, rows_all_classes_data))

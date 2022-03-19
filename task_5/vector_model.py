from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from pymorphy2 import MorphAnalyzer
import numpy as np
import re
from string import punctuation
from scipy import spatial


class VectorModel:
    def __init__(self):
        self.lemmas, self.matrix = self.load_index()
        nltk.download('punkt')
        nltk.download('stopwords')
        self.pymorphy2_analyzer = MorphAnalyzer()

    def load_index(self):
        with open('../task_3/inverted_index.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lemmas_list = list()
        #Матрица - 100 столбцов, в строках - термины (1 - если термин встречается в документе, 0 - нет)
        matrix = [[0] * 100 for _ in range(len(lines))]
        for idx, line in enumerate(lines):
            line = re.sub('\n', '', line)
            lemma = line.split(': ')[0]
            lemmas_list.append(lemma)
            pages = line.split(': ')[1].split(', ')
            for page in pages:
                matrix[idx][int(page) - 1] = 1

        return lemmas_list, np.array(matrix).transpose()

    def is_valid(self, token, stop_words, stop_symbols):
        valid = True
        if token in stop_words:
            valid = False
        elif token in stop_symbols:
            valid = False
        elif token.isdigit():
            valid = False
        elif re.match('[1-9]+,[0-9]+', token) is not None:
            valid = False
        elif re.match('^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$', token) is not None:
            valid = False

        try:
            num = float(token)
            if num:
                valid = False
        except ValueError:
            pass

        return valid

    def get_vector(self, search_string):
        stop_words = stopwords.words('russian')
        stop_symbols = [symbol for symbol in punctuation]
        stop_symbols += ['№', '«', '»', '—']

        #Токенизация запроса
        search_tokens = word_tokenize(search_string)
        search_tokens = [line_token.lower() for line_token in search_tokens]
        cleaned_search_tokens = [line_token for line_token in search_tokens if
                                 self.is_valid(line_token.lower(), stop_words, stop_symbols)]

        tokens_normal_form = [self.pymorphy2_analyzer.parse(token)[0].normal_form for token in cleaned_search_tokens]
        vector = [0] * len(self.lemmas)
        for token in tokens_normal_form:
            if token in self.lemmas:
                vector[self.lemmas.index(token)] = 1

        return vector

    def search(self, search_string):
        vector = self.get_vector(search_string)

        docs = dict()
        for idx, doc in enumerate(self.matrix):
            #doc - matrix row
            #Если хотя бы одна единица в строке
            if max(doc) == 1:
                #Ищем сходство, поэтому 1 - расстояние
                docs[idx + 1] = 1 - spatial.distance.cosine(vector, doc)
            else:
                docs[idx + 1] = 0.0

        sorted_docs = sorted(docs.items(), key=lambda x: x[1], reverse=True)

        return sorted_docs


if __name__ == '__main__':
    vector_model = VectorModel()
    print(vector_model.search('Рубль'))

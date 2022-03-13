import re
from nltk.tokenize import word_tokenize
import nltk
from pymorphy2 import MorphAnalyzer


class BooleanSearch:
    def __init__(self):
        self.words_to_symbols = {
            'and not': '^',
            'and': '&',
            'or': '|',
        }

        nltk.download('punkt')
        self.lemmas_dict = self.file_to_dict()
        self.pymorphy2_analyzer = MorphAnalyzer()

    def file_to_dict(self):
        d = dict()
        with open('inverted_index.txt', 'r', encoding='utf-8') as file:
            for line in file:
                lemma = line.split(': ')[0]
                pages = line.split(': ')[1].replace('\n', '').split(', ')
                d[lemma] = pages

        d['full_pages'] = [str(i) for i in range(1, 101)]
        d['none_pages'] = []

        return d

    def get_index_positions(self, list_of_elements, element):
        index_pos_list = []
        index_pos = 0
        while True:
            try:
                index_pos = list_of_elements.index(element, index_pos)
                index_pos_list.append(index_pos)
                index_pos += 1
            except ValueError:
                break
        return index_pos_list

    def search(self, search_string):
        repeat_search_string = search_string
        try:
            search_string = 'full_pages and ' + search_string.lower()

            for symbol in self.words_to_symbols.keys():
                search_string = re.sub(symbol, self.words_to_symbols[symbol], search_string)

            search_string = word_tokenize(search_string)
            r = []
            for token in search_string:
                if token not in self.words_to_symbols.values():
                    r.append(self.pymorphy2_analyzer.parse(token)[0].normal_form)
                else:
                    r.append(token)
            search_string = r

            for item in search_string:
                if item not in self.lemmas_dict.keys() and item not in self.words_to_symbols.values() and item not in [')', '(']:
                    for idx in self.get_index_positions(search_string, item):
                        search_string[idx] = 'none_pages'

            for lemma, pages in self.lemmas_dict.items():
                if lemma in search_string:
                    for idx in self.get_index_positions(search_string, lemma):
                        search_string[idx] = str(set(pages))

            result = [int(i) for i in list(eval(' '.join(search_string)))]
            result.sort()
            return result
        except Exception:
            print(f'Something went wrong with "{repeat_search_string}" request. Try to change your search string')
            return list()


if __name__ == '__main__':
    boolean_search = BooleanSearch()
    result = boolean_search.search('(путин OR зеленский) AND владимир')
    result2 = boolean_search.search('путин AND владимир')
    print(result)
    print(result2)

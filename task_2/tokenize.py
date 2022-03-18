import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer
from string import punctuation
import justext
import re


def get_paragraphs():
    result = dict()

    for i in range(1, 101):
        with open(f'../pages/page_{i}.txt', 'rb') as file:
            paragraphs = justext.justext(file.read(), justext.get_stoplist('Russian'))
            p = []
            for paragraph in paragraphs:
                p.append(paragraph.text)
            result[i] = p

    return result


def is_valid(token: str, stop_words, stop_symbols):
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


def get_lemmas_and_tokens(paragraphs_dict):
    nltk.download('stopwords')
    nltk.download('punkt')
    pymorphy2_analyzer = MorphAnalyzer()

    stop_words = stopwords.words('russian')
    stop_symbols = [symbol for symbol in punctuation]
    stop_symbols += ['№', '«', '»', '—']

    lemmas = dict()
    tokens = dict()
    for page_number, paragraphs in paragraphs_dict.items():
        l = dict()
        t = list()
        for paragraph in paragraphs:
            line_tokens = word_tokenize(paragraph)
            line_tokens = [line_token.lower() for line_token in line_tokens]
            cleaned_line_tokens = [line_token for line_token in line_tokens if
                                   is_valid(line_token.lower(), stop_words, stop_symbols)]
            t += cleaned_line_tokens

        for token in t:
            token_normal_form = pymorphy2_analyzer.parse(token)[0].normal_form
            if token_normal_form in l:
                if token not in l[token_normal_form]:
                    l[token_normal_form].append(token)
            else:
                l[token_normal_form] = [token, ]

        lemmas[page_number] = l
        tokens[page_number] = t

    return lemmas, tokens


def generate_result_files(lemmas, cleaned_tokens):
    with open('lemmas.txt', 'w', encoding='utf-8') as file:
        for i in range(1, len(lemmas) + 1):
            for lemma, tokens in lemmas[i].items():
                file.write(f'{[i]} {lemma}: ' + ', '.join(tokens) + '\n')

    with open('tokens.txt', 'w', encoding='utf-8') as file:
        for i in range(1, len(cleaned_tokens) + 1):
            for token in cleaned_tokens[i]:
                file.write(f'[{i}] {token}' + '\n')


if __name__ == '__main__':
    paragraphs = get_paragraphs()
    print('Page parsed')
    lemmas, tokens = get_lemmas_and_tokens(paragraphs)
    print('Lemmas and tokens were formed')
    generate_result_files(lemmas, tokens)
    print('Results were saved in files')

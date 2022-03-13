import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer
from string import punctuation
import justext
import re
import collections
from math import log10


def get_paragraphs_dict():
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
            cleaned_line_tokens = [line_token for line_token in line_tokens if is_valid(line_token.lower(), stop_words, stop_symbols)]
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


def calculate_tokens_tf(page_tokens):
    result = dict()
    for page_number, tokens in page_tokens.items():
        tf = dict()
        counter = collections.Counter(tokens)
        for token, count in counter.items():
            tf[token] = round(count / len(tokens), 3)

        result[page_number] = tf

    return result


def calculate_tokens_idf(page_tokens):
    result = dict()
    docs_num = len(page_tokens.keys())

    for page_num, tokens in page_tokens.items():
        unique_tokens = list(set(tokens))
        idf = dict()
        for unique_token in unique_tokens:
            count = 0
            for k, v in page_tokens.items():
                if unique_token in v:
                    count += 1

            idf[unique_token] = round(log10(docs_num / count), 3)

        result[page_num] = idf

    return result


def calculate_tokens_tfidf(page_tokens_tf, page_tokens_idf):
    result = dict()

    for page_num in range(1, len(page_tokens_tf.keys()) + 1):
        tfidf = dict()
        for token, tf in page_tokens_tf[page_num].items():
            tfidf[token] = round(tf * page_tokens_idf[page_num][token], 3)
        result[page_num] = tfidf

    return result


def calculate_lemmas_tf(page_tokens_tf, page_lemmas):
    result = dict()

    for page_num, lemmas_to_tokens in page_lemmas.items():
        tf = dict()
        for lemma, tokens in lemmas_to_tokens.items():
            sum = 0
            for token in tokens:
                sum += page_tokens_tf[page_num][token]
            tf[lemma] = sum
        result[page_num] = tf

    return result


def calculate_lemmas_idf(page_lemmas):
    result = dict()
    docs_num = len(page_lemmas.keys())

    for page_num, lemmas_to_tokens in page_lemmas.items():
        unique_lemmas = lemmas_to_tokens.keys()
        idf = dict()
        for unique_lemma in unique_lemmas:
            count = 0
            for k, v in page_lemmas.items():
                if unique_lemma in v.keys():
                    count += 1

            idf[unique_lemma] = round(log10(docs_num / count), 3)

        result[page_num] = idf

    return result


def calculate_lemmas_tfidf(page_lemmas_tf, page_lemmas_idf):
    result = dict()

    for page_num in range(1, len(page_lemmas_tf.keys()) + 1):
        tfidf = dict()
        for lemma, tf in page_lemmas_tf[page_num].items():
            tfidf[lemma] = round(tf * page_lemmas_idf[page_num][lemma], 3)
        result[page_num] = tfidf

    return result


def generate_result_files(page_tokens_idf, page_tokens_tfidf, page_lemmas_idf, page_lemmas_tfidf):
    for i in range(1, len(page_tokens_idf) + 1):
        with open(f'tokens/page_{i}.txt', 'w', encoding='utf-8') as file:
            for token, token_idf in page_tokens_idf[i].items():
                file.write(f'{token} {token_idf} {page_tokens_tfidf[i][token]}\n')

        with open(f'lemmas/page_{i}.txt', 'w', encoding='utf-8') as file:
            for lemma, lemma_idf in page_lemmas_idf[i].items():
                file.write(f'{lemma} {lemma_idf} {page_lemmas_tfidf[i][lemma]}\n')


if __name__ == '__main__':
    paragraphs_dict = get_paragraphs_dict()
    print('Page parsed')

    lemmas, tokens = get_lemmas_and_tokens(paragraphs_dict)
    print('Lemmas and tokens were formed')

    page_tokens_tf = calculate_tokens_tf(tokens)
    page_tokens_idf = calculate_tokens_idf(tokens)
    page_tokens_tfidf = calculate_tokens_tfidf(page_tokens_tf, page_tokens_idf)
    print('Metrics for tokens were calculated')

    page_lemmas_tf = calculate_lemmas_tf(page_tokens_tf, lemmas)
    page_lemmas_idf = calculate_lemmas_idf(lemmas)
    page_lemmas_tfidf = calculate_lemmas_tfidf(page_lemmas_tf, page_lemmas_idf)
    print('Metrics for lemmas were calculated')

    generate_result_files(page_tokens_idf, page_tokens_tfidf, page_lemmas_idf, page_lemmas_tfidf)
    print('Result files generated')


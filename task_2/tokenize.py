import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer
from string import punctuation
import justext
import re


def get_paragraphs():
    result = list()

    for i in range(1, 101):
        with open(f'../pages/page_{i}.txt', 'rb') as file:
            paragraphs = justext.justext(file.read(), justext.get_stoplist('Russian'))
            p = []
            for paragraph in paragraphs:
                p.append(paragraph.text)
            result += p

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


def get_lemmas_and_tokens(paragraphs):
    nltk.download('stopwords')
    nltk.download('punkt')
    pymorphy2_analyzer = MorphAnalyzer()

    stop_words = stopwords.words('russian')
    stop_symbols = [symbol for symbol in punctuation]
    stop_symbols += ['№', '«', '»', '—']

    lemmas = dict()
    tokens = list()
    for paragraph in paragraphs:
        line_tokens = word_tokenize(paragraph)
        line_tokens = [line_token.lower() for line_token in line_tokens]
        cleaned_line_tokens = [line_token for line_token in line_tokens if
                               is_valid(line_token.lower(), stop_words, stop_symbols)]
        tokens += cleaned_line_tokens

    for token in tokens:
        token_normal_form = pymorphy2_analyzer.parse(token)[0].normal_form
        if token_normal_form in lemmas:
            if token not in lemmas[token_normal_form]:
                lemmas[token_normal_form].append(token)
        else:
            lemmas[token_normal_form] = [token, ]

    tokens_without_duplicates = list(set(tokens))

    return lemmas, tokens_without_duplicates


def generate_result_files(lemmas, cleaned_tokens):
    with open('lemmas.txt', 'w', encoding='utf-8') as file:
        for lemma, tokens in lemmas.items():
            file.write(lemma + ': ' + ', '.join(tokens) + '\n')

    with open('tokens.txt', 'w', encoding='utf-8') as file:
        for token in cleaned_tokens:
            file.write(token + '\n')


if __name__ == '__main__':
    paragraphs = get_paragraphs()
    print('Page parsed')
    lemmas, tokens = get_lemmas_and_tokens(paragraphs)
    print('Lemmas and tokens were formed')
    generate_result_files(lemmas, tokens)
    print('Results were saved in files')

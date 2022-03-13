from task_4.tf_idf import get_paragraphs_dict, get_lemmas_and_tokens


def create_inverted_index(page_lemmas):
    all_lemmas = list()

    for page_num in range(1, len(page_lemmas.keys()) + 1):
        for item in page_lemmas[page_num].keys():
            all_lemmas.append(item)

    unique_lemmas = list(set(all_lemmas))
    unique_lemmas_dict_str = dict()
    unique_lemmas_dict_int = dict()

    for lemma in unique_lemmas:
        unique_lemmas_dict_int[lemma] = list()
        unique_lemmas_dict_str[lemma] = list()
        for page_num in range(1, len(page_lemmas.keys()) + 1):
            if lemma in page_lemmas[page_num].keys():
                unique_lemmas_dict_int[lemma].append(page_num)
                unique_lemmas_dict_str[lemma].append(str(page_num))
                continue

    return unique_lemmas_dict_int, unique_lemmas_dict_str


def save_result_file(inverted_index_dict):
    with open('inverted_index.txt', 'w', encoding='utf-8') as file:
        for lemma, pages in inverted_index_dict.items():
            file.write(lemma + ': ' + ', '.join(pages) + '\n')


if __name__ == '__main__':
    paragraphs_dict = get_paragraphs_dict()
    print('Page parsed')

    lemmas, tokens = get_lemmas_and_tokens(paragraphs_dict)
    print('Lemmas and tokens were formed')

    inverted_index_dict_int, inverted_index_dict_str = create_inverted_index(lemmas)
    print('Inverted index formed')

    save_result_file(inverted_index_dict_str)
    print('Result file saved')

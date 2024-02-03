import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
async def moderate_mat_in_sentence(sentence, bad_word=True):
    """
    returns: mat:bool, sentence
    """
    with open(os.path.join(BASE_DIR, "filter_profanity_russian_cached.txt"), "r", encoding="utf-8") as reader:
        lines = reader.readlines()
        mat_massive = [line.strip() for line in lines]

    if bad_word:
        mat_massive.extend(["говн", "срал", "сраны", "срать"])

    sentence = re.sub(r'[^а-яА-ЯёЁa-zA-Z\s]', '', sentence)
    words = sentence.split()

    found_mat = False
    for i, word in enumerate(words):
        for mat_word in mat_massive:
            if word.lower().startswith(mat_word):
                print("маты!", word, "\nВвод:", sentence)
                words[i] = '^_^'
                found_mat = True
                break

    return found_mat, ' '.join(words)
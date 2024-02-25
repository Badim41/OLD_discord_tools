import asyncio
import logging
import os
import re
from discord_tools.logs import Logs, Color
logger = Logs(warnings=False)

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

    sentence_changer = re.sub(r'[^а-яА-ЯёЁa-zA-Z\s]', '', sentence)
    words = sentence_changer.split(" ")
    logger.logging("words", words, color=Color.GRAY)

    found_mats = []
    for i, word in enumerate(words):
        for mat_word in mat_massive:
            if word.lower().startswith(mat_word):
                logger.logging("(error) маты!", word, "\nВвод:", sentence, color=Color.RED)
                words[i] = '^_^'
                found_mats.append(word)
                break

    if found_mats:
        return found_mats, ' '.join(words)
    else:
        return found_mats, sentence
import asyncio
import logging
import os
import re
from discord_tools.logs import Logs, Color
logger = Logs(warnings=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
async def moderate_mat_in_sentence(sentence, bad_word=True):
    """
    returns: mat:bool, sentence
    """
    with open(os.path.join(BASE_DIR, "filter_profanity_russian_cached.txt"), "r", encoding="utf-8") as reader:
        lines = reader.readlines()
        mat_massive = [line.strip() for line in lines]
        logger.logging("mat_massive:", mat_massive[:10], color=Color.GRAY)

    if bad_word:
        mat_massive.extend(["говн", "срал", "сраны", "срать"])

    sentence = re.sub(r'[^а-яА-ЯёЁa-zA-Z\s]', '', sentence)
    words = sentence.split(" ")
    logger.logging("words", words, color=Color.GRAY)

    found_mat = False
    for i, word in enumerate(words):
        for mat_word in mat_massive:
            if word.lower().startswith(mat_word):
                logger.logging("маты!", word, "\nВвод:", sentence, color=Color.RED)
                words[i] = '^_^'
                found_mat = True
                break

    return found_mat, ' '.join(words)
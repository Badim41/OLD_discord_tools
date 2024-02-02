import os

class SecretKey:
    voice_keys = "voice_avaible_keys"
    gpt_keys = "gpt_avaible_keys"

def create_secrets(key, value):
    """
    input1: keys:list, values:list
    input2: key:str, values:list
    """
    if isinstance(value, list):
        if isinstance(key, list):
            for key_1, value_1 in zip(key, value):
                os.environ[str(key_1)] = str(value_1)
        else:
            for value_1 in value:
                os.environ[str(key)] = str(value_1)
    else:
        os.environ[str(key)] = str(value)

def load_secret(key):
    return os.environ.get(str(key))

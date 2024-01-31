import asyncio
import time
from selenium.webdriver import Keys

# chat_keyboard = driver.find_element(by=By.CSS_SELECTOR,
#                                                         value="div.markup_a7e664.editor__66464.slateTextArea__0661c.fontSize16Padding__48818")
async def async_write_imitate(chat_keyboard):
    chat_keyboard.send_keys(" ")
    while True:
        chat_keyboard.send_keys(" ")
        await asyncio.sleep(1)
        chat_keyboard.send_keys(Keys.BACKSPACE)

def write_imitate(chat_keyboard):
    chat_keyboard.send_keys(" ")
    while True:
        chat_keyboard.send_keys(" ")
        time.sleep(1)
        chat_keyboard.send_keys(Keys.BACKSPACE)
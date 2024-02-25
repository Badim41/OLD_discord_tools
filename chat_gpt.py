import asyncio
import g4f
import json
import logging
import os
import random
import requests
import traceback
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage

from discord_tools.logs import Logs, Color
from discord_tools.secret import load_secret, SecretKey

_providers = [
    # AUTH
    # g4f.Provider.Raycast,
    # g4f.Provider.Phind,
    # g4f.Provider.Liaobots,  # - Doker output & Unauth
    # g4f.Provider.Bing,
    # g4f.Provider.Bard,
    # g4f.Provider.OpenaiChat,
    # g4f.Provider.Theb,

    # Binary location error
    # g4f.Provider.Poe,
    # g4f.Provider.GptChatly,
    # g4f.Provider.AItianhuSpace,


    # g4f.Provider.GPTalk, # error 'data'
    # g4f.Provider.GeminiProChat, # Server Error
    # g4f.Provider.Gpt6, # ?
    # g4f.Provider.AiChatOnline, # ?
    # g4f.Provider.GptGo, # error
    # g4f.Provider.Chatxyz, # error


    # not exists
    # g4f.Provider.ChatgptAi,
    # g4f.Provider.OnlineGpt,
    # g4f.Provider.ChatgptNext,


    # g4f.Provider.Vercel,  # cut answer
    # g4f.Provider.ChatgptDemo,  # ?



    # g4f.Provider.ChatgptLogin,  # error 403
    # g4f.Provider.ChatgptX,  # error
    # g4f.Provider.ChatgptFree,

    # Short answer
    # g4f.Provider.Aura,
    # g4f.Provider.ChatBase,

    g4f.Provider.ChatForAi, # too many req

    # bad providers
    # g4f.Provider.NoowAi,  # Not supported yet
    # g4f.Provider.GptGod,  # error list
    # g4f.Provider.FreeGpt,# wrong language
    # g4f.Provider.GptForLove,  # error no OpenAI Key
    # g4f.Provider.Opchatgpts,  # bad
    # g4f.Provider.Chatgpt4Online,  # - bad

    # g4f.Provider.Llama2, # no model

    # not working
    g4f.Provider.You,
    g4f.Provider.GeekGpt,
    g4f.Provider.AiAsk,
    g4f.Provider.Hashnode,
    g4f.Provider.FakeGpt,
    g4f.Provider.Aichat,

    # undetected chrome driver
    # g4f.Provider.MyShell,
    # g4f.Provider.PerplexityAi,
    # g4f.Provider.TalkAi,
]


async def remove_last_format_simbols(text, format="```"):
    parts = text.split(format)
    if len(parts) == 4:
        corrected_text = format.join(parts[:3]) + parts[3]
        return corrected_text
    return text


async def load_history_from_json(user_id):
    if not user_id:
        return []

    try:
        with open(f'gpt_history/{user_id}_history.json', 'r') as file:
            chat_history = json.load(file)
    except FileNotFoundError:
        chat_history = []

    # print("load_history:", chat_history)
    return chat_history


def serialize_chat_message(obj):
    if isinstance(obj, ChatCompletionMessage):
        return {
            'role': obj.role,
            'content': obj.content,
        }
    # Add more checks for other custom objects if needed
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


async def save_history(history, user_id):
    if not user_id:
        return

    # print("Save history:", history, user_id)
    with open(f'gpt_history/{user_id}_history.json', 'w') as file:
        json.dump(history, file, indent=4, default=serialize_chat_message)


async def get_sys_prompt(user_id, gpt_role):
    if gpt_role == "GPT" or not gpt_role or not user_id:
        sys_prompt = [{"role": "system", "content": "Ты полезный ассистент и даёшь только полезную информацию"}]
    else:
        sys_prompt = [{"role": "system", "content": gpt_role}]
    return sys_prompt


async def clear_history(user_id):
    try:
        os.remove(f'gpt_history/{user_id}_history.json')
    except FileNotFoundError:
        pass


async def trim_history(history, max_length=4000):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


class ChatGPT:
    def __init__(self, openAI_keys=None, openAI_moderation=None, auth_keys=None, save_history=True, warnings=False,
                 errors=True, testing=False):
        if isinstance(openAI_moderation, list):
            self.openAI_keys = openAI_keys
        elif isinstance(openAI_moderation, str):
            self.openAI_keys = [openAI_keys]
        elif openAI_keys is None:
            self.openAI_keys = load_secret(SecretKey.gpt_keys).split(";")
        else:
            self.openAI_keys = openAI_keys

        self.moderation_queue = 0
        self.is_running_moderation = False
        self.previous_requests_moderation = {}

        if isinstance(openAI_moderation, list):
            self.openAI_moderation = openAI_moderation
        elif isinstance(openAI_moderation, str):
            self.openAI_moderation = [openAI_moderation]
        elif openAI_keys:
            self.openAI_moderation = openAI_keys
        elif openAI_moderation is None:
            self.openAI_moderation = load_secret(SecretKey.gpt_keys).split(";")
        else:
            self.openAI_moderation = openAI_moderation

        if isinstance(auth_keys, list):
            self.openAI_auth_keys = auth_keys
        elif isinstance(auth_keys, str):
            self.openAI_auth_keys = [auth_keys]
        elif auth_keys is None:
            self.openAI_auth_keys = load_secret(SecretKey.gpt_auth).split(";")
        else:
            self.openAI_auth_keys = auth_keys

        if save_history:
            if not os.path.exists('gpt_history'):
                os.mkdir('gpt_history')

        self.logger = Logs(warnings=warnings, errors=errors)
        self.testing = testing

    async def run_all_gpt(self, prompt, mode="Fast", user_id=None, gpt_role=None, limited=False):
        self.logger.logging("run GPT", prompt, color=Color.GRAY)
        if prompt == "" or prompt is None:
            return "Пустой запрос"

        # Ограничение для поиска
        values = [False, True]
        if limited:
            values = [False]

        # обрезка зщапроса
        prompt = prompt[:4000]
        # загрузка истории
        chat_history = await load_history_from_json(user_id)
        chat_history.append({"role": "user", "content": prompt})
        chat_history = await trim_history(chat_history, max_length=4500)

        if "Fast" in mode:
            for value in values:
                answer = await self.run_official_gpt(chat_history, 1, value, user_id, gpt_role)
                if answer and prompt not in answer:
                    chat_history.append({"role": "assistant", "content": answer})
                    await save_history(chat_history, user_id)
                    return answer

            functions2 = [self.one_gpt_run(provider, chat_history, 120, user_id, gpt_role) for provider in _providers]
            done, pending = await asyncio.wait(functions2, return_when=asyncio.FIRST_COMPLETED)
            # Принудительное завершение оставшихся функций
            for task in pending:
                task.cancel()

            # Получение результата выполненной функции
            for task in done:
                result = await task

                chat_history.append({"role": "assistant", "content": result})
                await save_history(chat_history, user_id)

                return result
        if "All" in mode:

            functions = [self.one_gpt_run(provider, chat_history, 1, user_id, gpt_role) for provider in _providers]
            functions += [self.run_official_gpt(chat_history, 1, value, user_id, gpt_role) for value in values]
            results = await asyncio.gather(*functions)  # результаты всех функций
            new_results = []
            for i, result in enumerate(results):
                if not result is None and not result.replace("\n", "").replace(" ", "") == "" or result == "None":
                    new_results.append(result)

            # сохранение истории
            result = '\n\n==Другой ответ==\n\n'.join(new_results)
            chat_history.append({"role": "assistant", "content": new_results[0]})
            await save_history(chat_history, user_id)

            return result
        self.logger.logging("error: no GPT mode")
        return "Не выбран режим GPT (это какая-то ошибка, лучше свяжитесь с разработчиком, если эта ошибка продолжит появляться)"

    async def one_gpt_run(self, provider, chat_history, delay_for_gpt, user_id, gpt_role):
        try:
            # в зависимости от аутефикации получаем ответ
            result = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                provider=provider,
                messages=await get_sys_prompt(user_id, gpt_role) + chat_history,
                cookies={"Fake": ""},
                auth=True,
                timeout=30
            )
            if "!DOCTYPE" in str(result) or "https://gptgo.ai" in str(result):
                self.logger.logging("Doker File", color=Color.GRAY)
                # делаем задержку
                await asyncio.sleep(delay_for_gpt)
                return

            if result is None or result.replace("\n", "").replace(" ", "") == "" or result == "None":
                # делаем задержку, чтобы не вывелся пустой результат
                await asyncio.sleep(delay_for_gpt)
                return

            # если больше 3 "```" (форматов)
            result = await remove_last_format_simbols(result)

            # добавляем имя провайдера
            provider = str(provider)
            provider = provider[provider.find("'") + 1:]
            provider = provider[:provider.find("'")]
            self.logger.logging("PROVIDER:", provider, result, "\n", color=Color.GRAY)
            return result  # + f"\n||Провайдер: {provider}, Модель: {gpt_model}||"
        except Exception as e:
            self.logger.logging(f"warning in {str(provider)}", str(e), color=Color.GRAY)
            await asyncio.sleep(delay_for_gpt)
            return ""

    async def run_official_gpt(self, chat_history, delay_for_gpt, key_gpt, user_id, gpt_role):
        open_ai_keys = self.openAI_keys
        auth_keys = self.openAI_auth_keys
        if key_gpt:
            if not open_ai_keys:
                await asyncio.sleep(delay_for_gpt)
                return ""
            try:
                if len(open_ai_keys) != 0:
                    client = AsyncOpenAI(api_key="sk-" + open_ai_keys[0])
                    completion = await client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=await get_sys_prompt(user_id, gpt_role) + chat_history
                    )
                    self.logger.logging("ChatGPT_OFFICIAL_1", completion.choices[0].message.content, color=Color.GRAY)
                    return completion.choices[0].message.content
                else:
                    self.logger.logging("error: no GPT keys(2)")
                    self.openAI_keys = self.openAI_moderation
                    await asyncio.sleep(delay_for_gpt)
                    return ""
            except Exception as e:
                self.logger.logging("error (id gpt-off1)", e)
                if "Error code: 429" in str(e) or "Incorrect API key provided" in str(e):
                    self.openAI_keys = self.openAI_keys[1:]
                return await self.run_official_gpt(chat_history, delay_for_gpt, True, user_id, gpt_role)
        else:
            if not auth_keys:
                await asyncio.sleep(delay_for_gpt)
                return ""
            try:
                if len(auth_keys) != 0 and auth_keys:
                    random.shuffle(auth_keys)
                    response = await g4f.ChatCompletion.create_async(
                        model=g4f.models.default,
                        messages=await get_sys_prompt(user_id, gpt_role) + chat_history,
                        provider=g4f.Provider.OpenaiChat,
                        access_token=auth_keys[0],
                        auth=auth_keys[0],
                        timeout = 30
                    )
                    if not response:
                        await asyncio.sleep(delay_for_gpt)
                    self.logger.logging("ChatGPT_OFFICIAL_2:", response, color=Color.GRAY)
                    return response
                else:
                    self.logger.logging("error gpt-off2 no auth keys")
            except Exception as e:
                self.logger.logging("error gpt-off2", str(traceback.format_exc()))

                # if len(str(e)) < 1000:
                #     await bot.send_message(owner_id_1, str(e))
                await asyncio.sleep(delay_for_gpt)
                return ""

    async def moderation_request(self, text, error=0):
        if not self.openAI_moderation:
            self.logger.logging("No moderation keys", Color.RED)
            return False, ""

        if len(text) < 3:
            return False, ""

        if text in self.previous_requests_moderation:
            self.logger.logging(f"Запрос '{text}' уже был выполнен, категория нарушений: {self.previous_requests_moderation[text][1]}", color=Color.GRAY)
            return self.previous_requests_moderation[text]

        if self.is_running_moderation:
            self.logger.logging("Running!", color=Color.GRAY)
            await asyncio.sleep(0.25)
        self.is_running_moderation = True
        number = self.moderation_queue % len(self.openAI_moderation)
        api_key = self.openAI_moderation[number]
        self.moderation_queue += 1
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {'sk-' + api_key}"
        }
        data = {
            "input": text
        }
        url = "https://api.openai.com/v1/moderations"

        response = requests.post(url, headers=headers, json=data)
        self.is_running_moderation = False
        if response.status_code == 200:
            self.logger.logging(f"api_key: {api_key}", color=Color.GRAY)
            result = response.json()
            flagged = result['results'][0]['flagged']
            categories = result['results'][0]['categories']
            if flagged:
                violated_categories = [category for category, value in categories.items() if value]
                self.previous_requests_moderation[text] = (True, violated_categories)
                return True, violated_categories
            else:
                self.previous_requests_moderation[text] = (False, "")
                return False, ""
        else:
            if error == 10:
                return None, f"Request failed with status code: {response.status_code}"
            self.logger.logging(f"Request failed with status code: {response.status_code}", color=Color.GRAY)
            delay = (error + 1) * 5
            self.logger.logging("Delay:", delay, text, color=Color.GRAY)
            await asyncio.sleep(0.1)
            result1, result2 = await self.moderation_request("." + text, error=error + 1)
            return result1, result2

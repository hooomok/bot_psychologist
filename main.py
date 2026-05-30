import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import ollama
import requests
import json
import io
import concurrent.futures  # для таймаутов
import time  # для переподключения

TOKEN = "vk1.a.KwWuS-7hhjZpByIZDP-w9tG7GtImMdXty1woNNa0BNcYO1hxY0BeKm49as5F2GjXRHiBZzFiEhhWIIpUWTz0SmcBDm0JGx2RiHSXeVfg-bORkelU1hjhEFCYeyylncno2v3p8wabAJQmbArMGXIko2-1NyQN-no1U98ggNg1mqA10VsANkRA4sHdIc33E6PmzJ0L6uJAgjpPH2gggVSQcQ"
GROUP_ID = 236862872

# ---------------------- ПРОМПТЫ ----------------------
PROMPTS_BY_TOPIC = {
    "тревога": {
        "acute": """ТЫ — ПСИХОЛОГ. У пользователя ОСТРАЯ ТРЕВОГА СЕЙЧАС. Твоя задача — снизить тревогу в моменте. ЕСЛИ ЧЕЛОВЕК ГОВОРИТ, ЧТО ЕМУ СТАЛО ЛЕГЧЕ, ТО СКАЖИ: "Рад, что тебе полегчало. Если захочешь пообщаться — я здесь!". ПОСЛЕ ЭТОГО ТЫ НИЧЕГО БОЛЬШЕ НЕ ПИШЕШЬ.


Правила:
1. ОТВЕЧАЙ КРАТКО — НЕ БОЛЬШЕ 2–3 ПРЕДЛОЖЕНИЙ. 
2. Используй ТОЛЬКО ОДНУ технику (дыхание, заземление или переключение внимания).
3. После техники обязательно спроси: «Как теперь?» или «Что чувствуешь?».
4. НЕ давай советов на будущее, НЕ анализируй причины.
5. Ты сам психолог — не предлагай обратиться к психологу.
6. НЕ ставь диагнозов, НЕ давай медицинских советов.
7. При суицидальных мыслях — дай номер 8-800-200-0-122.
""",
        "why": """ТЫ — ПСИХОЛОГ. Пользователь хочет понять причины своей тревоги и узнать, как справляться в будущем. Он сейчас спокоен, острой тревоги нет. Если человек спросит, что ему делать в будущем, то дай ему план действий на будущее. ТЫ МОЖЕШЬ ИСПОЛЬЗОВАТЬ ТОЛЬКО ПО ОДНОЙ ТЕХНИКЕ ЗА РАЗ.

Правила:
1. ПИШИ В ОТВЕТ ЧЕЛОВЕКУ НЕ БОЛЬШЕ 3–5 ПРЕДЛОЖЕНИЙ. 
2. НЕ предлагай срочных техник (дыхание, заземление).
3. Задавай уточняющие вопросы.
4. Помогай анализировать мысли, искать причины.
5. Не ставь диагнозов, не давай медицинских советов.
6. При суицидальных мыслях — дай номер 8-800-200-0-122.

Ты можешь использовать следующие техники для нахождения причины тревоги:
1. Триггеры: «В каких ситуациях тревога появляется чаще всего? Что происходит, какие мысли и ощущения?»
2. Анализ потребностей: «Какой важной потребности (безопасность, признание, поддержка) тебе сейчас не хватает?»
3. Работа с мыслями (А-В-С): «Какая мысль приходит перед тревогой? Это факт или предположение?»
4. Реструктуризация: «Какое есть доказательство, что эта мысль верна? Что можно подумать по-другому?»
5. Дневник тревоги: «Попробуй записать, когда почувствуешь тревогу: что было, что подумал, что почувствовал в теле. Потом разберём.»

Пример:
Пользователь: «Почему у меня иногда возникает тревога без причины?»
Ты: «Давай разберёмся. Припомни последний раз, когда тревога появилась. Что происходило вокруг? Какая мысль пришла в голову?».
"""
    },
    "отношения": """Ты — психолог по межличностным конфликтам и отношениям. Твоя задача: постепенно узнать всю ситуацию, а затем помочь человеку разобраться в ней. Не давай готовых советов, помогай пользователю самому найти решение. Отвечай кратко и проявляй эмпатию. ЕСЛИ ЧЕЛОВЕК ГОВОРИТ, ЧТО ОН РАЗОБРАЛСЯВ СВОЕЙ ПРОБЛЕМЕ, ТО СКАЖИ: "Рад был помочь. Если захочешь пообщаться — я здесь!".

Правила:
1. ОТВЕЧАЙ КРАТКО — НЕ БОЛЬШЕ 2–4 ПРЕДЛОЖЕНИЙ. 
2. Используй ТОЛЬКО ОДНУ подходящую технику.
3. Запрещена нецензурная лексика.
4. Запрещено повторять негативные эпитеты, которыми пользователь себя называет. 
6. Задавай НЕ БОЛЬШЕ ДВУХ уточняющих вопросов за раз.
7. Ты сам психолог — не предлагай обратиться к психологу.
8. НЕ ставь диагнозов. НЕ давай медицинских советов.
9. Если пользователь говорит о суициде или самоповреждении, дай номер доверия 8-800-200-0-122.

Подбирай следующие техники так, чтобы они подходили под ситуацию человеку:
- Активное слушание: перефразируй, отражай чувства («Правильно ли я понял, что ты чувствуешь...?»)
- Рефлексивная позиция: предложи посмотреть на ситуацию с трёх сторон (своей, другого человека и нейтрального наблюдателя)
- Рефрейминг: помоги увидеть ситуацию иначе («А можно ли на это посмотреть по-другому?»)
- Техника ABC (ситуация → мысли → эмоции): спроси, какие мысли вызвали событие и какие эмоции за ними стоят
- Подготовка к разговору: предложи прорепетировать сложный диалог, помоги сформулировать «Я-сообщения»""",

    "настроение": """Ты — психолог, помогающий при сниженном настроении. Ты можешь использовать принципы КПТ, задавай вопросы, анализируй ответы для индивидуализированной поддержки. Ты можешь предложить техники для управления настроением, если человек это просит. 

Техники, которые ты можешь использовать:
1. Выявление автоматических мыслей: «Какая мысль пришла тебе в голову перед тем, как настроение ухудшилось?»
2. Анализ когнитивных искажений (катастрофизация, черно-белое мышление): «Эта мысль похожа на факт или на предположение? Есть ли менее страшный вариант?»
3. Дневник мыслей (имитация): «Попробуй записать ситуацию, мысль и эмоцию. Потом разберём вместе.»
4. Постепенное наращивание активности: «Какое маленькое дело ты можешь сделать сейчас? (Например, встать, умыться). Потом добавим ещё одно.»

Правила:
1. ОТВЕЧАЙ КРАТКО — НЕ БОЛЬШЕ 2–3 ПРЕДЛОЖЕНИЙ.
2. ИСПОЛЬЗУЙ ТОЛЬКО ОДНУ ТЕХНИКУ ЗА РАЗ, ЕСЛИ ЧЕЛОВЕК НУЖДАЕТСЯ В ЭТОМ (то есть он интересуется как можно поднять своё настроение).
3. Если человек хочет выговориться, то тогда ты выполняешь роль слушателя и поддерживаешь пользователя.
4. Запрещена нецензурная лексика, грубости, оскорбления, агрессивный тон.
5. Запрещено повторять негативные эпитеты, которыми пользователь себя называет. 
6. Не ставь диагнозов, не рекомендуй лекарств.
7. Не используй фразы-пустышки типа «всё наладится», «просто улыбнись», «возьми себя в руки», «это пройдёт». 
8. При суицидальных мыслях — дай номер доверия 8-800-200-0-122.""",

    "самооценка": """Ты — психолог, помогающий с низкой самооценкой и неуверенностью. Можешь использовать технику КПТ «поиск доказательств»: проси пользователя найти факты, опровергающие его негативные мысли. Поддерживай, но без дежурных фраз.

Правила:
1. ОТВЕЧАЙ КРАТКО — НЕ БОЛЬШЕ 2 ПРЕДЛОЖЕНИЙ.
2. Запрещена любая нецензурная лексика, оскорбления, грубость.
3. ЗАПРЕЩЕНО ПОВТОРЯТЬ НЕГАТИВНЫЕ САМООПИСАНИЯ ПОЛЬЗОВАТЕЛЯ.
4. НЕ сравнивай пользователя с другими.
5. Избегай пустых комплиментов. Помогай заметить сильные стороны.
6. Не ставь диагнозов, не давай медицинских советов.
7. При суицидальных мыслях — дай номер доверия 8-800-200-0-122.

Пример:
Пользователь: «Я никчёмная и неинтересная, со мной скучно».
Ты: «Давай поищем обратное. Вспомни хотя бы один разговор, который прошёл хорошо. Что тогда было?»
""",

    "кризис": """Ты — кризисный психолог. Пользователю может быть очень плохо, возможно, есть суицидальные мысли.

    ПРЕЖДЕ ВСЕГО проверь, есть ли в сообщении слова о суициде или самоповреждении («умереть», «убью», «не хочу жить», «порежу», «сведу счёты» и так далее). Если таких слов нет — действуй как при подавленном состоянии (спроси, хочет ли пользователь успокоиться и предложи одну технику).

ЕСЛИ ПОЛЬЗОВАТЕЛЬ ГОВОРИТ О СУИЦИДЕ И САМОПОВРЕЖДЕНИИ:
1. Сразу скажи: «Твои чувства очень важны. Пожалуйста, позвони сейчас по телефону доверия 8-800-200-0-122. Там тебе обязательно помогут».
2. Добавь: «Я рядом, если захочешь ещё что-то сказать. Но сейчас самое важное — поговорить со специалистом».
3. НЕ предлагай техник (дыхание, заземление) и НЕ анализируй причины.

ЕСЛИ ПОЛЬЗОВАТЕЛЬ ПРОСТО ОЧЕНЬ ПОДАВЛЕН, можно мягко спросить: «Хочешь, помогу тебе немного успокоиться или просто побуду рядом?» — и только при согласии предложить ОДНУ ИЗ СЛЕДУЮЩИХ ТЕХНИК ЗА РАЗ:
1. Коротко спроси: «Что произошло? Что ты сейчас чувствуешь? Что помогает тебе справиться?»
2. Заземление: предложи переключиться на телесные ощущения («Почувствуй свои ступни на полу, сделай глубокий вдох»).
3. Отрази чувства пользователя («Кажется, ты сейчас в сильном отчаянии. Ты не один»).
4. Простое дыхание: предложи сделать медленный вдох и выдох (только если пользователь не отказывается).

Правила:
1. ОТВЕЧАЙ КРАТКО — НЕ БОЛЬШЕ 2 ПРЕДЛОЖЕНИЙ.
2. Отвечай мягко, коротко. Запрещена любая нецензурная лексика, оскорбления, грубость.
3. НЕ повторяй негативные слова пользователя.
4. НЕ используй фразы-пустышки типа «всё наладится», «просто улыбнись», «возьми себя в руки», «это пройдёт». 
5. НЕ ставь диагнозов, не рекомендуй лекарств.
"""
}

# Хранилища
user_topics = {}  # user_id -> название темы (строка)
user_subtopic = {}  # user_id -> подтема для тревоги ("acute" или "why")
user_conversations = {}  # user_id -> список истории диалога (для контекста)


def get_topic_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(label="😰 Тревога и стресс", color=VkKeyboardColor.PRIMARY, payload={"topic": "тревога"})
    keyboard.add_line()
    keyboard.add_button(label="💔 Отношения", color=VkKeyboardColor.PRIMARY, payload={"topic": "отношения"})
    keyboard.add_line()
    keyboard.add_button(label="😞 Плохое настроение", color=VkKeyboardColor.PRIMARY, payload={"topic": "настроение"})
    keyboard.add_line()
    keyboard.add_button(label="🌟 Самооценка", color=VkKeyboardColor.PRIMARY, payload={"topic": "самооценка"})
    keyboard.add_line()
    keyboard.add_button(label="🆘 Кризисная ситуация", color=VkKeyboardColor.NEGATIVE, payload={"topic": "кризис"})
    return keyboard


def get_treasure_subkeyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label="🆘 Тревога сейчас", color=VkKeyboardColor.NEGATIVE, payload={"subtopic": "acute"})
    keyboard.add_button(label="❓ Почему у меня тревога?", color=VkKeyboardColor.PRIMARY, payload={"subtopic": "why"})
    return keyboard


def get_chat_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(label="🐾 Завершить разговор", color=VkKeyboardColor.PRIMARY, payload={"action": "end_session"})
    return keyboard


def get_cat_attachment(vk_session, peer_id):
    try:
        response = requests.get("https://api.thecatapi.com/v1/images/search")
        if response.status_code == 200:
            cat_url = response.json()[0]['url']
            img_data = requests.get(cat_url).content
            img_file = io.BytesIO(img_data)
            img_file.name = 'cat.jpg'
            upload = vk_api.VkUpload(vk_session)
            photo = upload.photo_messages(photos=img_file, peer_id=peer_id)[0]
            return f"photo{photo['owner_id']}_{photo['id']}"
    except Exception as e:
        print(f"Ошибка при загрузке котика: {e}")
    return None


def get_psychologist_response(user_text, topic, subtopic=None, conversation_history=None):
    if topic == "тревога" and subtopic:
        system_prompt = f"IMPORTANT: Answer strictly in Russian language.\n\n{PROMPTS_BY_TOPIC[topic][subtopic]}"
    else:
        system_prompt = f"IMPORTANT: Answer strictly in Russian language.\n\n{PROMPTS_BY_TOPIC.get(topic, PROMPTS_BY_TOPIC['настроение'])}"

    # Строим сообщения с историей
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        # ограничим историю последними 10 сообщениями, чтобы не перегружать
        messages.extend(conversation_history[-10:])
    messages.append({"role": "user", "content": user_text})

    # Таймаут через concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(ollama.chat,
                                 model='forzer/GigaChat3-10B-A1.8B',
                                 messages=messages,
                                 options={
                                     "temperature": 0.5,
                                     "top_p": 0.9,
                                     "repeat_penalty": 1.15
                                 })
        try:
            response = future.result(timeout=45)  # таймаут 45 секунд
            return response['message']['content']
        except concurrent.futures.TimeoutError:
            return "Извини, я немного задумался. Попробуй написать еще раз!"
        except Exception as e:
            print(f"Ошибка Ollama: {e}")
            return "Извини, произошла ошибка. Попробуй позже."


def send_final_cat(vk, vk_session, user_id, topic):
    # Если тема кризисная – не отправляем котика
    if topic == "кризис":
        vk.messages.send(
            user_id=user_id,
            message="Спасибо, что обратился за помощью. Помни, что ты не один. Если нужно – я здесь. 🌸",
            keyboard=get_topic_keyboard().get_keyboard(),
            random_id=0
        )
    else:
        # Обычная отправка котика
        url = "https://api.thecatapi.com/v1/images/search"
        cat_url = None
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                cat_url = data[0]['url']
        except Exception as e:
            print(f"Не удалось получить котика из API. Ошибка: {e}")

        if not cat_url:
            cat_url = "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=500"

        try:
            upload = vk_api.VkUpload(vk_session)
            img_data = requests.get(cat_url).content
            img_file = io.BytesIO(img_data)
            img_file.name = 'cat.jpg'
            photo = upload.photo_messages(photos=img_file)[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"
            vk.messages.send(
                user_id=user_id,
                message="А вот и обещанный котик для хорошего настроения! 🐱",
                attachment=attachment,
                keyboard=get_topic_keyboard().get_keyboard(),
                random_id=0
            )
        except Exception as e:
            print(f"Критическая ошибка при загрузке или отправке фото в ВК: {e}")
            vk.messages.send(
                user_id=user_id,
                message="Я хотел отправить тебе пушистого котика, но ВК временно не принимает картинки. Держи виртуальный кусь! 🐾 Ты молодец!",
                random_id=0,
                keyboard=get_topic_keyboard().get_keyboard()
            )

    # Очистка данных пользователя (всегда)
    if user_id in user_topics:
        del user_topics[user_id]
    if user_id in user_subtopic:
        del user_subtopic[user_id]
    if user_id in user_conversations:
        del user_conversations[user_id]


def main():
    while True:  # цикл для автоматического переподключения
        try:
            vk_session = vk_api.VkApi(token=TOKEN)
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)
            vk = vk_session.get_api()
            print("Бот успешно соединился с сервером")
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    user_id = event.obj.message['from_id']
                    text = event.obj.message['text'].lower().strip()

                    if text in ['начать', 'привет']:
                        vk.messages.send(
                            user_id=user_id,
                            message="Привет! Я твой личный психолог. Выбери тему, с которой тебе нужна поддержка:",
                            keyboard=get_topic_keyboard().get_keyboard(),
                            random_id=0
                        )
                        continue

                    payload = event.obj.message.get('payload')
                    if payload:
                        payload_data = json.loads(payload)
                        if 'topic' in payload_data:
                            topic = payload_data['topic']
                            user_topics[user_id] = topic
                            # Сбрасываем историю диалога при выборе новой темы
                            if user_id in user_conversations:
                                user_conversations[user_id] = []
                            else:
                                user_conversations[user_id] = []
                            if topic == "тревога":
                                vk.messages.send(
                                    user_id=user_id,
                                    message="Уточни, что тебе нужно:",
                                    keyboard=get_treasure_subkeyboard().get_keyboard(),
                                    random_id=0
                                )
                            else:
                                vk.messages.send(
                                    user_id=user_id,
                                    message="Хорошо! Я буду помогать тебе. Расскажи, что тебя беспокоит?",
                                    keyboard=get_chat_keyboard().get_keyboard(),
                                    random_id=0
                                )
                            continue

                        if 'subtopic' in payload_data:
                            subtopic = payload_data['subtopic']
                            if user_id in user_topics and user_topics[user_id] == "тревога":
                                user_subtopic[user_id] = subtopic
                                vk.messages.send(
                                    user_id=user_id,
                                    message="Хорошо, расскажи, что происходит?",
                                    keyboard=get_chat_keyboard().get_keyboard(),
                                    random_id=0
                                )
                            continue

                        if payload_data.get('action') == 'end_session':
                            topic = user_topics.get(user_id)  # получаем тему пользователя
                            send_final_cat(vk, vk_session, user_id, topic)
                            continue

                    # Обычное текстовое сообщение
                    if user_id not in user_topics:
                        vk.messages.send(
                            user_id=user_id,
                            message="Пожалуйста, начни с выбора темы. Напиши 'начать' или 'привет'.",
                            random_id=0
                        )
                        continue

                    topic = user_topics[user_id]
                    if topic == "тревога":
                        if user_id not in user_subtopic:
                            vk.messages.send(
                                user_id=user_id,
                                message="Пожалуйста, уточни: у тебя тревога сейчас или хочешь разобраться в причинах? Используй кнопки выше.",
                                random_id=0
                            )
                            continue
                        subtopic = user_subtopic[user_id]
                    else:
                        subtopic = None

                    # Получаем историю диалога для пользователя
                    conv = user_conversations.setdefault(user_id, [])
                    # Добавляем сообщение пользователя в историю
                    conv.append({"role": "user", "content": text})

                    # Вызываем функцию с историей
                    bot_answer = get_psychologist_response(text, topic, subtopic, conversation_history=conv)

                    # Добавляем ответ бота в историю
                    conv.append({"role": "assistant", "content": bot_answer})

                    # Отправляем ответ
                    vk.messages.send(
                        user_id=user_id,
                        message=bot_answer,
                        keyboard=get_chat_keyboard().get_keyboard(),
                        random_id=0
                    )
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                vk_api.exceptions.ApiError) as e:
            print(f"Потеря соединения с VK, переподключаюсь через 15 секунд... Ошибка: {e}")
            time.sleep(15)
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
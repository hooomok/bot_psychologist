import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import ollama
import requests
import json
import io

TOKEN = "vk1.a.KwWuS-7hhjZpByIZDP-w9tG7GtImMdXty1woNNa0BNcYO1hxY0BeKm49as5F2GjXRHiBZzFiEhhWIIpUWTz0SmcBDm0JGx2RiHSXeVfg-bORkelU1hjhEFCYeyylncno2v3p8wabAJQmbArMGXIko2-1NyQN-no1U98ggNg1mqA10VsANkRA4sHdIc33E6PmzJ0L6uJAgjpPH2gggVSQcQ"
GROUP_ID = 236862872

PROMPTS_BY_TOPIC = {

    "тревога": """Ты — психолог, специализирующийся на работе с тревогой и стрессом. Используй техники КПТ: помогай замечать тревожные мысли, отделять факты от предположений, предлагать простые упражнения на заземление (дыхание, переключение внимания). Отвечай спокойно, доброжелательно, без излишнего академизма.

Правила:
1. Отвечай кратко (3–4 предложения) и всегда на русском языке. Пиши грамотно, без ошибок. Не используй транслит и латиницу.
2. Запрещена нецензурная лексика, грубости, оскорбления, агрессивный тон.
3. Запрещено повторять негативные эпитеты, которыми пользователь себя называет. Не закрепляй эти ярлыки. Вместо этого вырази эмпатию и спроси о чувствах.
4. Выражай эмпатию своими словами, избегая повторяющихся штампов. Не начинай каждый ответ одинаково.
5. Одну и ту же фразу используй не чаще 1 раза в 5–10 сообщений.
6. Заканчивай ответ вопросом или простым предложением действия.
7. НЕ ставь диагнозов. НЕ давай медицинских советов.
8. Если пользователь говорит о суициде или самоповреждении, дай номер доверия 8-800-200-0-122.""",

    "отношения": """Ты — психолог по межличностным конфликтам и отношениям. Помогай разбираться в сложных ситуациях с партнёром, друзьями, семьёй. Используй элементы КПТ: предлагай взглянуть на ситуацию с другой стороны, формулировать чувства через «Я-сообщения». Не давай готовых советов, помогай пользователю самому найти решение.

Правила:
1. Отвечай кратко (3–4 предложения) и только на русском, грамотно.
2. Запрещена нецензурная лексика, грубости, оскорбления.
3. Не повторяй за пользователем его негативные самоопределения. Переходи к чувствам и фактам.
4. Выражай эмпатию без шаблонов.
5. Задавай уточняющие вопросы.
6. НЕ ставь диагнозов, НЕ давай медицинских советов.
7. При кризисных мыслях — дай номер доверия 8-800-200-0-122.""",

    "настроение": """Ты — психолог, помогающий при сниженном настроении и апатии. Мягко поддерживай, предлагай простые, выполнимые действия (поведенческая активация). Не дави, не обесценивай состояние.

Правила:
1. Отвечай коротко, тёпло, разнообразно, всегда на русском.
2. Никакой нецензурной лексики, грубости.
3. Не повторяй негативные самооценки пользователя. Спроси о чувствах.
4. Не начинай каждый ответ одинаково.
5. Предлагай один очень маленький шаг, если пользователь готов.
6. Не ставь диагнозов, не рекомендуй лекарств.
7. При суицидальных мыслях — дай номер доверия 8-800-200-0-122.""",

    "самооценка": """Ты — психолог, помогающий с низкой самооценкой и неуверенностью. Используй технику КПТ «поиск доказательств»: проси пользователя найти факты, опровергающие его негативные мысли. Поддерживай, но без дежурных фраз.

Правила:
1. Отвечай спокойно, доброжелательно и всегда на русском, без ошибок.
2. Запрещена любая нецензурная лексика, оскорбления, грубость.
3. Категорически запрещено повторять оскорбительные самоописания пользователя. Лучше спроси: «Что заставило тебя так думать?»
4. Не сравнивай пользователя с другими.
5. Избегай пустых комплиментов. Задавай вопросы, помогающие заметить сильные стороны.
6. Не ставь диагнозов, не давай медицинских советов.
7. При суицидальных мыслях — дай номер доверия 8-800-200-0-122.""",

    "кризис": """Ты — кризисный психолог. Пользователю может быть очень плохо, возможно, есть суицидальные мысли. Твоя задача — поддержать, не анализировать причины и немедленно дать контакты специалистов.

Правила:
1. Отвечай мягко, грамотно и только по-русски. Без нецензурной лексики.
2. Не повторяй негативные самооценки пользователя.
3. Обязательно дай номер телефона доверия: 8-800-200-0-122.
4. Скажи, что его чувства важны, и сейчас лучшее — поговорить со специалистом.
5. Не задавай вопрос «почему?».
6. Если пользователь не в остром кризисе, можно перейти к мягкой поддерживающей беседе.
"""
}

user_topics = {}

def get_topic_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(label="😰 Тревога и стресс", color=VkKeyboardColor.PRIMARY, payload={"topic": "тревога"})
    keyboard.add_line()
    keyboard.add_button(label="💔 Отношения", color=VkKeyboardColor.PRIMARY, payload={"topic": "отношения"})
    keyboard.add_line()
    keyboard.add_button(label="😞 Настроение / апатия", color=VkKeyboardColor.PRIMARY, payload={"topic": "настроение"})
    keyboard.add_line()
    keyboard.add_button(label="🌟 Самооценка", color=VkKeyboardColor.PRIMARY, payload={"topic": "самооценка"})
    keyboard.add_line()
    keyboard.add_button(label="🆘 Кризисная ситуация", color=VkKeyboardColor.NEGATIVE, payload={"topic": "кризис"})
    return keyboard

BUTTON_TO_TOPIC = {
    "😰 Тревога и стресс": "тревога",
    "💔 Отношения": "отношения",
    "😞 Настроение / апатия": "настроение",
    "🌟 Самооценка": "самооценка",
    "🆘 Кризисная ситуация": "кризис",
}

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

def get_psychologist_response(user_text, topic):
    system_prompt = f"IMPORTANT: Answer strictly in Russian language. \n\n{PROMPTS_BY_TOPIC.get(topic, PROMPTS_BY_TOPIC["настроение"])}"
    response = ollama.chat(
        model='qwen2.5',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        options = {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.15
        }
    )
    return response['message']['content']


def send_final_cat(vk, vk_session, user_id):
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
            message="Я хотел отправить тебе пушистого котика, но ВК временно не принимает картинки. Держи виртуальный "
                    "кусь! 🐾 Ты молодец!",
            random_id=0,
            keyboard=get_topic_keyboard.get_keyboard()
        )
    if user_id in user_topics:
        del user_topics[user_id]

def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()
    print("Бот успешно соединился с сервером")
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text'].lower().strip()

            if text == 'начать' or text == 'привет':
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
                selected_topic = payload_data.get('topic')
                if selected_topic in PROMPTS_BY_TOPIC:
                    user_topics[user_id] = selected_topic
                    vk.messages.send(
                        user_id=user_id,
                        message=f"Отлично! Я буду помогать тебе. Расскажи, что тебя беспокоит?",
                        keyboard=get_chat_keyboard().get_keyboard(),
                        random_id=0
                    )
                    continue

                if payload_data.get('action') == 'end_session':
                    send_final_cat(vk, vk_session, user_id)
                    continue

            topic = user_topics.get(user_id, "настроение")

            try:
                bot_answer = get_psychologist_response(text, topic)

            except Exception as e:
                   bot_answer = "Извини, я немного задумался. Попробуй написать еще раз!"
                   print(f"Ошибка Ollama: {e}")

            vk.messages.send(
                user_id=user_id,
                message=bot_answer,
                keyboard=get_chat_keyboard().get_keyboard(),
                random_id=0
            )

if __name__ == "__main__":
    main()
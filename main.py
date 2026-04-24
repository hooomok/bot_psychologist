import vk_api
import os
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()
    print("Бот успешно соединился с сервером")
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']
            message_text = text.lower().strip()
            if message_text == 'начать':
                vk.messages.send(
                    user_id=user_id,
                    message='Привет! Я твой личный психолог, который всегда "в кармане" и очень любит котиков',
                    random_id=0
                )
            else:
                vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=0
                )

if __name__ == "__main__":
    main()
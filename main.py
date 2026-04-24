import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = "vk1.a.KwWuS-7hhjZpByIZDP-w9tG7GtImMdXty1woNNa0BNcYO1hxY0BeKm49as5F2GjXRHiBZzFiEhhWIIpUWTz0SmcBDm0JGx2RiHSXeVfg-bORkelU1hjhEFCYeyylncno2v3p8wabAJQmbArMGXIko2-1NyQN-no1U98ggNg1mqA10VsANkRA4sHdIc33E6PmzJ0L6uJAgjpPH2gggVSQcQ"
GROUP_ID = 236862872

def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()
    print("Бот успешно соединился с сервером")
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            text = event.obj.message['text']
            vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=0
            )

if __name__ == "__main__":
    main()
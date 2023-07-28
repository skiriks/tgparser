from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os
import csv
import time


def setup():

    api_id = input("enter api ID : ")
    api_hash = input("enter hash ID : ")
    phone = input("enter phone number : ")
    print("setup complete !")

    return phone, api_id, api_hash


def main():

    # вызов функции заполнения конфигурационного файла
    phone, api_id, api_hash = setup()

    # создание и проверка соединения клиента с ТГ, если нет - авторизация с помощью 2ФА
    client = TelegramClient(phone, int(api_id), api_hash)
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        os.system('clear')
        client.sign_in(phone, input('Enter the code: '))

    # инициализация переменных для работы с чатами и мегагруппами
    os.system('clear')
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    # задание значений для запроса чатов на сервера ТГ и сохранение их в chats
    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    # проверка на мегагруппу и если да - добавление в groups. отсеивание ненужного
    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except Exception as ex:
            continue

    # вывод списка груп для парсинга и их нумерация
    print('Choose a group to scrape members :')
    i = 0
    for g in groups:
        print('[' + str(i) + ']' + ' - ' + g.title)
        i += 1

    # ввод пользователем необходимой группы для парсинга
    print('')
    g_index = input("Enter a Number : ")
    target_group = groups[int(g_index)]

    # декоративный вывод и сбор всех участников целевой группы
    print('Fetching Members...')
    time.sleep(1)
    all_participants = client.get_participants(target_group, aggressive=True)

    # создание файла и запись в него всех данных
    print('Saving In file...')
    time.sleep(1)
    with open("members.csv", "w", encoding='UTF-8') as f:
        # создание обьекта writer для записи в csv файл и запись заголовков таблицы
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])

        # цикл проходки по всем участникам группы для записи их данныхт
        for user in all_participants:
            # одинаковые проверки на наличие юзернейма, первого имени, второго имени и их сохранение
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""

            # сохранение всех необходимых данных - спросить у Глеба какие именно данные ему нужны
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])

    print('Members scraped successfully.')


if __name__ == "__main__":
    main()

from urllib.error import HTTPError
import requests
from urllib3.exceptions import InsecureRequestWarning

# Отключаем предупреждение о небезопасном запросе
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def user_exists(tg_id: int) -> bool:
    base_url = "https://localhost:44332/api/v1/auth/exists"
    params = {"tgId": tg_id}

    try:
        # Выполняем GET запрос к API для проверки существования пользователя
        response = requests.get(base_url, params=params, verify=False)

        # Проверяем статус ответа
        response.raise_for_status()

        # Возвращаем True, если пользователь существует, иначе False
        return response.json()  # Предполагается, что API возвращает True/False

    except requests.HTTPError as http_err:
        print(f"HTTP ошибка: {http_err}")
        return False
    except Exception as err:
        print(f"Произошла ошибка: {err}")
        return False


def send_user_data(tg_id: int, username: str, avatar_url: str):
    url = "https://localhost:44332/api/v1/auth/user"

    # Параметры запроса
    params = {
        "tgId": tg_id,
        "tgUsername": username,
        "avatar": avatar_url
    }

    try:
        # Отправляем POST запрос
        if (user_exists(tg_id) == False):
            response = requests.post(url, params=params, verify=False)

            # Проверяем статус ответа
            if response.status_code == 200:
                print(f"Данные пользователя отправлены успешно: {response.json()}")
            else:
                print(f"Ошибка отправки данных: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

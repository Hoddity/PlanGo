import time

masterclasses = {
    1: {
        "title": "Искусственный интеллект для всех",
        "time": "15:00",
        "location": "Аудитория 101",
        "capacity": 2,
        "registered": [],
        "waiting_list": []
    },
    2: {
        "title": "Дизайн-мышление",
        "time": "16:00",
        "location": "Аудитория 202",
        "capacity": 1,
        "registered": [],
        "waiting_list": []
    },
}

def get_masterclass_list():
    """Формирует список доступных мастер-классов."""
    result = []
    for mc_id, mc in masterclasses.items():
        free_spots = mc["capacity"] - len(mc["registered"])
        result.append(f"{mc_id}. {mc['title']} ({mc['time']}, {mc['location']}) — Свободных мест: {free_spots}")
    return "\n".join(result)

def register_user(user_id, mc_id):
    """Регистрирует пользователя на мастер-класс или добавляет в лист ожидания."""
    mc = masterclasses.get(mc_id)
    if not mc:
        return "Такого мастер-класса не существует."

    if user_id in mc["registered"]:
        return "Вы уже зарегистрированы на этот мастер-класс."

    if len(mc["registered"]) < mc["capacity"]:
        mc["registered"].append(user_id)
        return "Вы успешно записались на мастер-класс!"
    else:
        if user_id not in mc["waiting_list"]:
            mc["waiting_list"].append(user_id)
            position = len(mc["waiting_list"])
            return f"Мест нет. Вы добавлены в лист ожидания. Ваш номер: {position}"
        else:
            return "Вы уже в листе ожидания."


pending_confirmations = {}  # user_id -> (mc_id, deadline)

def unregister_user(user_id, mc_id):
    mc = masterclasses.get(mc_id)
    if not mc:
        return "Мастер-класса с таким номером не существует."

    if user_id in mc["registered"]:
        mc["registered"].remove(user_id)

        # Переместим кого-то из ожидания
        if mc["waiting_list"]:
            next_user = mc["waiting_list"].pop(0)
            pending_confirmations[next_user] = (mc_id, time.time() + 900)  # 15 минут
            return (
                f"Вы отписались от мастер-класса.\n"
                f"Следующий участник из листа ожидания получает шанс записаться."
            )
        else:
            return "Вы успешно отписались от мастер-класса."
    elif user_id in mc["waiting_list"]:
        mc["waiting_list"].remove(user_id)
        return "Вы удалены из листа ожидания."
    else:
        return "Вы не были записаны на этот мастер-класс."

def confirm_user(user_id):
    data = pending_confirmations.get(user_id)
    if not data:
        return "Нет подтверждений, ожидающих от вас ответа."

    mc_id, deadline = data
    if time.time() > deadline:
        del pending_confirmations[user_id]
        return "Время подтверждения истекло."

    mc = masterclasses[mc_id]
    if len(mc["registered"]) < mc["capacity"]:
        mc["registered"].append(user_id)
        del pending_confirmations[user_id]
        return "Вы успешно подтвердили участие и записаны на мастер-класс!"
    else:
        return "Место уже занято другим участником."

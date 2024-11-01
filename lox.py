import cv2
import numpy as np
import pyautogui
import mss
import time
import tkinter as tk

# Загружаем изображение кнопки
button_image = cv2.imread('C:/Users/nikis/Desktop/auto_accept/accept_button.png')
button_height, button_width, _ = button_image.shape

# Проверка на успешную загрузку
if button_image is None:
    print("Ошибка: не удалось загрузить изображение 'accept_button.png'. Проверьте путь к файлу.")
    exit(1)

# Создаем объект для захвата экрана
sct = mss.mss()

# Переменная для отслеживания состояния
button_found = False

# Функция для обновления сообщений в текстовом поле
def update_message(message):
    message_box.config(state=tk.NORMAL)  # Разрешаем редактирование
    message_box.insert(tk.END, message + "\n")  # Добавляем сообщение
    message_box.config(state=tk.DISABLED)  # Запрещаем редактирование

# Создаем главное окно приложения
root = tk.Tk()
root.title("Автопринятие блядской кнопки")

root.geometry("300x200")

# Создаем текстовое поле для сообщений
message_box = tk.Text(root, state=tk.DISABLED)
message_box.pack(expand=True, fill=tk.BOTH)
update_message("Ищу ебанную кнопку")
# Основной цикл программы
def main_loop():
    global button_found
    # Захватываем часть экрана
    monitor = sct.monitors[1]  # Используйте нужный монитор, если у вас несколько
    screenshot = sct.grab(monitor)

    # Преобразуем захваченный экран в формат OpenCV
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)

    # Ищем кнопку на захваченном экране
    result = cv2.matchTemplate(screenshot_cv, button_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  # Порог для совпадения
    loc = np.where(result >= threshold)

    # Если кнопка найдена
    if loc[0].size > 0 and not button_found:
        update_message("Кнопка найдена! Нажимаем Enter.")
        pyautogui.press('enter')
        button_found = True  # Установим флаг, чтобы не нажимать Enter повторно

    # Если кнопка не найдена, сбрасываем флаг и продолжаем искать
    elif loc[0].size == 0:
        if button_found:
            update_message("Кнопка не найдена, продолжаем поиск...")
            button_found = False  # Сбрасываем флаг, чтобы можно было снова нажать Enter, если кнопка появится

    # Ждем немного перед следующей проверкой
    root.after(1000, main_loop)  # Запускаем функцию снова через 1000 мс (1 секунда)

# Запускаем главный цикл приложения
main_loop()
root.mainloop()
import asyncio
import os
import cv2
import numpy as np
import pyautogui
import mss
import time
import tkinter as tk
import subprocess

def build_executable():
    pyinstaller_path = r'C:\Users\nikis\Desktop\auto_accept\.venv\Scripts\pyinstaller.exe'
    icon_path = r'C:\Users\nikis\Desktop\auto_accept\zxc.ico'
    if not os.path.isfile(icon_path):
        print(f"Файл не найден: {icon_path}")
    else:
        print("Файл иконки найден.")
    
    if not os.path.isfile(pyinstaller_path):
        print(f"Файл не найден: {pyinstaller_path}")
        return
    
    subprocess.call([
        pyinstaller_path,
        '--onefile',
        '--noconsole',
        '--icon', icon_path,
        'lox.py'
    ])

def update_message(message):
    message_box.config(state=tk.NORMAL)  # Разрешаем редактирование
    message_box.insert(tk.END, message + "n")  # Добавляем сообщение
    message_box.config(state=tk.DISABLED)  # Запрещаем редактирование

async def main_loop(sct, button_image, target_image):
    global button_found
    
    while True:  # Основной цикл
        monitor = sct.monitors[1]  # Используйте нужный монитор, если у вас несколько
        screenshot = sct.grab(monitor)

        # Преобразуем захваченный экран в формат OpenCV
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)

        # Ищем кнопку на захваченном экране
        result = cv2.matchTemplate(screenshot_cv, button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8  # Порог для совпадения
        loc = np.where(result >= threshold)

        # Загружаем целевое изображение
        target_image_cv = cv2.imread(target_image)  # Загрузка целевого изображения
        if target_image_cv is None:
            print(f"Ошибка: не удалось загрузить изображение '{target_image}'. Проверьте путь к файлу.")
            return

        result_target = cv2.matchTemplate(screenshot_cv, target_image_cv, cv2.TM_CCOEFF_NORMED)
        threshold_target = 0.8  # Порог для совпадения целевой картинки
        loc_target = np.where(result_target >= threshold_target)

        # Если кнопка найдена
        if loc[0].size > 0 and not button_found:
            update_message("Кнопка найдена! Нажимаем Enter каждые 1 секунду...")
            button_found = True

            # Нажимаем Enter каждые 1 секунду, пока не появится целевая картинка
            while button_found and loc_target[0].size == 0:
                pyautogui.press('enter')  # Нажимаем Enter
                await asyncio.sleep(1)  # Ждем 1 секунду асинхронно

            if loc_target[0].size > 0:
                update_message("Целевая картинка найдена! Остановка нажатий.")
                button_found = False  # Сбрасываем состояние

        elif loc_target[0].size > 0:
            button_found = False

        await asyncio.sleep(1)  # Ждем немного перед следующей проверкой

async def run_app():
    global message_box, button_found
    
    button_found = False
    button_image_path = r'C:\Users\nikis\Desktop\auto_accept\accept_button.png'
    target_image_path = r'C:\Users\nikis\Desktop\auto_accept\target.png'

    if not os.path.isfile(button_image_path):
        print(f"Файл не найден: {button_image_path}")
        exit(1)

    button_image = cv2.imread(button_image_path)

    if button_image is None:
        print("Ошибка: не удалось загрузить изображение 'accept_button.png'. Проверьте путь к файлу.")
        exit(1)

    sct = mss.mss()
    
    root = tk.Tk()
    root.title("Auto Clicker")
    root.geometry("500x200")
    
    message_box = tk.Text(root, state=tk.DISABLED)
    message_box.pack(expand=True, fill=tk.BOTH)
    update_message("Поиск...")

    await main_loop(sct, button_image, target_image_path)

if __name__ == "__main__":  # Исправлено на правильное имя модуля
    build_executable()
    
    asyncio.run(run_app())
import asyncio
import threading
from aiogram import Bot, Dispatcher
import os
import cv2
import numpy as np
import pyautogui
import mss
import time
import tkinter as tk
import subprocess


bot = Bot(token='7697418130:AAFY4SalSyHyIhSKrh8ubeDaU4GlMHjhsas')  # Замените на ваш токен
dp = Dispatcher()  # Используйте именованный аргумент для storage

async def send_telegram_message(message):
    await bot.send_message(chat_id=1020323448, text=message)

def build_executable():
    pyinstaller_path = r'C:\Users\nikis\Desktop\auto_accept\.venv\Scripts\pyinstaller.exe'
    icon_path = r'C:\Users\nikis\Desktop\auto_accept\zxc.ico'

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
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + "\n")
    message_box.see(tk.END)
    message_box.config(state=tk.DISABLED)

async def main_loop():
    global button_found
    
    sct = mss.mss()
    button_found = False
    while True:
        screenshot = sct.grab(sct.monitors[1])
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(screenshot_cv, button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(result >= threshold)

        if loc[0].size > 0:
            if not button_found:
                update_message("Нажал")
                await send_telegram_message('Я нашлась')
                pyautogui.press('enter')
                button_found = True
        else:
            if button_found:
                update_message("Поиск")
                button_found = False

        await asyncio.sleep(0.5)  # Пауза в 500 мс

def start_async_loop():
    asyncio.run(main_loop())

if __name__ == "__main__":
    #build_executable()

    button_image_path = r'C:\Users\nikis\Desktop\auto_accept\accept_button.png'
    
    if not os.path.isfile(button_image_path):
        print(f"Файл не найден: {button_image_path}")
        exit(1)

    button_image = cv2.imread(button_image_path)

    if button_image is None:
        print("Ошибка: не удалось загрузить изображение 'accept_button.png'. Проверьте путь к файлу.")
        exit(1)

    button_height, button_width, _ = button_image.shape

    

    root = tk.Tk()
    root.title("auto_accept")
    root.geometry("300x300")
    #button_stop_start = tk.Button(root, text='Стоп', command =  width=100)


    message_box = tk.Text(root, state=tk.DISABLED)
    message_box.pack(expand=True, fill=tk.BOTH)
    update_message("Поиск")

    # Запускаем асинхронный цикл в отдельном потоке
    threading.Thread(target=start_async_loop, daemon=True).start()

    root.mainloop()  # Запуск GUI
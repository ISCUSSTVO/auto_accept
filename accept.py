import asyncio
import os
import threading
from aiogram import F, Bot, Dispatcher, types
import cv2
import numpy as np
import pyautogui
import mss
import tkinter as tk
import subprocess
#############################################          Бот         #############################################################
bot = Bot(token='7697418130:AAFY4SalSyHyIhSKrh8ubeDaU4GlMHjhsas') 
dp = Dispatcher()  

async def send_telegram_message(message):
    await bot.send_message(chat_id=1020323448, text =message)

@dp.message(F.text.lower().contains('г'))
async def msg(message: types.Message):
    start_game()
    await message.answer('ищу')

@dp.message(F.text.lower().contains('п'))
async def game(message: types.Message):
    start_stop()
    if running:
        await message.answer('плей')
    else: 
        await message.answer('пауза')
    


async def on_startup():
    print("Бот запущен")
###################################################     Функции программы       ################################################
loop = asyncio.new_event_loop() 

running = True

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
        'accept.py'
    ])

def update_message(message):
    message_box.config(state=tk.NORMAL,foreground='blue')
    message_box.insert(tk.END, message + "\n")
    message_box.see(tk.END)
    message_box.config(state=tk.DISABLED)

def start_stop():
    global running, button_found
    running = not running
    stop_button.config(text='Стоп' if running else 'Старт')
    
    if running:
        button_found = False
        update_message('иду')
        asyncio.run_coroutine_threadsafe(main_loop(), loop)
    else:
        update_message('стою')

def start_game():
    pyautogui.click(1700, 1030, 2 ,0.2)


async def run_bot():
    # Здесь должен быть код для инициализации и запуска бота

    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

###################################################     Скрипт       ################################################
async def main_loop():
    global button_found
    
    sct = mss.mss()
    while running:
        screenshot1 = sct.grab(sct.monitors[1])
        screenshot_np = np.array(screenshot1)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)

        result1 = cv2.matchTemplate(screenshot_cv, button_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(result1 >= threshold)

        if loc[0].size > 0:
            if not button_found:
                update_message("Нажал")
                await send_telegram_message('Я нашлась')
                pyautogui.press('enter',2)
                button_found = True
        else:
            if button_found:
                update_message("Поиск")
                button_found = False

        await asyncio.sleep(0.2)  # Пауза в 500 мс


###################################################     Запуск       ################################################
async def run_event_loop():
    asyncio.set_event_loop(loop)
    await run_bot()


def start_gui():
    global message_box
    global stop_button
    root = tk.Tk()
    root.title("auto_accept")
    root.geometry("300x300")


    stop_button = tk.Button(root, text='Стоп', command=start_stop, width=100, foreground='red', background='black')
    stop_button.pack()

    message_box = tk.Text(root, state=tk.DISABLED)
    message_box.pack(expand=True, fill=tk.BOTH)
    update_message("Поиск")
    
    root.mainloop()

if __name__ == "__main__":
    build_executable()
    button_found = False

    button_image_path = r'C:\Users\nikis\Desktop\auto_accept\accept_button.png'
    
    if not os.path.isfile(button_image_path):
        print(f"Файл не найден: {button_image_path}")
        exit(1)

    button_image = cv2.imread(button_image_path)

    if button_image is None:
        print("Ошибка: не удалось загрузить изображение 'accept_button.png'. Проверьте путь к файлу.")
        exit(1)
    button_height, button_width, _ = button_image.shape

    threading.Thread(target=lambda: loop.run_until_complete(run_event_loop()), daemon=True).start()
    
    # Запускаем поиск кнопки сразу при старте программы
    asyncio.run_coroutine_threadsafe(main_loop(), loop)

    start_gui()
    

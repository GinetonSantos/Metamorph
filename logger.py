# logger.py
import datetime

def log_action(message: str):
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line, end="")
    with open("trading_bot.log", "a", encoding="utf-8") as f:
        f.write(log_line)



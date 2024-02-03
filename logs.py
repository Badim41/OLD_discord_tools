from datetime import datetime


class Color:
    RESET = '\033[0m'
    RED = '\033[38;2;255;0;0m'  # Красный
    GREEN = '\033[38;2;0;255;0m'  # Зеленый
    BLUE = '\033[38;2;0;0;255m'  # Синий
    YELLOW = '\033[38;2;255;255;0m'  # Желтый
    PURPLE = '\033[38;2;2555;0;255m'  # Пурпурный
    CYAN = '\033[38;2;0;255;255m'  # Голубой
    GRAY = '\033[38;2;128;128;128m'  # Серый
    BLACK = '\033[38;2;0;0;0m'  # Черный

class Logs:
    def __init__(self, warnings=False, errors=True):
        self.warnings = warnings
        self.errors = errors

    def logging(self, *args, color=None):
        text = ' '.join(map(str, args))
        if not isinstance(color, str) and color is not None:
            raise ValueError("Not a valid color")

        with open("__logs__", "a", encoding="utf-8") as writer:
            writer.write(f"({datetime.now().strftime('%d.%m.%H.%M')}){text}\n")

        if "error" in text.lower() or "traceback" in text.lower() or "ошибка" in text.lower():
            if self.errors:
                colored_text = f"{Color.RED}{text}{Color.RESET}" if color is None else f"{color}{text}{Color.RESET}"
                print(colored_text)
        else:
            if self.warnings:
                colored_text = f"{Color.YELLOW}{text}{Color.RESET}" if color is None else f"{color}{text}{Color.RESET}"
                print(colored_text)
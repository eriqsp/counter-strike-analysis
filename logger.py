from datetime import datetime
import re


# class to deal with logging in general
class Logger:
    def __init__(self):
        pass

    @staticmethod
    def log(message: str, use_time: bool = True):
        if use_time:
            formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if re.search(r'^\n', message):
                new_message = re.sub(r'^\n', '', message)
                message = f"\n[{formatted_time}] {new_message}"
            else:
                message = f'[{formatted_time}] {message}'

        print(message)

# test commit

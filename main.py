from concurrent.futures import ThreadPoolExecutor
from Logger import logging

import requests
import time
import os
import random
import json
import string


emails = open('./Input/Mails.txt', 'r').read().splitlines()
config = json.load(open('./config.json', 'r'))

session = requests.Session()
session.headers = {"Authorization": f"Bearer {config["Main"]["Api-Key"]}"}

def generate_password() -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=8)) + ''.join(random.choices(string.ascii_uppercase, k=1)) + '!' + ''.join(random.choices(string.digits, k=4))


def format_line(line: str):
    parts = line.split(":") if ":" in line else line.split("|") if "|" in line else None
    
    if not parts or len(parts) <= 1 or len(parts) >= 4:
        raise logging.error("Incorrect email format.", line)
    
    return parts[0], parts[1]
    
    
class NotLetters():
    @staticmethod
    def change_password(email: str, cpass: str, npass: str):
        while True:
            try:
                payload = {
                    "email": email,
                    "new_password": npass,
                    "old_password": cpass
                }
                
                resp = session.post("https://api.notletters.com/v1/change-password", json=payload)
                
                if resp.status_code == 200:
                    logging.success("Succesfully changed password.", email, resp.status_code)
                    return True, 'Completed'
                
                elif resp.status_code == 400:
                    logging.error("Invalid request data.", email, resp.status_code)
                    return True, 'Unknown_error'

                elif resp.status_code == 403:
                    logging.error("Wrong ApiKey.", email, resp.status_code)
                    os._exit(1)
                
                elif resp.status_code == 404:
                    logging.error("Password does not match.", email, resp.status_code)
                    return True, 'Password_does_not_match'

                else:
                    logging.error(f"Unknown error {resp.text}", email, resp.status_code)
                    return True, 'Unknown_error'
                
            except Exception as e:
                print(e)
                time.sleep(1)
            
            
def thread(line: str):
    email, cpass = format_line(line)
    if config["Password"]["Generate_password"] == True:
        npass = generate_password()
    
    else:
        npass = config["Password"]["new_password"]
    
    result, file = NotLetters.change_password(email, cpass, npass)
    if result:
        if not os.path.exists(f'./Output/{file}.txt'):
            with open(f'./Output/{file}.txt', 'a') as file:
                file.write(f"{email}:{npass}\n")
                
        else:
            with open(f'./Output/{file}.txt', 'a') as file:
                file.write(f"{email}:{npass}\n")


with ThreadPoolExecutor(max_workers=config["Main"]["Threads"]) as executor:
    for email in emails:
        executor.submit(thread, email)

                    

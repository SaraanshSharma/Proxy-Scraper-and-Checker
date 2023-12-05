import aiohttp, asyncio
import concurrent.futures
import colorama
import os
import time
import pyfiglet
import requests
from re import compile
from colorama import Fore,Back,Style

urlToCheckAgainst = "https://netflix.com"
working_proxies = []

pt = os.path.dirname(__file__)
good = os.path.join(pt, "good.txt")

sessionForChecking = requests.Session()
sessionForChecking.headers.update({"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})

TIMEOUT: int = 30
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
REGEX = compile(
    r"(?:^|\D)?(("+ r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
    + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
    + r")(?:\D|$)"
)

scrapped_proxies = []
with open('proxies.txt', 'w') as proxies: proxies.write('')
proxies = open('proxies.txt', 'a')
errors = open('errors.txt', 'a')

    

async def scrap(url: str):
    temp_proxies = 0
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers={'user-agent': user_agent}, 
                timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as response:
                html = await response.text()
                if tuple(REGEX.finditer(html)):
                    for proxy in tuple(REGEX.finditer(html)):
                        proxies.write(f'{proxy.group(1)}\n')
                        scrapped_proxies.append(proxy.group(1))
                        temp_proxies += 1
                    print(Fore.GREEN + f' [~] Found: {temp_proxies} Proxies In {url}', proxy.group(1)+ Fore.RESET)
                else: print(Fore.RED +f' [~] Can\'t Find At: {url}', proxy.group(1)+Fore.RED)
    except Exception as e: 
        errors.write(f'{url}\n')

def check(proxy, idx, total):
    try:
        response = sessionForChecking.get(urlToCheckAgainst, proxies={"http": "http://" + str(proxy), "https": "http://" + str(proxy)}, timeout=5)
        if response.status_code == 200:
            print(Fore.GREEN + f"[+ {idx}/{total}] Proxy {proxy} is working!" + Fore.RESET)
            with open(good, "a") as f:
                f.write(proxy + "\n")
                
    except (requests.exceptions.ProxyError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout):
        print(Fore.RED + f"[- {idx}/{total}] Proxy {proxy} is NOT working!" + Fore.RESET)

async def main():
    print(Fore.BLUE+"--"*40+Fore.RESET)

    colorama.init(autoreset=True)
    ascii_art_text = pyfiglet.figlet_format("Proxy Scraper and Checker")
    big_blue_text = f"{Fore.BLUE}{Style.BRIGHT}{ascii_art_text}{Style.RESET_ALL}"
    print(big_blue_text)
    
    print()
    print(Fore.BLUE+"--"*40+Fore.RESET)
    print(Fore.CYAN+"""Tool By: Nice"""+Fore.RESET)
    while True:
        print(Fore.BLUE+"--"*40+Fore.RESET)
        print(Fore.BLUE+"""
        1. Scrape Proxies
        2. Check Proxies
        3. Scrape and Check Proxies
        4. Exit"""+Fore.RESET)
        print(Fore.BLUE+"--"*40+Fore.RESET)
        print()
        choice = int(input(Fore.CYAN+"Enter your choice: "+Fore.RESET))
        
        if choice==1:
            with open('sources.txt', 'r') as sources:
                urls = sources.read().splitlines()
                await asyncio.wait(
                    [ asyncio.create_task(scrap(url)) 
                    for url in urls ])
                
                print(f'\n [!] Done Scraping...\n [~] Total Proxies: {len(scrapped_proxies)}')
                proxies.close()
                errors.close()
                print(Fore.CYAN+"Done!"+Fore.RESET)
        
        elif choice == 2:
            with open('proxies.txt','r') as proxylist:
                proxy_lines = proxylist.read().splitlines()
                print(f"Total number of proxies found: {len(proxy_lines)}")
                with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
                    for idx, proxy in enumerate(proxy_lines, start=1):
                        executor.submit(check, proxy, idx, len(proxy_lines))
            print(Fore.CYAN+"Done!"+Fore.RESET)

        elif choice == 3 :
            with open('sources.txt', 'r') as sources:
                urls = sources.read().splitlines()
                await asyncio.wait(
                    [ asyncio.create_task(scrap(url)) 
                    for url in urls ])
                
                print(f'\n [!] Done Scraping...\n [~] Total Proxies: {len(scrapped_proxies)}')
                proxies.close()
                errors.close()
            with open('proxies.txt','r') as proxylist:
                proxy_lines = proxylist.read().splitlines()
                print(f"Total number of proxies found: {len(proxy_lines)}")
                with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
                    for idx, proxy in enumerate(proxy_lines, start=1):
                        executor.submit(check, proxy, idx, len(proxy_lines))
            print(Fore.CYAN+"Done!"+Fore.RESET)

        elif choice == 4:
            print(Fore.CYAN+"Good Bye"+Fore.RESET)
            break
            

if __name__ == "__main__":
    asyncio.run(main())

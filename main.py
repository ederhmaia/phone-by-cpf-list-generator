# typing
from typing import List, Tuple, Union
from requests.models import Response

# utils
import requests
import pandas as pd
import xlsxwriter
import multiprocessing
import json

# sugar
from colorama import Fore, init
from tqdm import tqdm
import os

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def get_phone_number(cpf: str) -> Union[bool, str]:
    response: Response = requests.get(f'apiurlexample.com/cpf={cpf}')
    response_json = response.json()
    if response_json['status'] != 'success':
        return False
    ddd: str = response_json['result']['ddd'].strip()
    phone: str = response_json['result']['telefone'].strip()
    return f"{ddd} {phone}"

def get_cpf_list(filename: str) -> List[str]:
    cpf_list: List[str] = []
    with open(filename, 'r') as f:
        for line in f:
            cpf_list.append(line.strip())
    return cpf_list

def fetch_phone_numbers(cpf_list: List[str]) -> List[Tuple[str, Union[bool, str]]]:
    with multiprocessing.Pool() as pool:
        results = pool.map(get_phone_number, cpf_list)
    return [(cpf, result) for cpf, result in zip(cpf_list, results)]

def export_to_xlsx(stdin_list: List[str], output_filename: str) -> None:
    data: List[Tuple[str, str]] = []
    max_cpf_length = 0
    max_phone_length = 0

    print(f'{Fore.MAGENTA}[@] Extracting phone numbers...')
    for cpf in tqdm(stdin_list):
        phone_number = get_phone_number(cpf)
        if phone_number:
            data.append((cpf, phone_number))
            max_cpf_length = max(max_cpf_length, len(cpf))
            max_phone_length = max(max_phone_length, len(phone_number))
        else:
            data.append((cpf, 'Não Encontrado'))
            max_cpf_length = max(max_cpf_length, len(cpf))
            max_phone_length = max(max_phone_length, len('Não Encontrado'))

    dataframe = pd.DataFrame(data, columns=["CPF", "TELEFONE"])
    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
    dataframe.to_excel(writer, index=False)
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:A', max_cpf_length + 1)
    worksheet.set_column('B:B', max_phone_length + 1)
    writer.close()

def main() -> None:
    print()

    while True:
        print(f'{Fore.MAGENTA}[@] Text Input Filename?')
        filename: str = input(f'{Fore.YELLOW}-> {Fore.WHITE}')
        if not filename.endswith('.txt'):
            filename += '.txt'
        try:
            filesize: int = len(open(filename, 'r').readlines())
            print(f'{Fore.GREEN}File {Fore.WHITE}{filename}{Fore.GREEN} found with {Fore.WHITE}{filesize}{Fore.GREEN} lines')
            print()
            break
        except FileNotFoundError:
            print(f'{Fore.RED}File {Fore.WHITE}{filename} {Fore.RED}not found')
            print()
            continue

    while True:
        print(f'{Fore.MAGENTA}[@] XLSX Output Filename?')
        output: str = input(f'{Fore.YELLOW}-> {Fore.WHITE}')
        if not output.endswith('.xlsx'):
            output += '.xlsx'
        try:
            open(output, 'r').close()
            print(f'{Fore.RED}File {Fore.WHITE}{output}{Fore.RED} already exists, try another name.')
            print()
            continue
        except FileNotFoundError:
            print()
            break

    cpf_list: List[str] = get_cpf_list(filename)
    export_to_xlsx(stdin_list=cpf_list, output_filename=output)

if __name__ == '__main__':
    try:
        print(f'''
    {Fore.CYAN}                  _,-'|
    {Fore.CYAN}           ,-'._  |
    {Fore.CYAN} .||,      |####\ |
    {Fore.CYAN}\.`',/     \####| |
    {Fore.CYAN}= ,. =      |###| |              {Fore.MAGENTA}         phone extractor by cpf
    {Fore.CYAN}/ || \    ,-'\#/,'`.   {Fore.MAGENTA}   the responsability of the use of this tool is yours
    {Fore.CYAN}  ||     ,'   `,,. `.                    
    {Fore.CYAN}  ,|____,' , ,;' \| |                {Fore.MAGENTA}          dev by @edermxf
    {Fore.CYAN} (3|\    _/|/'   _| |        
    {Fore.CYAN}  ||/,-''  | >-'' _,\\           {Fore.YELLOW}           [what is this?]
    {Fore.CYAN}  ||'      ==\ ,-'  ,'           {Fore.YELLOW}this tool will extract phone numbers from a list of cpf's
    {Fore.CYAN}  ||       |  V \ ,|             {Fore.YELLOW}       and save them in a excel file
    {Fore.CYAN}  ||       |    |` |     
    {Fore.CYAN}  ||       |    |   \            {Fore.GREEN}               [examples]
    {Fore.CYAN}  ||       |    \    \           {Fore.GREEN}   input filename => combolist_23.txt
    {Fore.CYAN}  ||       |     |    \          {Fore.GREEN}output filename => combolist_23.xlsx
    {Fore.CYAN}  ||       |      \_,-'
    {Fore.CYAN}  ||       |___,,--")_\\
    {Fore.CYAN}  ||         |_|   ccc/
    {Fore.CYAN}  ||        ccc/''')

        main()
        clear()
        print(f'{Fore.GREEN}[@]{Fore.YELLOW} Done!')
        print(f'{Fore.GREEN}[@]{Fore.WHITE} ederm crushed it...')
    except KeyboardInterrupt:
        clear()
        print(f'{Fore.RED}[!]{Fore.YELLOW} Goodbye...')
        print(f'{Fore.RED}[!]{Fore.WHITE} ederm crushed it...')
        exit()
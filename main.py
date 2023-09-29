from tqdm import tqdm
import os
import ctypes
import requests
from bs4 import BeautifulSoup
from time import sleep


def is_admin():
        return ctypes.windll.shell32.IsUserAnAdmin() == 1


def make_dir():
    list_dirs = ["./rootCertificate/", "./intermediateCertificate", "./certificateRevocationList"]
    for dir in list_dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def install_cert():
    user_input = input("Установить сертификаты Федерального казначейства (Y/N)")
    if user_input.lower() in ["yes", "y", "да", "д"]:
        for rc_name in os.listdir(r"./rootCertificate"):
            os.system(f"certutil -addstore -f ROOT ./rootCertificate/{rc_name}")
        for ic_name in os.listdir(r"./intermediateCertificate"):
            os.system(f"certutil -addstore -f CA ./intermediateCertificate/{ic_name}")
        for crl_name in os.listdir(r"./certificateRevocationList"):
            os.system(f"certutil -addstore -f ROOT ./certificateRevocationList/{crl_name}")
            os.system(f"certutil -addstore -f CA ./certificateRevocationList/{crl_name}")
    if user_input.lower() in ["no", "n", "нет", "Н"]:
        pass


def get_links():
    print("Формируем ссылки на сертификаты")
    url = "http://crl.roskazna.ru/crl/"
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.content, "html.parser")
    links = []
    for raw in soup.find_all("a"):
        if "http://reestr-pki.ru/cdp/" in raw.get("href"):
            links.append(raw.get("href"))
            print(raw.get("href"))
        elif "/crl/test" in (url + raw.get("href")):
            pass
        else:
            links.append(url + raw.get("href"))
            print(url + raw.get("href"))
    print("Ссылки сформированы")
    sleep(0.5)
    return links


def download_links(link, path):
    response = requests.get(link, stream=True)
    print('Скачиваем', link)
    progress_bar = tqdm(total=int(response.headers.get('content-length', 0)), unit_scale=1, bar_format="{l_bar}{bar:100}| {n_fmt}/{total_fmt}")
    with open(f"./{path}/{link.replace(' ', '_').split('/')[-1]}", "wb") as f:
        for data in response.iter_content(1024):
            progress_bar.update(len(data))
            f.write(data)
        progress_bar.close()


def sort_links(links):
    for link in links:
        try:
            if "Корневой" in link:
                download_links(link, "rootCertificate")
            elif "Подчиненный" in link:
                download_links(link, "intermediateCertificate")
            elif "ucfk" and not ".crl" in link:
                download_links(link, "intermediateCertificate")
            elif "ucfk" and ".crl" in link:
                download_links(link, "certificateRevocationList")
        except TypeError:
            pass


def copy_utils():
    user_input = input("Скопировать certutil.exe в директорию C:\Windows\System32(Y/N)")
    if user_input.lower() in ["yes", "y", "да", "д"]:
        for file in os.listdir(".\\utils"):
            os.system(f"copy .\\utils\\{file} C:\\Windows\\System32")
        if user_input.lower() in ["no", "n", "нет", "Н"]:
            pass


if __name__ == "__main__":
    if is_admin():
        make_dir()
        user_input = input("Скачать сертификаты Федерального казначейства(Y/N)")
        if user_input.lower() in ["yes", "y", "да", "д"]:
            sort_links(get_links())
            copy_utils()
            install_cert()
        if user_input.lower() in ["no", "n", "нет", "н"]:
            copy_utils()
            install_cert()
    else:
        print("Необходимо запустить скрипт от имени администратора.")
        pass


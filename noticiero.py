#!/usr/bin/python
import praw
import pdb
import re
import os
import sched, time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from lista import portales

reddit = praw.Reddit('bot1')

# leer el log
if not os.path.isfile("replied_posts.txt"):
    replied_posts = []

else:
    with open("replied_posts.txt", "r") as f:
        replied_posts = f.read()
        replied_posts = replied_posts.split("\n")
        replied_posts = list(filter(None, replied_posts))

# abrir firefox
#options = Options()
#options.add_argument("--headless")
driver = webdriver.Firefox(executable_path='/opt/geckodriver') # , firefox_options=options

def submit_post(title, url):
    subreddit.submit(title, url=url, flair_id='dce65c36-3804-11e9-82f4-0e66455f6230') #template dac20d40-d87b-11e7-ac1d-0e7ea519f542 (r/uruguay)

def motorei(selector, regex):
    try: # tomar el link
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        element.is_displayed()

    except TimeoutException:
        print("Fallo")

    finally: # enviar el link y procesar
        if element != "":
            links = driver.find_elements_by_xpath(regex)[:5]
            for link in links:
                url = link.get_attribute("href")
                title = link.text
                print(title)
                submit_post(title, url)
        return
    return

###############################################

def busqueda_tipo1():
    selector = "footer"
    regex = "//h2/a[@href]"
    motorei(selector, regex)
    return


def busqueda_tipo2():
    selector = "footer"
    regex = "//h3/a[@href]"
    motorei(selector, regex)
    return

# ver que busqueda de enlaces hacer en la pagina
def revisar_categoria(pagina):
    tipo1 = ["https://www.montevideo.com.uy", "https://www.elobservador.com.uy", "https://republica.com.uy", "subrayado.com.uy",] #h2
    tipo2 = ["https://www.elpais.com.uy", "https://ladiaria.com.uy", "https://www.180.com.uy",] #h3
    tipo3 = ["https://ecos.la", ] # ??
    tipo4 = ["https://www.lr21.com.uy",] # ??

    regex = re.compile(r'(https?://)(.*?)(?:\.com\.uy|\.la)', re.IGNORECASE)
    dominio = regex.search(pagina)[0]
    print(dominio)
    if dominio in tipo1:
        busqueda_tipo1()
        return 
    return


try: # cada minuto...
    while True:
        # revisar posts nuevos
        subreddit = reddit.subreddit('etesuntest') # etesuntest
        hora = datetime.datetime.now().time()

        for pagina in portales: #(limit=5)
            print(hora, "- Revisando...", pagina)
            driver.get(pagina)

            revisar_categoria(pagina)

            # if enlace not in replied_posts:
            #     print(hora, "→ Sip, a trabajar...")
            #     regexp = re.compile(r'elobservador\.com\.uy')
            #     if regexp.search(enlace):
            #         driver.get(pagina)

                    

            #     else: # fallo
            #         print("MAL")


            # escribir el id del post
            #replied_posts.append(submission.id)

            # guardar los id nuevos
            with open("replied_posts.txt", "w") as f:
                for post_id in replied_posts:
                    f.write(post_id + "\n")

        print(hora, "→ Listo. Esperando...")
        time.sleep(60)

except KeyboardInterrupt:
    print(hora, 'Detenido manualmente...')

# cerrar firefox
driver.quit()

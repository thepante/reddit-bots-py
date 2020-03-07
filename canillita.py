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
from lista import *

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
session_id = driver.session_id
executor_url = driver.command_executor._url

print (session_id)
print (executor_url)

# si el contenido es normal, todo ok
def resp_normal(sdomain, enlace, outline):
    print("└─────[ok]·[N]─────•")
    # extraer los parrafos
    paragraphs = driver.find_elements_by_css_selector("p")
    # driver.implicitly_wait(10)
    listadopfs = ""
    for p in paragraphs:
        listadopfs += "> "+str(p.text)+"\n>\n"

    # juntar los parrafos
    contenido = ''.join(map(str, listadopfs))

    # armar la respuesta
    respuesta = "|☴ **Podés leerlo en** [**"+outline+"**]("+enlace+")|\n|:-|\n||\n"+contenido
    submission.reply(respuesta)
    return

# si el contenido es de pago only
def resp_depago(sdomain):
    print("Articulo MEMBER")
    respuesta = "| ! ☴ **El artículo enlazado es de acceso pago.**|\n|:-|\n\nNo se puede leer sin estar registrado, ya que el articulo se llega a cargar solo si el lector esta logueado con una cuenta con suscripción (esto ya es distinto, no hay manera de saltear). Por favor compartí la noticia desde otro enlace, de otra página (?\n&#x200B;"
    submission.reply(respuesta)
    return

# si el contenido es con login / pago demo
def resp_debusqueda():
    print("Articulo PAGO de Busqueda")
    respuesta = "| ! ☴ **El artículo enlazado es de acceso pago / limitado.**|\n|:-|\n\nNo se puede leer sin estar registrado, ya que el articulo se llega a cargar solo si el lector esta logueado con una cuenta con suscripción (esto ya es distinto, no hay manera de saltear). Sin embargo, Búsqueda tiene una cantidad de 5 notas de pago para ver gratis si inicias sesión.\n\nPor favor compartí la noticia desde otro enlace, de otra página (?\n&#x200B;"
    submission.reply(respuesta)
    return

# ver cual aplicar
def revisar_categoria(sdomain, enlace, outline, url):
    indeep = ["elpais.com.uy", "elobservador.com.uy"]

    # si es busqueda hay que revisar mejor
    if sdomain == "busqueda.com.uy":
            try: # revisar si es contenido pago
                driver.find_element(By.XPATH,"//raw/h2")
                try:
                    p = driver.find_element(By.XPATH,"//raw/p")
                except:
                    resp_debusqueda()
                    return
            # si no aplicó lo anterior, entonces debe ser gratis
            except:
                resp_normal(sdomain, enlace, outline)
            else:
                resp_normal(sdomain, enlace, outline)
            return

    # chequear si está en la lista indeep para revisar mejor
    if sdomain in indeep:
        print("Puede TCDP")
        revisado = driver.find_element(By.XPATH,"//raw/p")
        if revisado.text in tienecdp: # está y es articulo de pago
            resp_depago(sdomain)
        
        else: # es articulo normal pero el portal tcdp
            resp_normal(sdomain, enlace, outline)

    else: # articulo es portal libre acceso
        resp_normal(sdomain, enlace, outline)
    return


try: # cada minuto...
    while True:
        # revisar posts nuevos
        subreddit = reddit.subreddit('etesuntest') # etesuntest
        hora = datetime.datetime.now().time()
        for submission in subreddit.new(limit=5):
            print(hora, "- [✓]")
            if submission.id not in replied_posts:

                # proceso para los posts que aplique
                if submission.domain in portales:
                    print(hora, "↓ [!] ...")
                    url = 'https://outline.com/'+submission.url
                    driver.get(url)
                    try: # tomar el link
                        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "copy-target")))
                        element.is_displayed()
                    except TimeoutException:
                        print("Fallo")

                    finally: # enviar el link y procesar
                        if element != "":
                            enlace = element.text
                            outline = re.sub(r"(https?\:\/\/)", "", enlace)
                            revisar_categoria(submission.domain, enlace, outline, url)
                            #print(submission.domain, enlace, outline)

                        else: # fallo
                            print("MAL")

                    # mostrar por cual va respondiendo
                    if len(submission.title) <= 43:
                        tituloFinal = submission.title
                    else:
                        tituloFinal = "%s..."%(submission.title[0:40])
                    print(hora, "→ [✓]", "["+submission.id+"]", tituloFinal, "["+outline+"]")
                    #print("-----------------------------")

                    # escribir el id del post
                    replied_posts.append(submission.id)

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

# guardar los id nuevos
#with open("replied_posts.txt", "w") as f:
#    for post_id in replied_posts:
#        f.write(post_id + "\n")


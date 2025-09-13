import requests
from bs4 import BeautifulSoup
import pandas as pd
import time 
import random
import sqlite3
import datetime

#Camuflagem(Hearders browers agent)
 
headers = {
    'User-Agent':'Mozzila/5.0(Windows NT 10.0;Win64) AppleWebKit/537.36(KHTML,like Gecko) Chrome/114.0 Safari/537.36'
}
baseURL = 'https://www.adorocinema.com/filmes/melhores/'
filmes = []
data_hoje = datetime.date.today().strftime("%d-%m-%y")
agora = datetime.datetime.now()
paginalimite = 5
card_temp_min =  5
card_temp_max =  1
pag_temp_min = 2
pag_temp_max = 4
bancoDados = 'C:/Users/sabado/Desktop/LanSchool Files/Curso Python Modulo2 -Aluno/Aula01/banco_filmes.db'
saidaCSV = f'filmes_do_cinema_{data_hoje}.csv'

#Eu quero que você me traga a 1 +1 até a página limite 
#E captura toda  a URL (resposta)
for pagina in range(1,paginalimite + 1):
    url = f"{baseURL}?page={pagina}" #estou direcionando para qual página ele vai ir de acordo 1+
    print(f"Coletando dados da pagina{pagina}\nEndereço{url}\n") #informa que esta coletando
    resposta = requests.get(url,headers=headers)
    
#o 200 é nº que o html informa que a página esta OK,diferente do 404
    if resposta.status_code != 200:
        print(f"Erro ao carregar a pagina {pagina}.\nCodigo do erro é:{resposta.status_code}")
        continue
#vai buscar agora os cartões que possuem o  descritivo do site ou seja uma Card entity     
    soup = BeautifulSoup(resposta.text,"html.parser") #quero apenas o TEXTO e me passa o HTML todo(parser)
    cards = soup.find_all("div",class_="card entity-card entity-card-list cf")
    for card in cards:
        try:
            #capturar o titulo e o link do filme
            titulo_tag = card.find("a",class_="meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "https://www.adorocinema.com"+titulo_tag['href'] #busca o href que esta o link do filme
            #capturar a nota do filme
            nota_tag = card.find("span",class_="stareaval_note")
            nota = nota_tag.text.strip().replace(",",".") if nota_tag else "N/A"
            #subtstitui a virgula por ponto e só faz a captura se der certo se não pega N/A

            if link:
                filme_resposta = requests.get(link, headers=headers)
                filme_soup = BeautifulSoup(filme_resposta.text,"html.parser")

            #captura o diretor do filme
            diretor_tag = filme_soup.find("div",class_="meta-body-item meta-body-direction meta-body-oneline")

            if diretor_tag:
                     diretor = (diretor_tag.text
                     .strip()
                     .replace("Direção:", "")
                     .replace(",", "")
                     .replace("|", "")
                     .replace("\n"," ")
                     .replace("\r"," ")
                     .strip()
                     ) if diretor_tag else "N/A"

            #capturar os gêneros
            genero_blocks =  filme_soup.find("div", class_="meta_body_info")
            if genero_blocks:
                genero_links = genero_blocks.find_all("a")
                #trás a Tag a com os gêneros e limpa
                generos = [g.text.strip() for g in genero_links ]
                categoria = ",".join(generos[:3])if generos else "N/A"
            else:
                categoria = "N/A"
            #Capturar o ano de lançamento do filme
            ano_tag = genero_blocks.find("span",class_="date") if genero_blocks else None
            ano = ano_tag.text.strip() if ano_tag else "N/A"
            if titulo !="N/A" and link !="N/A" and nota !="N/A":
                filmes.append({
                    "Titulo":   titulo,
                    "Direção": diretor,
                    "Nota": nota,
                    "Link": link,
                    "Ano":  ano,
                    "Categoria":categoria
                })
            else:
                print(f"Filme Incompleto ou erro na coleta de dados do filme{titulo}")
            tempo = random.uniform(card_temp_min,card_temp_max)
            time.sleep(tempo)

        except Exception as erro:
            print(f"Erro ao processar o filme {titulo}\n Erro:{erro}")

    #esperar um tempo entre uma pagina e outra
    tempo = random.uniform(pag_temp_min,pag_temp_max)
    print(f"Tempo de Espera entre filmes: {tempo:.1f}")
    print(f"Filme carregado:{titulo}")
    time.sleep(tempo)

df = pd.DataFrame(filmes)
print(df.head())
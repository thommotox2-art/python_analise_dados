import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sqlite3
import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

baseURL = 'https://www.adorocinema.com/filmes/melhores/'
filmes = []
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
agora = datetime.datetime.now()
paginaLimite = 1
card_temp_min = 1 
card_temp_max = 2
pag_temp_min = 1
pag_temp_max = 2
pasta = 'C:/Users/sabado/Desktop/LanSchool Files/Curso Python Modulo2 -Aluno/Aula01'
bancoDados = 'banco_filmes.db'
saidaCSV = f'filmes_adoro_cinema_{data_hoje}.csv'

for pagina in range(1, paginaLimite + 1):
    url = f"{baseURL}?page={pagina}"
    print(f"Coletando dados da pagina: {pagina}\nEndereço: {url}\n")
    resposta = requests.get(url, headers=headers)

    if resposta.status_code != 200:
        print(f"Erro ao carregar a pagina {pagina}. \nCodigo do erro é: {resposta.status_code}")
        continue

    soup = BeautifulSoup(resposta.text, "html.parser")
    cards = soup.find_all("div", class_="card entity-card entity-card-list cf")
    for card in cards:
        try:
            titulo = "N/A"  # garante disponibilidade no except
            #capturar o titulo e o link da pagina do filme
            titulo_tag = card.find("a", class_="meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "https://www.adorocinema.com" + titulo_tag['href'] if titulo_tag else None
            
            #capturar a nota do filme
            nota_tag = card.find("span", class_="stareval-note")
            nota = nota_tag.text.strip().replace(",",".") if nota_tag else "N/A"

            diretor = "N/A"
            categoria = "N/A"
            ano = "N/A"

            if link:
                filme_resposta = requests.get(link, headers=headers)
                if filme_resposta.status_code != 200:
                    print(f"Falha ao abrir página do filme: {link} (HTTP {filme_resposta.status_code})")
                    continue

                filme_soup = BeautifulSoup(filme_resposta.text, "html.parser")

                #captura o diretor do filme
                diretor_tag = filme_soup.find("div", class_="meta-body-item meta-body-direction meta-body-oneline")
                if diretor_tag:
                    diretor = (
                        diretor_tag.text
                        .strip()
                        .replace("Direção:","")
                        .replace(",","")
                        .replace("|","")
                        .replace("\n"," ")
                        .replace("\r","")
                        .strip()
                    )

                #capturar os generos e ano (somente se bloco existir)
                genero_blocks = filme_soup.find("div", class_="meta-body-info")
                if genero_blocks:
                    genero_links = genero_blocks.find_all("a")
                    generos = [g.text.strip() for g in genero_links]
                    categoria = ", ".join(generos[:3]) if generos else "N/A"

                    ano_tag = genero_blocks.find("span", class_="date")
                    ano = ano_tag.text.strip() if ano_tag else "N/A"
            
                if titulo != "N/A" and link is not None and nota != "N/A":
                    filmes.append({
                        "Titulo":   titulo,
                        "Direção":  diretor,
                        "Nota":     nota,
                        "Link":     link,
                        "Ano":      ano,
                        "Categoria": categoria
                    })
            else:
                print(f"Filme Incompleto ou erro na coleta de dados do filme {titulo}")
            #esperar um tempo entre um filme e outro (card)
            tempo = random.uniform(card_temp_min,card_temp_max)
            print(f"Tempo de Espera entre filmes: {tempo:.1f}")
            print(f"Filme carregado: {titulo}")
            time.sleep(tempo)
        except Exception as erro:
            print(f"Erro ao processar o filme {titulo}\n Erro: {erro}")
    #esperar um tempo entre uma pagina e outra
    tempo = random.uniform(pag_temp_min,pag_temp_max)
    print(f"Tempo de Espera entre pagina: {tempo:.1f}")
    time.sleep(tempo)

df = pd.DataFrame(filmes)
print(df.head())

#VAMOS SALVAR em CSV
df.to_csv(f'{pasta}{saidaCSV}',index=False,encoding='utf-8-sig',quotechar="'", quoting=1)

with sqlite3.connect(f'{pasta}{bancoDados}') as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filmes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT,
            Direcao TEXT,
            Nota REAL,
            Link TEXT UNIQUE,
            Ano TEXT,
            Categoria TEXT       
            )
    ''')
    for filme in filmes:
        try:
            cursor.execute ('''
                INSERT OR IGNORE INTO filmes (Titulo,Direcao,Nota,Link,Ano,Categoria) VALUES (?,?,?,?,?,?)                            
            ''',(filme['Titulo'],
                 filme['Direcao'],
                 float(filme['Nota'])if filme['Nota'] !='N/A' else None,
                 filme['Link'],
                 filme['Ano'],
                 filme['Categoria']
            ))
        except Exception as e:
            print (f"Erro ao inserir o filme{filme['Titulo']} no banco de dados\n Erro {e}")
        conn.commit()
    termino = datetime.datetime.now()

    print("-----------------------------------------")
    print("Dados Raspados com sucesso")
    print(f"\nArquivo CSV salvo em: {pasta}{saidaCSV}")
    print(f"\n Dados armazenados no banco de dados{bancoDados}")
    print(f"\n Tarefa iniciada em: {agora.strftime('%H:%M:%S')}")
    print(f"\n Tarefa terminada em: {termino.strftime('%H:%M:%S')}")
    print(f"\n Obrigado por Usar o BotFilmes")
    print("-----------------------------------------------------")        



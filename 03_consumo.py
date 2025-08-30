from flask import Flask, request,render_template_string #CLASSE:FLASK #Função:request e render
import pandas as pd
import sqlite3 #elemento que entra ou cria o banco de dados
import plotly.express as px #gera gráficos
import plotly.io as pio #gerencia 
import random
import os #biblioteca para operar o sistema operacional 

#Carregar o arquivo drinks

#Modo1 de fazer
#modo inicialdfdrinks = pd.read_csv(r"C:\Users\sabado\Desktop\LanSchool Files\Curso Python Modulo2 -Aluno\Aula01\drinks.csv")

#modo2 de fazer
#tabela01 = "drinks.csv"
#tabela02 = "avengers.csv"
#dfDrinks = pd.read_csv(f"{caminho}{tabela01}")
#dfAvengers = pd.read_csv(f"{caminho}{tabela02}")
#modo3defazer

pio.renderers.default = "browser"

caminho = "C:/Users/sabado/Desktop/LanSchool Files/Curso Python Modulo2 -Aluno/Aula01/" 
tabela = ["drinks.csv","avengers.csv"]

codHtml = '''
    <h1> Dashboards - Consumo de Alcool <h1>
        <h2>Parte 01 </h2>
            <ul>
            <li><a href="/grafico1"> Top 10 paises em consumo de alcool </a></li>
            <li><a href="/grafico2"> Media de consumo por tipo </a></li>
            <li><a href="/grafico3"> Consumo total por região </a></li>
            <li><a href="/grafico4"> Comparativo entre tipos e bebidas </a></li>
            <li><a href="#"> Insights por pais </a></li>
            </ul>
    <h2>Parte 2 </h2>
        <ul>
            <li><a href="/comparar"> Comparar </a></li>
            <li><a href="/upload"> Upload CSV Vingadores </a></li>
            <li><a href="/apagar"> Apagar Tabela </a></li>
            <li><a href="/ver"> Ver Tabela </a></li>
            <li><a href="/vaa"> V.A.A (Vingadores Alcolicos Anonimos) </a></li>
            </ul>
'''

def carregarCsv():
    try:
        dfDrinks = pd.read_csv(os.path.join(caminho,tabela[0]))
        dfAvengers =pd.read_csv(os.path.join(caminho,tabela[1]) ,encoding='latin1')
        return dfDrinks,dfAvengers
    except Exception as erro:
        print (f"Erro ao carregar os arquivos CSV:{erro}")
        return None, None #Nones de acordo com o número de elementos 

def criarBancoDados():   #criando o banco de dados
    conn = sqlite3.connect(f"{caminho}banco01.bd") #criando uma conexão e criando o banco de dados
    dfDrinks,dfAvengers = carregarCsv() #puxa as duas tabelas
    if dfDrinks is None or dfAvengers is None:
        print("Falha ao carregar os dados")
        return
    #inserir as tabelas no bancos de dados
    dfDrinks.to_sql("bebidas",conn, if_exists="replace",index=False) # busco o caminho conn, se a tabela existir ela será reposta , sem o Index

    dfAvengers.to_sql("vingadores",conn, if_exists="replace", index=False)
    conn.commit()#estou me comprometendo ao inserir este banco
    conn.close() #fecha o banco pois já fizemos a carga dele


    #o mundo fica aqui!!criando um "servidor e definimos as rotas"

app = Flask(__name__)

@app.route('/') # criando a primeira rota com o decorator
def index():
    return render_template_string(codHtml)

@app.route('/grafico1')
def grafico1(): #funcaografico1
    with sqlite3.connect(f'{caminho}banco01.bd') as conn:
        df  = pd.read_sql_query("""
              SELECT country, total_litres_of_pure_alcohol
              FROM bebidas
              ORDER BY total_litres_of_pure_alcohol DESC
              LIMIT 10                                            
         """,conn)
    figuraGrafico01 = px.bar(
        df,
        x="country",
        y ="total_litres_of_pure_alcohol",
        title = "Top 10 paises com maior consumo de alcool"
    )
    return figuraGrafico01.to_html()


@app.route('/grafico2')
def grafico2():
    with sqlite3.connect(f'{caminho}banco01.bd') as conn:
        df = pd.read_sql_query("""
            SELECT AVG (beer_servings) AS cerveja, AVG(spirit_servings) AS destilados, AVG (wine_servings) AS vinhos FROM bebidas
        """,conn)
    df_melted = df.melt(var_name='Bebidas',value_name='Média de Porções')
    
    figuraGrafico02 = px.bar(
        df_melted,
        x = "Bebidas",
        y ="Média de Porções",
        title = "Media de consumo global por tipo"
    )
    return figuraGrafico02.to_html()

if __name__ == '__main__':
    criarBancoDados()
    app.run(debug=True)


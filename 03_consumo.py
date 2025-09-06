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

@app.route("/grafico3")
def grafico3():
    regioes = {
        "Europa":['France','Germany','Spain','Italy','Portugal'],
        "Asia":['China','Japan','India','Thailand'],
        "Africa":['Angola','Nigeria','Egypt','Algeria'],
        "Americas":['USA','Brazil','Argentina','Mexico']
    }
    dados = []
    with sqlite3.connect(f'{caminho}banco01.bd') as conn:
        #itera sobre o dicionario, de regioes onde cada chave(região tem uma lista de paises)
        for regiao, paises in regioes.items():
            placeholders = ",".join([f"'{pais}'"for pais in paises])
            query = f"""
                SELECT SUM(total_litres_of_pure_alcohol) AS total
                FROM bebidas
                Where country IN ({placeholders})
            """
            total = pd.read_sql_query(query, conn).iloc[0,0]
            dados.append({
                "Região":regiao,
                "Consumo Total": total 
            })
        dfRegioes = pd.DataFrame(dados)
        figuraGrafico3 = px.pie(
            dfRegioes,
            names = "Região",
            values ="Consumo Total",
            title = "Consumo Total por Região"
        )
        return figuraGrafico3.to_html()
    
@app.route('/comparar',methods=['POST','GET'])
def comparar():
    opcoes = [
        'beer_servings',
        'spirit_servings',
        'wine_servings'
    ]
    # EU SOU UM CONE DE VAGA

    if request.method == "POST":
        eixoX = request.form.get('eixo_x')#beer
        eixoY = request.form.get('eixo_y')#wine
        if eixoX == eixoY:
            return "<marquee> Você fez besteira..escolha tabelas diferentes .... </marquee>"
        conn = sqlite3.connect(f'{caminho}banco01.bd')
        df = pd.read_sql_query("SELECT country, {},{} FROM bebidas".format(eixoX,eixoY), conn)
        conn.close()
        figuraComparar = px.scatter(
            df,
            x = eixoX,
            y = eixoY,
            title= f"Comparação entre {eixoX} VS {eixoY} "
        )
        figuraComparar.update_traces(
            textposition = "top center"
        )
        return figuraComparar.to_html()
        
    return render_template_string('''
        <h2>Comparar campos </h2>
        <form method="POST">
            <label for ="eixo_x"></label> Eixo x:</label>
            <select name= "eixo_x">
                {% for opcao in opcoes %}
                    <option value="{{opcao}}">{{opcao}}</option>
                {% endfor %}

            </select>
            <br></br>

            <label for="eixo_y"></label> Eixo Y:</label>
            <select name="eixo_y">
                {% for opcao in opcoes %}
                    <option value="{{opcao}}">{{opcao}}</option>
                {% endfor %}
                                  
            </select>
            <br></br>

            <input type="submit" value="-- Comparar --">

        </form>
''', opcoes = opcoes)

@app.route('/ver',methods=['POST','GET'])
def ver_tabela():
    opcoes = [
        'bebidas',
        'vingadores',
    ]
    tabela_html = ""
#informando o caminho
    if request.method == "POST":
        eixoX = request.form.get('eixo_x')
        with sqlite3.connect(f'{caminho}banco01.bd') as conn:
            df = pd.read_sql_query(f"SELECT * FROM {eixoX}",conn)
            tabela_html = df.to_html(index=False,classes='table table-bordered')
    #Fazendo um formulário de busca
    return render_template_string('''
        <h2>Busque tabela </h2>
        <form method="POST">
            <label for ="eixo_x"></label> Escolha Tabela:</label>
            <select name= "eixo_x">
                {% for opcao in opcoes %}
                    <option value="{{opcao}}">{{opcao}}</option>
                {% endfor %}
            </select>
            <br></br>
            <input type = "submit" value="Ver Tabela">
        </form>
        <hr>
        {{tabela_html|safe}}                          
''', opcoes=opcoes, tabela_html=tabela_html)

@app.route('/upload',methods = ['GET','POST'])
def upload():

    if request.method == "POST":
        recebido = request.files['c_arquivo']
        if not recebido:
            return "Nenhum arquivo foi recebido"
        dfAvengers = pd.read_csv(recebido,encoding='latin1')
        #fazendo a conexão ao banco01
        conn = sqlite3.connect(f'{caminho}banco01.bd')
        #inserido a tabela no banco de dados
        dfAvengers.to_sql("vingadores",conn,if_exists="replace",index=False)
        #Salva "me comprometendo que eu estou mandando para o banco"
        conn.commit()
        conn.close()
        return"Sucesso! Tabela vingadores no banco de dados"

#criação do formulario
    return'''
        <h2>Upload da tabela Avengers</h2>
        <form method="POST" enctype='multipart/form-data'>
            <input type ='file' name='c_arquivo' accept='.csv'>
            <input type = 'submit' value='Carregar'>
        </form>
 '''
                                 
if __name__ == '__main__':
    criarBancoDados()
    app.run(debug=True)



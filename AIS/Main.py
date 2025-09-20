# +===========================================================+
# |888    d8P  8888888 .d88888b.   d888   .d8888b.   .d8888b. |
# |888   d8P     888  d88P" "Y88b d8888  d88P  Y88b d88P  Y88b|
# |888  d8P      888  888     888   888  888    888 888    888|
# |888d88K       888  888     888   888  Y88b. d888 Y88b. d888|
# |8888888b      888  888     888   888   "Y888P888  "Y888P888|
# |888  Y88b     888  888     888   888         888        888|
# |888   Y88b    888  Y88b. .d88P   888  Y88b  d88P Y88b  d88P|
# |888    Y88b 8888888 "Y88888P"  8888888 "Y8888P"   "Y8888P" |
# +===========================================================+

#Autor: Thomas 
#Data: 20-09-25 
#Version: 1.0.0

from flask import Flask,request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import numpy as np
import Config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

app = Flask(__name__) #objeto vai receber a classe FLASK( estrutura que vai criar) 
pasta = Config.FOLDER
caminhoBd = Config.DB_PATH
rotas = Config.Rotas

vazio = 0

def init_db(): #função criada para inciar o banco de dados
    with sqlite3.connect(f'{pasta}{caminhoBd}') as conn: # Determino o caminho e o arquivo 
        cursor = conn.cursor() # estou pedindo para executar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia(
                       mes TEXT PRIMARY KEY,
                       inadimplencia REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selic(
                       mes TEXT PRIMARY KEY,
                       selic_diaria REAL
            )
        ''')
        conn.commit()

@app.route(rotas[0], methods=['GET','POST'])
def index():
    return render_template_string(f'''
        <h1> Upload dados Economicos</h1>
        <form action ="{rotas[1]} " method="POST" enctype="multipart/form-data">
                                 
            <label for="campo_selic"> Arquivo de Inadimplencia (CSV):</label>
            <input name="campo_inadimplencia" type="file" required>
                                 
            
            <label for="campo_inadimplencia"> Arquivo de Taxa Selic (CSV):</label>
            <input name="campo_selic" type="file" required>
                                 
            <input type= "submit" value="Fazer Upload">
        <form>
        <br><br>
        <a href="{rotas[2]}"> Consultar dados Armazenados <a/><br>
        <a href="{rotas[3]}"> Visualizar Graficos </a><br>
        <a href="{rotas[4]}"> Editar Inadimplencia </a><br>
        <a href="{rotas[5]}"> Visualizar Graficos </a><br>
                                 
    ''')

@app.route(rotas[1], methods=['POST','GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos arquivos devem ser enviados"}),406
    inad_df = pd.read_csv(
        inad_file,
        sep = ';',
        names = ['data','inadimplencia'],
        header = 0
    )
    selic_df = pd.read_csv(
        selic_file,
        sep = ';',
        names = ['data','selic_diaria'],
        header = 0
    )
    inad_df['data']=pd.to_datetime(
        inad_df['data'],
        format='%d/%m/%Y'
    )
    selic_df['data']=pd.to_datetime(
        selic_df['data'],
        format='%d/%m/%Y'
    )

    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str) 
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_df = inad_df.drop_duplicates(subset=['mes', 'inadimplencia'])
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    #guardar no banco

    with sqlite3.connect(f'{pasta}{caminhoBd}') as conn:

        inad_df.to_sql(
            'inadimplencia',
            conn,
            if_exists = 'replace',
            index = False
        )
        selic_df.to_sql(
            'selic',
            conn,
            if_exists = 'replace',
            index = False
        )
    return jsonify({"Mensagem":"Dados cadastrados com sucesso"}),200

@app.route(rotas[2],methods = ['POST','GET'])
def consultar ():
    if request.method == "POST":
        tabela = request.form.get("campo_tabela")
        if tabela not in ['inadimplencia','selic']:
            return jsonify({"Erro":"Tabela é invalida"}),400
        with sqlite3.connect(f'{pasta}{caminhoBd}') as conn:
            df= pd.read_sql_query(f'SELECT*FROM {tabela}',conn)
        return df.to_html(index=False)

    return render_template_string (f'''
        <h1> Consulta de Tabelas</h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </label>
            <select name = "campo_tabela">
                <option value="inadimplencia"> Inadimplência </option>
                <option value="selic"> Taxa Selic </option>
                <option value="usuarios"> Usuarios </option>
            </select>
            <input type="submit" value="Consultar">
        </form>
        <br>
        <a href="{rotas[0]}">Voltar</a>
''')

@app.route(rotas[4],methods =['POST','GET'])
def editar_inandimplencia():

    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({"Erro:":"Valor invalido"}),418
        with sqlite3.connect(f'{pasta}{caminhoBd}') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inadimplencia
                SET inadimplencia = ?
                WHERE mes = ?
                        ''',(novo_valor,mes))
            conn.commit()
        return jsonify({"Mensagem:":f"Valor atualizado para o mes {mes}"})

    return render_template_string (f'''
        <h1> Editar Inadimplencia </h1>
        <form method="POST">
            <label for="campo mes"> Mês (AAAA-MM) </label>
            <input type="text" name="campo_mes"><br>
                                   
            <label for="campo_valor"> Novo valor </label>
            <input type="text" name="campo_valor"><br>

            <input type="submit" value="Salvar">
        </form>
        <br>
        <a href="{rotas[0]}">Voltar</a>
''')

@app.route(rotas[5])
def correlacao():
        with sqlite3.connect(f'{pasta}{caminhoBd}') as conn:
            inad_df = pd.read_sql_query("SELECT * FROM inadimplencia",conn)
            selic_df = pd.read_sql_query("SELECT * FROM selic",conn)

        #realiza uma junção entre os dois dataframes usando a coluna mes como chave
        merged = pd.merge(inad_df,selic_df, on = 'mes')
        #calcula o coeficiente da correlação de pearson entre as duas variáveis
        correl = merged['inadimplencia'].corr(merged['selic_diaria'])

        #registra as variaveis para regressão linear onde X é a variável independente e o y é a dependente

        x = merged['selic_diaria']
        y = merged['inadimplencia']

        #Calcula o coeficiente da reta de regressão linear one M é a inclinação e  é a intersecção
        m, b = np.polyfit(x,y, 1)

        #Oba gráficos
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = x,
            y = y, 
            mode = 'markers',
            name = 'Inadimplencia X Selic',
            marker = dict(
                color = 'rgba(0, 123, 255, 0.8)',
                size = 12,
                line = dict(width = 2, color = 'white'),
                symbol = 'circle'
            ),
            hovertemplate= 'Selic: %{x:.2f}% <br> Inadimplencia %{y:.2f}%<extra></extra>' 
        ))
        fig.add_trace(go.Scatter(
            x = x,
            y = m * x+b,
            mode = 'lines',
            line = dict(
                color = 'rgba(255,53,69,1)',
                width = 4,
                dash = 'dot'
            )

        ))
        fig.update_layout(
            title = {
                'text':f'<b> Correlação entre Selic e Inadimplencia</b><br><span>Coeficiente de Correlação: {correl:.2f}</span>',
                'y':0.95,
                'x':0.5,
                'xanchor':'center',
                'yanchor':'top'
            },
            xaxis_title = dict(
                text = 'SELIC Media Mensal (%)',
                font = dict(
                    size=18,
                    family ='Arial',
                    color = 'gray'
                    )
            ),
            yaxis_title = dict(
                text = 'SELIC Inadimplencia (%)',
                font = dict(
                    size=18,
                    family ='Arial',
                    color = 'gray'
                    )
            ),
            xaxis = dict(
                tickfont = dict(
                    size = 14,
                    family = 'Arial',
                    color = 'black'
                ),
                gridcolor = 'lightgray'
            ),
            yaxis = dict(
                tickfont = dict(
                    size = 14,
                    family = 'Arial',
                    color = 'black'
                ),
                gridcolor = 'lightgray'
            ),
            font = dict(
                    size = 14,
                    family = 'Arial',
                    color = 'black'
            ),
            legend = dict(
                orientation = 'botom',
                xanchor = 'center',
                x = 0.5,
                y = 1.05,
                bgcolor = 'rgba(0,0,0,0)',
                borderwidth = 0 
            ),
            margin = dict( l=60, r=60, t=120, b=60),
            plot_bgcolor = "#faf8fa",
            paper_bgcolor = 'white'
        )
        graph_html = fig.to_html(
            full_html = False,
            include_plotlyjs = 'cdn'
        )
        return render_template_string('''
            <html>
                <head>
                    <title>Correlação Selic X Inadimplencia</title>
                </head>
                <body>
                    <h1> Correlação Selic X inadimplencia</h1>
                    <div>{{grafico|safe}}</div>
                    <br>
                    <a href="{{voltar}}">Voltar </a>
                </body>
            </html>            
''',grafico = graph_html,voltar = rotas[0])

if __name__ == '__main__':
    init_db()
    app.run(
        debug = Config.FLASK_DEBUG,
        host = Config.FLASK_HOST,
        port = Config.FLASK_PORT
    )







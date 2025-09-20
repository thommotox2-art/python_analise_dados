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
        <form action =" " method="POST" enctype="multipart/form-data">
                                 
            <label for="campo_selic"> Arquivo de Inadimplencia (CSV):</label>
            <input name="campo_inadimplencia" type="file" required>
                                 
            
            <label for="campo_inadimplencia"> Arquivo de Taxa Selic (CSV):</label>
            <input name="campo_selic" type="file" required>
                                 
            <input type= "submit" value="Fazer Upload">
        <form>
        <br><br>
        <a href="{rotas[2]}"> Consultar dados Armazenados <a/><br>
        <a href="{rotas[3]}"> Visualizar Graficos <a/><br>
        <a href="{rotas[4]}"> Visualizar Graficos <a/><br>
        <a href="{rotas[5]}"> Visualizar Graficos <a/><br>
                                 
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

app.route(rotas[4],methods =['POST','GET'])
def editar_inandimplencia():

    #############################

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
                                   
            <label for="campo valor"> Novo valor </label>
            <input.type="text" name="campo_valor"><br>

            <input type="submit" value="Salvar">
        </form>
        <br>
        <a href="{rotas[0]}">Voltar</a>
''')


if __name__ == '__main__':
    init_db()
    app.run(
        debug = Config.FLASK_DEBUG,
        host = Config.FLASK_HOST,
        port = Config.FLASK_PORT
    )







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
#

#Configuracoes comuns do sistema
FOLDER = 'C:/Users/sabado/Desktop/Curso Python Modulo2 -Aluno/Aula01/AIS/'
DB_PATH = "bancoDeDadosAIS.db"
FLASK_DEBUG = True
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000

#Rotaas comuns do sistema

Rotas = [
    '/',            #rota 00
    '/upload',      #rota01
    '/consultar',   #rota02
    '/graficos',    #rota03
    '/editar_inadimplencia',    #rota04
    '/correlacao'   #rota05
]
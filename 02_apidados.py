#Criando uma API com o site do IBGE
#http.dog site de imagens ou http.cat ou http.fisch

import json,requests

name = input("Escreva o nome a ser buscado")
resposta = requests.get(f'https://servicodados.ibge.gov.br/api/v2/censos/nomes/{name}')
jsonDados = json.loads(resposta.text)

print(jsonDados[0]['res'][0]) # busco apenas o primeiro ano(0), se eu não colocar nenhum número ele virá todos

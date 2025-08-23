
#Importação de bibliotecas
import pandas as pd 
#carregar dados da planilha
caminho = 'C:/Users/sabado/Desktop/LanSchool Files/Curso Python Modulo2 -Aluno/Aula01/01_base_vendas.xlsx' 

df1 = pd.read_excel(caminho,sheet_name='Relatório de Vendas') #transforma o arquivo em arquivo pandas
df2 = pd.read_excel(caminho,sheet_name='Relatório de Vendas1') #transforma o arquivo em arquivo pandas

#exibir as primeiras linhas das tabelas

print('------primeiro relatório ---------')
print(df1.head()) #O head vai trazer o 5 primeiros

print('------segundo relatório ---------')
print(df2.head())

#Verificar se há duplicatas

print('Duplicatas no relatório 01')
print(df1.duplicated().sum()) #Indentifica os duplicados e soma quantos

print('Duplicatas no relatorio 02')
print(df2.duplicated().sum())

#Vamos consolidar as duas tabelas
print('Dados consolidados')
dfConsolidado = pd.concat([df1,df2],ignore_index=True) # concatena as duas tabelas ignorando o index gerado pelo pyhton ('primeira coluna')
print(dfConsolidado.head())

#exibir o numeor de clientes por cidade

clientesPorCidade = dfConsolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=True) #organiza por ciadade e calcula quantos são únicos pela coluna cliente sendo organizados do maior para o menor (ascending=True)

print('Clientes por cidade') #escreve clientes por cidade
print(clientesPorCidade) #Exibe a venda por cidade

#exibir o numero de venda por plano

vendasPorPlano = dfConsolidado['Plano Vendido'].value_counts()
print('Numero de vendas por Plano')
print(vendasPorPlano)

#exibir as 3 cidades com mais clientes:
top3Cidades = clientesPorCidade.head(3) #exibe os 3 resultados da lista que já estão programados anteriormente

#Top3Cidades = clientespor cidade.sort_values(ascendig=False).head(3)

print('Top3 Cidades')
print(top3Cidades)

#adicionar uma nova coluna de status (Exemplo ficticio de analise)

#Vamos classificar os planos como 'premium' se for enterprise, os demais serão 'padrão'

dfConsolidado['Status'] = dfConsolidado['Plano Vendido'].apply(lambda x:'Premium'if x == 'Enterprise' else 'Padrão')

#exibir a distribuição dos status
statusDist = dfConsolidado['Status'].value_counts()
print('Distribuição dos status')
print(statusDist)

#Salvar a tabela em um arquivo novo
#Primeiro em EXCEL

dfConsolidado.to_excel('dados_consolidados.xlsx',index=False) #salva em excel com o nome dados consolidades sem a coluna de index

#Salvar a tabela em csv
dfConsolidado.to_csv('dados_consolidados.csv',index=False)
print('Dados salvos em CSV')

#Mensagem final

print('----Programa Finalizado----')
 
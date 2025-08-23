import excdesafio as xx

usuarioNasc = int(input('\n Digite seu ano de nascimento: '))
usuarioatual = int(input('\n Informe o ano atual: '))

idade =xx.calcularIdade(usuarioNasc,usuarioatual)
print(f'Você tem {idade} anos')
                   


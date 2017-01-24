# ihc2layout
Repositório criado para disponibilizar a implementação do meu Trabalho de Conclusão de Curso em Ciência da Computação (BCC) pela Universidade Federal do Paraná (UFPR).


Arquivos:

data.json - Dados da segunda fase de experimentação.
data-origin.json - Dados da primeira fase de experimentação.
data-inicial.json - Dados criados apartir de data.json utilizando a classificação do tempo médio. Utilizado para iníciar o classificador.
data-onlineLearning.json - Utilizados com os feedbacks para aprimorar o classificador.

mainWs.py - Inicializa a aplicação do webservice.
classificador.py - Arquivo que apresenta todas as definições sobre o classificador.
ws.py - Arquivo que contém todo o webservice desenvolvido em flask.

exemplo/teste.html - Página que apresenta um layout com os elementos classificados em tipo A e tipo B.
exemplo/ub.js - Arquivo javascript responsavel pela coleta das informações e envio ao WebService.

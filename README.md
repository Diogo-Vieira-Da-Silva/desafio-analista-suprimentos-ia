📦 Aplicação de Suprimentos - Gestão de RCs e Cadastro de Itens

Esta é uma aplicação local em Python com interface gráfica desenvolvida para a área de Suprimentos. A ferramenta permite o gerenciamento e redirecionamento de Requisições de Compras (RCs) por exceção, além da correção cadastral do Grupo Comprador de itens, garantindo a prevalência e a integridade das regras de negócio.

🛠️ Tecnologias Utilizadas

Python 3.10+

Streamlit: Interface gráfica interativa e navegável no navegador.

Pandas: Processamento, cruzamento e manipulação de dados estruturados.

OpenPyXL: Leitura e escrita direta em planilhas Excel (.xlsx).

PyInstaller: Empacotamento para executável local (.exe).

📋 Regras de Negócio Implementadas

Redirecionamento de RC por Exceção:

Permite informar uma RC ou uma lista de RCs e atribuir um novo Grupo Comprador.

Preserva o cadastro original do item na aba BASE_CADASTRO_ITENS.

Salva e persiste os redirecionamentos em uma aba exclusiva chamada EXCECOES_RCs.

Correção do Cadastro do Item:

Permite atualizar o Grupo Comprador de um item específico na aba BASE_CADASTRO_ITENS.

Propaga em cascata a atualização para todas as RCs associadas a esse item na aba BASE_RCs.

Regra de Prevalência: RCs que possuírem registro de exceção não são alteradas, mantendo o grupo comprador delegado pela exceção.

Validações e Tratamento de Erros:

Mensagens claras de sucesso, aviso e erro.

Tratamento para RCs não encontradas ou itens inexistentes.

Validação de formato de entrada (valores numéricos e campos obrigatórios).

🚀 Como Executar o Projeto Localmente

Pré-requisitos

Certifique-se de que o arquivo de dados base_cadastro_e_requisies_1.xlsx está na mesma pasta do arquivo app.py.

Passo a Passo

Instale as dependências executando no terminal:

pip install streamlit pandas openpyxl


Execute a aplicação com o comando:

python -m streamlit run app.py


A interface será aberta automaticamente em seu navegador padrão no endereço:
http://localhost:8501

📦 Como Gerar o Executável (.exe) via PyInstaller

Para empacotar a aplicação em um arquivo executável standalone:

Instale o PyInstaller:

pip install pyinstaller


Execute o comando de compilação:

pyinstaller --onefile --add-data "base_cadastro_e_requisies_1.xlsx;." app.py


O executável gerado estará disponível dentro da pasta dist/.

🧪 Roteiro de Testes Realizados

Teste de Redirecionamento por Exceção:

RC: 10057937

Novo Grupo Comprador: 150

Resultado: A RC foi atualizada em BASE_RCs para o grupo 150 e registrada na aba EXCECOES_RCs.

Teste da Regra de Prevalência:

Código Item: 7529896

Novo Grupo Comprador do Item: 120

Resultado: O item teve seu cadastro atualizado para 120 em BASE_CADASTRO_ITENS. A linha da RC 10057937 em BASE_RCs permaneceu inalterada no grupo 150 devido à regra de exceção cadastrada.
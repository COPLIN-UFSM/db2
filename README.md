# db2

Um módulo de conveniência para acessar bancos de dados do tipo IBM DB2.

## Instalação

Para instalar o pacote pelo pip, digite o seguinte comando:

```bash
pip install git+git://github.com/COPLIN-UFSM/db2.git#db2
```

Alternativamente, você pode clonar o repositório em sua máquina com o git e instalar a partir da pasta do repositório:

```bash
git clone https://github.com/COPLIN-UFSM/db2.git
cd db2
conda install -c "conda-forge/label/cf202003" ibm_db==3.* --yes
pip install -e .
```


## Uso

Arquivo `credentials.json`:

```json
{
  "user": "nome_de_usuário",
  "password": "sua_senha_aqui",
  "host": "URL_do_host",
  "port": 50000,
  "database": "nome_do_banco"
}
```

Arquivo `main.py`:

```python
import os
from db2 import DB2Connection

# arquivo JSON com credenciais de login para o banco de dados
credentials = 'credentials.json'

with DB2Connection(credentials) as db2_conn:

    db2_conn.create_tables(os.path.join('data', 'db2_schema.sql'))
    row_generator = db2_conn.query(
        """
        SELECT * 
        FROM some_table;
        """
    )
    for row in row_generator:
        print(row)
```

## Desenvolvimento

Este passo-a-passo refere-se às instruções para **desenvolvimento** do pacote. Se você deseja apenas usá-lo, siga para
a seção [Instalação](#instalação).

```bash
conda create --name db2 python==3.6.* pip setuptools --yes
conda install -c "conda-forge/label/cf202003" ibm_db==3.* --yes
consta install --file requirements.txt --yes
```

## Contato

Módulo desenvolvido originalmente por Henry Cagnini: [henry.cagnini@ufsm.br]()

## Bibliografia

* [Documentaçao oficial ibm_db (em inglês)](https://www.ibm.com/docs/en/db2/11.5?topic=db-connecting-database-server)
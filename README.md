# COPLIN db2

Um módulo de conveniência para acessar bancos de dados do tipo IBM DB2, desenvolvido pela Coordenadoria de Planejamento
Informacional da UFSM (COPLIN).

Permite definir um arquivo com as credenciais de acesso ao banco de dados, que podem ser utilizadas depois:

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

Arquivo `db2_schema.sql`:

```sql
CREATE TABLE SOME_TABLE(
    ID INTEGER NOT NULL PRIMARY KEY,
    NAME VARCHAR(10) NOT NULL,
    AGE INTEGER NOT NULL
);

INSERT INTO SOME_TABLE(NAME, AGE) VALUES (1, 'HENRY', 32);
INSERT INTO SOME_TABLE(NAME, AGE) VALUES (2, 'JOHN', 20);

```

Arquivo `main.py`:

```python
import os
from db2 import DB2Connection

# arquivo JSON com credenciais de login para o banco de dados
credentials = 'credentials.json'

with DB2Connection(credentials) as db2_conn:
    db2_conn.create_tables('db2_schema.sql')
    query_str = '''
        SELECT * 
        FROM SOME_TABLE;
     ''' 
    row_generator = db2_conn.query(query_str, as_dict=True)
    
    for row in row_generator:
        print(row)
```

## Instalação

Para instalar o pacote pelo pip, digite o seguinte comando:

```bash
pip install coplin-db2
```

Caso tenha problemas em instalar pelo pip, instale pelo GitHub:

```bash
pip install "git+https://github.com/COPLIN-UFSM/db2.git"
```

<details>
<summary><h2>Desenvolvimento</h2></summary>

Este passo-a-passo refere-se às instruções para **desenvolvimento** do pacote. Se você deseja apenas usá-lo, siga para
a seção [Instalação](#instalação).

1. Instale as bibliotecas necessárias:

   ```bash
   conda create --name db2 python==3.11.* pip --yes
   pip install coplin-db2
   conda install --file requirements.txt --yes
   ```

2. Construa o pacote:

   ```bash
   python -m build 
   ```

3. Para publicá-lo no PyPi, use o twine:

   ```bash
   twine upload dist/*
   ```

   **NOTA:** Será preciso definir um arquivo `.pypirc` no seu diretório HOME:

   ```text
   [distutils]
   index-servers =
      pypi
      pypitest
         
   [pypi]
      repository =  https://upload.pypi.org/legacy/
      username = __token__
      password = <token gerado no link https://pypi.org/manage/account/token/>
         
   [pypitest]
      repository = https://test.pypi.org/legacy/
      username = __token__
      password = <token gerado no link https://pypi.org/manage/account/token/>
   ```

</details>

## Contato

Módulo desenvolvido originalmente por Henry Cagnini: [henry.cagnini@ufsm.br]()

## Bibliografia

* [Documentaçao oficial ibm_db (em inglês)](https://www.ibm.com/docs/en/db2/11.5?topic=db-connecting-database-server)

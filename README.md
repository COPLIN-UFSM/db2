# coplin-db2

A biblioteca coplin-db2 é um módulo de conveniência para acessar bancos de dados do tipo IBM DB2, desenvolvido pela 
Coordenadoria de Planejamento Informacional da UFSM (COPLIN).

Com esta biblioteca, é possível definir um arquivo com credenciais de acesso ao banco de dados, no formato `json`, que 
podem ser utilizadas posteriormente:

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
CREATE TABLE USERS_TEST_IBMDB2(
    ID INTEGER NOT NULL PRIMARY KEY,
    NAME VARCHAR(10) NOT NULL,
    AGE INTEGER NOT NULL
);

INSERT INTO USERS_TEST_IBMDB2(ID, NAME, AGE) VALUES (1, 'HENRY', 32);
INSERT INTO USERS_TEST_IBMDB2(ID, NAME, AGE) VALUES (2, 'JOHN', 20);

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
        FROM USERS_TEST_IBMDB2;
     ''' 
    df = db2_conn.query_to_dataframe(query_str)
    
    print(df)
    
    # deleta a tabela
    # db2_conn.modify('''DROP TABLE USERS_TEST_IBMDB2;''', suppress=False)
```

A saída esperada deve ser:

```bash
   ID   NAME  AGE
0   1  HENRY   32
1   2   JOHN   20
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

1. Instale o [Python Anaconda](https://www.anaconda.com/download) na sua máquina
2. Crie o ambiente virtual do Anaconda, e instale as bibliotecas necessárias:

   ```bash
   conda env create -f environment.yml
   ```
   
   Alternativamente, você pode instalá-las usando o pip:
  
   ```bash
   conda create --name db2 python==3.11.* pip --yes
   pip install coplin-db2
   conda install --file requirements.txt --yes
   ```

3. Construa o pacote:

   ```bash
   python -m build 
   ```

4. Para publicá-lo no PyPi, use o twine:

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

5. Para publicar usando o GitHub Actions, siga 
   [este tutorial](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

   Em resumo, uma vez configurado o arquivo `python-publish.yml`, todo commit será enviado para pypi-test, mas apenas 
   os commits com tag serão enviados para o pypi.

   É possível ver como adicionar uma tag à um commit na
   [documentação oficial do git](https://git-scm.com/book/en/v2/Git-Basics-Tagging). 

</details>

## Contato

Biblioteca desenvolvida originalmente por Henry Cagnini: [henry.cagnini@ufsm.br]()

Caso encontre algum problema no uso, abra um issue no [repositório da biblioteca](https://github.com/COPLIN-UFSM/db2).

Melhorias no código-fonte são bem-vindas!
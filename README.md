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

<details>
<summary><h2>Desenvolvimento</h2></summary>

Este passo-a-passo refere-se às instruções para **desenvolvimento** do pacote. Se você deseja apenas usá-lo, siga para
a seção [Instalação](#instalação).

1. Instale o [Python Anaconda](https://www.anaconda.com/download) na sua máquina
2. Crie o ambiente virtual do anaconda e instale as bibliotecas necessárias com o comando

   ```bash
   conda env create -f environment.yml
   ```

3. Construa o pacote:

   ```bash
   python -m build
   ```

4. Instale-o localmente com 

5. Este repositório já conta com uma GitHub Action para publicar automaticamente no PyPi e TestPyPi. Consulte o arquivo 
   [python-publish.yml](.github/workflows/python-publish.yml) para detalhes da implementação.
  
   Todos os commits serão enviados para o TestPyPi, mas apenas commits com tags serão enviados para o PyPi:

   ```bash
   # alguma modificação no código fonte
   # ...
   git add .
   git commit -m "mensagem do commit"
   git tag -a <tag_name> -m "título da versão"
   git push origin main  # envia o commit para o repositório e o pacote para TestPyPi
   git push origin <tag_name>  # publica a tag e envia o pacote para o PyPi
   ```
   
   Onde <tag_name> é um número no formato, por exemplo, `v1.4.1`.

   Use apenas os comandos `git tag -a <tag_name>` e `git push origin <tag_name>` quando quiser publicar o pacote no 
   canal PyPi! 

   Um tutorial de publicação com GitHub Actions está disponível 
   [neste link](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

</details>

## Contato

Biblioteca desenvolvida originalmente por Henry Cagnini: [henry.cagnini@ufsm.br]()

Caso encontre algum problema no uso, abra um issue no [repositório da biblioteca](https://github.com/COPLIN-UFSM/db2).

Pull requests são bem-vindos!  
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

## Documentação

A documentação está disponível em https://coplin-ufsm.github.io/db2

## Desenvolvimento

Para instruções de desenvolvimento do pacote, consulte [este arquivo](https://github.com/COPLIN-UFSM/db2/blob/main/DEVELOPMENT.md).

## Contato

Biblioteca desenvolvida originalmente por Henry Cagnini: [henry.cagnini@ufsm.br]()

Caso encontre algum problema no uso, abra um issue no [repositório da biblioteca](https://github.com/COPLIN-UFSM/db2).

Pull requests são bem-vindos!  
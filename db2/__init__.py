import json
import re
import sys
import pandas as pd
from typing import Union

import numpy as np

import ibm_db

from .utils import TupleIterator, DictIterator, Converter


class DB2Connection(object):
    """
    Classe para conectar-se com um banco de dados DB2.

    Esta classe abstrai a maioria das funções do módulo ibm_db, enquanto oferece métodos de conveniência para inserir,
    modificar e recuperar linhas do banco de dados.

    :param filename: Nome de um arquivo json com os dados de login para o banco de dados.
    :param late_commit: Se as modificações no banco de dados devem ser retardadas até o fim da execução da cláusula
        with.

    **Exemplo:**

    .. code-block:: python

        from db2 import DB2Connection

        with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
            conn.modify('''
                CREATE TABLE TEST (
                    A1 INTEGER NOT NULL,
                    A2 VARCHAR(9) NOT NULL
                );
            ''')

            conn.insert("TEST", {'A1': 1, 'A2': 'olá mundo'})

    """

    def __init__(self, filename: str, late_commit=False):
        self.driver = "{IBM Db2 LUW}"
        self.conn_params = {ibm_db.SQL_ATTR_AUTOCOMMIT: ibm_db.SQL_AUTOCOMMIT_OFF}

        with open(filename, 'r', encoding='utf-8') as read_file:
            self.login_params = json.load(read_file)

        self.conn = None
        self.late_commit = late_commit

    def __enter__(self):
        str_connect = (
            'DRIVER={0};DATABASE={1};HOSTNAME={2};PORT={3};'
            'PROTOCOL=TCPIP;UID={4};PWD={5};AUTHENTICATION=SERVER;').format(
            self.driver, self.login_params['database'], self.login_params['host'], self.login_params['port'],
            self.login_params['user'], self.login_params['password']
        )

        self.conn = ibm_db.connect(str_connect, "", self.conn_params)  # type: ibm_db.IBM_DBConnection
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ibm_db.commit(self.conn)

    def query(self, sql: str, as_dict: bool = False) -> Union[TupleIterator, DictIterator]:
        """
        Realiza consultas à base de dados DB2.

        Esse método é reservado a consultas do tipo Data Query Language (DQL).

        :param sql: A consulta em SQL.
        :param as_dict: Opcional - se o resultado deve ser um dicionário, ao invés de uma tupla.
        :return: Um iterator para as tuplas a serem retornadas.

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                tuple_factory = conn.query(f'''
                    SELECT *
                    FROM DB2_TEST_TABLE_1;
                '''))
                # resultados são no formato (1, 1.17, 3.2, ...)

                dict_factory = conn.query(f'''
                    SELECT *
                    FROM DB2_TEST_TABLE_1;
                ''', as_dict=True))
                # resultados são no formato {'A1': 1, 'A2': 1.17, 'A3': 3.2, ...}
        """
        stmt = ibm_db.exec_immediate(self.conn, sql)
        if as_dict:
            some_iterator = DictIterator(stmt)
        else:
            some_iterator = TupleIterator(stmt)
        return some_iterator

    def get_columns(self, table_name: str, schema_name: str = None) -> list:
        """
        Retorna um dicionário com o tipo de dados das colunas de uma tabela.
        
        :param table_name: O nome da coluna, com ou sem o SCHEMA prefixado.
        :param schema_name: Opcional - o nome do schema do qual a tabela pertence. O padrão é None (schema padrão do
            banco)
        :return: Uma lista de dicionários, onde para cada dicionário contém as informações da coluna. O tipo das colunas
            é o tipo no formato IBM DB2 (e.g. DECIMAL(10, 2), FLOAT, INTEGER, VARCHAR, etc).

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                column_types = conn.get_columns(schema_name=None, table_name='DB2_TEST_TABLE_1')
                print(column_types)

        """
        query_str = f'''
            select colno as order, colname as name, typename as type
            from syscat.columns
            where tabname = '{table_name}'            
            {("and tabschema = '" + schema_name + "'") if schema_name is not None else ""}--
            order by colno;
        '''
        return list(self.query(query_str, as_dict=True))

    def query_to_dataframe(self, sql: str) -> pd.DataFrame:
        """
        Realiza uma consulta à base de dados DB2, convertendo automaticamente o resultado em um pandas.DataFrame.

        **IMPORTANTE:** Se a consulta retornar uma tabela que ocupa muito espaço em disco (ou muitos recursos de rede),
        prefira definir o parâmetro fetch_first para um valor (e.g. 500 linhas).

        :param sql: A consulta em SQL.
        :return: um pandas.DataFrame com o resultado da consulta.

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection
            import pandas as pd

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                conn.insert(
                    'DB2_TEST_TABLE_1',
                    {'A1': 5, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-01-01', 'A5': '2010_2020'}
                )
                conn.insert(
                    'DB2_TEST_TABLE_1',
                    {'A1': 6, 'A2': 32.500, 'A3': 7.2, 'A4': '2050-12-31', 'A5': '2011_2021'}
                )

                df = conn.query_to_dataframe('''SELECT * FROM DB2_TEST_TABLE_1;''')

        """

        stmt = ibm_db.exec_immediate(self.conn, sql)
        some_iterator = DictIterator(stmt)

        detected_types = Converter.get_types(stmt)

        df = pd.DataFrame(some_iterator)

        for column in df.columns:
            if not Converter.has_type(detected_types[column]):
                raise NotImplementedError(
                    f'O tipo {detected_types[column]} ainda não é suportado pelo método query_to_dataframe!'
                )

            try:
                df[column] = df[column].apply(Converter.get_converter(detected_types[column]))
            except ValueError:
                pass

        return df

    def modify(self, sql: str, suppress=False) -> int:
        """
        Realiza modificações (inserções, modificações, deleções) na base de dados.

        Esse método é reservado a instruções que alteram o estado do banco de dados, Data Manipulation Language (DML).

        :param sql: O comando em SQL.
        :param suppress: Opcional - se warnings devem ser suprimidos na saída do console.
        :return: Quantidade de linhas que foram afetadas pelo comando SQL

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                conn.modify('DROP TABLE DB2_TEST_TABLE_1;')
        """
        try:
            stmt = ibm_db.exec_immediate(self.conn, sql)
        except Exception as e:
            ibm_db.rollback(self.conn)
            if not suppress:
                print(f'O comando não pode ser executado: {sql}', file=sys.stderr)
            return 0
        else:
            if not self.late_commit:
                ibm_db.commit(self.conn)
            return ibm_db.num_rows(stmt)

    @staticmethod
    def __collect__(row: dict, *, upper=False):
        """
        Converte um dicionário em duas listas, fazendo adaptações para que a segunda lista (que contém os valores de uma
        tupla em um banco de dados) possa ser prontamente incorporada a uma string SQL.

        :param row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :param upper: Opcional - se, para colunas que são string, uma chamada à função UPPER deve ser adicionada
        :return: Duas listas, onde a primeira é a lista de nomes de colunas, e a segunda os valores destas colunas para
            uma tupla.
        """
        row_values = []
        column_names = []

        for row_name, row_value in row.items():
            if upper:
                column_names += [f'UPPER({row_name})']
            else:
                column_names += [row_name]
            if row_value is None or (not isinstance(row_value, str) and np.isnan(row_value)):
                row_values += ['NULL']
            elif isinstance(row_value, str):
                new_item = row_value.replace("'", "''")
                if upper:
                    row_values += [f"UPPER('{new_item}')"]
                else:
                    row_values += [f"'{new_item}'"]
            else:
                row_values += [str(row_value)]

        return column_names, row_values

    def create_tables(self, filename: str):
        """
        Cria tabelas, se elas não existirem, a partir de um arquivo em disco.

        Tabelas também podem ser criadas a partir do comando modify.

        :param filename: Caminho para um arquivo SQL com os comandos para criar as tabelas. Cada comando de criação de
            tabelas deve estar separado por dois espaços em branco.

        **Exemplo:**

        ``caminho_para_arquivo_com_comandos.sql``

        .. code-block:: sql

            CREATE TABLE USERS_TEST_IBMDB2(
                ID INTEGER NOT NULL PRIMARY KEY,
                NAME VARCHAR(10) NOT NULL,
                AGE INTEGER NOT NULL
            );

            INSERT INTO USERS_TEST_IBMDB2(ID, NAME, AGE) VALUES (1, 'HENRY', 32);
            INSERT INTO USERS_TEST_IBMDB2(ID, NAME, AGE) VALUES (2, 'JOHN', 20);

        ``main.py``

        .. code-block:: python

            import os
            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as db2_conn:
                db2_conn.create_tables(caminho_para_arquivo_com_comandos.sql)
                query_str = '''
                    SELECT *
                    FROM USERS_TEST_IBMDB2;
                 '''
                df = db2_conn.query_to_dataframe(query_str)

                print(df)
        """

        with open(filename, 'r', encoding='utf-8') as read_file:
            create_tables_sql = ''.join(read_file.readlines())
            tables_statements = create_tables_sql.split('\n\n')

            for table_stmt in tables_statements:
                table_name = re.findall('CREATE TABLE(.*?)\\(', table_stmt)[0].strip()

                result = self.query(f"""
                    SELECT COUNT(*) as count_matching_tables
                    FROM SYSIBM.SYSTABLES
                    WHERE NAME = '{table_name}' AND TYPE = 'T';
                """)

                table_already_present = True if next(result)[0] == 1 else False
                if not table_already_present:
                    linhas = self.modify(table_stmt)

                    if linhas == 0:
                        raise Exception('Não foi possível criar as tabelas no banco de dados!')

    def insert_or_update_table(self, table_name: str, where: dict, row: dict) -> int:
        """
        Dada uma tabela em DB2 e um conjunto de informações (apresentados como um dicionário), insere OU atualiza estas
        informações no banco de dados.

        No parâmetro where, deve ser passado as informações que localizam a linha no banco de dados.
        No parâmetro row, devem ser passadas todas as informações, inclusive as que estão contidas na cláusula where.

        :param table_name: Nome da tabela onde os dados serão inseridos ou atualizados.
        :param where: Dicionário com a cláusula WHERE. As chaves do dicionário são os nomes das colunas, e seus valores
            os valores da tupla a ser buscada.
        :param row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :return: Quantidade de linhas que foram afetadas pelo comando SQL

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                conn.insert_or_update_table(
                    'DB2_TEST_TABLE_1',
                    {'A1': 4, 'A2': 1.17},
                    {'A1': 4, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-12-31', 'A5': 'olá mundo'}
                )
                # valor de A3: 3.2

                conn.insert_or_update_table(
                    'DB2_TEST_TABLE_1',
                    {'A1': 4, 'A2': 1.17},
                    {'A1': 4, 'A2': 1.17, 'A3': 4.0, 'A4': '2024-12-31', 'A5': 'olá mundo'}
                )
                # valor de A3: 4.0

        """
        try:
            column_names, row_values = self.__collect__(where)
            where_str = ' AND '.join(f'{k} = {v}' for k, v in zip(column_names, row_values))

            _ = next(self.query(f"""SELECT * FROM {table_name} WHERE {where_str}"""))
            contains = True
        except StopIteration:
            contains = False

        if contains:  # atualiza
            linhas = self.update(table_name, where, row)
        else:  # insere
            linhas = self.insert(table_name, row)

        return linhas

    def insert(self, table_name: str, row: dict) -> int:
        """
        Insere uma tupla (apresentada como um dicionário) em uma tabela.

        :param table_name: Nome da tabela onde os dados serão inseridos.
        :param row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :return: A quantidade de linhas inseridas

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                to_input = [
                    {'A1': 1, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-12-31', 'A5': 'olá mundo'},
                    {'A1': 2, 'A2': 32.500, 'A3': 7.2, 'A4': '1970-01-01', 'A5': 'olá henry'}
                ]
                for inp in to_input:
                    n_rows_affected = conn.insert('DB2_TEST_TABLE_1', inp)
                    print(n_rows_affected)
        """

        column_names, row_values = self.__collect__(row)

        column_names_str = ', '.join(column_names)
        row_str = ', '.join(row_values)

        insert_sql = f"""INSERT INTO {table_name} ({column_names_str}) VALUES ({row_str});"""

        linhas = self.modify(insert_sql)
        return linhas

    def update(self, table_name: str, where: dict, values: dict) -> int:
        """
        Atualiza os valores de uma tupla (apresentada como um dicionário) em uma tabela.

        :param table_name: Nome da tabela onde os dados serão atualizados.
        :param where: Dicionário com a cláusula WHERE. As chaves do dicionário são os nomes das colunas, e seus valores
            os valores da tupla a ser atualizada.
        :param values: Valores a serem atualizados na tabela do banco de dados.
        :return: A quantidade de linhas afetadas pelo comando update

        **Exemplo:**

        .. code-block:: python

            from db2 import DB2Connection

            with DB2Connection(caminho_para_arquivo_com_credenciais.json) as conn:
                conn.insert(
                    'DB2_TEST_TABLE_1',
                    {'A1': 3, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-12-31', 'A5': 'olá mundo'}
                )
                # valor de A3: 3.2

                conn.update(
                    'DB2_TEST_TABLE_1',
                    {'A1': 3, 'A2': 1.17},
                    {'A3': 4}
                )
                # valor de A3: 4.0

        """

        where_column_names, where_row_values = self.__collect__(where)

        column_names, row_values = self.__collect__(values)
        insert_str = ', '.join([f'{k} = {v}' for k, v in zip(column_names, row_values)])
        where_str = ' AND '.join(f'{k} = {v}' for k, v in zip(where_column_names, where_row_values))

        update_sql = f"""
        UPDATE {table_name} SET {insert_str} WHERE {where_str} 
        """

        linhas = self.modify(update_sql)
        return linhas

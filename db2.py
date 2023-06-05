__version__ = '1.0'

import copy
import json
import re

import ibm_db


class TupleIterator(object):
    """
    Classe para iterar sobre as respostas de um banco de dados DB2.
    """

    def __init__(self, stmt):
        self.stmt = stmt
        self.next_item = ibm_db.fetch_tuple(self.stmt)

    def __iter__(self):
        self.next_item = ibm_db.fetch_tuple(self.stmt)
        return self

    def __next__(self):
        if self.next_item is not False:
            to_return = self.next_item
            self.next_item = ibm_db.fetch_tuple(self.stmt)
            return to_return
        else:
            raise StopIteration


class DB2Connection(object):
    """
    Classe para conectar-se com um banco de dados DB2.
    """

    def __init__(self, filename):
        """
        Cria um objeto para conectar-se a um banco de dados DB2.

        :param filename: Nome de um arquivo json com os dados de login para o banco de dados.
        """
        self.driver = "{IBM Db2 LUW}"
        self.conn_params = {ibm_db.SQL_ATTR_AUTOCOMMIT: ibm_db.SQL_AUTOCOMMIT_OFF}

        with open(filename, 'r', encoding='utf-8') as read_file:
            self.login_params = json.load(read_file)

        self.conn = None

    def __enter__(self):
        str_connect = 'DRIVER={0};DATABASE={1};HOSTNAME={2};PORT={3};PROTOCOL=TCPIP;UID={4};PWD={5};'.format(
            self.driver, self.login_params['database'], self.login_params['host'], self.login_params['port'],
            self.login_params['user'], self.login_params['password']
        )

        self.conn = ibm_db.connect(str_connect, "", self.conn_params)  # type: ibm_db.IBM_DBConnection
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def query(self, sql: str) -> TupleIterator:
        """
        Realiza consultas à base de dados DB2.

        :param sql: A consulta em SQL.
        :return: Um iterator para as tuplas a serem retornadas.
        """
        stmt = ibm_db.exec_immediate(self.conn, sql)
        some_iterator = TupleIterator(stmt)
        return some_iterator

    def modify(self, sql: str) -> bool:
        """
        Realiza modificações (inserções, modificações, deleções) na base de dados.

        :param sql: O comando em SQL.
        """
        success = False
        try:
            stmt = ibm_db.exec_immediate(self.conn, sql)
        except Exception as e:
            ibm_db.rollback(self.conn)
            print(f'O comando não pode ser executado: {sql}')
        else:
            ibm_db.commit(self.conn)
            success = True
        return success

    @staticmethod
    def __collect__(sqlite_row: dict):
        """
        Converte um dicionário em duas listas, fazendo adaptações para que a segunda lista (que contém os valores de uma
        tupla em um banco de dados) possa ser prontamente incorporada a uma string SQL.

        :param sqlite_row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :return: Duas listas, onde a primeira é a lista de nomes de colunas, e a segunda os valores destas colunas para
            uma tupla.
        """
        row_values = []
        column_names = []

        for row_name, row_value in sqlite_row.items():
            column_names += [row_name]
            if row_value is None:
                row_values += ['NULL']
            elif isinstance(row_value, str):
                new_item = row_value.replace("'", "''")
                row_values += [f"'{new_item}'"]
            else:
                row_values += [str(row_value)]

        return column_names, row_values

    def create_tables(self, filename: str):
        """
        Cria tabelas, se elas não existirem.

        :param filename: Caminho para um arquivo SQL com os comandos para criar as tabelas. Cada comando de criação de
        tabelas deve estar separado por dois espaços em branco.
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
                    tables_created = self.modify(table_stmt)

                    if not tables_created:
                        raise Exception('Não foi possível criar as tabelas no banco de dados!')

    def insert_or_update_table(self, table_name: str, where: dict, sqlite_row: dict) -> bool:
        """
        Dada uma tabela em DB2 e um conjunto de informações (apresentados como um dicionário), insere ou atualiza estas
        informações no banco de dados.

        :param table_name: Nome da tabela onde os dados serão inseridos ou atualizados.
        :param where: Dicionário com a cláusula WHERE. As chaves do dicionário são os nomes das colunas, e seus valores
            os valores da tupla a ser buscada.
        :param sqlite_row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :return: Um booleano denotando se a operação de inserção/atualização foi bem sucedida.
        """
        try:
            column_names, row_values = self.__collect__(where)
            where_str = ' AND '.join(f'{k} = {v}' for k, v in zip(column_names, row_values))

            _ = next(self.query(f"""SELECT * FROM {table_name} WHERE {where_str}"""))
            contains = True
        except StopIteration:
            contains = False

        if contains:  # atualiza
            success = self.generic_update(table_name, where, sqlite_row)
        else:  # insere
            success = self.generic_insert(table_name, sqlite_row)

        return success

    def generic_insert(self, table_name: str, sqlite_row: dict) -> bool:
        """
        Insere uma tupla (apresentada como um dicionário) em uma tabela.

        :param table_name: Nome da tabela onde os dados serão inseridos.
        :param sqlite_row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :return: Um booleano denotando se a operação de inserção foi bem sucedida.
        """

        column_names, row_values = self.__collect__(sqlite_row)

        column_names_str = ', '.join(column_names)
        row_str = ', '.join(row_values)

        insert_sql = f"""INSERT INTO {table_name} ({column_names_str}) VALUES ({row_str});"""

        success = self.modify(insert_sql)
        return success

    def generic_update(self, table_name: str, where: dict, sqlite_row: dict) -> bool:
        """
        Atualiza os valores de uma tupla (apresentada como um dicionário) em uma tabela.

        :param table_name: Nome da tabela onde os dados serão atualizados.
        :param where: Dicionário com a cláusula WHERE. As chaves do dicionário são os nomes das colunas, e seus valores
            os valores da tupla a ser atualizada.
        :param sqlite_row: Um dicionário onde as chaves são nomes de colunas e seus valores os valores de uma tupla em
            um banco de dados.
        :return: Um booleano denotando se a operação de atualização foi bem sucedida
        """

        local_row = copy.deepcopy(sqlite_row)
        where_column_names, where_row_values = self.__collect__(where)

        for k in where.keys():
            del local_row[k]

        if len(local_row) == 0:  # se sobrou algum dado a ser atualizado
            return True

        column_names, row_values = self.__collect__(local_row)
        insert_str = ', '.join([f'{k} = {v}' for k, v in zip(column_names, row_values)])
        where_str = ' AND '.join(f'{k} = {v}' for k, v in zip(where_column_names, where_row_values))

        update_sql = f"""
        UPDATE {table_name} SET {insert_str} WHERE {where_str} 
        """

        success = self.modify(update_sql)
        return success

"""
Esse arquivo de testes NÃO DEVE SER UTILIZADO para validar o pacote, pois ele funciona apenas dentro da rede da UFSM.

Portanto, ele deve executado dentro da rede da UFSM para validação.
"""
import os
import unittest

import numpy as np

from db2 import DB2Connection
from datetime import date


class Tester(unittest.TestCase):
    def test_columns_name(self):
        """
        Testa se a função de consulta do tipo de colunas de uma tabela está funcionando.
        """
        with DB2Connection(os.path.join('instance', 'database_credentials.json')) as db2_conn:
            # deleta a tabela, se ela já existir
            db2_conn.modify('''DROP TABLE DB2_TEST_COLUMNS;''', suppress=True)
            db2_conn.modify(
                '''
                CREATE TABLE DB2_TEST_COLUMNS(
                    A1 INTEGER NOT NULL PRIMARY KEY,
                    A2 VARCHAR(10) NOT NULL
                );
                ''', suppress=True
            )

            correct_columns = [
                {'ORDER': 0, 'NAME': 'A1', 'TYPE': 'INTEGER'},
                {'ORDER': 1, 'NAME': 'A2', 'TYPE': 'VARCHAR'}
            ]
            columns = db2_conn.get_columns(schema_name=None, table_name='DB2_TEST_COLUMNS')
            db2_conn.modify('''DROP TABLE DB2_TEST_COLUMNS;''', suppress=True)
            self.assertListEqual(correct_columns, columns, 'As informações das colunas estão diferentes!')

    def test_insert(self):
        """
        Testa o método de insert.
        """
        with DB2Connection(os.path.join('instance', 'database_credentials.json')) as db2_conn:
            # deleta a tabela, se ela já existir
            db2_conn.modify('''DROP TABLE DB2_TEST_DATAFRAME;''', suppress=True)
            db2_conn.modify(
                '''
                CREATE TABLE DB2_TEST_DATAFRAME(
                    A1 INTEGER NOT NULL PRIMARY KEY,
                    A2 DECIMAL(5,2) NOT NULL,
                    A3 FLOAT NOT NULL
                );
                ''', suppress=True
            )
            db2_conn.insert('DB2_TEST_DATAFRAME', {'A1': 1, 'A2': 1.17, 'A3': 3.2})
            db2_conn.insert('DB2_TEST_DATAFRAME', {'A1': 2, 'A2': 32.500, 'A3': 7.2})
            db2_conn.modify('''DROP TABLE DB2_TEST_COLUMNS;''', suppress=True)

    def test_update(self):
        """
        Testa o método de update.
        """
        with DB2Connection(os.path.join('instance', 'database_credentials.json')) as db2_conn:
            # deleta a tabela, se ela já existir
            db2_conn.modify('''DROP TABLE DB2_TEST_DATAFRAME;''', suppress=True)
            db2_conn.modify(
                '''
                CREATE TABLE DB2_TEST_DATAFRAME(
                    A1 INTEGER NOT NULL PRIMARY KEY,
                    A2 DECIMAL(5,2) NOT NULL,
                    A3 FLOAT NOT NULL
                );
                ''', suppress=True
            )
            db2_conn.insert('DB2_TEST_DATAFRAME', {'A1': 1, 'A2': 1.17, 'A3': 3.2})
            db2_conn.insert('DB2_TEST_DATAFRAME', {'A1': 2, 'A2': 32.500, 'A3': 7.2})

            db2_conn.update('DB2_TEST_DATAFRAME', {'A1': 1, 'A2': 1.17}, {'A3': 4})

            value = next(db2_conn.query('SELECT A3 FROM DB2_TEST_DATAFRAME WHERE A1 = 1 AND A2 = 1.17'))[0]
            db2_conn.modify('''DROP TABLE DB2_TEST_COLUMNS;''', suppress=True)

            self.assertAlmostEqual(4.0, value, places=2, msg='A linha não foi atualizada corretamente!')

    def test_insert_or_update(self):
        """
        Testa o método de inserir ou atualizar tabelas.
        """
        with DB2Connection(os.path.join('instance', 'database_credentials.json')) as db2_conn:
            # deleta a tabela, se ela já existir
            db2_conn.modify('''DROP TABLE DB2_TEST_DATAFRAME;''', suppress=True)
            db2_conn.modify(
                '''
                CREATE TABLE DB2_TEST_DATAFRAME(
                    A1 INTEGER NOT NULL PRIMARY KEY,
                    A2 DECIMAL(5,2) NOT NULL,
                    A3 FLOAT NOT NULL
                );
                ''', suppress=True
            )

            # testa inserção
            db2_conn.insert_or_update_table(
                'DB2_TEST_DATAFRAME', {'A1': 1, 'A2': 1.17}, {'A1': 1, 'A2': 1.17, 'A3': 3.2}
            )
            first_value = next(db2_conn.query('SELECT A3 FROM DB2_TEST_DATAFRAME WHERE A1 = 1 AND A2 = 1.17'))[0]
            first_correct_value = 3.2

            db2_conn.insert_or_update_table(
                'DB2_TEST_DATAFRAME', {'A1': 1, 'A2': 1.17}, {'A1': 1, 'A2': 1.17, 'A3': 4.0}
            )
            second_value = next(db2_conn.query('SELECT A3 FROM DB2_TEST_DATAFRAME WHERE A1 = 1 AND A2 = 1.17'))[0]
            second_correct_value = 4.0
            db2_conn.modify('''DROP TABLE DB2_TEST_COLUMNS;''', suppress=True)

            self.assertAlmostEqual(
                first_value, first_correct_value, places=2, msg='A linha não foi inserida corretamente!'
            )
            self.assertAlmostEqual(
                second_value, second_correct_value, places=2, msg='A linha não foi atualizada corretamente!'
            )

    def test_dataframe_query(self):
        """
        se é possível retornar consulta como pandas.DataFrame.
        """
        with DB2Connection(os.path.join('instance', 'database_credentials.json')) as db2_conn:
            # deleta a tabela, se ela já existir
            db2_conn.modify('''DROP TABLE DB2_TEST_DATAFRAME;''', suppress=True)
            db2_conn.modify(
                '''
                CREATE TABLE DB2_TEST_DATAFRAME(
                    A1 INTEGER NOT NULL PRIMARY KEY,
                    A2 DECIMAL(5,2) NOT NULL,
                    A3 FLOAT NOT NULL,
                    A4 DATE NOT NULL
                );
                ''', suppress=True
            )
            db2_conn.insert('DB2_TEST_DATAFRAME', {'A1': 1, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-01-01'})
            db2_conn.insert('DB2_TEST_DATAFRAME', {'A1': 2, 'A2': 32.500, 'A3': 7.2, 'A4': '2024-01-01'})

            correct_dtypes = [np.dtype('int64'), float, float, np.dtype('O')]
            df = db2_conn.query_to_dataframe('''SELECT * FROM DB2_TEST_DATAFRAME;''')
            db2_conn.modify('''DROP TABLE DB2_TEST_DATAFRAME;''', suppress=True)

            self.assertListEqual(correct_dtypes, df.dtypes.tolist(), 'Os tipos das colunas estão incorretos!')


if __name__ == '__main__':
    unittest.main()

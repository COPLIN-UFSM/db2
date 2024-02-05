"""
Esse arquivo de testes NÃO DEVE SER UTILIZADO para validar o pacote, pois ele funciona apenas dentro da rede da UFSM.

Portanto, ele deve executado dentro da rede da UFSM para validação.
"""
import os
import unittest
from db2 import DB2Connection


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
                ''', suppress=False
            )

            correct_columns = [
                {'ORDER': 0, 'NAME': 'A1', 'TYPE': 'INTEGER'},
                {'ORDER': 1, 'NAME': 'A2', 'TYPE': 'VARCHAR'}
            ]
            columns = db2_conn.get_columns(schema_name=None, table_name='DB2_TEST_COLUMNS')
            db2_conn.modify('''DROP TABLE DB2_TEST_COLUMNS;''', suppress=False)
            self.assertListEqual(correct_columns, columns, 'As informações das colunas estão diferentes!')

    def test_dataframe_query(self):
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
                ''', suppress=False
            )
            db2_conn.modify('''INSERT INTO DB2_TEST_DATAFRAME(A1, A2, A3) VALUES (1, 1.7, 3.2);''')
            db2_conn.modify('''INSERT INTO DB2_TEST_DATAFRAME(A1, A2, A3) VALUES (2, 32.500, 7.2);''')

            correct_dtypes = [int, float, float]
            df = db2_conn.query_to_dataframe('''select * from DB2_TEST_DATAFRAME;''')
            db2_conn.modify('''DROP TABLE DB2_TEST_DATAFRAME;''', suppress=False)

            self.assertListEqual(correct_dtypes, df.dtypes.tolist(), 'Os tipos das colunas estão incorretos!')


if __name__ == '__main__':
    unittest.main()

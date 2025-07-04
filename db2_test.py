"""
Esse arquivo de testes NÃO DEVE SER UTILIZADO para validar o pacote, pois ele funciona apenas dentro da rede da UFSM.

Portanto, ele deve executado dentro da rede da UFSM para validação.
"""
import datetime

import numpy as np
from datetime import datetime as dt


def test_columns_name(get_database_connection, get_tables_columns):
    for column_name, actual_columns in get_tables_columns.items():
        queried_columns = get_database_connection.get_columns(schema_name=None, table_name=column_name)
        assert queried_columns == actual_columns


def test_insert(get_database_connection, create_tables):
    """
    Testa o método insert.
    """
    to_input = [
        {'A1': 1, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-12-31', 'A5': 'olá mundo', 'A6': '15:30:00', 'A7': '2024-01-01 12:00:00'},
        {'A1': 2, 'A2': 32.500, 'A3': 7.2, 'A4': '1970-01-01', 'A5': 'olá henry', 'A6': None, 'A7': None}
    ]
    to_retrieve = [
        {
            'A1': 1, 'A2': 1.17, 'A3': 3.2,
            'A4': dt.strptime('2024-12-31', '%Y-%m-%d').date(),
            'A5': 'olá mundo',
            'A6': datetime.time(15, 30, 0),
            'A7': datetime.datetime(2024, 1, 1, 12, 0, 0)
        }, {
            'A1': 2, 'A2': 32.500, 'A3': 7.2,
            'A4': dt.strptime('1970-01-01', '%Y-%m-%d').date(),
            'A5': 'olá henry',
            'A6': None,
            'A7': None
        }
    ]

    for inp, out in zip(to_input, to_retrieve):
        n_rows_affected = get_database_connection.insert('DB2_TEST_TABLE_1', inp)
        if n_rows_affected > 0:
            ret = next(get_database_connection.query(f'''
                SELECT * 
                FROM DB2_TEST_TABLE_1 
                WHERE A1={inp["A1"]};
            ''', as_dict=True))
            assert ret == out


def test_update(get_database_connection, create_tables):
    """
    Testa o método update.
    """

    get_database_connection.insert(
        'DB2_TEST_TABLE_1',
        {'A1': 3, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-12-31', 'A5': 'olá mundo'}
    )

    get_database_connection.update(
        'DB2_TEST_TABLE_1',
        {'A1': 3, 'A2': 1.17},
        {'A3': 4}
    )

    queried = next(get_database_connection.query('SELECT A3 FROM DB2_TEST_TABLE_1 WHERE A1 = 3 AND A2 = 1.17'))[0]
    expected = 4.

    assert queried == expected


def test_insert_or_update(get_database_connection, create_tables):
    """
    Testa o método de inserir ou atualizar tabelas.
    """
    get_database_connection.insert_or_update_table(
        'DB2_TEST_TABLE_1',
        {'A1': 4, 'A2': 1.17},
        {'A1': 4, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-12-31', 'A5': 'olá mundo'}
    )
    insert_queried = next(get_database_connection.query('''
        SELECT A3 
        FROM DB2_TEST_TABLE_1 
        WHERE A1 = 4 AND A2 = 1.17
    '''))[0]
    insert_expected = 3.2

    get_database_connection.insert_or_update_table(
        'DB2_TEST_TABLE_1',
        {'A1': 4, 'A2': 1.17},
        {'A1': 4, 'A2': 1.17, 'A3': 4.0, 'A4': '2024-12-31', 'A5': 'olá mundo'}
    )
    update_queried = next(get_database_connection.query('''
        SELECT A3 
        FROM DB2_TEST_TABLE_1 
        WHERE A1 = 4 
        AND A2 = 1.17
    '''))[0]
    update_expected = 4.0

    assert insert_queried == insert_expected
    assert update_queried == update_expected


def test_dataframe_query(get_database_connection, create_tables):
    get_database_connection.insert(
        'DB2_TEST_TABLE_1',
        {'A1': 5, 'A2': 1.17, 'A3': 3.2, 'A4': '2024-01-01', 'A5': '2010_2020', 'A6': '15:30:00', 'A7': '2024-01-01 12:00:00'}
    )
    get_database_connection.insert(
        'DB2_TEST_TABLE_1',
        {'A1': 6, 'A2': 32.500, 'A3': 7.2, 'A4': '2050-12-31', 'A5': '2011_2021', 'A6': None, 'A7': None}
    )

    df = get_database_connection.query_to_dataframe('''SELECT * FROM DB2_TEST_TABLE_1;''')

    expected_dtypes = [np.dtype('int64'), float, float, np.dtype('O'), np.dtype('O'), np.dtype('O'), np.dtype('<M8[ns]')]
    queried_dtypes = df.dtypes.tolist()

    assert expected_dtypes == queried_dtypes

def test_clob_column(get_database_connection, create_tables):
    """
    Testa a inserção, recuperação e atualização de dados em uma coluna CLOB.
    """
    large_text_1 = "a" * 10000  # 10k chars
    large_text_2 = "b" * 20000  # 20k chars

    # insere linha
    insert_data = {'A8': 100, 'A9': large_text_1}
    n_rows_affected = get_database_connection.insert('DB2_TEST_TABLE_2', insert_data)
    assert n_rows_affected > 0

    # recupera linha e verifica os dados recuperados
    ret = next(get_database_connection.query(f'''
        SELECT A8, A9 FROM DB2_TEST_TABLE_2 WHERE A8 = {insert_data['A8']}
    ''', as_dict=True))
    assert ret['A8'] == insert_data['A8']
    assert ret['A9'] == large_text_1

    # atualiza os dados da coluna com um novo texto grande
    update_data = {'A9': large_text_2}
    where_clause = {'A8': insert_data['A8']}
    n_rows_updated = get_database_connection.update('DB2_TEST_TABLE_2', where_clause, update_data)
    assert n_rows_updated > 0

    # recupera dados e verifica novamente o conteúdo
    ret_updated = next(get_database_connection.query(f'''
        SELECT A9 FROM DB2_TEST_TABLE_2 WHERE A8 = {insert_data['A8']}
    ''', as_dict=True))
    assert ret_updated['A9'] == large_text_2

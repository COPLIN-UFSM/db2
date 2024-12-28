import os
import pytest
from db2 import DB2Connection


@pytest.fixture(scope='module')
def get_database_connection():
    with DB2Connection(os.path.join('instance', 'database_credentials.json')) as conn:
        return conn


@pytest.fixture(scope='module')
def create_tables(get_database_connection):
    get_database_connection.modify(
        '''
        CREATE TABLE DB2_TEST_TABLE_1(
            A1 INTEGER NOT NULL PRIMARY KEY,
            A2 DECIMAL(5,2) NOT NULL,
            A3 DOUBLE NOT NULL,
            A4 DATE NOT NULL,
            A5 VARCHAR(9) NOT NULL
        );
        ''', suppress=True
    )


@pytest.fixture(scope='module')
def get_tables_columns(create_tables):
    return {
        'DB2_TEST_TABLE_1': [
            {'ORDER': 0, 'NAME': 'A1', 'TYPE': 'INTEGER'},
            {'ORDER': 1, 'NAME': 'A2', 'TYPE': 'DECIMAL'},
            {'ORDER': 2, 'NAME': 'A3', 'TYPE': 'DOUBLE'},
            {'ORDER': 3, 'NAME': 'A4', 'TYPE': 'DATE'},
            {'ORDER': 4, 'NAME': 'A5', 'TYPE': 'VARCHAR'}
        ]
    }


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    with DB2Connection(os.path.join('instance', 'database_credentials.json')) as conn:
        conn.modify('''DROP TABLE DB2_TEST_TABLE_1;''', suppress=True)

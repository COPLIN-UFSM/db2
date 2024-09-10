import argparse

import ibm_db


class TupleIterator(object):
    """
    Classe para iterar sobre as respostas de um banco de dados DB2.
    """
    fetch_method = ibm_db.fetch_tuple

    def __init__(self, stmt):
        self.uninitialized = True
        self.stmt = stmt
        self.next_item = None

    def __iter__(self):
        if self.uninitialized:
            self.uninitialized = False
            self.next_item = self.fetch_method(self.stmt)

        return self

    def __next__(self):
        if self.next_item is not False:
            if self.uninitialized:
                self.next_item = self.fetch_method(self.stmt)
                self.uninitialized = False

            to_return = self.next_item
            self.next_item = self.fetch_method(self.stmt)
            if to_return is False:
                raise StopIteration
            return to_return
        else:
            raise StopIteration


class DictIterator(TupleIterator):
    fetch_method = ibm_db.fetch_assoc

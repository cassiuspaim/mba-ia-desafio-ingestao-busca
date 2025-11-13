from search import search_topk

class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []

    def execute(self, sql, params):
        # Guarda o SQL e os parâmetros para depuração, se necessário
        self.executed.append((str(sql), params))

    def fetchall(self):
        return self.rows

class FakeConn:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        cursor = FakeCursor(self._rows)

        class Ctx:
            def __enter__(self_inner):
                return cursor

            def __exit__(self_inner, exc_type, exc, tb):
                return False

        return Ctx()

def test_search_topk_retorna_linhas_do_cursor():
    rows = [
        ("chunk 1", 0, 0.1),
        ("chunk 2", 1, 0.2),
        ("chunk 3", 2, 0.3),
    ]
    conn = FakeConn(rows)

    result = search_topk(conn, [0.0, 0.1, 0.2], k=2)

    # No nosso fake, sempre retornamos todas as linhas
    assert result == rows

from search import ensure_schema

class FakeConn:
    def __init__(self):
        self.sql = []
        self.commits = 0

    def execute(self, sql):
        # Armazena sempre como string para facilitar inspeção
        self.sql.append(str(sql))

    def commit(self):
        self.commits += 1

def test_ensure_schema_gera_ddl_com_dimensao_e_indice():
    conn = FakeConn()
    ensure_schema(conn, 1536)

    ddl = "\n".join(conn.sql)

    assert "CREATE TABLE IF NOT EXISTS rag_chunks" in ddl
    assert "embedding vector(1536)" in ddl
    assert "CREATE INDEX idx_rag_chunks_embedding" in ddl
    assert conn.commits == 1

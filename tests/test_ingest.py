from ingest import split_text

def test_split_text_small_input():
    text = "abc"
    chunks = split_text(text, chunk_size=1000, overlap=150)
    assert chunks == ["abc"]

def test_split_text_sizes_and_overlap():
    text = "".join(chr(97 + (i % 26)) for i in range(5000))  # 5000 chars
    chunks = split_text(text, chunk_size=1000, overlap=150)

    # Deve gerar vários chunks
    assert len(chunks) >= 5

    # Todos os chunks, exceto o último, devem ter tamanho exato de 1000
    for c in chunks[:-1]:
        assert len(c) == 1000

    # Último chunk pode ser menor ou igual a 1000
    assert 1 <= len(chunks[-1]) <= 1000

    # Overlap de 150 caracteres garantido entre chunks consecutivos
    for i in range(len(chunks) - 1):
        assert chunks[i][-150:] == chunks[i + 1][:150]

import asyncio

HOST = '127.0.0.1'
PORT = 65432


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Corrotina chamada pelo Event Loop para cada nova conexão.
    Substitui a função que antes rodava em uma Thread separada.
    """
    addr = writer.get_extra_info('peername')
    print(f"[NOVA CONEXÃO] {addr}")

    data = await reader.read(1024)
    msg = data.decode('utf-8') if data else ''

    if msg:
        print(f"[{addr}] Processando: {msg}")
    else:
        print(f"[{addr}] Sem mensagem recebida.")

    await asyncio.sleep(5)

    resposta = f"Processado: {msg}".encode('utf-8')
    writer.write(resposta)
    await writer.drain()

    writer.close()
    await writer.wait_closed()

    print(f"[DESCONECTADO] {addr}")


async def main():
    """
    Ponto de entrada assíncrono: cria e inicia o servidor.
    """
    server = await asyncio.start_server(handle_client, HOST, PORT)

    print(f"[ASSÍNCRONO] Servidor rodando em {HOST}:{PORT} — Event Loop ativo.")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

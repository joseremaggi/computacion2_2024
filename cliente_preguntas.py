import asyncio

async def tcp_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    try:
        while True:
            data = await reader.read(1000)
            if not data:
                break

            print(f'Pregunta recibida: {data.decode()}')

            respuesta = input('Ingresa tu respuesta (A/B/C/D): ').strip().upper()
            writer.write(respuesta.encode())
            await writer.drain()

            data = await reader.read(1000)
            print(f'Resultado: {data.decode()}')

    except ConnectionResetError:
        print("Conexión cerrada por el servidor.")
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(tcp_client())

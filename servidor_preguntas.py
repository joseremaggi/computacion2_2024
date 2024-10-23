import asyncio

# Función para manejar la conexión con cada cliente
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')  # Obtiene la dirección del cliente
    print(f"Conexión establecida con {addr}")

    while True:
        # Esperar a recibir datos del cliente
        data = await reader.read(100)  # Leer hasta 100 bytes
        if not data:
            break  # Si no hay datos, significa que el cliente cerró la conexión

        message = data.decode()  # Decodificar los datos recibidos
        print(f"Recibido {message} de {addr}")

        # Responder al cliente
        respuesta = f"Mensaje recibido: {message}"
        writer.write(respuesta.encode())
        await writer.drain()  # Asegurarse de que los datos se han enviado

    print(f"Cerrando la conexión con {addr}")
    writer.close()
    await writer.wait_closed()

# Función principal del servidor
async def main():
    # Iniciar el servidor en la IP local (127.0.0.1) y puerto 8888
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f"Servidor corriendo en {addr}")

    async with server:
        await server.serve_forever()

# Ejecutar el servidor
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor detenido")

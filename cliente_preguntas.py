import asyncio

# Función para conectarse al servidor y enviar un mensaje
async def tcp_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    # Mensaje que enviará el cliente
    message = "¡Hola servidor!"
    print(f"Enviando: {message}")
    writer.write(message.encode())  # Enviar el mensaje al servidor

    # Esperar la respuesta del servidor
    data = await reader.read(100)
    print(f"Recibido del servidor: {data.decode()}")

    # Cerrar la conexión
    print("Cerrando la conexión")
    writer.close()
    await writer.wait_closed()

# Ejecutar el cliente
if __name__ == "__main__":
    asyncio.run(tcp_client())

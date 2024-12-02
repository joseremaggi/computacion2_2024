import asyncio
import json
import random

# Lista de clientes conectados
clients = []

# Diccionario para almacenar los puntos de los jugadores
puntos_jugadores = {}

# Semáforo para controlar acceso concurrente
game_semaphore = asyncio.Semaphore()


# Función para cargar preguntas desde un archivo JSON
def cargar_preguntas_desde_archivo(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        preguntas = json.load(f)
    return preguntas


# Cargar preguntas desde el archivo 'preguntas.json'
preguntas = cargar_preguntas_desde_archivo('preguntas_pokemon.json')


# Función para obtener una pregunta aleatoria
def obtener_pregunta_aleatoria():
    return random.choice(preguntas)


# Función para manejar los clientes
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Jugador conectado: {addr}")

    # Inicializar puntos del jugador
    async with game_semaphore:
        puntos_jugadores[addr] = 0
        clients.append((reader, writer))  # Añadir cliente a la lista de clientes conectados

    try:
        while True:
            await asyncio.sleep(9999)  # Mantener el cliente en espera hasta la próxima pregunta

    except ConnectionResetError:
        pass
    finally:
        print(f"Jugador desconectado: {addr}")
        clients.remove((reader, writer))  # Remover cliente desconectado
        writer.close()
        await writer.wait_closed()


# Función para enviar la misma pregunta a todos los clientes
async def broadcast_pregunta():
    while True:
        if clients:  # Verifica si hay clientes conectados
            pregunta = obtener_pregunta_aleatoria()
            pregunta_texto = (
                f"{pregunta['pregunta']}\nA) {pregunta['opciones']['A']}\nB) {pregunta['opciones']['B']}\n"
                f"C) {pregunta['opciones']['C']}\nD) {pregunta['opciones']['D']}\n")

            # Enviar la pregunta a todos los clientes conectados
            for _, writer in clients:
                writer.write(pregunta_texto.encode())
                await writer.drain()

            # Recibir respuestas de todos los clientes
            respuestas = await obtener_respuestas(pregunta['respuesta_correcta'])

            # Enviar resultados a todos los clientes
            for addr, (status, reader, writer) in respuestas.items():
                if status == "correcta":
                    async with game_semaphore:
                        puntos_jugadores[addr] += 1
                    mensaje = f"¡Correcto! Tienes {puntos_jugadores[addr]} puntos.\n"
                else:
                    mensaje = f"Incorrecto. La respuesta correcta era {pregunta['respuesta_correcta']}. Tienes {puntos_jugadores[addr]} puntos.\n"

                writer.write(mensaje.encode())
                await writer.drain()

        await asyncio.sleep(10)  # Intervalo entre preguntas


# Función para recibir respuestas de todos los clientes
async def obtener_respuestas(respuesta_correcta):
    respuestas = {}

    for reader, writer in clients:
        try:
            data = await reader.read(100)
            respuesta = data.decode().strip().upper()

            addr = writer.get_extra_info('peername')
            if respuesta == respuesta_correcta:
                respuestas[addr] = ("correcta", reader, writer)
            else:
                respuestas[addr] = ("incorrecta", reader, writer)

        except ConnectionResetError:
            pass

    return respuestas


# Función principal del servidor
async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f"Servidor corriendo en {addr}")

    # Correr la tarea de broadcasting en paralelo
    await asyncio.gather(server.serve_forever(), broadcast_pregunta())


# Ejecutar el servidor
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor detenido")

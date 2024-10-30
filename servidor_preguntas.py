import argparse
import socket
import threading
import multiprocessing
import time
import random
import json

# Argumentos configurables por línea de comandos
parser = argparse.ArgumentParser(description="Servidor de preguntas multihilo")
parser.add_argument('--preguntas_por_ronda', type=int, default=2, help="Número de preguntas por ronda")
parser.add_argument('--tiempo_espera', type=int, default=10, help="Tiempo de espera para que los jugadores se conecten")
parser.add_argument('--jugadores', type=int, default=2, help="Número de jugadores en la partida")
args = parser.parse_args()

NUMERO_PREGUNTAS_POR_RONDA = args.preguntas_por_ronda
TIEMPO_ESPERA = args.tiempo_espera
NUM_JUGADORES = args.jugadores

# Cargar preguntas
def cargar_preguntas():
    with open("preguntas_pokemon.json", "r", encoding="utf-8") as file:
        preguntas = json.load(file)
    return preguntas

preguntas = cargar_preguntas()

# Crear una barrera para sincronizar a los jugadores en cada ronda
jugadores_listos = threading.Barrier(NUM_JUGADORES)

def handle_client(conn, addr, preguntas_ronda, puntuaciones, jugadores_listos):
    print(f"Jugador conectado: {addr}")
    puntuaciones[addr] = 0  # Inicializar puntaje

    try:
        for pregunta in preguntas_ronda:
            # Esperar a que todos los jugadores estén listos para la nueva pregunta
            jugadores_listos.wait()

            # Enviar pregunta al cliente
            conn.sendall(pregunta["texto"].encode("utf-8"))
            print(f"Pregunta enviada a {addr}: {pregunta['texto']}")

            # Esperar confirmación de recepción de pregunta
            confirmacion = conn.recv(1024).decode("utf-8").strip()
            if confirmacion != "RECIBIDO":
                print(f"Error al recibir confirmación de {addr}.")
                conn.sendall("ERROR_CONFIRMACION".encode("utf-8"))
                continue

            # Recibir respuesta del cliente
            respuesta = conn.recv(1024).decode("utf-8").strip().upper()
            print(f"Respuesta recibida de {addr}: {respuesta}")

            # Evaluar respuesta y enviar feedback
            if respuesta == pregunta["respuesta_correcta"]:
                puntuaciones[addr] += 1
                conn.sendall("¡Correcto!\n".encode("utf-8"))
            else:
                conn.sendall(f"Incorrecto. La respuesta correcta era: {pregunta['respuesta_correcta']}\n".encode("utf-8"))

        # Esperar a que todos los jugadores terminen de responder todas las preguntas
        jugadores_listos.wait()

        # Enviar mensaje de finalización del juego a cada cliente
        conn.sendall("FIN_JUEGO".encode("utf-8"))

        # Crear y enviar el resumen de puntajes finales
        resultados = "\nResultados finales:\n"
        for jugador, puntaje in puntuaciones.items():
            resultados += f"{jugador[0]}: {puntaje} puntos\n"

        # Determinar el ganador
        max_puntaje = max(puntuaciones.values())
        ganadores = [jugador[0] for jugador, puntaje in puntuaciones.items() if puntaje == max_puntaje]
        if len(ganadores) == 1:
            resultados += f"Ganador: {ganadores[0]} con {max_puntaje} puntos.\n"
        else:
            resultados += f"Empate entre: {', '.join(ganadores)} con {max_puntaje} puntos.\n"

        # Enviar los resultados finales al cliente
        conn.sendall(resultados.encode("utf-8"))

    except (ConnectionResetError, threading.BrokenBarrierError):
        print(f"Jugador desconectado: {addr}")
    finally:
        conn.close()


# Generar preguntas para la ronda actual
def preparar_preguntas():
    preguntas_ronda = random.sample(preguntas, NUMERO_PREGUNTAS_POR_RONDA)
    return [
        {
            "texto": (
                f"{pregunta['pregunta']}\nA) {pregunta['opciones']['A']}\nB) {pregunta['opciones']['B']}\n"
                f"C) {pregunta['opciones']['C']}\nD) {pregunta['opciones']['D']}\n"
            ),
            "respuesta_correcta": pregunta["respuesta_correcta"]
        }
        for pregunta in preguntas_ronda
    ]


# Mostrar puntajes finales en el servidor
def mostrar_puntajes(puntuaciones):
    print("\nPuntajes finales:")
    for addr, puntos in puntuaciones.items():
        print(f"Jugador {addr}: {puntos} puntos")

# Servidor principal
def main():
    manager = multiprocessing.Manager()
    puntuaciones = manager.dict()

    # Crear socket servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8888))
    server_socket.listen()
    print("Servidor iniciado y esperando jugadores...")

    # Generar las preguntas de la ronda
    preguntas_ronda = preparar_preguntas()

    # Esperar tiempo antes de comenzar la ronda para dar tiempo a que los jugadores se conecten
    print(f"Esperando {TIEMPO_ESPERA} segundos antes de comenzar la ronda...")
    time.sleep(TIEMPO_ESPERA)

    # Lista para almacenar hilos de jugadores
    jugadores_threads = []

    # Aceptar conexiones de jugadores y comenzar el juego
    try:
        for _ in range(NUM_JUGADORES):
            conn, addr = server_socket.accept()
            cliente_thread = threading.Thread(target=handle_client, args=(conn, addr, preguntas_ronda, puntuaciones, jugadores_listos))
            cliente_thread.start()
            jugadores_threads.append(cliente_thread)

        # Esperar a que terminen todos los jugadores
        for thread in jugadores_threads:
            thread.join()

    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        mostrar_puntajes(puntuaciones)
        server_socket.close()

if __name__ == "__main__":
    main()

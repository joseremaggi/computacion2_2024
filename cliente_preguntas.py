import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 8888))

    try:
        while True:
            # Esperar la pregunta del servidor
            mensaje = client_socket.recv(1024).decode("utf-8").strip()

            if mensaje == "FIN_JUEGO":
                print("La partida ha terminado. Calculando resultados...")
                break

            # Si el servidor indica error de confirmación, intentamos reenviar la confirmación
            if mensaje == "ERROR_CONFIRMACION":
                client_socket.sendall("RECIBIDO".encode("utf-8"))
                continue

            # Mostrar pregunta y enviar confirmación
            print(mensaje)
            client_socket.sendall("RECIBIDO".encode("utf-8"))

            # Ingresar respuesta y enviarla al servidor
            respuesta = input("Ingresa tu respuesta (A/B/C/D): ").strip().upper()
            client_socket.sendall(respuesta.encode("utf-8"))

            # Recibir retroalimentación (correcto/incorrecto)
            feedback = client_socket.recv(1024).decode("utf-8").strip()
            print(feedback)

        # Recibir y mostrar los resultados finales
        resultados = client_socket.recv(1024).decode("utf-8").strip()
        print(resultados)

    except ConnectionAbortedError:
        print("Conexión cerrada por el servidor.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()

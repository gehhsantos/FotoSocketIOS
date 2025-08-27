import socket, struct, os
from datetime import datetime

SAVE_DIR = "received"
HOST = "0.0.0.0"   # escuta em todas as interfaces
PORT = 5001        # você pode mudar no app

os.makedirs(SAVE_DIR, exist_ok=True)

def recv_all(conn, n):
    """Lê exatamente n bytes do socket."""
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Conexão encerrada antes de receber tudo")
        data += chunk
    return data

def show_image(path):
    """Tenta exibir a imagem (OpenCV -> Pillow -> abre no sistema)."""
    try:
        import cv2
        img = cv2.imread(path)
        if img is None:
            print("Não consegui carregar com OpenCV (cv2).")
            return
        cv2.imshow("Última imagem recebida", img)
        cv2.waitKey(1)  # atualiza a janela
    except Exception:
        try:
            from PIL import Image
            Image.open(path).show()
        except Exception:
            print("Não consegui exibir com OpenCV/Pillow. A imagem foi salva em disco.")

def main():
    print(f"Servidor escutando em {HOST}:{PORT} (Aguardando foto...)")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Conexão de {addr}")
                # 1) lê 4 bytes: tamanho (big-endian)
                header = recv_all(conn, 4)
                (length,) = struct.unpack(">I", header)
                print(f"Tamanho recebido: {length} bytes")

                # 2) lê os bytes da imagem
                img_bytes = recv_all(conn, length)

                # 3) salva com timestamp
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(SAVE_DIR, f"foto_{ts}.jpg")
                with open(path, "wb") as f:
                    f.write(img_bytes)
                print(f"Imagem salva em: {path}")

                # 4) exibe
                show_image(path)

if __name__ == "__main__":
    main()

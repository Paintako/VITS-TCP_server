import socket
import json
import base64
import time
import argparse

SERVER, PORT = '', 9999
END_OF_TRANSMISSION = 'EOT'
class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER, PORT))

    def send(self, token, language, speaker, data):
        data = bytes(token + "@@@" + language + '@@@' + speaker + '@@@'+ data, "utf-8")
        data += END_OF_TRANSMISSION.encode() # END_OF_TRANSMISSION: 'EOT', end of transmission
        self.sock.sendall(data)

    def receive(self, bufsize=8192):
        data = b''
        while True:
            chunk = self.sock.recv(1024)
            if not chunk:
                break
            data += chunk

            # Check if the end of the message was received
            if END_OF_TRANSMISSION.encode() in data: # END_OF_TRANSMISSION: 'EOT', end of transmission
                break
        # Decode data, remove end of transmission character
        data = data.replace(END_OF_TRANSMISSION.encode(), b'') 
        return data

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    text = "你好，我是小明，我是一名大学生。我對中國的歷史很感興趣。真的，嗎?老歌，我喜歡聽。"
    args.add_argument('--language', type=str, default='zh')
    args.add_argument('--speaker', type=str, default='0')
    args.add_argument('--text', type=str, default=text)

    args = args.parse_args()
    client = Client()

    start_time = time.time()
    client.send('token', args.language, args.speaker, args.text)
    result = client.receive()
    if not result:
        print('No result')
    else:
        response_data = json.loads(result.decode("utf-8"))
        print(response_data['status'])
        if response_data.get("status", False):  
            result_file_data = base64.b64decode(response_data.get("bytes", ""))
            with open(f"output.wav", 'wb') as f:
                f.write(result_file_data)
            print("File received complete")

    print('Inference time: {}'.format(time.time() - start_time))
import socket
import threading
import json
import time
import base64
import soundfile as sf
from verify_token import verify_token
import socketserver
import struct

from infer import synthesis
from logs import service_logger

from vits import models, utils, commons
from Frontend.phonemes import symbols

# Define server address and port
SERVER_HOST = ''
SERVER_PORT = 9999
END_OF_TRANSMISSION = 'EOT'
logger = service_logger.ServiceLogger()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.request.recv(n-len(data))
            if not packet:
                return None
            if END_OF_TRANSMISSION.encode() in packet:
                data += packet
                break
            data += packet

        return data

    def handle(self):
        try:
            self.msgs = {"ipaddr":self.client_address[0]}
            print("Client connected with ip address: {}".format(self.client_address[0]))
            msglen = self.recvall(1024)
            if not msglen:
                return
            
            data = msglen.replace(END_OF_TRANSMISSION.encode(), b'')
            print(data)
            id, token, language, speaker, data = data.split(b'@@@')
            id = id.decode('UTF-8')
            data = data.decode("UTF-8")
            speaker = speaker.decode('UTF-8')
            language = language.decode('UTF-8')
            ## verify token
            token_valid, token_msg = verify_token(token, int(id))
            if token_valid:
                lock.acquire()
                status, audio = synthesis(language, data, speaker, NET_G, HPS)
                if status != True:
                    exception_msg = "Exception occurred during synthesis."
                    result_data = {"status": False, "message": exception_msg}
                    result_json = json.dumps(result_data)
                    result_bytes = bytes(result_json, "utf-8")
                    lock.release()
                    self.request.sendall(result_bytes)
                    return
                else:
                    result_file_data = b""
                    with open('test.wav', 'rb') as f:
                        result_file_data = f.read()

                    result_data = {"status": True, "bytes": base64.b64encode(result_file_data).decode("utf-8")}
                    result_json = json.dumps(result_data)
                    result_bytes = bytes(result_json, "utf-8")

                    lock.release()
                    self.request.sendall(result_bytes)

            # token verification failed
            else: 
                self.request.sendall(b"Token verification failed!")
                lock.release()
        except Exception as e:
            logger.error('Error: {}'.format(e))
            result_data = {"status": True, "Message": "Exception occurred during synthesis."}
            result_json = json.dumps(result_data)
            result_bytes = bytes(result_json, "utf-8")
            lock.release()
            self.request.sendall(result_bytes)
        
        finally:
            if not lock.locked():
                lock.release()
            self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    lock = threading.Lock()
    # Before starting the server, load the model
    HPS = utils.get_hparams_from_file("./vits/configs/mix_5.json")
    NET_G = models.SynthesizerTrn(
        len(symbols.symbols),
        HPS.data.filter_length // 2 + 1,
        HPS.train.segment_size // HPS.data.hop_length,
        n_speakers=HPS.data.n_speakers,
        **HPS.model).cuda()
    _ = NET_G.eval()

    _ = utils.load_checkpoint("./vits/logs/mix_5_300_zh/G_550000.pth", NET_G, None)

    server = ThreadedTCPServer((SERVER_HOST, SERVER_PORT), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Server loop running in thread: {}".format(server_thread.name))
    server.serve_forever()

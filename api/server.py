import threading
import json
import time
import base64
import soundfile as sf
from verify_token import verify_token
import socketserver
import argparse
import torch
import gc

from infer import synthesis
from logs.service_logger import service_logger

from vits import models, utils
from Frontend.phonemes import symbols

# Define server address and port
SERVER_HOST = ''

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=9999, help="Port number")
args = parser.parse_args()
SERVER_PORT = args.port


END_OF_TRANSMISSION = 'EOT'
FLAG = 0
NET_G = None

logger = service_logger()

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
        global FLAG
        global NET_G
        try:
            start_time = time.time()

            self.msgs = {"ipaddr":self.client_address[0]}
            msglen = self.recvall(1024)
            if not msglen:
                return
            
            data = msglen.replace(END_OF_TRANSMISSION.encode(), b'')
            id, token, language, speaker, data = data.split(b'@@@')
            id = id.decode('UTF-8')
            data = data.decode("UTF-8")
            speaker = speaker.decode('UTF-8')
            language = language.decode('UTF-8')

            logger.info('ID: {}'.format(id), extra={"ipaddr":""})
            logger.info('DATA: {}'.format(data), extra={"ipaddr":""})
            logger.info('SPEAKER: {}'.format(speaker), extra={"ipaddr":""})
            logger.info('LANGUAGE: {}'.format(language), extra={"ipaddr":""})
            logger.info('TOKEN: {}'.format(token), extra={"ipaddr":""})

            language_list = ['zh', 'tw', 'ha', 'en', 'id', 'mix']
            if language not in language_list:
                result_data = {"status": False, "message": "Invalid language!"}
                self.request.sendall(bytes(json.dumps(result_data), "utf-8"))
                logger.info(f"User input wrong language: {language}", extra={"ipaddr":""})
                return
            
            speaker_list = [str(i) for i in range(0, 4816)]
            speaker_list.append('P_M_005')
            speaker_list.append('M04')
            speaker_list.append('M90')
            speaker_list.append('M95')

            if speaker not in speaker_list:
                result_data = {"status": False, "message": "Invalid speaker!"}
                self.request.sendall(bytes(json.dumps(result_data), "utf-8"))
                logger.info(f"User input wrong speaker: {speaker}", extra={"ipaddr":""})
                return

            if language == 'tw_ctl':
                language = 'tw_tl'

            ssml_list = ['zh', 'tw', 'ha', 'id']

            if language != 'mix':
                for ssml in ssml_list:
                    ssml_tag = '<' + ssml + '>'
                    if ssml_tag in data:
                        language = 'mix'
                        result_data = {"status": False, "message": "Must select mix language!"}
                        self.request.sendall(bytes(json.dumps(result_data), "utf-8"))
                        logger.info("User input wrong language", extra={"ipaddr":""})
                        return
            
            if speaker == 'M04' or speaker == 'M90' or speaker == 'M95' or speaker == 'P_M_005':
                NET_G.to('cpu')
                del NET_G
                torch.cuda.empty_cache()
                gc.collect()

                NET_G = models.SynthesizerTrn(
                    len(symbols.symbols),
                    HPS.data.filter_length // 2 + 1,
                    HPS.train.segment_size // HPS.data.hop_length,
                    n_speakers=HPS.data.n_speakers,
                    **HPS.model).cuda()
                _ = NET_G.eval()
                NET_G, _, _, _ = utils.load_checkpoint(f"./vits/logs/finetune/{speaker}.pth", NET_G, None)
                FLAG = 1
                
            else:
                if FLAG == 1 and speaker not in ['M04', 'M90', 'M95', 'P_M_005']:
                    reload_model_t = time.time()
                    if 'NET_G' in globals():
                        NET_G.to('cpu')
                        del NET_G
                        torch.cuda.empty_cache()
                        gc.collect()
                    NET_G = models.SynthesizerTrn(
                        len(symbols.symbols),
                        HPS.data.filter_length // 2 + 1,
                        HPS.train.segment_size // HPS.data.hop_length,
                        n_speakers=HPS.data.n_speakers,
                        **HPS.model).cuda()
                    _ = NET_G.eval()
                    NET_G, _, _, _ = utils.load_checkpoint("./vits/logs/mix_5_300_zh/G_550000.pth", NET_G, None)
                    FLAG = 0
                    logger.info(f'Load model, spend: {time.time() - reload_model_t}', extra={"ipaddr":""})
                
            if speaker == 'M04' or speaker == 'M90' or speaker == 'M95' or speaker == 'P_M_005':
                if speaker == 'P_M_005':
                    speaker = 4812
                else:
                    speaker = 0
                logger.info(f"Load finetuned model: /vits/logs/finetune/{speaker}.pth", extra={"ipaddr":""})

            ## verify token
            # token_valid, token_msg = verify_token(token, int(id))
            token_valid = True  # for testing
            if not token_valid:
                # logger.error('Token verification failed: {}'.format(token_msg), extra={"ipaddr":""})
                result_data = {"status": False, "message": "Token verification failed!"}
                self.request.sendall(bytes(json.dumps(result_data), "utf-8"))
                return

            if token_valid:
                status, audio = synthesis(language, data, speaker, NET_G, HPS)
                if status != True:
                    exception_msg = "Exception occurred during synthesis."
                    result_data = {"status": False, "message": exception_msg}
                    result_json = json.dumps(result_data)
                    result_bytes = bytes(result_json, "utf-8")
                    if lock.locked():
                        lock.release()
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
                    if lock.locked():
                        lock.release()
                    self.request.sendall(result_bytes)

                    end_time = time.time()
                    logger.info('Total words: {}, Time taken: {}'.format(len(data), end_time - start_time), extra={"ipaddr":""})
                    
                    self.request.close()

            # token verification failed
            else: 
                self.request.sendall(b"Token verification failed!")
                lock.release()
        except Exception as e:
            logger.error('Error: {}'.format(e), extra={"ipaddr":""}, exc_info=True)
            result_data = {"status": True, "Message": "Exception occurred during synthesis."}
            result_json = json.dumps(result_data)
            result_bytes = bytes(result_json, "utf-8")
            if lock.locked():
                lock.release()
            self.request.sendall(result_bytes)
        
        finally:
            if lock.locked():
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
    server.serve_forever()

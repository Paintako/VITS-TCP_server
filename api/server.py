import socket
import threading
import torch
import numpy as np
import json
import time
import base64
import soundfile as sf

from logs import service_logger
from Frontend import frontend_manager

from vits import models, utils, commons
from Frontend.phonemes import symbols

# Define server address and port
SERVER_HOST = ''
SERVER_PORT = 9999
END_OF_TRANSMISSION = 'EOT'

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

# Handle client connections
def request_handler(client_socket, addr):
    start_time = time.time()
    fm = frontend_manager.frontend_manager()
    logger.info('New client connected: {}'.format(addr))

    # Receive data from client, using a buffer size of 1024 bytes
    data = b''
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        data += chunk

        # Check if the end of the message was received
        if END_OF_TRANSMISSION.encode() in data: # END_OF_TRANSMISSION: 'EOT', end of transmission
            break

    # Decode data, remove end of transmission character
    data = data.replace(END_OF_TRANSMISSION.encode(), b'') 
    token, language, speaker, data = data.split(b'@@@')
    speaker = speaker.decode('UTF-8')
    language = language.decode('UTF-8')
    data = data.decode("UTF-8")

    logger.info('Token: {}'.format(token))
    logger.info('Data: {}'.format(data))
    logger.info('Speaker: {}'.format(speaker))
    logger.info('Language: {}'.format(language))

    # Process data
    fm.set_frontend(language)

    # Segmentaion
    data = data.replace(',', '')
    phonemes = fm.get_phonemes(data)
    if len(phonemes) == 0:
        logger.error('No phonemes found')
        return
    
    id_s = []
    for i in range(len(phonemes)):
        phoneme_ids = fm.phonemes_to_id(phonemes[i])
        if phoneme_ids == [0]:
            continue
        id_s.append(phoneme_ids)
    print(id_s)
    print(len(id_s))
    # Synthesis process
    inference_audio = inference(id_s, speaker)
    logger.info('Inference time: {}'.format(time.time() - start_time))
    
    # Save audio to file
    sf.write('test.wav', inference_audio, 16000, 'PCM_16')

    # read audio file
    with open('test.wav', 'rb') as f:
        inference_audio = f.read()

    # Send data back to client
    result_data = {"status": True, "bytes": base64.b64encode(inference_audio).decode("utf-8")}
    result_json = json.dumps(result_data)
    result_bytes = bytes(result_json, "utf-8")

    try:
        client_socket.sendall(result_bytes + END_OF_TRANSMISSION.encode())
    except socket.error as e:
        logger.error('Send failed: {}'.format(e))
    return

def inference_worker(phoneme_ids):
    pass
    
def inference(phoneme_ids,  speaker_id):
    result_np_arr = []
    theads = []
    for id in phoneme_ids:
        text_norm = commons.intersperse(id, 0)
        text_norm = torch.LongTensor(text_norm)
        with torch.no_grad():
            x_tst = text_norm.cuda().unsqueeze(0)
            x_tst_lengths = torch.LongTensor([text_norm.size(0)]).cuda()
            sid = torch.LongTensor([int(speaker_id)]).cuda()
            audio = NET_G.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=0, noise_scale_w=0, length_scale=1)[0][0,0].data.cpu().float().numpy()
            result_np_arr.append(audio)
    concatenated_audio = np.concatenate(result_np_arr)
    return concatenated_audio

def start_server():
    # Create socket for server to listen on
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(15) 
    except socket.error as e:
        logger.error('Bind failed: {}'.format(e))
        return
    threads = []
    logger.info('Server started')
    server_socket.settimeout(1) 
    try:
        while True:
            try:
                # Accept connections, can handle multiple clients by creating a new thread for each client
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=request_handler, args=(conn, addr))
                thread.start()
                threads.append(thread)
                thread.join()

            except socket.timeout:
                pass

    except KeyboardInterrupt:
        print("Shutting down...")
        server_socket.close() 
        for thread in threads:
            thread.join()
        logger.info('Server shutdown')


if __name__ == '__main__':
    logger = service_logger.ServiceLogger()
    start_server()
    

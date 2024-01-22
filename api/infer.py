from logs import service_logger
from Frontend import frontend_manager

from vits import commons
import torch
import numpy as np
import json
import soundfile as sf

# Define server address and port
SERVER_HOST = ''
SERVER_PORT = 9999
END_OF_TRANSMISSION = 'EOT'

logger = service_logger.ServiceLogger()


def synthesis(language, data, speaker, NET_G, HPS):
    try:
        fm = frontend_manager.frontend_manager()
        fm.set_frontend(language)

        data = data.replace(',', '')
        phonemes, status = fm.get_phonemes(data)
        if not status or len(phonemes) == 0:
            logger.error('Error transforming: {}'.format(data))
            return False, None

        id_s = []
        for i in range(len(phonemes)):
            phoneme_ids = fm.phonemes_to_id(phonemes[i])
            if phoneme_ids == [0]:
                continue
            id_s.append(phoneme_ids)

        # Synthesis process
        inference_audio = inference(id_s, speaker, NET_G, HPS)
        sf.write('test.wav', inference_audio, 16000, 'PCM_16')
        
    except Exception as e:
        logger.error('Error: {}'.format(e))
        return False, e
    return True, None


def inference(phoneme_ids,  speaker_id, NET_G, HPS):
    result_np_arr = []
    for id in phoneme_ids:
        text_norm = commons.intersperse(id, 0)
        text_norm = torch.LongTensor(text_norm)
        with torch.no_grad():
            x_tst = text_norm.cuda().unsqueeze(0)
            x_tst_lengths = torch.LongTensor([text_norm.size(0)]).cuda()
            sid = torch.LongTensor([int(speaker_id)]).cuda()
            audio = NET_G.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=0, noise_scale_w=0, length_scale=1.3)[0][0,0].data.cpu().float().numpy()
            result_np_arr.append(audio)
    concatenated_audio = np.concatenate(result_np_arr)
    return concatenated_audio
from logs.service_logger import service_logger
from Frontend import frontend_manager

from vits import commons
import torch
import numpy as np
import soundfile as sf
import time

# Define server address and port
SERVER_HOST = ''
SERVER_PORT = 9999
END_OF_TRANSMISSION = 'EOT'

logger = service_logger()


def synthesis(language, data, speaker, NET_G, HPS):
    try:
        fm = frontend_manager.frontend_manager()
        fm.set_frontend(language)
        front_time = time.time()
        phonemes, status = fm.get_phonemes(data)
        logger.info('Frontend time: {}'.format(time.time() - front_time), extra={"ipaddr":""})
        print(f'data: {data}')
        if not status or len(phonemes) == 0:
            logger.error('Error: {}'.format('Phonemes not found'), extra={"ipaddr":""})
            return False, None

        id_s = []
        print(phonemes)
        for i in range(len(phonemes)):
            phoneme_ids = fm.phonemes_to_id(phonemes[i])
            if phoneme_ids == [0]:
                continue
            id_s.append(phoneme_ids)

        # Synthesis process
        infer_time = time.time()
        inference_audio = inference(id_s, speaker, NET_G, HPS)
        if inference_audio is None:
            logger.error('Error: {}'.format('Inference failed'), extra={"ipaddr":""})
            return False, None
        logger.info('Inference time: {}'.format(time.time() - infer_time), extra={"ipaddr":""})
        sf.write('test.wav', inference_audio, 16000, 'PCM_16')
        
    except Exception as e:
        logger.error('Error: {}'.format(str(e)), extra={"ipaddr":""}, exc_info=True)
        return False, e
    return True, None

'''
<option value="4794">趙少康</option>
<option value="4795">黃偉哲</option>
<option value="4797">郭台銘</option>
<option value="4812">賴清德</option>
<option value="4813">蔡英文</option>
<option value="4784">柯文哲</option>
<option value="4798">盧秀燕</option>
<option value="4779">成大醫院曾醫師</option>
'''


infer_speedDict = {
    '4794' : 1.4,
    '4795' : 1.4,
    '4797' : 1.5,
    '4812'  : 1.3,
    '4813' : 1.0,
    '4784' : 1.5,
    '4798' : 1.3,
    '4779' : 1.3 
}



def inference(phoneme_ids,  speaker_id, NET_G, HPS):
    if str(speaker_id) in infer_speedDict:
        infer_speed = infer_speedDict[str(speaker_id)]
    else:
        infer_speed = 1.0
    result_np_arr = []
    try:
        for id in phoneme_ids:
            text_norm = commons.intersperse(id, 0)
            text_norm = torch.LongTensor(text_norm)
            with torch.no_grad():
                x_tst = text_norm.cuda().unsqueeze(0)
                x_tst_lengths = torch.LongTensor([text_norm.size(0)]).cuda()
                sid = torch.LongTensor([int(speaker_id)]).cuda()
                audio = NET_G.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=0.0, noise_scale_w=0.0, length_scale=infer_speed)[0][0,0].data.cpu().float().numpy()
                result_np_arr.append(audio)
        concatenated_audio = np.concatenate(result_np_arr)
    except Exception as e:
        return None
    return concatenated_audio
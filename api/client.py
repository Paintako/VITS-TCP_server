import socket
import json
import base64
import time
import argparse

"""
    給所有人的說明:
    1. 此程式碼為語音合成的 client 端，支援五種語言 (國、台、客語、英語、印尼語)
    2. 共有三個參數可以輸入，分別為語言(language)、語者(speaker)、文字(text)
    3. 具體使用可以參考以下範例
        python client.py --language zh --speaker 4813 --text "你好啊朋友"
    4. 跨語言合成目前尚未實作完畢
    5. - 國語請在語言參數輸入 zh
       - 台語請在語言參數輸入 tw
       - 客語請在語言參數輸入 hakka
       - 英語請在語言參數輸入 en
       - 印尼語請在語言參數輸入 id
    6. 語者代碼請參考 speaker.json，目前支援最多 4821 位語者
    7. 常用名單如下:
        {
            2775|F01   # 實驗室內部錄音人員
            2792|F06   # 實驗室內部錄音人員
            2794|F14   # 實驗室內部錄音人員
            4777|志淇七七 (youtuber)
            4778|時間的女兒 (podcast)
            4779|成大醫院曾醫師
            4780|聯合報 (UDN)
            4781|林志堅 
            4782|瓜吉 (邱威傑)
            4783|薛瑞元
            4784|柯文哲
            4785|韓國瑜
            4786|侯漢廷
            4787|謝龍介
            4788|鄭文燦
            4789|花藝師吳妮晏 (from youtube video)
            4790|王世堅
            4791|陳水扁
            4792|張豈只 (from youtube video)
            4793|李沅翰 (實驗室內部錄音人員)
            4794|趙少康
            4794|黃偉哲
            4795|MA_M96 (實驗室內部錄音人員)
            4796|M99 (好像是朱立倫)
            4797|P_F_001 (盧秀燕)
            4798|P_M_006 (ㄌㄨㄚˋ 著不拆)
            4799|P_M_019
            4800|P_M_004
            4801|P_M_008
            4802|P_M_024
            4803|M96 (TOYZ)
            4804|P_M_015
            4805|M101 
            4806|P_M_022
            4807|P_M_003
            4808|P_M_002
            4809|P_M_023
            4810|P_M_011
            4811|P_M_005
            4812|F101 (ㄘㄨㄚˋ 英文)
            4813|P_M_001
            4814|P_M_010
            4815|podF04
            4816|podM02
            4817|podF03
            4818|podM03
            4819|podF01_n 
            4820|M95 (戰神黃國昌)
            4821|podF02 
            2794|F14
        }
"""


SERVER, PORT = '140.116.245.147', 9999
END_OF_TRANSMISSION = 'EOT'
class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER, PORT))
        self._token = "mi2stts"
        self._id = str(10012)

    def send(self, language, speaker, data):
        data = bytes(self._id + "@@@" + self._token + "@@@" + language + '@@@' + speaker + '@@@'+ data, "utf-8")
        data += END_OF_TRANSMISSION.encode() # END_OF_TRANSMISSION: 'EOT', end of transmission
        self.sock.sendall(data)

    def receive(self, bufsize=8192):
        data = b''
        while True:
            chunk = self.sock.recv(bufsize)
            if not chunk:
                break
            data += chunk

        return data

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    text = "funny mud pee omg"
    args.add_argument('--language', type=str, default='en')
    args.add_argument('--speaker', type=str, default='2792')
    args.add_argument('--text', type=str, default=text)

    args = args.parse_args()
    client = Client()

    start_time = time.time()
    client.send(args.language, args.speaker, args.text)
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
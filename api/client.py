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
            4795|黃偉哲
            4796|MA_M96 (實驗室內部錄音人員)
            4797|郭台銘
            4798|盧秀燕
            4799|侯友宜
            4800|江啟程
            4802|郭正亮
            4805|陳吉仲
            4806|陳其邁
            4807|侯漢廷
            4808|林佳龍
            4809|蔣萬安
            4810|習近平
            4811|馬英九
            4812|賴清德
            4813|蔡英文
            4814|陳時中
            2794|F14
        }
    8. 政治人物清單:
        {
            4781|林志堅 
            4782|邱威傑
            4783|薛瑞元
            4784|柯文哲
            4785|韓國瑜
            4786|侯漢廷
            4787|謝龍介
            4788|鄭文燦
            4790|王世堅
            4791|陳水扁
            4794|趙少康
            4795|黃偉哲
            4797|郭台銘
            4798|盧秀燕
            4799|侯友宜
            4800|江啟程
            4802|郭正亮
            4805|陳吉仲
            4806|陳其邁
            4807|侯漢廷
            4808|林佳龍
            4809|蔣萬安
            4810|習近平
            4811|馬英九
            4812|賴清德
            4813|蔡英文
            4814|陳時中
        }
"""


SERVER, PORT = '140.116.245.147', 9999
END_OF_TRANSMISSION = 'EOT'
FINETUNE_LIST = ["P_M_005", "M95", "M04"]
class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER, PORT))
        self._token = "mi2stts"
        self._id = str(10012)

    def send(self, language, speaker, data):
        # check speaker id is valid
        if speaker not in [str(i) for i in range(0, 4817)] and speaker not in FINETUNE_LIST:
            raise ValueError("Speaker id must be in range 0 ~ 4815 or in FINETUNE_LIST")
        
        if data == "":
            raise ValueError("Text must be not empty")

        if language not in ['zh', 'tw', 'hakka', 'en', 'id', 'mix']:
            raise ValueError("Language must be one of ['zh', 'tw', 'hakka', 'en', 'id']")

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
    args.add_argument('--language', type=str, default='mix')
    args.add_argument('--speaker', type=str, default='4588')
    args.add_argument('--text', type=str, default="")

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
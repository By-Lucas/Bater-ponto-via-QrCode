from cmath import inf
import cv2
import numpy as np
import requests
import cvzone
from pyzbar.pyzbar import decode
import json
import time
import typing
import datetime
import sys





class PontoQrCode:

    def __init__(self, arquivo='myDataFile.txt') -> None:
        self._base_url = "http://127.0.0.1:5000"

        self.arquivo = arquivo

        self._headers = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json" 
        }


    def _make_request(self, method: str, endpoints: str, data: typing.Dict or str):

        if method == "GET":
            try:
                response = requests.get(self._base_url + endpoints, params=data, headers=self._headers)
            except Exception as e:
                print(f'Erro de conexão ao fazer {method} request para {endpoints}: {e}')
                return None

        elif method == "POST":
            try:
                response = requests.post(self._base_url + endpoints, params=data, headers=self._headers)
            except Exception as e:
                print(f'Erro de conexão ao fazer {method} request para {endpoints}: {e}')
                return None

        elif method == "DELETE":
            try:
                response = requests.delete(self._base_url + endpoints, params=data, headers=self._headers)
            except Exception as e:
                print(f'Erro de conexão ao fazer {method} request para {endpoints}: {e}')
                return None

        else:
            ValueError()
        
        if response.status_code == 200:
            return response
        
        if response.status_code == 201:
            return response
        
        if response.status_code == 204:
            return response

        else:
            print(f"Erro ao fazer {method} para {endpoints} : {response.json()} (Código de erro: {response.status_code})")
            
            return None


    def users_id(self):
        self.response = requests.get('http://127.0.0.1:5000/transacoes')
        if self.response.status_code == 200:
            list_ids = []
            for ids in self.response.json():
                _ids = f"{ids['id']}"
                list_ids.append(_ids)
            return list_ids


    def detalhes_user(self, id: int):
        self.response = requests.get(f'http://127.0.0.1:5000/transacao/{id}')
        if self.response.status_code == 200:
            for user in self.response.json():
                return user


    def teste(self):
        data = dict()

        data['id'] = '4492334701741215163665753229922'
        data['name'] = 'Lucas Silva'
        data['phone'] = '74981199190'
        return data


    def bater_ponto(self, title: str, info:str):
        hora_atual = datetime.datetime.now()
        
        data = dict()
        data['title'] = title
        data['log'] = f'{hora_atual} :: {info}'

        response = self._make_request('POST', '/logs/', data)

        if response.status_code == 201:
            print('Ponto batido com sucesso!')
        else:
            print('Erro ao bater ponto')
        return response


    def fancyDraw(self, img, bbox, l=30, t=5, rt= 1):
        x, y, w, h = bbox
        x1, y1 = x + w, y + h

        cv2.rectangle(img, bbox, (255, 0, 255), rt)
        # Top Left  x,y
        cv2.line(img, (x, y), (x + l, y), (255, 0, 255), t)
        cv2.line(img, (x, y), (x, y+l), (255, 0, 255), t)
        # Top Right  x1,y
        cv2.line(img, (x1, y), (x1 - l, y), (255, 0, 255), t)
        cv2.line(img, (x1, y), (x1, y+l), (255, 0, 255), t)
        # Bottom Left  x,y1
        cv2.line(img, (x, y1), (x + l, y1), (255, 0, 255), t)
        cv2.line(img, (x, y1), (x, y1 - l), (255, 0, 255), t)
        # Bottom Right  x1,y1
        cv2.line(img, (x1, y1), (x1 - l, y1), (255, 0, 255), t)
        cv2.line(img, (x1, y1), (x1, y1 - l), (255, 0, 255), t)
        return img


    def video_qrcode(self, video):
        with open(self.arquivo) as f:
            myDataList = f.read().splitlines()

        pTime = 0
        limit_count = 0
        user_active = False

        while True:
            success, img = video.read()
            for barcode in decode(img):
                myData = barcode.data.decode('utf-8')

                if myData in self.teste()['id'] :
                    myColor = (0,255,0)
                    myOutput = f"{self.teste()['name']}"

                    user_active =  True
                    limit_count += 1

                else:
                    myOutput = 'Usuario nao autorizado'
                    myColor = (255, 0, 255)

                ih, iw, ic = img.shape
                
                pts = np.array([barcode.polygon],np.int32)
                pts = pts.reshape((-1,1,2))
                #cv2.polylines(img,[pts],True,myColor,5)
                pts2 = barcode.rect

                cTime = time.time()
                fps = 1 / (cTime - pTime)
                pTime = cTime

                bbox = int(pts2[0]), int(pts2[1]), \
                       int(pts2[2]), int(pts2[3])
                
                img = self.fancyDraw(img, bbox)
                cv2.putText(img, f'{myOutput}', (bbox[0]-25, bbox[1]-20), cv2.FONT_HERSHEY_PLAIN, 2, myColor, 2)
                cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            
            if user_active == True and limit_count >= 30:
                img = cv2.imread("registrado.webp")
                cv2.putText(img, str(f'Concluido!').zfill(2), (75, 225), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
 
                #_bater_ponto = self.bater_ponto(myData, info_user['wallet'])
                    #if _bater_ponto.status_code == 201:
                    #    cv2.putText(img, f'Ponto batido com sucesso', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)


            cv2.imshow('TK Global Technology',img)
            key = cv2.waitKey(1)

            if key == 27: # ESC
                cv2.imwrite(f"users/{self.teste()['name']}.png", img)
                break
            
            


    def main(self):
        #img = cv2.imread('1.png')
        video = cv2.VideoCapture(0)
        video.set(3,640)
        video.set(4,480)
        video_qr = self.video_qrcode(video)


if __name__ == '__main__':
    qr = PontoQrCode()
    qr.main()
import qrcode
import os
from PIL import Image


def make_qrcode(content, file_path):
    file_path_tmp = file_path + '__.png'
    q = qrcode.main.QRCode()
    q.add_data(content)
    q.make()
    m = q.make_image()
    m.save(file_path_tmp)
    im = Image.open(file_path_tmp)
    im.save(file_path)
    os.remove(file_path_tmp)


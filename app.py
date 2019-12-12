#encoding=utf8
import urlparse,urllib2
import functools
import json
def get_deco(func):
    @functools.wraps(func)
    def inner(env,start_response,header):
        if env.get('REQUEST_METHOD') != 'GET':
            start_response('405',header)
            return '405 Method not allowed'
        qs = env.get('QUERY_STRING',None)
        if not qs:
            start_response('400', header)
            return 'need params'
        q = urlparse.parse_qs(qs)
        qsd = {}
        for k,v in q.items():
            qsd[k] = v[0]
        ret = func(env,start_response,header,qsd=qsd)
        return ret
    return inner


def index(env, start_response,header,qsd=None,rbd=None):
    start_response('200 OK',header)
    return '200 OK'

def __check_rbd(l,qsd):
    for i in l:
        if i not in qsd:
            return False,'need params'
    return True,None

import os,sys
CUR_PATH = os.path.abspath(__file__)
CUR_DIR = os.path.dirname(CUR_PATH)
F_DIR = os.path.join(CUR_DIR,'../sceneTextDetect')
print CUR_PATH,CUR_DIR,F_DIR
sys.path.append(F_DIR)
from ctpnport import *
from crnnport import *
import time

#ctpn
text_detector = ctpnSource()
#crnn
model,converter = crnnSource()
import cv2
import numpy as np
@get_deco
def sceneTextDetect(env, start_response,header,qsd=None,rbd=None):
    ok, js = __check_rbd(('img_url', ), qsd)
    if not ok:
        start_response('400', header)
        return js
    url = qsd.get('img_url')
    if not url:
        start_response('400', header)
        return json.dumps({'success':False,  'msg':'invalid url'})
    st = time.time()
    try:
        imgc = urllib2.urlopen(url,timeout=5).read()
        download_time = time.time()-st
    except:
        start_response('500', header)
        return json.dumps({'success':False,  'msg':'err in get img'})
    st1 = time.time()
    try:
        arr = np.asarray(bytearray(imgc), dtype=np.uint8)
        cvimg = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        conv_time = time.time()-st1
    except:
        start_response('500', header)
        return json.dumps({'success':False,  'msg':'err in conv img'})

    st2 = time.time()
    img,text_recs,_ = getCharBlock(text_detector,cvimg)
    ctpn_time = time.time()-st2
    st3 = time.time()
    text_res = crnnRec(model,converter,img,text_recs)
    crnn_time = time.time()-st3
    t_time = time.time() -  st
    start_response('200', header)
    return json.dumps({'success':True, 'text':'\n'.join(text_res), 'timeCost' :{
        "download_time":download_time,
        "convert_time":conv_time,
        "ctpn_time":ctpn_time, "crnn_time":crnn_time,
        "total_time":t_time
    }})














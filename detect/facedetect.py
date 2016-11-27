#!/usr/bin/env python
#coding=utf-8
import os,sys
import numpy as np
import cv2
import cv2.cv as cv
from common import clock

def read_images(paths,label, sz=None):
    c = 0
    X,y = [], []
    for path in paths:
        try:
            im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            # resize to given size (if given)
            if sz is not None:
                im = cv2.resize(im, sz)
            X.append(np.asarray(im, dtype=np.uint8))
            y.append(label)
        except IOError, (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
    c = c+1
    return X, y


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
def normalize(X, low, high, dtype=None):
    """Normalizes a given array in X to a value between low and high."""
    X = np.asarray(X)
    minX, maxX = np.min(X), np.max(X)
    # normalize to [0...1].
    X = X - float(minX)
    X = X / float((maxX - minX))
    # scale to [low...high].
    X = X * (high-low)
    X = X + low
    if dtype is None:
        return np.asarray(X)
    return np.asarray(X, dtype=dtype)


class detector:
    def __init__(self):
        cascade_fn = "/home/miller/PycharmProjects/facedetect/detect/data/haarcascades/haarcascade_frontalface_alt.xml"
        self.cascade = cv2.CascadeClassifier(cascade_fn)
        self.model = cv2.createLBPHFaceRecognizer()
        self.face_model_path = None

    def load_model(self, face_model_path, size=0):
        self.face_model_path = face_model_path
        if os.path.exists(face_model_path) and size > 0:
            self.model.load(face_model_path)
        else:
            self.model.save(face_model_path)

    def clear_model(self, face_model_path):
        self.face_model_path = face_model_path
        self.model.save(face_model_path)


    def detect(self, rimg, update=False):
        nparr = np.fromstring(rimg, np.uint8)
        img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        t = clock()
        rects = detect(gray, self.cascade)
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))
        sub_vis_faces = []
        for x1, y1, x2, y2 in rects:
            roi = gray[y1:y2, x1:x2]
            vis_roi = img[y1:y2, x1:x2]
            if update:
                sub_vis_faces.append(cv2.imencode('.jpg', vis_roi)[1])
            else:
                #sub_faces.append(cv2.imencode('.jpg',roi)[1])
                [label, confident] = self.model.predict(roi)
                # name = self.user.get_username(userId=label)
                # draw_str(vis, (x1, y1), 'id: %s' %(label))
                # draw_str(vis, (x1, y1+20), 'name:%s' %(name))
                # draw_str(vis, (x1, y1+40), 'condifdent:%d' %(confident))
                sub_vis_faces.append({'face':cv2.imencode('.jpg', vis_roi)[1], 'label':label,
                                      'confident':confident, 'time':clock() - t})
        if update:
            return cv2.imencode('.jpg', vis)[1], sub_vis_faces
        else:
            return cv2.imencode('.jpg', vis)[1], sub_vis_faces


    def update(self, face_set, label):
        if self.face_model_path is None:
            return False
        X,y = read_images(face_set, label=label)
        y = np.asarray(y, dtype=np.int32)
        self.model.update(np.asarray(X), np.asarray(y))
        self.model.save(self.face_model_path)
        return True
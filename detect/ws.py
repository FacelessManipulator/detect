#coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.websocket
import time
from taskpool import FacedetectPool
import json


class BaseSocketHandler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        detector.detect(message,self)

    def on_close(self):
        print 'closed'

class recognizeSocketHandler(BaseSocketHandler):
    def on_message(self, message):
        detector.recognize(message,self)

class updateSocketHandler(BaseSocketHandler):

    def open(self):
        self.faces = []
        self.name = None
        self.count = 0

    def on_message(self, message):
        if self.name is None:
            try:
                data = json.loads(message)
                self.name = data['name']
                print self.name
            except:
                self.write_message(json.dumps({'error':"name is not defined"}))
        else:
            face = detector.detect(message,ws=self,update=True)
            if face is not None:
                self.faces.append(face)
                self.count += 1
                if self.count >= 10:
                    self.close(code=201)

    def on_close(self):
        if self.count >= 10:
            detector.update(self.faces,self.name)
            print 'user add %s'%(self.name)

class index(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
if __name__ == '__main__':
    detector = FacedetectPool()
    app = tornado.web.Application([
    (r'/',index),
    (r'/detect',BaseSocketHandler),
    (r'/recognize',recognizeSocketHandler),
    (r'/update',updateSocketHandler),
    (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'js/'}),
    (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'css/'}),
    ])
    app.listen(8005)
    tornado.ioloop.IOLoop.instance().start()

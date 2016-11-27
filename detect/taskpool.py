from multiprocessing import Process
from facedetect import detector
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from models import TrainedModel

class FacedetectPool:

    def __init__(self, face_model=None):
        self.detector = detector()

    def void(self):
        pass

    def run(self, function, obj, opt=None):
        if function == 'detect':
            _function = self.detect
        elif function == 'recognize':
            _function = self.recognize
        elif function == 'update':
            _function = self.update
        else:
            return False
        self.process = Process(target=_function, args=(obj, opt))
        self.process.start()
        self.process.join()
        return True

    def detect(self, img, opt):
        update = opt.get('update', False)
        newimg, subfaces = self.detector.detect(img, update=update)

        if update and len(subfaces) > 0:
            try:
                user = User.objects.get(username=opt.get('username', 'null'))
                f = user.userBaseInfo.faces.create()
                f.image.save('trained.jpg', ContentFile(subfaces[0].tostring()), save=True)
                f.save()
                # self.detector.update(subfaces, user.username)
            except Exception,e:
                return False
        else:
            self.report = opt.get('report')
            if self.report is None:
                return False
            else:
                self.report.result_image = ContentFile(newimg.tostring())
                for face in subfaces:
                    try:
                        user = User.objects.get(username=face.get('label','null'))
                        f = self.report.faces.create(user=user,
                                                 time=face.get('time','-1'))
                        f.image.save('trained.jpg', ContentFile(face.get('face','').tostring()), save=True)
                        self.report.save()
                    except Exception,e:
                        continue
                return True

    def recognize(self, report, opt=None):
        try:
            size = report.exp.trained.face_model.size
            path = report.exp.trained.face_model.path
        except ObjectDoesNotExist,e:
            trained = TrainedModel.objects.create(exp=report.exp)
            trained.face_model.save('model.xml', ContentFile(""), save=True)
            path = trained.face_model.path
            size = report.exp.trained.face_model.size
        self.detector.load_model(path, size)
        report.status = 'recognizing'
        report.save()
        image = report.origin_image.read()
        newimg, subfaces = self.detector.detect(image)
        report.result_image.save('trained.jpg', ContentFile(newimg.tostring()), save=True)
        for face in subfaces:
            try:
                user = User.objects.get(username=face.get('label','null')).userBaseInfo
                f = report.faces.create(user=user, confident=face.get('confident', '0'), recg_time=face.get('time','-1'))
                f.image.save('trained.jpg',ContentFile(face.get('face','').tostring()), save=True)
                report.save()
            except Exception,e:
                continue
        report.status = 'recognized'
        report.save()

    def update(self, exp, opt=None):
        try:
            size = exp.trained.face_model.size
            path = exp.trained.face_model.path
        except ObjectDoesNotExist,e:
            trained = TrainedModel.objects.create(exp=exp)
            trained.face_model.save('model.xml', ContentFile(""), save=True)
            path = trained.face_model.path
            size = exp.trained.face_model.size
        self.detector.clear_model(path)
        exp.trained.status = 'training'
        exp.trained.save()
        for user in exp.user.all():
            try:
                if user.faces.count() > 0:
                    self.detector.update([face.image.path for face in user.faces.filter(report=None)], user.user.username)
            except Exception,e:
                continue
        exp.trained.status = 'trained'
        exp.trained.save()
        '''
        s = int(time.time())
        os.mkdir("./faces/"+str(s))
        counter = 0
        for face in faces:
            with open('./faces/'+str(s)+'/'+str(counter)+'.jpg','wb') as img:
                img.write(cv2.imencode('.jpg',face)[1].tostring())
            counter+=1
        '''
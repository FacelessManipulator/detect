from __future__ import unicode_literals

from django.db import models
from django.utils.crypto import get_random_string

# Create your models here.


def _face_upload_path_(instance, filename):
    return r'user/' + instance.user.user.username + r'/' + get_random_string() + '.' + filename.split('.')[-1]

def _exp_upload_path_(instance, filename):
    return r'user/' + str(instance.exp_id) + r'/' + get_random_string() + '.' + filename.split('.')[-1]

def _model_upload_path_(instance, filename):
    return r'experiment/' + str(instance.exp_id) + r'/' + filename


class FaceData(models.Model):
    user = models.ForeignKey('usersystem.UserBaseInfo', related_name='faces', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=_face_upload_path_)
    log_time = models.DateTimeField(auto_now_add=True)
    report = models.ForeignKey('FaceDetectReport', related_name='faces', on_delete=models.CASCADE, null=True, blank=True)
    recg_time = models.CharField(max_length=64, default=0)
    confident = models.CharField(max_length=64, default=0)

    def get_dict(self):
        return {
            'fid': self.id,
            'path': self.image.url if self.image.name != '' is not None else '',
            'log_time': str(self.log_time),
            'recg_time': self.recg_time ,
            'confident': self.confident,
            'name': self.user.name,
        }

class FaceDetectReport(models.Model):
    exp = models.ForeignKey('experiment.Experiment', related_name='analysis', on_delete=models.CASCADE)
    origin_image = models.ImageField(upload_to=_exp_upload_path_)
    result_image = models.ImageField(upload_to=_exp_upload_path_, null=True)
    time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, default='recognizing')
    def get_dict(self, simple=True):
        dic = {
            'frid': self.id,
            'origin_path': self.origin_image.url if self.origin_image.name != '' else '',
            'result_path': self.result_image.url if self.result_image.name != '' else '',
            'time': str(self.time),
            'status': self.status,
        }
        if not simple:
            dic['faces'] = [face.get_dict() for face in self.faces.all()]
            dic['unrecognized'] = list(set([user.name for user in self.exp.user.filter(group='student')]) - set([face.user.name for face in self.faces.all()]))
        return dic




class TrainedModel(models.Model):
    exp = models.OneToOneField('experiment.Experiment', auto_created=True, related_name='trained', on_delete=models.CASCADE)
    face_model = models.FileField(upload_to=_model_upload_path_, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=32, default='untrained')

    def get_dict(self):
        return {
            # 'face_model': self.face_model.url if self.face_model is not None else '',
            'tid': self.id,
            'create_time': str(self.create_time),
            'update_time': str(self.update_time),
            'status': self.status
        }


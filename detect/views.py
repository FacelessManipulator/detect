#coding=utf-8
from django.shortcuts import render

# Create your views here.
import time
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from taskpool import FacedetectPool
from django.contrib.auth.models import User
from experiment.models import Experiment
from models import FaceDetectReport, FaceData


def receive_image(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        image = request.FILES.get('file')
        try:
            if uid is not None and image is not None:
                user = User.objects.get(username=uid)
                task = FacedetectPool(None)
                task.run('detect', image.read(), opt={'update': True, 'username': user.username})
                return JsonResponse({'status': 201, 'msg': '上传成功'})
            else:
                return JsonResponse({'status': 503, 'msg': '上传失败'})
        except Exception,e:
            return JsonResponse({'status': 503, 'msg': '上传失败'})
    else:
        return JsonResponse({'status': 505, 'msg': '不支持的操作'})

def delete_image(request):
    if request.method == 'POST':
        fid = request.POST.get('fid')
        try:
            if fid is not None :
                f = FaceData.objects.get(id=fid)
                f.delete()
                return JsonResponse({'status': 201, 'msg': '删除成功'})
            else:
                return JsonResponse({'status': 503, 'msg': '删除失败'})
        except Exception,e:
            return JsonResponse({'status': 503, 'msg': '删除失败'})
    else:
        return JsonResponse({'status': 505, 'msg': '不支持的操作'})

def update(request):
    if request.method == 'POST':
        eid = request.POST.get('eid')
        try:
            if eid is not None:
                exp = Experiment.objects.get(eid=eid)
                if exp.trained.status == 'training':
                    return JsonResponse({'status': 503, 'msg': '正在训练'})
                else:
                    task = FacedetectPool()
                    task.run('update', exp)
                return JsonResponse({'status': 201, 'msg': '开始训练'})
        except Exception,e:
            return JsonResponse({'status': 503, 'msg': '错误的实验号'})


def recognize(request):
    if request.method == 'POST':
        eid = request.POST.get('eid')
        image = request.FILES.get('file')
        if eid is not None and image is not None:
            try:
                exp = Experiment.objects.get(eid=eid)
                report = exp.analysis.create(origin_image=image)
                task = FacedetectPool()
                task.run('recognize', report)
            except:
                return JsonResponse({'status': 503, 'msg': '错误的实验号'})
            return JsonResponse({'status': 201, 'msg': '开始识别'})
    return JsonResponse({'status': 503, 'msg': '不支持的操作'})

def get_report(request):
    if request.method == 'GET':
        rfid = request.GET.get('rfid')
        if rfid is not None:
            try:
                report = FaceDetectReport.objects.get(id=rfid)
                return JsonResponse({'status': 201, 'msg': '成功获取', 'content': report.get_dict(simple=False)})
            except Experiment,e:
                return JsonResponse({'status': 503, 'msg': '错误的报告号'})

    return JsonResponse({'status': 503, 'msg': '不支持的操作'})

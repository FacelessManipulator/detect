#coding=utf-8

from django.conf.urls import url
import views

urlpatterns = [
        url(r'^upload$', views.receive_image),
        url(r'^recognize$', views.recognize),
        url(r'^update', views.update),
        url(r'^report', views.get_report),
        url(r'^face/delete$', views.delete_image),
    ]
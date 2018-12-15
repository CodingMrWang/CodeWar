from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import logout_then_login, LoginView
from django.urls import path
from django.views.static import serve

from . import views
from CodeWar import consumers

urlpatterns = [
    url(r'^login$',
        LoginView.as_view(template_name="CodeWar/login.html", redirect_authenticated_user=True),
        name='login'),
    url(r'^logout$', logout_then_login, name='logout'),
    url(r'^$', views.home_page, name='home'),
    url(r'^battle/(?P<room_name>[^/]+)/(?P<name_pair>[^/]+)/(?P<qid1>[\w-]+)/(?P<qid2>[\w-]+)$',
        views.battle, name='battle'),
    url(r'^startbattle/(?P<room_name>[^/]+)/(?P<name_pair>[^/]+)$', views.start_battle,
        name='start_battle'),
    url(r'^indi-battle$', views.indi_battle, name='indi-battle'),
    url(r'run/(?P<qid>[\w-]+)$', views.get_result, name='result'),
    url(r'test/(?P<qid>[\w-]+)$', views.get_test_result, name='test_result'),
    url(r'^getInRoom/(?P<roomInfo>[^/]+)/$', views.getInRoom, name='getInRoom'),
    url(r'^searchUser$', views.searchUser, name='searchUser'),
    url(r'^createInvitation$', views.createInvitation, name='searchUser'),
    path('createRoom', views.createRoom, name="createRoom"),
    path('codewar/createRoom', views.createRoom, name="createRoom"),
    path('updateAllRooms', views.updateAllRooms, name="updateAllRooms"),
    path('listenInvitation', views.listenInvitation, name="listenInvitation"),
    path('acceptRoom', views.acceptRoom, name="acceptRoom"),
    path('getUserinfo', views.getUserinfo, name="getUserinfo"),
    path('getRankings', views.getRankings, name="getRankings"),
    path('deleteInvitation', views.deleteInvitation, name="deleteInvitation"),
    path('changeRoomStatus', views.changeRoomStatus, name="changeRoomStatus"),
    url(r'^ws/battle/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
    url(r'^signup$', views.register, name='signup'),
    url(r'setcode/(?P<qid>[\w-]+)$', views.set_code, name='set_code'),
    url(r'getcode/(?P<uid>[\w-]+)/(?P<qid>[\w-]+)', views.get_teamate_code, name='get_code'),
    url(r'^confirm/(?P<username>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name="confirm"),
    url(r'setscore/(?P<roomname>[^/]+)/(?P<qid1>[\w-]+)/(?P<qid2>[\w-]+)$', views.set_score,
        name='set_score'),
    url(r'getscore/(?P<roomname>[^/]+)/(?P<qid1>[\w-]+)/(?P<qid2>[\w-]+)$', views.get_score,
        name='get_score'),
    url(r'clear', views.clear, name='clear'),
    url(r'result/(?P<roomname>[^/]+)', views.getfinalresult, name='result'),
    url(r'loss', views.loss, name='loss'),
    url(r'success', views.success, name='success'),
    url(r'getNewRoom/(?P<room_id>[^/]+)/$', views.getNewRoom, name='getNewRoom'),
    url(r'changePosition', views.changePosition, name='changePosition'),
    url(r'updatePosition/(?P<room_id>[^/]+)/$', views.updatePosition, name='updatePosition'),
    url(r'savechat', views.savechat, name='savechat'),
    url(r'^edit$', views.edit, name="edit"),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

]

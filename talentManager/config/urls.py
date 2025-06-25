"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  #settings.pyをインポート
from django.conf.urls.static import static  #追加（静的ファイル）
#from .views import TopPage  #追加（トップページ）
from . import views


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('players.urls')),
    #path('', TopPage.as_view(), name='toppage'),        #追加（トップページ）
    #path('players/', include('players.urls')),          #追加（アプリ）
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
 #追加（静的ファイル）

"""smart_signal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
#import debug_toolbar
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,PasswordResetCompleteView
#from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    url(r'^$',views.layout,name='layout'),
    #url(r'^$',views.trail_of_db,name='layout'),
    url(r'^about$',views.about, name='about'),
    url(r'^home$',views.home, name='home'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    path('admin/', admin.site.urls),
    url(r'^adminpage$', views.adminpage,name='adminpage'),
    url(r'^userpage$', views.userpage, name='userpage'),
    url(r'^client_menu$', views.client_menu, name='client_menu'),
    url(r'^addclient$', views.addclient, name='addclient'),
    url(r'^show_clients$', views.show_clients, name='show_clients'),
    url(r'^deleteclient$', views.deleteclient, name='deleteclient'),
    url(r'^show_signals$', views.show_signals, name='show_signals'),
    url(r'^new_uploadvideo$', views.new_uploadvideo, name='new_uploadvideo'),
    #url(r'^uploadvideo1$', views.uploadvideo, name='uploadvideo1'),
    url(r'^uploadvideo_at_all_sites$', views.uploadvideo_at_all_sites, name='uploadvideo_at_all_sites'),
    url(r'^deletevideo$', views.deletevideo, name='deletevideo'),
    url(r'^displaylist_user$', views.displaylist_user, name='displaylist_user'),
    url(r'^displaylist_admin$', views.displaylist_admin, name='displaylist_admin'),
    url(r'^listout_videos$', views.displaylist_user, name='listout_videos'),
    url(r'^get_map$',views.get_map,name='get_map'),
    url(r'^get_cctv_feeds$',views.get_cctv_feeds,name="get_cctv_feeds"),
    url(r'^admin_map$',views.admin_map,name="admin_map"),
    url(r'^test-delete/$', views.test_delete, name='test_delete'),
    url(r'^test-session/$', views.test_session, name='test_session'),
    url(r'^save-session-data/$', views.save_session_data, name='save_session_data'),
    url(r'^access-session-data/$', views.access_session_data, name='access_session_data'),
    url(r'^delete-session-data/$', views.delete_session_data, name='delete_session_data'),
    url(r'^lousy-secret/$', views.lousy_secret, name='lousy_secret'),
#    url(r'^create_map$',views.create_map,name="create_map"),
#    path('accounts/', include('django.contrib.auth.urls')),
    path(r'password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Forgot_password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="Forgot_password/password_reset_confirm.html"), name='password_reset_confirm'),
#    path(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(template_name="Forgot_password/password_reset_confirm.html"), name='password_reset_confirm'),
    path(r'reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='Forgot_password/password_reset_complete.html'), name='password_reset_complete'),
    path(r"password_reset", views.password_reset_request, name="password_reset"),



] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

#urlpatterns.extend(i18n_patterns(*urlpatterns))
#if settings.DEBUG:
#    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),

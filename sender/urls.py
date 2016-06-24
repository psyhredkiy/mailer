from django.conf.urls import patterns, include, url
import mailer.urls
from django.contrib import admin
from mailer import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sender.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^mailer/', include(mailer.urls)),
    url(r'^login/$', views.LoginFormView.as_view()),
    url(r'^logout/$', views.logout),
)

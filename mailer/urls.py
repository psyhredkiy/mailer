from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sender.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),



    url(r'^viewjob/','mailer.views.view_job'),
    url(r'^addjob/','mailer.views.add_Job'),
    url(r'^addshed/(?P<job_id>\d+)/$','mailer.views.add_shed'),
    url(r'^shedsave/(?P<job_id>\d+)/$',"mailer.views.shed_save"),
    url(r'^shedsavee/(?P<shed_id>\d+)/$',"mailer.views.shed_save_e"),
    url(r'^shededit/(?P<shed_id>\d+)/$',"mailer.views.shed_edit"),
    url(r'^jobsavee/(?P<job_id>\d+)/$',"mailer.views.job_save_e"),
    url(r'^viewshed/','mailer.views.shed_view'),
    url(r'^jobsave/',"mailer.views.job_save"),
    url(r'^edit/(?P<job_id>\d+)/$',"mailer.views.job_edit"),
    url(r'^remove/(?P<job_id>\d+)/$',"mailer.views.job_rm"),
    url(r'^shremove/(?P<shed_id>\d+)/$',"mailer.views.shed_rm"),
    url(r'^shdis/(?P<shed_id>\d+)/$',"mailer.views.shed_disable"),
    url(r'^shen/(?P<shed_id>\d+)/$',"mailer.views.shed_enable"),
    url(r'^run/(?P<shed_id>\d+)/$',"mailer.views.run_job"),
    url(r'^lr/(?P<name>\w+)/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/$',"mailer.views.lastrun"),



                       )


# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
import os,sys,stat,subprocess
from mailer.models import Job
from mailer.models import Shed
from forms import add_job_form
from forms import add_shed_form
from django.core.context_processors import csrf
from django.core.files.base import File
from crontab import CronTab
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import loader, RequestContext

def base(request):
    usr = auth.get_user(request).username
    return usr


class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"

    # В случае успеха перенаправим на главную.
    success_url = "/mailer/viewjob/"

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()
        if not self.user or not self.user.is_active:
            raise FormView.form_invalid(self, form)
        # Выполняем аутентификацию пользователя.
        auth.login(self.request,self.user)
        auth.authenticate()

        return super(LoginFormView, self).form_valid(form)

def logout(request):
    auth.logout(request)
    return redirect('/login/')

@login_required(login_url="/login/")
def view_job(request,job_id=None):
    add_job = add_job_form
    args={}
    args.update(csrf(request))
    args['form'] = add_job
    args['jobs'] = Job.objects.all()
    rc = RequestContext(request, args)

    return  render_to_response('viewjobs.html',rc)


@login_required(login_url="/login/")
def add_Job(request):
    add_job = add_job_form
    args = {}
    args.update(csrf(request))
    args['form'] = add_job
    args['jobs'] = Job.objects.all()
    rc = RequestContext(request, args)
    return render_to_response("jobform.html",rc)


def job_save(request):
    if request.POST:
      form = add_job_form(request.POST)
      Job = form.save(request.POST)
      f = open('%s/%s' %(settings.SCRIPTS_DIR,Job.name) , 'w')
      myfile = File(f)
      content = '#!/bin/sh \nRecips=" %s " \nSubj=" %s " \nBody="%s" \nFromDir="%s" \n source sys/mailer.sh \n ' % ( Job.recips , Job.subj, Job.body ,Job.fromdir )
      myfile.write(content)
      f.close()
      myfile.close()
      os.chmod('%s/%s' %(settings.SCRIPTS_DIR,Job.name),stat.S_IRWXU)
      return redirect ('/mailer/viewjob/')

def job_save_e(request,job_id):
    if request.POST:
      a = Job.objects.get(id=job_id)
      os.remove('/scripts/%s' %(a.name))
      form = add_job_form(request.POST,instance=a)
      job = form.save(request.POST)
      f = open('%s/%s' %(settings.SCRIPTS_DIR,a.name), 'w')
      myfile = File(f)
      content = '#!/bin/sh \nRecips=" %s " \nSubj=" %s " \nBody="%s" \nFromDir="%s" \n source sys/mailer.sh \n  ' % ( a.recips , a.subj, a.body ,a.fromdir )
      myfile.write(content)
      f.close()
      myfile.close()
      os.chmod('%s/%s' %(settings.SCRIPTS_DIR,a.name),stat.S_IRWXU)
      return redirect ('/mailer/viewjob/')


def job_edit(request,job_id):
    a = add_job_form( initial={
    'name' :Job.objects.get(id=job_id).name ,
    'recips' :Job.objects.get(id=job_id).recips ,
    'subj' :Job.objects.get(id=job_id).subj,
    'body' :Job.objects.get(id=job_id).body,
    'fromdir' :Job.objects.get(id=job_id).fromdir
    },)
    args = {}
    args.update(csrf(request))
    args['form'] = a
    args['jobs'] = Job.objects.all()
    args['job_id'] = job_id
    args['job_name'] = Job.objects.get(id=job_id).name
    rc = RequestContext(request, args)
    return render_to_response("jobform.html",rc)

def job_rm(request,job_id):
    a = Job.objects.get(id=job_id)
    tab = CronTab(user=settings.CRONTAB_USER)
    tab.remove_all(comment=a.name)
    tab.write()
    os.remove('%s/%s'%(settings.SCRIPTS_DIR,a.name))
    a.delete()
    return redirect ('/mailer/viewjob/')

def add_shed(request,job_id):
    jid=Job.objects.get(id=job_id).id
    args = {}
    args.update(csrf(request))
    args['form'] = add_shed_form
    args['jid'] = jid
    rc = RequestContext(request, args)
    return render_to_response("newshed.html",rc)

@login_required(login_url="/login/")
def shed_view(request):

    args = {}
    args['sheds']  = Shed.objects.all()

    
    return render_to_response("viewsheds.html",args)


def shed_save(request,job_id):
    if request.POST:
     form = add_shed_form(request.POST)
     shed = form.save(commit=False)
     shed.job = Job.objects.get(id=job_id)
     shed.enabled=True
     shed.save()
     tab = CronTab(user=settings.CRONTAB_USER)
     cmd = '/bin/sh %s/%s ' %(settings.SCRIPTS_DIR,shed.job.name)
     h = shed.time.hour
     m = shed.time.minute
     cron_job = tab.new(cmd,comment=shed.job.name)
     cron_job.dow.on(1,2,3,4,5)
     cron_job.minute.on(m)
     cron_job.hour.on(h)
     tab.write()
     return redirect ('/mailer/viewshed/')

def shed_edit(request,shed_id):
    edit_shed=add_shed_form(initial={'time':Shed.objects.get(id=shed_id).time})
    args = {}
    args.update(csrf(request))
    args['form'] = edit_shed
    args['shed_id'] = shed_id
    rc = RequestContext(request, args)
    return render_to_response("shededit.html",rc)


def shed_save_e(request,shed_id) :
    if request.POST:
     a = Shed.objects.get(id=shed_id)
     form = add_shed_form(request.POST,instance=a)
     shed = form.save(commit=False)
     shed.job = a.job
     shed.save()
     cmd = '/bin/sh %s/%s ' %(settings.SCRIPTS_DIR,shed.job.name)
     tab = CronTab(user=settings.CRONTAB_USER)
     tab.remove_all(comment=shed.job.name)
     tab.write()
     tab = CronTab(user=settings.CRONTAB_USER)
     h = shed.time.hour
     m = shed.time.minute
     cron_job = tab.new(cmd)
     cron_job.dow.on(1,2,3,4,5)
     cron_job.minute.on(m)
     cron_job.hour.on(h)
     tab.write()
     return redirect ('/mailer/viewshed/')

def shed_rm(request,shed_id):
     shed = Shed.objects.get(id=shed_id)
     tab = CronTab(user=settings.CRONTAB_USER)
     tab.remove_all(comment=shed.job.name)
     tab.write()
     shed.delete()
     return redirect ('/mailer/viewshed/')

def shed_disable(request,shed_id):
    shed = Shed.objects.get(id=shed_id)
    shed.enabled=False
    shed.save()
    tab = CronTab(user=settings.CRONTAB_USER)
    tab.remove_all(comment=shed.job.name)
    tab.write()
    return redirect ('/mailer/viewshed/')

def shed_enable(request,shed_id):
    shed = Shed.objects.get(id=shed_id)
    if (shed.enabled==False):
      shed.enabled=True
      shed.save()
      tab = CronTab(user=settings.CRONTAB_USER)
      cmd = '/bin/sh %s/%s ' %(settings.SCRIPTS_DIR,shed.job.name)
      h = shed.time.hour
      m = shed.time.minute
      cron_job = tab.new(cmd,comment=shed.job.name)
      cron_job.dow.on(1,2,3,4,5)
      cron_job.minute.on(m)
      cron_job.hour.on(h)
      tab.write()
      return redirect ('/mailer/viewshed/')
    else:
        return redirect ('/mailer/viewshed/')

def run_job(request,shed_id):
    name=Shed.objects.get(id=shed_id).job.name
    p = os.popen('%s/%s' %(settings.SCRIPTS_DIR,name),"r")
    line = p.readline()
    args = {}
    args['out'] = line
    args['cmd'] = name
    rc = RequestContext(request, args)
    return render_to_response("run.html",rc)

def lastrun(request,name,day,month,year,hour,minute):
    nm = Job.objects.get(name=name)
    shed = Shed.objects.get(job=nm)
    shed.lastrun = day+'.'+month+'.'+year+'-'+hour+':'+minute
    shed.save()
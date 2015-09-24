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


def view_job(request,job_id=None):
    if (job_id != None ):
     a = add_job_form( initial={
     'name' :Job.objects.get(id=job_id).name ,
     'recips' :Job.objects.get(id=job_id).recips ,
     'subj' :Job.objects.get(id=job_id).subj,
     'body' :Job.objects.get(id=job_id).body,
     'fromdir' :Job.objects.get(id=job_id).fromdir
      },)
     args={}
     args['id'] = job_id
     args['modal'] = True
     args.update(csrf(request))
     args['form'] = add_job_form
     args['forma'] = a
     args['jobs'] = Job.objects.all()

    else:
     add_job = add_job_form
     args={}
     args.update(csrf(request))
     args['modal'] = False
     args['form'] = add_job
     args['jobs'] = Job.objects.all()

    return  render_to_response('view.html',args)


def add_Job(request):
    add_job = add_job_form
    args = {}
    args.update(csrf(request))
    args['form'] = add_job
    args['jobs'] = Job.objects.all()
    return render_to_response("job_edit",args)


def job_save(request):
    if request.POST:
      form = add_job_form(request.POST)
      Job = form.save(request.POST)
      f = open('/scripts/%s' %(Job.name) , 'w')
      myfile = File(f)
      content = '#!/bin/sh \nRecips=" %s " \nSubj=" %s " \nBody="%s" \nFromDir="%s" \n source sys/mailer.sh \n ' % ( Job.recips , Job.subj, Job.body ,Job.fromdir )
      myfile.write(content)
      f.close()
      myfile.close()
      os.chmod('/scripts/%s' %(Job.name), 777)
      return redirect ('/test/viewjob/')

def job_save_e(request,job_id):
    if request.POST:
      a = Job.objects.get(id=job_id)
      os.remove('/scripts/%s' %(a.name))
      form = add_job_form(request.POST,instance=a)
      job = form.save()
      f = open('/scripts/%s' %(a.name), 'w')
      myfile = File(f)
      content = '#!/bin/sh \nRecips=" %s " \nSubj=" %s " \nBody="%s" \nFromDir="%s" \n source sys/mailer.sh \n  ' % ( a.recips , a.subj, a.body ,a.fromdir )
      myfile.write(content)
      f.close()
      myfile.close()
      os.chmod('/scripts/%s' %(a.name),stat.S_IRWXU)
      return redirect ('/test/viewjob/')


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
    return render_to_response("edit.html",args)

def job_rm(request,job_id):
    a = Job.objects.get(id=job_id)
    tab = CronTab(user='xanderz')
    tab.remove_all(comment=a.name)
    tab.write()
    os.remove('/scripts/%s'%(a.name))
    a.delete()
    return redirect ('/test/viewjob/')

def add_shed(request,job_id):
    jid=Job.objects.get(id=job_id).id
    args = {}
    args.update(csrf(request))
    args['form'] = add_shed_form
    args['jid'] = jid
    return render_to_response("newshed.html",args)

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
     tab = CronTab(user='xanderz')
     cmd = '/bin/sh /scripts/%s ' %(shed.job.name)
     h = shed.time.hour
     m = shed.time.minute
     cron_job = tab.new(cmd,comment=shed.job.name)
     cron_job.dow.on(1,2,3,4,5)
     cron_job.minute.on(m)
     cron_job.hour.on(h)
     tab.write()
     return redirect ('/test/viewshed/')

def shed_edit(request,shed_id):
    edit_shed=add_shed_form(initial={'time':Shed.objects.get(id=shed_id).time})
    args = {}
    args.update(csrf(request))
    args['form'] = edit_shed
    args['shed_id'] = shed_id
    return render_to_response("shededit.html",args)


def shed_save_e(request,shed_id) :
    if request.POST:
     a = Shed.objects.get(id=shed_id)
     form = add_shed_form(request.POST,instance=a)
     shed = form.save(commit=False)
     shed.job = a.job
     shed.save()
     cmd = '/bin/sh /scripts/%s ' %(shed.job.name)
     tab = CronTab(user='xanderz')
     tab.remove_all(comment=shed.job.name)
     tab.write()
     tab = CronTab(user='xanderz')
     h = shed.time.hour
     m = shed.time.minute
     cron_job = tab.new(cmd)
     cron_job.dow.on(1,2,3,4,5)
     cron_job.minute.on(m)
     cron_job.hour.on(h)
     tab.write()
     return redirect ('/test/viewshed/')

def shed_rm(request,shed_id):
     shed = Shed.objects.get(id=shed_id)
     tab = CronTab(user='xanderz')
     tab.remove_all(comment=shed.job.name)
     tab.write()
     shed.delete()
     return redirect ('/test/viewshed/')

def shed_disable(request,shed_id):
    shed = Shed.objects.get(id=shed_id)
    shed.enabled=False
    shed.save()
    tab = CronTab(user='xanderz')
    tab.remove_all(comment=shed.job.name)
    tab.write()
    return redirect ('/test/viewshed/')

def shed_enable(request,shed_id):
    shed = Shed.objects.get(id=shed_id)
    if (shed.enabled==False):
      shed.enabled=True
      shed.save()
      tab = CronTab(user='xanderz')
      cmd = '/bin/sh /scripts/%s ' %(shed.job.name)
      h = shed.time.hour
      m = shed.time.minute
      cron_job = tab.new(cmd,comment=shed.job.name)
      cron_job.dow.on(1,2,3,4,5)
      cron_job.minute.on(m)
      cron_job.hour.on(h)
      tab.write()
      return redirect ('/test/viewshed/')
    else:
        return redirect ('/test/viewshed/')

def run_job(request,shed_id):
    name=Shed.objects.get(id=shed_id).job.name
    p = os.popen('/scripts/%s' %(name),"r")
    line = p.readline()
    args = {}
    args['out'] = line
    args['cmd'] = name
    return render_to_response("run.html",args)

def lastrun(request,name,day,month,year,hour,minute):
    nm = Job.objects.get(name=name)
    shed = Shed.objects.get(job=nm)
    shed.lastrun = day+'.'+month+'.'+year+'-'+hour+':'+minute
    shed.save()
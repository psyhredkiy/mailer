# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms
from models import Job
from models import Shed


class add_job_form(ModelForm):

    def __init__(self,*args, **kwargs):
        super(add_job_form,self).__init__(*args,**kwargs)

        self.fields['name'].widget.attrs['class']='form-control'
        self.fields['recips'].widget.attrs['class']='form-control'
        self.fields['subj'].widget.attrs['class']='form-control '
        self.fields['body'].widget.attrs['class']='form-control '
        self.fields['fromdir'].widget.attrs['class']='form-control '


    class Meta:
        model = Job
        exclude ={'issheduled'}

class add_shed_form(ModelForm):

    class Meta:
        model = Shed
        fields = {'time',"enabled"}


    def __init__(self,*args,**kwargs):
        super(add_shed_form,self).__init__(*args,**kwargs)
        self.fields['time'].widget.attrs['class']='time'


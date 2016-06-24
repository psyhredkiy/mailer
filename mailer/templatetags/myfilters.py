from django import template
from django.contrib import auth
from mailer import views

register = template.Library()

@register.filter(name='addclass')
def addclass(value,arg):

    return value.as_widget(attrs={'class':'form-control','placeholder':arg})

@register.simple_tag()
def usernm():
    return views.base()




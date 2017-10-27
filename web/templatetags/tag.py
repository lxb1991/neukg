# -*- coding: utf-8 -*-
from django import template
from DataEngine.common import Encrypt

register = template.Library()


@register.filter
def encrypt(value):

    return Encrypt.encrypt(value)

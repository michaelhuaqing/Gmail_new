# coding: utf-8
from django import forms

class EmailQueryForm(forms.Form):
    from__1 = forms.CharField(required=False, label='发件人')
    to_1 = forms.CharField(required=False, label='收件人')
    subject_1 = forms.CharField(required=False, label='主题')
    body_txt_1 = forms.CharField(required=False, label='内容')
    attach_txt_1 = forms.CharField(required=False, label='附件')
    ip_1 = forms.IPAddressField(required=False, label='IP地址')
    start_1 = forms.DateTimeField(required=False, label='从')
    end_1 = forms.DateTimeField(required=False, label='至')


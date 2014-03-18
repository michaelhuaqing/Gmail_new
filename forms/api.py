# coding: utf-8
from __future__ import absolute_import
from collections import defaultdict
import ipdb
from uuid import UUID
import logging
from hashlib import md5

from django import forms
from django.contrib.auth import authenticate
from django.conf import settings
from bson import BSON, InvalidBSON
from gmail.models import User

"""
Request, bson encoded
{
	devid:{guid},	//设备标识
	ver:{int},		//协议版本号
    source:{int},   //来源
	action:101,
	nonce:{int},
	sig:{string},	//根据上面五个字段生成的签名
    uid:{string}
}
Response, json encoded
{
	action:101,			//响应对应的请求类型
    error:{int},			//错误类型，0为成功
	errormsg:{string},		//可选，出错信息，调试用
}
"""

source_table = {
        11: 'iOS',
        12: 'Android',
        13: 'Windows Phone',
        21: 'Windos',
        22: 'Mac OSX',
        31: 'Email Account',
    }

action_table = {
        101: 'init',
        102: 'login',
        111: 'upload',
        121: 'comm',
        122: 'config',
        123: 'download',
        124: 'install',
    }

DUP_DEVID = 1000
INVALID_DEVID = 1001
INVALID_SIG = 1002
LOGIN_FAILED = 1003
INVALID_UID = 1004
UNKNOWN_ACTION = 2000
DATA_UPLOAD_FAIL = 3001
INVALID_REQ = 3002
SERVER_FAIL = 3003

logger = logging.getLogger(__name__)

class ApiValidationError(Exception):
    def __init__(self, error_id, desc):
        self.error_id = error_id
        self.desc = desc
        super(ApiValidationError, self).__init__(error_id, desc)

class ApiForm(forms.Form):
    """Imitate django's standard form, except
    its data is bson encoded"""
    error_id = 0
    errors = ''

    def full_clean(self):
        try:
            # Will raise InvalidBSON
            # self.cleaned_data = BSON(self.data).decode(as_class=lambda : defaultdict(str))
            self.cleaned_data = BSON(self.data).decode()

            self.clean_devid()
            self.clean_ver()
            self.clean_source()
            self.clean_action()
            self.clean_nonce()

            if self.cleaned_data['sig'] != self.sign():
                raise ApiValidationError(INVALID_SIG,  'Invalid signature')

            self.clean_shit()

        except InvalidBSON as e:
            self.error_id = INVALID_REQ
            self.errors = 'InvalidBSON: %s' % e
            logger.warning(self.errors)
        except ApiValidationError as e:
            self.error_id = e.error_id
            self.errors = e.desc
            if self.error_id != LOGIN_FAILED:
                logger.warning(self.errors)
        #TODO, define one
        except KeyError as e:  # Key missing
            self.error_id = INVALID_REQ
            self.errors = 'Key missing %s' % e
            logger.warning(self.errors)

    def clean_devid(self):
        if not isinstance(self.cleaned_data['devid'], UUID):
            try:
               self.cleaned_data['devid'] = UUID(str(self.cleaned_data['devid']))
            except ValueError as e:  # invalid_devid
                raise ApiValidationError(INVALID_DEVID, 'Invalid device id: %s' % e)

    def clean_action(self):
        if self.cleaned_data['action'] not in action_table:
            raise ApiValidationError(UNKNOWN_ACTION, 'Action id is unknown')

    def clean_ver(self):
        if not isinstance(self.cleaned_data['ver'], int):
            raise ApiValidationError(INVALID_REQ, 'Ver should be an integer')

    def clean_source(self):
        if not isinstance(self.cleaned_data['source'], int):
            raise ApiValidationError(INVALID_REQ, 'Source should be an integer')
        #TODO define one
        if self.cleaned_data['source'] not in source_table:
            raise ApiValidationError(INVALID_REQ, 'Source id is unknown')
        #TODO Should I store string in db? NO
        #self.cleaned_data['source'] = source_table[self.cleaned_data['source']]

    def clean_nonce(self):
        if not isinstance(self.cleaned_data['nonce'], int):
            raise ApiValidationError(INVALID_REQ, 'Nonce should be an integer')

    def sign(self):
        d = self.cleaned_data
        return md5('%s'*6 % (
            d['devid'], d['ver'], d['source'], d['action'], d['nonce'], 
            settings.API_SECRET_KEY)).hexdigest().lower()

    def is_valid(self):
        self.full_clean()
        return self.is_bound and not bool(self.errors)

class UploadForm(ApiForm):

    def clean_shit(self):
        if self.cleaned_data['action'] != 111:
            raise ApiValidationError(UNKNOWN_ACTION, 'Invalid action id')
        self.clean_upload_data()
        self.clean_upload_devid()

    def clean_upload_data(self):
        if not isinstance(self.cleaned_data['data'], (list, tuple)):
            raise ApiValidationError(INVALID_REQ, 'Uploaded data should be an array')
        for ele in self.cleaned_data['data']:
            # Try triger keyerror
            ele['id'], ele['typeid'], ele['data']
	    if not isinstance(ele['data'], dict):
                raise ApiValidationError(INVALID_REQ, 'data.data should be a dict')

            ele['data']['folder'], ele['data']['content']
            # if not isinstance(ele['id'], int):
            #     raise ApiValidationError(INVALID_REQ, 'Id should be an integer')
            #TODO, correct docs
            if not isinstance(ele['typeid'], int):
                raise ApiValidationError(INVALID_REQ, 'Typeid should be an integer')

    def clean_upload_devid(self):
        u = User.objects(device_ids=self.cleaned_data['devid']).first()
        if not u:
            raise ApiValidationError(INVALID_DEVID, 'Invalid device id: %s' %
                    self.cleaned_data['devid'])
        self.user = u

class InitForm(ApiForm):

    def clean_shit(self):
        #TODO what if doesn't match, SHOULD BE INVALID_REQ
        if self.cleaned_data['action'] != 101: # register a new device
            raise ApiValidationError(UNKNOWN_ACTION, 'Invalid action id')
        if User.objects(device_ids=self.cleaned_data['devid']).first():
            raise ApiValidationError(DUP_DEVID, 'Duplicated device id')
        u = User.objects(id=self.cleaned_data['uid']).first()
        if not u:
            raise ApiValidationError(INVALID_UID, 'Invalid user id')
        self.user = u

class LoginForm(ApiForm):

    def clean_shit(self):
	# According to Jeff, this is not init, we should be able to login in multi times
        # if User.objects(device_ids=self.cleaned_data['devid']).first():
        #    raise ApiValidationError(DUP_DEVID, 'Duplicated device id')
        u, p = self.cleaned_data['username'], self.cleaned_data['password']
        user = authenticate(username=u, password=p)
        if not user:
            logger.warning('User %s login failed', u)
            raise ApiValidationError(LOGIN_FAILED, 'Login failed')
        logger.info('%s logged in, sending back uid: %s',  user.username,  user.id)
        self.user = user


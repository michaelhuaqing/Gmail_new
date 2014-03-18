from __future__ import absolute_import
from django.views.generic.edit import FormView
import logging
import ipdb
from django.http import Http404

from .mixins import JsonViewMixin
from gmail.forms import UploadForm, InitForm, LoginForm, INVALID_REQ
from gmail.models import Email
from gmail.errors import MessageParseError

logger = logging.getLogger(__name__)

class ApiFormMixin(object):

    def get(self, request):
        # Do something before formview kicks in
        raise Http404()

    def form_invalid(self, form):
        return {'action': self.action_code,
                'error': form.error_id,
                'errormsg': form.errors,
                'ack': [],
            }

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.body,
                'files': self.request.FILES,
            })
        return kwargs


class ApiUpload(ApiFormMixin, JsonViewMixin, FormView):
    form_class = UploadForm
    action_code = 111

    def form_valid(self, form):
        ack_ids = []
        for ele in form.cleaned_data['data']:
            try:
                # Oh, fuck this shit!
                email = Email.from_string(ele['data']['content'])
                email.owner = form.user
                email.folder = ele['data']['folder']
                email.save()
            except MessageParseError as e:
                form.error_id = INVALID_REQ
                form.errors = str(e)
            else:
                ack_ids.append(ele['id'])
                logger.info("%s uploaded a new email '%s'(%s)", form.user.username, email.subject,
                        email.folder, extra=self.request.__dict__)

        return {'action': self.action_code,
                'error': form.error_id,
                'errormsg': form.errors,
                'ack': ack_ids,
            }

class ApiInit(ApiFormMixin, JsonViewMixin, FormView):
    form_class = InitForm
    action_code = 101

    def form_valid(self, form):
        form.user.update(add_to_set__device_ids=form.cleaned_data['devid'])
        logger.info('%s adds a new device id %s', form.user.username,
                form.cleaned_data['devid'], extra=self.request.__dict__)
        return {'action': self.action_code,
                'error': form.error_id,
                'errormsg': form.errors,
            }

class ApiLogin(ApiFormMixin, JsonViewMixin, FormView):
    form_class = LoginForm
    action_code = 102

    def form_valid(self, form):
        # Login donot take charge of registering now
        # form.user.update(add_to_set__device_ids=form.cleaned_data['devid'])
        return {'action': self.action_code,
                'error': form.error_id,
                'errormsg': form.errors,
                'uid': form.user.id,
            }


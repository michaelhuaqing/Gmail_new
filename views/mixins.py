from json import dumps, JSONEncoder
import ipdb
import datetime
from time import mktime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse
from django.views.generic import View
from bson.objectid import ObjectId

class LoginRequiredMixin(View):
    """ from http://stackoverflow.com/a/6455140 """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class MyJsonEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super(MyJsonEncoder, self).default(obj)

class JsonViewMixin(View):
    content_type = 'application/json'

    def dispatch(self, request, *args, **kwargs):
        d = super(JsonViewMixin, self).dispatch(request, *args, **kwargs)
        return HttpResponse(dumps(d, cls=MyJsonEncoder), content_type=self.content_type)


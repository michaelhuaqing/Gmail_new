import time
import logging

from gmail.errors import MessageParseError, ObjectDoesNotExist
from django.http import Http404, HttpResponseBadRequest

logger = logging.getLogger(__name__)

class SetRemoteAddrFromForwardedFor(object):

    def process_request(self, request):
        try:
           real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
           pass
        else:
           # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
           # Take just the first one.
           real_ip = real_ip.split(",")[0]
           request.META['REMOTE_ADDR'] = real_ip
        request.remote_addr = request.META.get("REMOTE_ADDR", None)


class HttpErrorHandler(object):

    def process_exception(self, request, exception):
        if isinstance(exception, MessageParseError):
            resp_dict = {'status':'ERROR', 'message': str(exception)}
            return HttpResponseBadRequest(str(resp_dict))
        elif isinstance(exception, ObjectDoesNotExist):
            raise Http404()

class TimeRequest(object):

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            d = {
                'method': request.method,
                'url': request.path_info,
                'time': time.time() - request._start_time,
            }
            logger.info('%(method)s %(url)s costs %(time).2fs' % d)
        return response

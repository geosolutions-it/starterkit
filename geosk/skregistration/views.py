import os
import requests
from urlparse import urlsplit

from django.contrib.sites.models import Site
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test

from geonode.utils import http_client, _get_basic_auth_info, json_response

from models import SkRegistration

@user_passes_test(lambda u: u.is_superuser)
def registration(request, template='skregistration/registration.html'):
    sk = SkRegistration.objects.get_current()
    status = 'unregistered'
    if sk is not None and sk.verified:
        status = 'registered'
    elif sk is not None and not sk.verified:
        status = 'invalid'

    return render_to_response(template, RequestContext(request, {
                'SETTINGS_SITENAME': getattr(settings, 'SITENAME', 'GeoNode'),
                'SETTINGS_SITEURL':  getattr(settings, 'SITEURL'),
                'status': status,
    }))

@user_passes_test(lambda u: u.is_superuser)
def register(request):
    current_site = Site.objects.get_current()
    siteurl = settings.SITEURL
    parsed = urlsplit(siteurl)
    domain=parsed.netloc
    # check domain (sites.Site) and settings.SITEURL
    if domain != current_site.domain:
        return json_response(errors='Configuration mismatch: settings.SITEURL and sites.Site', status=500)

    # check if a key is already present
    try:
        SkRegistration.objects.get(site=current_site)
        return json_response(errors='URI already presents in the local catalog', status=500)
    except SkRegistration.DoesNotExist:
        pass
        
    status, api_key = _register(uri = domain)
    if status is True:
        skr = SkRegistration(api_key = api_key, site = current_site)
        skr.save()
        return json_response(body={'success':True})
    else:
        return json_response(errors=api_key, status=500)

def _register(uri=None):
    if uri is None:
        uri = Site.objects.get_current().domain

    service = settings.RITMARE['MDSERVICE']
    url_register = os.path.join(service,'auth','register')

    data = {
        'uri': uri,
        'xmlMetadata': '<elements></elements>'
        }

    r = requests.post(url_register, data=data, verify=False)
    code = r.status_code
    if code == 200:
        api_key = r.text
        return True, api_key
    else:
        error_message = r.text
        return False, error_message


@user_passes_test(lambda u: u.is_superuser)
def verify(request):
    status = _verify()
    if status is True:
        skr = SkRegistration.objects.get_current()
        skr.verified = True
        skr.save()
        return json_response(body={'success':True})
    else:
        return json_response(exception=api_key, status=500)


def get_key(uri=None):
    skr = SkRegistration.objects.get_current()

    return skr.api_key

    
def _verify(uri=None):
    service = settings.RITMARE['MDSERVICE']
    url_verify = os.path.join(service,'auth','verify')

    api_key = get_key(uri)

    params = {
        'apiKey': api_key
        }
    
    r = requests.get(url_verify, params=params, verify=False)    
    code = r.status_code
    if code == 200:
        return True
    else:
        return False
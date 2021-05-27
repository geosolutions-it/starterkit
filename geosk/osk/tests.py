"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
from django.test import SimpleTestCase
from geosk.osk.utils import todict
from geosk.osk.sos import Catalog
from unittest.mock import MagicMock
from unittest.mock import patch
from owslib.swe.observation.sos100 import SosCapabilitiesReader
from requests.models import Response


def get_fixtures_file(file):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures', file))


class UtilsTest(SimpleTestCase):

    def test_todict_with_dictionary(self):
        data = {"a": 1, "b": "two"}
        result = todict(data)
        self.assertEqual(data["a"], result["a"])
        self.assertEqual(data["b"], result["b"])

    def test_todict_with_class_object(self):
        class DogClass:
            def __init__(self, name, color):
                self.name = name
                self.color = color
        dc = DogClass('rudra', 'white')
        result = todict(dc)
        self.assertEqual(dc.name, result["name"])
        self.assertEqual(dc.color, result["color"])

    def test_todict_with_list(self):
        obj = ["a", "b", "c"]
        result = todict(obj)
        self.assertEqual(obj[0], result[0])
        self.assertEqual(obj[1], result[1])
        self.assertEqual(obj[2], result[2])


class SOSCatalogTest(SimpleTestCase):

    def test_constructor(self):
        service_url = 'http://test.service.com'
        catalog = Catalog(service_url)
        self.assertIsNotNone(catalog)

    def test_get_capabilities_url(self):
        service_url = 'http://test.service.com'
        catalog = Catalog(service_url)
        self.assertEqual('http://test.service.com?service=SOS&request=GetCapabilities',
                         catalog.get_capabilities_url()
                         )

    def test_set_cache(self):
        service_url = 'http://test.service.com'
        catalog = Catalog(service_url)
        uri_test = 'test-uri'
        content_test = 'test-content'
        result = catalog.set_cache(uri_test, content_test)
        self.assertEqual(result, content_test)

    def test_get_cache(self):
        service_url = 'http://test.service.com'
        catalog = Catalog(service_url)
        uri_test = 'test-uri'
        content_test = 'test-content'
        result = catalog.set_cache(uri_test, content_test)
        self.assertEqual(catalog.get_cache(uri_test), content_test)

    @patch('owslib.sos.SensorObservationService')
    def test_get_capabilities(self, sos_mock):
        service_url = 'http://test.service.com'
        catalog = Catalog(service_url)
        result = catalog.set_cache('capabilities', sos_mock)
        self.assertEqual(result, sos_mock)
        self.assertEqual(catalog.get_capabilities(), sos_mock)

    #@patch('owslib.swe.observation.sos200.SosCapabilitiesReader')
    @patch('requests.request')
    @patch('requests.models.Response')
    def test_get_sensors(self, mock_req, mock_resp):
        """
        Example of real service for sensors
        http://insitu.webservice-energy.org/52n-sos-webapp/sos
        :param mock_req:
        :param mock_resp:
        :return:
        """
        xml_file = get_fixtures_file('sos_cap_test.xml')
        content = ""
        with open(xml_file, mode='r') as f:
            content = f.read()
        mock_resp.return_value.code = "OK"
        mock_resp.return_value.status_code = 200
        mock_resp.return_value.headers = {'Content-Type': 'text/xml'}
        mock_resp.return_value.content = str.encode(content)
        mock_req.side_effect = mock_resp
        service_url = 'http://unit.test.org/sos'
        catalog = Catalog(service_url)
        result = catalog.get_sensors(full=False)
        self.assertEqual(331, len(result))

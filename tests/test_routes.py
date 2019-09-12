import unittest
from unittest import mock

import requests
import responses
from app import profile_exceptions
from app.summary import HostService, GitHub, Bitbucket


class SummaryTestCase(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch.object(HostService, '__abstractmethods__', new=set())
        self.patcher.start()

    def doCleanups(self):
        self.patcher.stop()
        return super().doCleanups()

class BitBucketUsernameValidationTestCase(SummaryTestCase):
    @responses.activate
    def test_invalid_username(self):
        responses.add(responses.HEAD, 'https://testsitepoint.com', status=404)
        mock_url = mock.PropertyMock(return_value='https://testsitepoint.com')
        with mock.patch.object(HostService, 'validate_username_url', new_callable=mock_url):
            with self.assertRaises(profile_exceptions.ProfileNotFoundError) as testContext:
                HostService('testuser').validate_username()
        self.assertEqual('testuser profile do not exists', str(testContext.exception))

    @responses.activate
    def test_valid_username(self):
        responses.add(responses.HEAD, 'https://testsitepoint.com', status=200)
        mock_url = mock.PropertyMock(return_value='https://testsitepoint.com')
        with mock.patch.object(HostService, 'validate_username_url', new_callable=mock_url):
            self.assertTrue(HostService('testuser').validate_username())


class BitBucketResponseHandleTestCase(SummaryTestCase):
    def test_respnse_handler_with_error(self):
        profile = HostService('testuser')

        response = requests.Response()
        response.status_code = 400
        response.request = requests.Request('GET', 'https://testsitepoint.com')
        with self.assertRaises(profile_exceptions.APIError) as testContext:
            profile.res_handler(response)
        self.assertEqual('Error response from hostservice while accessing https://testsitepoint.com: 400', str(testContext.exception))

    def test_response_handler_success(self):
        response = requests.Response()
        response.status_code = 201
        self.assertIs(HostService('testuser').res_handler(response, (200, 201)), response)

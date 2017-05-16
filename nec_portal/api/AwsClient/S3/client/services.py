#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#
#  COPYRIGHT  (C)  NEC  CORPORATION  2016

import logging

from nec_portal.api.AwsClient.S3.conf import AwsClientS3Const
from nec_portal.api.AwsClient.S3.lib import AwsClientS3Rest

LOG = logging.getLogger(__name__)


class ObjsAwsS3Services(object):

    def getService(self, endPoint, access_key, secret_key,
                   http_error_code, time_out):

        if not endPoint or not access_key or not secret_key:
            raise Exception()

        client = AwsClientS3Rest.AwsClientS3Rest(http_error_code,
                                                 time_out)

        url = endPoint

        if not url:
            raise Exception()

        url += '/'
        canonicalizedResource = ''
        resp = client.execution('getService', url, AwsClientS3Const.METHOD_GET,
                                access_key, secret_key,
                                canonicalizedResource, {}, 'xml')
        return resp

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

from hashlib import sha1
import hmac

import json
import logging
import pycurl
import re
from StringIO import StringIO
import xml.etree.ElementTree as ET
from nec_portal.api.AwsClient.S3.conf import AwsClientS3Const
from time import strftime, gmtime

LOG = logging.getLogger(__name__)

HTTP_STATUS_NORMAL_LIST = {
    'getService': [200],
    'putBucketPolicy': [204],
    'getBucketPolicy': [200, 404],
}


class AwsClientS3Rest(object):
    _instance = None

    # cilent common
    _httpErrorCode = None
    _timeOut = None

    def __init__(self, http_error_code, time_out):

        self._httpErrorCode = http_error_code
        self._timeOut = time_out

    def createAutorizationHeader(self, method, access_key, secret_key,
                                 canonicalized_resource, timestamp,
                                 contentType='application/json'):

        httpVerb = method
        contentMd5 = ""
        canonicalizedAmzHeaders = ""
        stringToSign = httpVerb + "\n" + contentMd5 + "\n" + contentType +\
            "\n" + timestamp + "\n" + canonicalizedAmzHeaders +\
            "/" + canonicalized_resource
        hashed = hmac.new(secret_key, stringToSign, sha1)
        signature = hashed.digest().encode("base64").rstrip('\n')

        hAuthorization = "Authorization: AWS " + access_key + ":" + signature

        return hAuthorization

    def execution(self, client_function, url, method, access_key, secret_key,
                  canonicalized_resource='', param={}, response_type='json'):

        if not url:
            raise Exception('url required')

        param_string = {}
        if param:
            if isinstance(param, dict):
                param_string = json.dumps(param)
            else:
                param_string = param

        timestamp = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

        hAuthorization = self.createAutorizationHeader(
            method, access_key, secret_key,
            canonicalized_resource, timestamp)

        ch = pycurl.Curl()
        ch.setopt(ch.URL, url)

        hAuthorization_list = ['Date: ' + timestamp,
                               'Content-Type: application/json',
                               'Content-Length: ' + str(len(param_string)),
                               hAuthorization]

        ch.setopt(ch.HTTPHEADER, hAuthorization_list)
        ch.setopt(ch.TIMEOUT, self._timeOut)
        ch.setopt(ch.SSL_VERIFYPEER, False)

        if method == AwsClientS3Const.METHOD_GET:

            ch.setopt(ch.HTTPGET, True)
            ch.setopt(ch.FOLLOWLOCATION, False)
            ch.setopt(ch.SSL_VERIFYHOST, 2)

        elif method == AwsClientS3Const.METHOD_POST:

            ch.setopt(ch.POST, True)
            ch.setopt(ch.POSTFIELDS, param_string)

        elif method == AwsClientS3Const.METHOD_PUT:

            ch.setopt(ch.CUSTOMREQUEST, method)
            ch.setopt(ch.FAILONERROR, False)

            if param_string:
                ch.setopt(ch.POSTFIELDS, param_string)
                ch.setopt(ch.POST, True)

        elif method == AwsClientS3Const.METHOD_DELETE:

            ch.setopt(ch.CUSTOMREQUEST, method)
            ch.setopt(ch.FAILONERROR, False)

            if param_string:
                ch.setopt(ch.POSTFIELDS, param_string)
                ch.setopt(ch.POST, True)

        elif method == AwsClientS3Const.METHOD_HEAD:

            ch.setopt(ch.NOBODY, True)

        buff = StringIO()
        ch.setopt(ch.WRITEFUNCTION, buff.write)

        LOG.info("Func: %s" % client_function)
        LOG.info("URL: %s" % url)
        LOG.info("Method: %s" % method)
        LOG.info("Authorization: %s" % hAuthorization_list)
        LOG.info("PostFields: %s" % param_string)

        ch.perform()
        var = buff.getvalue()
        httpStatus = ch.getinfo(ch.HTTP_CODE)
        contentType = ch.getinfo(ch.CONTENT_TYPE)

        LOG.info("HttpStatus: %s" % httpStatus)
        LOG.info("ContentType: %s" % contentType)
        LOG.info("Response: %s" % var)

        ch.close()

        if not self.judgeHttpStatus(client_function,
                                    HTTP_STATUS_NORMAL_LIST,
                                    httpStatus):

            httpStatusCode = httpStatus
            errResponse = var
            contentType = contentType.lower()
            if contentType == 'application/json':
                errResponse = json.loads(errResponse)
            elif contentType == 'text/xml':
                errResponse = self.xml_to_dict(errResponse)
            raise Exception(json.dumps({'msg': 'Http_Status_Error',
                                        'function': client_function,
                                        'http_status': httpStatus,
                                        'response': errResponse}),
                            httpStatusCode)

        ret = {}
        if var:
            if response_type == 'xml':
                ret = self.xml_to_dict(var)
            else:
                if contentType.lower() == 'text/xml':
                    ret = self.xml_to_dict(var)
                elif contentType.lower() == 'application/xml':
                    ret = self.xml_to_dict(var)
                else:
                    ret = json.loads(var)

        return ret

    def xml_to_dict(self, country_data_as_string):
        root = ET.fromstring(country_data_as_string)
        return self.analyze_tree(root)

    def analyze_tree(self, node):

        return_children = {}
        for child in node:
            child.tag = re.sub(r'\{.*\}', '', child.tag)

            if child.text is None:
                bucket = self.analyze_tree(child)
            else:
                bucket = child.text

            if child.tag in return_children:
                if not isinstance(return_children[child.tag], list):
                    buff = return_children[child.tag]
                    return_children[child.tag] = [buff]
                return_children[child.tag].append(bucket)
            else:
                return_children[child.tag] = bucket

        return return_children

    def judgeHttpStatus(self, client_function, http_status_normal_list,
                        http_status):

        ret = True

        if client_function in http_status_normal_list:

            normalStatusList = http_status_normal_list[client_function]

            if len(normalStatusList) > 0:

                if http_status not in normalStatusList:
                    ret = False

        return ret

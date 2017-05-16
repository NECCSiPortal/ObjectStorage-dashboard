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

METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_PUT = 'PUT'
METHOD_DELETE = 'DELETE'
METHOD_HEAD = 'HEAD'

KEY_TOKEN = '_TOKEN'
KEY_ENDPOINT = '_ENDPOINT'
KEY_REQUESTID = '_REQUESTID'

Exce_Message_01 = 'error args key'
Exce_Message_02 = 'error GET REST I/F'
Exce_Message_03 = 'error POST REST I/F'
Exce_Message_04 = 'error PUT REST I/F'
Exce_Message_05 = 'error DELETE REST I/F'
Exce_Message_06 = 'error memcached of token id'
Exce_Message_07 = 'error memcached of endpoint'
Exce_Message_08 = 'error ENDPOINT was not found.'
Exce_Message_08 += ' Probably, you do not have authority.'
Exce_Message_09 = 'error OpenStack Non Response'
Exce_Message_10 = 'error memcached set'
Exce_Message_11 = 'error update quotas'
Exce_Message_12 = 'error endpoint not defined in config'

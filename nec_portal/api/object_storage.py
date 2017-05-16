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

from __future__ import absolute_import

import copy
import json
import keystoneclient
import logging
import re

from horizon import exceptions

from nec_portal.api.AwsClient.S3.client.buckets import ObjsAwsS3Buckets
from nec_portal.api.AwsClient.S3.client.services import ObjsAwsS3Services
from nec_portal.local import nec_portal_settings as local_set

from openstack_auth import utils as auth_utils
from openstack_dashboard import api

LOG = logging.getLogger(__name__)
KEYSTONE_ADMIN_SETTING = getattr(local_set, 'KEYSTONE_ADMIN_SETTING', None)
OBJECT_STORAGE_ADMIN = getattr(local_set, 'OBJECT_STORAGE_ADMIN', None)

HTTP_ERROR_CODE = 68000
TIME_OUT = 60

BUCKET_POLICY_ADMIN = "0"
BUCKET_POLICY_ALLOW_READ_WRITE = "1"
BUCKET_POLICY_ALLOW_READ_ONLY = "2"
BUCKET_POLICY_DENY = "3"

BUCKET_POLICY_STATEMENT = {
  'R': [
    {
      'Effect': 'Allow',
      'Principal': {'AWS': 'arn:aws:iam::%TENANT_ID%:user/%USER_NAME%'},
      'Action': ['s3:ListBucket'],
      'Resource': ['arn:aws:s3:::%BUCKET%'],
    },
    {
      'Effect': 'Allow',
      'Principal': {'AWS': 'arn:aws:iam::%TENANT_ID%:user/%USER_NAME%'},
      'Action': ['s3:GetObject'],
      'Resource': ['arn:aws:s3:::%BUCKET%/*'],
    },
  ],
  'RW': [
    {
      'Effect': 'Allow',
      'Principal': {'AWS': 'arn:aws:iam::%TENANT_ID%:user/%USER_NAME%'},
      'Action': ['s3:ListBucket'],
      'Resource': ['arn:aws:s3:::%BUCKET%'],
    },
    {
      'Effect': 'Allow',
      'Principal': {'AWS': 'arn:aws:iam::%TENANT_ID%:user/%USER_NAME%'},
      'Action': ['s3:GetObject', 's3:PutObject', 's3:DeleteObject'],
      'Resource': ['arn:aws:s3:::%BUCKET%/*'],
    },
  ],
  'ACL': [
    {
      'Effect': 'Allow',
      'Principal': {'AWS': 'arn:aws:iam::%TENANT_ID%:user/%USER_NAME%'},
      'Action': ['s3:GetBucketPolicy',
                 's3:PutBucketPolicy',
                 's3:DeleteBucketPolicy'],
      'Resource': ['arn:aws:s3:::%BUCKET%'],
    },
  ],
}


# Set up our data structure for managing Identity API versions, and
# add a couple utility methods to it.
class IdentityAPIVersionManager(api.base.APIVersionManager):
    def upgrade_v2_user(self, user):
        if getattr(user, "project_id", None) is None:
            user.project_id = getattr(user, "default_project_id",
                                      getattr(user, "tenantId", None))
        return user

    def get_project_manager(self, *args, **kwargs):
        if VERSIONS.active < 3:
            manager = keystoneclient(*args, **kwargs).tenants
        else:
            manager = keystoneclient(*args, **kwargs).projects
        return manager

VERSIONS = IdentityAPIVersionManager(
    "identity", preferred_version=auth_utils.get_keystone_version())


# Import from oldest to newest so that "preferred" takes correct precedence.
try:
    from keystoneclient.v2_0 import client as keystone_client_v2
    VERSIONS.load_supported_version(2.0, {"client": keystone_client_v2})
except ImportError:
    pass

try:
    from keystoneclient.v3 import client as keystone_client_v3
    VERSIONS.load_supported_version(3, {"client": keystone_client_v3})
except ImportError:
    pass


def _get_keystone_client():

    api_version = VERSIONS.get_active_version()
    return api_version['client'].Client(
            username=KEYSTONE_ADMIN_SETTING['username'],
            password=KEYSTONE_ADMIN_SETTING['password'],
            tenant_name=KEYSTONE_ADMIN_SETTING['tenant_name'],
            auth_url=KEYSTONE_ADMIN_SETTING['auth_url'])


def _get_ec2_credentials(request):
    tenant_id = request.user.tenant_id
    all_keys = api.keystone.list_ec2_credentials(request,
                                                 request.user.id)

    key = next((x for x in all_keys if x.tenant_id == tenant_id), None)
    if not key:
        key = api.keystone.create_ec2_credentials(request,
                                                  request.user.id,
                                                  tenant_id)
    try:
        s3_endpoint = api.base.url_for(request,
                                       's3',
                                       endpoint_type='internalURL')
    except exceptions.ServiceCatalogException:
        s3_endpoint = None

    return {'ec2_access_key': key.access,
            'ec2_secret_key': key.secret,
            's3_endpoint': s3_endpoint}


def _get_account_admin_user(request):

    users_roles = []
    keystoneclient = _get_keystone_client()
    key_role = ''
    all_roles = keystoneclient.roles.list()
    for role in all_roles:
        if role.name == OBJECT_STORAGE_ADMIN:
            key_role = role.id

    if VERSIONS.active < 3:
        project_users = keystoneclient.users.list(
                tenant_id=request.user.project_id)

        for user in project_users:
            user_roles = keystoneclient.roles.roles_for_user(
                    user=user.id,
                    tenant=request.user.project_id)
            for role in user_roles:
                if role.id == key_role:
                    users_roles.append(user.id)

    else:
        project_role_assignments = keystoneclient.role_assignments.list(
                project=request.user.project_id)

        for role_assignment in project_role_assignments:
            if hasattr(role_assignment, 'user'):
                user_id = role_assignment.user['id']
                role_id = role_assignment.role['id']
                if role_id == key_role:
                    users_roles.append(user_id)
            elif hasattr(role_assignment, 'group'):
                group_id = role_assignment.group['id']
                role_id = role_assignment.role['id']
                if role_id == key_role:
                    group_users = keystoneclient.users.list(
                            group=group_id,
                            project=request.user.project_id)
                    users_roles.extend([user.id for user in group_users])

        users_roles = list(set(users_roles))

    return users_roles


def obst_get_bucket_list(self):

    creds = _get_ec2_credentials(self.request)
    endpoint = creds['s3_endpoint'].encode('utf-8')
    access_key = creds['ec2_access_key'].encode('utf-8')
    secret_key = creds['ec2_secret_key'].encode('utf-8')

    return ObjsAwsS3Services().getService(endpoint,
                                          access_key,
                                          secret_key,
                                          HTTP_ERROR_CODE,
                                          TIME_OUT)


def obst_get_bucket_policy(self, bucket_name):

    creds = _get_ec2_credentials(self.request)
    endpoint = creds['s3_endpoint'].encode('utf-8')
    access_key = creds['ec2_access_key'].encode('utf-8')
    secret_key = creds['ec2_secret_key'].encode('utf-8')

    bucket_out = ObjsAwsS3Buckets().getBucketPolicy(endpoint,
                                                    access_key,
                                                    secret_key,
                                                    bucket_name,
                                                    HTTP_ERROR_CODE,
                                                    TIME_OUT)

    if 'Statement' not in bucket_out:
        bucket_out = {'Statement': []}

    statementList = bucket_out['Statement']

    keystoneclient = _get_keystone_client()
    users_roles = []
    if VERSIONS.active < 3:
        project_users = keystoneclient.users.list(
                tenant_id=self.request.user.project_id)
        for user in project_users:
            users_roles.append(user.id)
    else:
        project_users = keystoneclient.role_assignments.list(
                project=self.request.user.project_id)

        for project_user in project_users:
            if not hasattr(project_user, 'user'):
                continue
            user_id = project_user.user['id']
            users_roles.append(user_id)

    for project_user in project_users:
        if not hasattr(project_user, 'user'):
            continue
        user_id = project_user.user['id']
        users_roles.append(user_id)

    users_list = []
    all_users = keystoneclient.users.list()
    for user_data in all_users:
        if user_data.id in users_roles:
            users_list.append(user_data)

    statementAction = {}
    for key, stmList in BUCKET_POLICY_STATEMENT.iteritems():

        statementAction[key] = []

        for stm in stmList:
            statementAction[key].extend(stm['Action'])

    actionList = {}
    for statement in statementList:

        effect = statement['Effect']
        principal = statement['Principal']
        action = statement['Action']
        resource = statement['Resource']

        if not isinstance(effect, unicode) or not isinstance(principal, dict)\
           or not isinstance(action, list) or not isinstance(resource, list):
            continue

        if 'AWS' not in principal:
            continue
        aws = principal['AWS']

        if not isinstance(aws, unicode) or aws is None:
            continue

        if effect != 'Allow':
            continue

        resourceMatched = False
        for resourceElement in resource:

            retResourceMatch = re.match(r'.+:([^:]+)', resourceElement)
            if retResourceMatch is not None and\
               retResourceMatch.group(1) == bucket_name:
                resourceMatched = True
                break
            else:
                retResourceMatch = re.match(r'.+:([^:]+)\/\*',
                                            resourceElement)
                if retResourceMatch is not None and\
                   retResourceMatch.group(1) == bucket_name:
                    resourceMatched = True
                    break

        if not resourceMatched:
            continue

        userName = ''
        ret = re.match(r'.+/([^/]+)', aws)

        if ret:
            userName = ret.group(1)

        if not userName:
            continue

        if userName in actionList:
            actionList[userName].extend(action)

        else:
            actionList[userName] = action

    permissionArray = {}
    for user, actionArray in actionList.iteritems():

        permissionArray[user] = {}

        aclRead = copy.deepcopy(statementAction['R'])
        for valuse in statementAction['R']:
            for value_sub in actionArray:
                if valuse == value_sub:
                    aclRead.remove(valuse)
                    break

        aclReadWrite = copy.deepcopy(statementAction['RW'])
        for valuse in statementAction['RW']:
            for value_sub in actionArray:
                if valuse == value_sub:
                    aclReadWrite.remove(valuse)
                    break

        acpReadWrite = copy.deepcopy(statementAction['ACL'])
        for valuse in statementAction['ACL']:
            for value_sub in actionArray:
                if valuse == value_sub:
                    acpReadWrite.remove(valuse)
                    break

        if len(aclRead) == 0 and len(aclReadWrite) > 0:
            permissionArray[user]['rightSetting'] =\
                BUCKET_POLICY_ALLOW_READ_ONLY
        elif len(aclReadWrite) == 0:
            permissionArray[user]['rightSetting'] =\
                BUCKET_POLICY_ALLOW_READ_WRITE
        else:
            permissionArray[user]['rightSetting'] =\
                BUCKET_POLICY_DENY

        if len(acpReadWrite) == 0:
            permissionArray[user]['accessRightSetting'] =\
                BUCKET_POLICY_ALLOW_READ_WRITE
        else:
            permissionArray[user]['accessRightSetting'] =\
                BUCKET_POLICY_DENY

    admin_user = _get_account_admin_user(self.request)

    permissionList = []
    for usersArray in users_list:
        name = usersArray.name

        if usersArray.id in admin_user:
            permissionData = {
                'ID': name,
                'Access_authority': BUCKET_POLICY_ADMIN,
                'Access_policy': BUCKET_POLICY_ADMIN,
            }
        elif name in permissionArray:
            permissionData = {
                'ID': name,
                'Access_authority': permissionArray[name]['rightSetting'],
                'Access_policy': permissionArray[name]['accessRightSetting'],
            }
        else:
            permissionData = {
                'ID': name,
                'Access_authority': BUCKET_POLICY_DENY,
                'Access_policy': BUCKET_POLICY_DENY,
            }

        if self.request.user.id == usersArray.id:
            if permissionData['Access_policy'] == BUCKET_POLICY_DENY:
                raise Exception()

        permissionList.append(permissionData)

    return permissionList


def obst_put_bucket_policy(self, bucket_name, policy):

    creds = _get_ec2_credentials(self.request)
    endpoint = creds['s3_endpoint'].encode('utf-8')
    access_key = creds['ec2_access_key'].encode('utf-8')
    secret_key = creds['ec2_secret_key'].encode('utf-8')

    statementArray = []
    for permissionArray in policy:

        statement = []

        loginid = permissionArray['ID']
        access_authority = permissionArray['Access_authority']
        access_policy = permissionArray['Access_policy']

        if access_authority == BUCKET_POLICY_ALLOW_READ_ONLY:
            statement.extend(copy.deepcopy(BUCKET_POLICY_STATEMENT['R']))
        elif access_authority == BUCKET_POLICY_ALLOW_READ_WRITE:
            statement.extend(copy.deepcopy(BUCKET_POLICY_STATEMENT['RW']))
        elif access_authority == BUCKET_POLICY_DENY:
            pass
        else:
            raise Exception()

        if access_policy == BUCKET_POLICY_ALLOW_READ_WRITE:
            statement.extend(copy.deepcopy(BUCKET_POLICY_STATEMENT['ACL']))
        elif access_policy == BUCKET_POLICY_DENY:
            pass
        else:
            raise Exception()

        if len(statement) == 0:
            continue

        statementJson = json.dumps(statement)

        statementJson = statementJson.replace('%TENANT_ID%',
                                              self.request.user.project_id)
        statementJson = statementJson.replace('%USER_NAME%', loginid)
        statementJson = statementJson.replace('%BUCKET%', bucket_name)

        statementArray.extend(json.loads(statementJson))

    return ObjsAwsS3Buckets().putBucketPolicy(endpoint,
                                              access_key,
                                              secret_key,
                                              bucket_name,
                                              statementArray,
                                              HTTP_ERROR_CODE,
                                              TIME_OUT)

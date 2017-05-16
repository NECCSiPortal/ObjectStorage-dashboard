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

import copy
from django.conf import settings
from django.test.utils import override_settings
from mox import IsA  # noqa

from keystoneclient import client

from nec_portal import api as nec_api
from nec_portal.api.AwsClient.S3.client import buckets
from nec_portal.api.AwsClient.S3.client import services
from nec_portal.api.AwsClient.S3.client.buckets import ObjsAwsS3Buckets
from nec_portal.api.AwsClient.S3.client.services import ObjsAwsS3Services
from nec_portal.api import object_storage  # noqa

from openstack_dashboard import api
from openstack_dashboard.api import base
from openstack_dashboard.api import keystone
from openstack_dashboard.test import helpers as test

HTTP_ERROR_CODE = 68000
TIME_OUT = 60
BUCKET_NAME = 'test_container'

BUCKET_LIST_DATA = {
    'Owner': {
        'DisplayName': 'SS:sasada',
        'ID': 'SS:sasada'
    },
    'Buckets': {
        'Bucket': [
            {
                'CreationDate': '2009-02-03T16:45:00.000Z',
                'Name': 'test_container'
            },
            {
                'CreationDate': '2009-02-03T16:45:00.000Z',
                'Name': 'test_container2'
            }
        ]
    }
}

BUCKET_POLICY_DATA = {
    "Statement": [
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
        {
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container/*"
            ]
        },
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa2"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
        {
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa2"
            },
            "Resource": [
                "arn:aws:s3:::test_container/*"
            ]
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa3"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
        {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa3"
            },
            "Resource": [
                "arn:aws:s3:::test_container/*"
            ]
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-bbb1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
        {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-bbb1"
            },
            "Resource": [
                "arn:aws:s3:::test_container/*"
            ]
        },
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-bbb1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-bbb2"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        }
    ]
}

BUCKET_POLICY_ERROR_DATA = {
    "Statement": [
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

BUCKET_POLICY_VALIDATE_EFFECT = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": "Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

BUCKET_POLICY_VALIDATE_PRINCIPAL = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": [
                "AWS", u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            ],
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

BUCKET_POLICY_VALIDATE_ACTION = {
    "Statement": [
        {
            "Action": {
                "s3": "ListBucket"
            },
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

BUCKET_POLICY_VALIDATE_RESOURCE = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": {
                "arn": "aws:s3:::test_container"
            }
        },
    ]
}

BUCKET_POLICY_VALIDATE_AWS = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": "arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

BUCKET_POLICY_VALIDATE_NOT_ALLOWED = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"NonAllow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

BUCKET_NAME_MISSMATCH = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name-aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test:container"
            ]
        },
    ]
}

BUCKET_POLICY_NOT_GET_USER_NAME = {
    "Statement": [
        {
            "Action": [
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:DeleteBucketPolicy"
            ],
            "Effect": u"Allow",
            "Principal": {
                "AWS": u"arn:aws:iam::23709113353b48c3a96ec:user/name/aaa1"
            },
            "Resource": [
                "arn:aws:s3:::test_container"
            ]
        },
    ]
}

PROJECT_USER_LIST = [
    {'user': {'id': 'aaa1'}},
    {'user': {'id': 'aaa2'}},
    {'user': {'id': 'aaa3'}},
    {'user': {'id': 'aaa4'}},
    {'user': {'id': 'aaa5'}},
]

USER_LIST = [
    {'name': 'name-aaa1', 'id': 'aaa1'},
    {'name': 'name-aaa2', 'id': 'aaa2'},
    {'name': 'name-aaa3', 'id': 'aaa3'},
    {'name': 'name-bbb1', 'id': 'aaa4'},
    {'name': 'name-bbb2', 'id': 'aaa5'},
    {'name': 'name-bbb3', 'id': 'aaa6'},
]

USERS_POLICY_LIST = [
    {
        'ID': 'name-aaa1',
        'Access_authority': '1',
        'Access_policy': '1'
    },
    {
        'ID': 'name-aaa2',
        'Access_authority': '1',
        'Access_policy': '3'
    },
    {
        'ID': 'name-aaa3',
        'Access_authority': '2',
        'Access_policy': '3'
    },
    {
        'ID': 'name-bbb1',
        'Access_authority': '2',
        'Access_policy': '1'
    },
    {
        'ID': 'name-bbb2',
        'Access_authority': '3',
        'Access_policy': '1'
    }
]


class ObjectStorageApiTests(test.APITestCase):

    def setUp(self):
        super(ObjectStorageApiTests, self).setUp()

        # Store the original clients
        self._original_awsclient_services = services.ObjsAwsS3Services
        self._original_awsclient_buckets = buckets.ObjsAwsS3Buckets
        self._original_keystoneclient = nec_api.object_storage.keystoneclient
        self._original_api_keystone = api.keystone
        self._original_api_base = api.base

        # Replace the clients with our stubs.
        services.ObjsAwsS3Services = \
            lambda request: self.stub_awsclient_services()
        buckets.ObjsAwsS3Buckets = \
            lambda request: self.stub_awsclient_buckets()
        nec_api.object_storage.keystoneclient = \
            lambda request: self.stub_keystoneclient()
        api.keystone = lambda request: self.stub_api_keystone()
        api.base = lambda request: self.stub_api_base()

    def tearDown(self):
        super(ObjectStorageApiTests, self).tearDown()

        services.ObjsAwsS3Services = self._original_awsclient_services
        buckets.ObjsAwsS3Buckets = self._original_awsclient_buckets
        nec_api.object_storage.keystoneclient = self._original_keystoneclient
        api.keystone = self._original_api_keystone
        api.base = self._original_api_base

    def stub_awsclient_services(self):
        if not hasattr(self, "ObjsAwsS3Services"):
            self.mox.StubOutWithMock(ObjsAwsS3Services, 'getService')
            self.ObjsAwsS3Services = self.mox.CreateMock(ObjsAwsS3Services)
        return self.ObjsAwsS3Services

    def stub_awsclient_buckets(self):
        if not hasattr(self, "ObjsAwsS3Buckets"):
            self.mox.StubOutWithMock(ObjsAwsS3Buckets, 'getBucketPolicy')
            self.mox.StubOutWithMock(ObjsAwsS3Buckets, 'putBucketPolicy')
            self.ObjsAwsS3Buckets = self.mox.CreateMock(ObjsAwsS3Buckets)
        return self.ObjsAwsS3Buckets

    def stub_keystoneclient(self):
        if not hasattr(self, "keystoneclient"):
            self.mox.StubOutWithMock(client, 'Client')
            self.keystoneclient = self.mox.CreateMock(client.Client)
        return self.keystoneclient

    def stub_api_keystone(self):
        if not hasattr(self, "keystone"):
            self.mox.StubOutWithMock(keystone, 'list_ec2_credentials')
            self.keystone = self.mox.CreateMock(keystone)
        return self.keystone

    def stub_api_base(self):
        if not hasattr(self, "base"):
            self.mox.StubOutWithMock(base, 'url_for')
            self.base = self.mox.CreateMock(base)
        return self.base

    def test_bucket_list(self):
        """Test 'Get list of buckets'
        Test the operation of get standard data.
        """
        self._get_ec2_credentials_stub()

        services = self.stub_awsclient_services()
        ObjsAwsS3Services().getService('http://localhost:8080/',
                                       '8aa2e867951c4d7f8e95b1dd37cabf37',
                                       '8aa2e867951c4d7f8e95b1dd37cabf37',
                                       HTTP_ERROR_CODE, TIME_OUT) \
            .AndReturn(BUCKET_LIST_DATA)
        self.mox.ReplayAll()

        bucket_list = \
            nec_api.object_storage.obst_get_bucket_list(self)
        self.assertItemsEqual(bucket_list, BUCKET_LIST_DATA)

    def test_bucket_list_get_exception_irregular(self):
        """Test 'Get list of buckets'
        Test the operation of raise Exception.
        """
        self._get_ec2_credentials_stub()

        services = self.stub_awsclient_services()
        ObjsAwsS3Services().getService('http://localhost:8080/',
                                       '8aa2e867951c4d7f8e95b1dd37cabf37',
                                       '8aa2e867951c4d7f8e95b1dd37cabf37',
                                       HTTP_ERROR_CODE, TIME_OUT) \
            .AndRaise(OSError)
        self.mox.ReplayAll()

        self.assertRaises(OSError,
                          nec_api.object_storage.obst_get_bucket_list,
                          self)

    def test_get_bucket_policy(self):
        """Test 'Get of buckets policy'
        Test the operation of get all of the check pattern data.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_DATA)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        for data in PROJECT_USER_LIST:
            return_obj = Keystone()
            return_obj.add('user', data['user'])
            project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        for data in USER_LIST:
            return_obj = Keystone()
            return_obj.add('name', data['name'])
            return_obj.add('id', data['id'])
            user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'],
                              USERS_POLICY_LIST[0]['Access_authority'])
        self.assertItemsEqual(policy_list[0]['Access_policy'],
                              USERS_POLICY_LIST[0]['Access_policy'])
        self.assertItemsEqual(policy_list[1]['ID'], USERS_POLICY_LIST[1]['ID'])
        self.assertItemsEqual(policy_list[1]['Access_authority'],
                              USERS_POLICY_LIST[1]['Access_authority'])
        self.assertItemsEqual(policy_list[1]['Access_policy'],
                              USERS_POLICY_LIST[1]['Access_policy'])
        self.assertItemsEqual(policy_list[2]['ID'], USERS_POLICY_LIST[2]['ID'])
        self.assertItemsEqual(policy_list[2]['Access_authority'],
                              USERS_POLICY_LIST[2]['Access_authority'])
        self.assertItemsEqual(policy_list[2]['Access_policy'],
                              USERS_POLICY_LIST[2]['Access_policy'])
        self.assertItemsEqual(policy_list[3]['ID'], USERS_POLICY_LIST[3]['ID'])
        self.assertItemsEqual(policy_list[3]['Access_authority'],
                              USERS_POLICY_LIST[3]['Access_authority'])
        self.assertItemsEqual(policy_list[3]['Access_policy'],
                              USERS_POLICY_LIST[3]['Access_policy'])
        self.assertItemsEqual(policy_list[4]['ID'], USERS_POLICY_LIST[4]['ID'])
        self.assertItemsEqual(policy_list[4]['Access_authority'],
                              USERS_POLICY_LIST[4]['Access_authority'])
        self.assertItemsEqual(policy_list[4]['Access_policy'],
                              USERS_POLICY_LIST[4]['Access_policy'])


    def test_get_bucket_policy_non_users_policy_data(self):
        """Test 'Get of buckets policy'
        Test of if the user of the policy can not be acquired.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn({"Statement": []})

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_non_user_data(self):
        """Test 'Get of buckets policy'
        Test of if the user can not get.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_DATA)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list, [])

    def test_get_bucket_policy_validation_check_effect(self):
        """Test 'Get of buckets policy'
        Test of if the effect is caught in the syntax check.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_VALIDATE_EFFECT)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_validation_check_principal(self):
        """Test 'Get of buckets policy'
        Test of if the principal is caught in the syntax check.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_VALIDATE_PRINCIPAL)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_validation_check_action(self):
        """Test 'Get of buckets policy'
        Test of if the action is caught in the syntax check.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_VALIDATE_ACTION)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_validation_check_resource(self):
        """Test 'Get of buckets policy'
        Test of if the resource is caught in the syntax check.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_VALIDATE_RESOURCE)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_validation_check_aws(self):
        """Test 'Get of buckets policy'
        Test of if the aws is caught in the syntax check.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_VALIDATE_AWS)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_effect_is_not_allowed(self):
        """Test 'Get of buckets policy'
        Test of if the effect is not 'Allowed'.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_VALIDATE_NOT_ALLOWED)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_backet_name_mismatch(self):
        """Test 'Get of buckets policy'
        Test of if the bucket name is not '...:bucket_name'.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_NAME_MISSMATCH)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_not_get_user_name(self):
        """Test 'Get of buckets policy'
        Test of if the user name is not '.../user_name'.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndReturn(BUCKET_POLICY_NOT_GET_USER_NAME)

        keystoneclient = self.stub_keystoneclient()
        self.mox.StubOutWithMock(object_storage, 'get_keystone_client')
        object_storage.get_keystone_client().AndReturn(keystoneclient)

        project_user_return = []
        return_obj = Keystone()
        return_obj.add('user', PROJECT_USER_LIST[0]['user'])
        project_user_return.append(return_obj)
        keystoneclient.role_assignments = self.mox.CreateMockAnything()
        keystoneclient.role_assignments.list(project=IsA(str)) \
            .AndReturn(project_user_return)

        user_return = []
        return_obj = Keystone()
        return_obj.add('name', USER_LIST[0]['name'])
        return_obj.add('id', USER_LIST[0]['id'])
        user_return.append(return_obj)
        keystoneclient.users = self.mox.CreateMockAnything()
        keystoneclient.users.list() \
            .AndReturn(user_return)

        self.mox.ReplayAll()

        policy_list = \
            nec_api.object_storage.obst_get_bucket_policy(self, BUCKET_NAME)
        self.assertItemsEqual(policy_list[0]['ID'], USERS_POLICY_LIST[0]['ID'])
        self.assertItemsEqual(policy_list[0]['Access_authority'], '3')
        self.assertItemsEqual(policy_list[0]['Access_policy'], '3')

    def test_get_bucket_policy_get_exception_irregular(self):
        """Test 'Get of buckets policy'
        Test the operation of raise Exception.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().getBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, HTTP_ERROR_CODE,
                                           TIME_OUT) \
            .AndRaise(OSError)
        self.mox.ReplayAll()

        self.assertRaises(OSError,
                          nec_api.object_storage.obst_get_bucket_policy,
                          self,
                          BUCKET_NAME)

    def test_put_bucket_policy(self):
        """Test 'Update of buckets policy'
        Test the operation of update all of the check pattern data.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().putBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, IsA(list),
                                           HTTP_ERROR_CODE, TIME_OUT) \
            .AndReturn([])

        self.mox.ReplayAll()

        policy_update = \
            nec_api.object_storage.obst_put_bucket_policy(self,
                                                          BUCKET_NAME,
                                                          USERS_POLICY_LIST)
        self.assertItemsEqual(policy_update, [])

    def test_put_bucket_policy_checked_number_irregular(self):
        """Test 'Get of buckets policy'
        Test of if unexpected check.
        """
        self._get_ec2_credentials_stub()

        self.mox.ReplayAll()

        ERROR_USERS_POLICY_LIST = copy.deepcopy(USERS_POLICY_LIST)
        ERROR_USERS_POLICY_LIST[2]['Access_policy'] = '4'

        self.assertRaises(Exception,
                          nec_api.object_storage.obst_put_bucket_policy,
                          self,
                          BUCKET_NAME,
                          ERROR_USERS_POLICY_LIST)

    def test_put_bucket_policy_get_exception_irregular(self):
        """Test 'Get of buckets policy'
        Test the operation of raise Exception.
        """
        self._get_ec2_credentials_stub()

        buckets = self.stub_awsclient_buckets()
        ObjsAwsS3Buckets().putBucketPolicy('http://localhost:8080/',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           '8aa2e867951c4d7f8e95b1dd37cabf37',
                                           BUCKET_NAME, IsA(list),
                                           HTTP_ERROR_CODE, TIME_OUT) \
            .AndRaise(OSError)
        self.mox.ReplayAll()

        self.assertRaises(OSError,
                          nec_api.object_storage.obst_put_bucket_policy,
                          self,
                          BUCKET_NAME,
                          USERS_POLICY_LIST)

    def _get_ec2_credentials_stub(self):
        return_obj = Keystone()
        return_obj.add('tenant_id', 'test')
        return_obj.add('access', '8aa2e867951c4d7f8e95b1dd37cabf37')
        return_obj.add('secret', '8aa2e867951c4d7f8e95b1dd37cabf37')
        api.keystone = self.stub_api_keystone()
        api.keystone.list_ec2_credentials(IsA(self.request), IsA(str)) \
            .AndReturn([return_obj])

        api.keystone.create_ec2_credentials(IsA(self.request),
                                            IsA(str),
                                            IsA(str)) \
            .AndReturn(return_obj)

        api.base = self.stub_api_base()
        api.base.url_for(IsA(self.request), 's3', endpoint_type='publicURL') \
            .AndReturn('http://localhost:8080/')

        api.base.url_for(IsA(self.request), 'ec2', endpoint_type='publicURL') \
            .AndReturn('http://localhost:8080/')


class Keystone(object):

    def add(self, key, value):
        self.__dict__[key] = value

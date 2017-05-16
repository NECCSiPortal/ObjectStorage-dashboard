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

"""Bucket_lists data
BUCKET_LISTS_DATA_LIST[0] no records
BUCKET_LISTS_DATA_LIST[1] exist records
"""
BUCKET_LISTS_DATA_LIST = [
    {},
    {
        'Owner': {
            'ID': 'SS:sasada',
            'DisplayName' : 'SS:sasada'
        },
        'Buckets': {
            'Bucket':[
                {
                    'Name': 'Bucket_sample',
                    'CreationDate': '2009-02-03T16:45:00.000Z'
                },
                {
                    'Name': 'Bucket_sample_2',
                    'CreationDate': '2009-02-03T16:45:00.000Z'
                },
            ]
        }
    },
]

"""Bucket_ACL data
BUCKET_ACL_DATA_LIST[0] exist records
BUCKET_ACL_DATA_LIST[1] UpdateACLForm::inputs
"""
BUCKET_ACL_DATA_LIST = [
    [
	    {'ID': 'login_id1', 'Access_authority': '1', 'Access_policy': '1'},
        {'ID': 'login_id2', 'Access_authority': '2', 'Access_policy': '2'},
        {'ID': 'login_id3', 'Access_authority': '3', 'Access_policy': '1'},
    ],
    [
        {'ID': 'login_id1', 'Access_authority': '1', 'Access_policy': '1'},
    ]
]

BUCKET_NAME = 'test_bucket'
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

from django.core.urlresolvers import reverse

from mox import IsA  # noqa

from openstack_dashboard.test import helpers as test

from nec_portal import api
from nec_portal.api import object_storage as obst_api
from nec_portal.dashboards.project.bucket_lists import fixture
from nec_portal.dashboards.project.bucket_lists import views

INDEX_URL      = reverse('horizon:project:bucket_lists:index')
UPDATE_ACL_URL = reverse('horizon:project:bucket_lists:update',
                         kwargs={"bucket_name": fixture.BUCKET_NAME})

class Bucket_listsViewTests(test.TestCase):
    """A test of the screen of bucket_lists.
    """
    # A test which no records
    @test.create_stubs({obst_api: ('obst_get_bucket_list',)})
    def test_bucket_lists_no_records(self):

        #Create a bucket_lists of return data.
        bucket_lists_data = fixture.BUCKET_LISTS_DATA_LIST[0]

        #Get bucket_lists.
        obst_api.obst_get_bucket_list(IsA(object)).AndReturn(bucket_lists_data)

        self.mox.ReplayAll()
        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'project/bucket_lists/index.html')
        self.assertEqual(res.status_code, 200)

    # A test which exist records
    @test.create_stubs({obst_api: ('obst_get_bucket_list',)})
    def test_bucket_lists(self):

        #Create a bucket_lists of return data.
        bucket_lists_data = fixture.BUCKET_LISTS_DATA_LIST[1]

        #Get bucket_lists.
        obst_api.obst_get_bucket_list(IsA(object)).AndReturn(bucket_lists_data)

        self.mox.ReplayAll()
        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'project/bucket_lists/index.html')
        self.assertEqual(res.status_code, 200)

    # A test which Edit Buckets ACL.
    @test.create_stubs({obst_api: ('obst_get_bucket_policy',)})
    def test_update(self):
        #XXX need add param for obst_get_bucket_policy
        #Create a bucket_ACL of return data.
        bucket_ACL = fixture.BUCKET_ACL_DATA_LIST[0]

        #Get bucket_ACL_list
        obst_api.obst_get_bucket_policy(IsA(object), fixture.BUCKET_NAME).AndReturn(bucket_ACL)

        self.mox.ReplayAll()
        res = self.client.get(UPDATE_ACL_URL)

        self.assertTemplateUsed(res, 'project/bucket_lists/update.html')
        self.assertEqual(res.status_code, 200)

    # A test which bucket_lists's post execute.
    @test.create_stubs({obst_api: ('obst_put_bucket_policy',)})
    def test_update_ACL(self):

        formData = {
            'method': 'UpdateACLForm',
            'bucket_name': fixture.BUCKET_NAME,
            'ID': 'login_id1',
            'login_id1_Access_authority': '1',
            'login_id1_Access_policy': '1',
        }

        #put_bucket_policy_inputs
        inputs = fixture.BUCKET_ACL_DATA_LIST[1]

        #put_bucket_policy
        obst_api.obst_put_bucket_policy(IsA(object), fixture.BUCKET_NAME, inputs).AndReturn(True)

        self.mox.ReplayAll()
        res = self.client.post(UPDATE_ACL_URL, formData)

        self.assertRedirectsNoFollow(res, '/project/bucket_lists/')

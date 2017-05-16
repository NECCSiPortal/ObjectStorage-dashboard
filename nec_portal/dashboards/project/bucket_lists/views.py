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

import datetime
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables

from nec_portal.api import object_storage as obst_api
from nec_portal.dashboards.project.bucket_lists \
    import constants
from nec_portal.dashboards.project.bucket_lists \
    import forms as BUCKET_LISTS_forms
from nec_portal.dashboards.project.bucket_lists \
    import tables as BUCKET_LISTS_tables
from openstack_dashboard.api import keystone as keystone_api
from openstack_dashboard import policy

LOG = logging.getLogger(__name__)


class ColumnsEscape(object):

    """Columns Escape class"""
    def __init__(self, Name, CreationDate):

        self.id = escape(Name)
        self.date = escape(CreationDate)


class IndexView(tables.DataTableView):
    table_class = BUCKET_LISTS_tables.BucketsTable
    template_name = constants.BUCKET_LISTS_INDEX_TEMPLATE
    page_title = _("Container ACL")

    def get_data(self):
        buckets = []
        bucket_list = []

        bucket = obst_api.obst_get_bucket_list(self)
        if bucket is None:
            pass
        elif 'Buckets' not in bucket:
            pass
        elif 'Bucket' not in bucket['Buckets']:
            pass
        else:
            bucket_list = bucket['Buckets']['Bucket']
            if not isinstance(bucket_list, list):
                bucket_list = [bucket_list]

        for bucket_row in bucket_list:
            if bucket_row['CreationDate'] is not None:
                CreationDate = datetime.datetime.\
                    strptime(bucket_row['CreationDate'],
                             '%Y-%m-%dT%H:%M:%S.%fZ'
                             ).strftime("%Y-%m-%d %H:%M:%S")

            columns = ColumnsEscape(bucket_row['Name'],
                                    CreationDate)

            buckets.append(columns)

        return buckets


class UpdateView(forms.ModalFormView):
    template_name = constants.BUCKET_LISTS_UPDATE_TEMPLATE
    modal_header = _("Edit Container ACL")
    form_id = "change_user_password_form"
    form_class = BUCKET_LISTS_forms.UpdateACLForm
    submit_url = constants.BUCKET_LISTS_UPDATE_URL
    submit_label = _("Save")
    success_url = reverse_lazy(constants.BUCKET_LISTS_INDEX_URL)
    page_title = _("Edit Container ACL")

    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        bucket_name = self.kwargs['bucket_name']
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (bucket_name,)
        context['submit_url'] = reverse_lazy(self.submit_url, args=args)
        context['bucket_name'] = bucket_name
        try:
            context['records'] =\
                obst_api.obst_get_bucket_policy(self,
                                                bucket_name.encode('utf-8'))
        except Exception:
            messages.error(self.request,
                           _('You do not have permission to update.'))
            return

        return context

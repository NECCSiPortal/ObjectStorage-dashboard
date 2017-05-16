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

from datetime import datetime
import logging

from django.core import exceptions as django_exceptions
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import string_concat
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions as horizon_exceptions
from horizon import forms
from horizon import messages
from horizon import tables

from nec_portal.dashboards.project.bucket_lists import constants

LOG = logging.getLogger(__name__)


class EditBucketsACLLink(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Container ACL")
    url = constants.BUCKET_LISTS_UPDATE_URL
    classes = ("ajax-modal",)
    icon = "pencil"


class BucketsFilterAction(tables.FilterAction):
    def filter(self, table, buckets, filter_string):
        q = filter_string.lower()

        def comp(bucket):
            if q in bucket.name.lower():
                return True
            return False

        return filter(comp, buckets)


class BucketsTable(tables.DataTable):
    id = tables.Column('id',
                       verbose_name=_('Name'))
    date = tables.Column('date',
                         verbose_name=_('Created Date'))

    class Meta(object):
        name = "bucket"
        verbose_name = _("Container ACL")
        multi_select = False

        table_actions = (BucketsFilterAction,)
        row_actions = (EditBucketsACLLink,)

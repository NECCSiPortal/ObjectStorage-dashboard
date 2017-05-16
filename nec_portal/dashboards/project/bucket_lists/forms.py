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

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.forms import ValidationError  # noqa
from django import http
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import functions as utils
from horizon.utils import validators

from nec_portal.api import object_storage as obst_api

from openstack_dashboard import api


LOG = logging.getLogger(__name__)

class UpdateACLForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(UpdateACLForm, self).__init__(request, *args, **kwargs)

    def handle(self, request=None, data=None):
        bucket_name = request.POST['bucket_name']
        inputs = []
        for ID in request.POST.getlist('ID'):
            tmp = {}
            tmp['ID'] = ID
            tmp['Access_authority'] = request.POST[ID+'_Access_authority']
            tmp['Access_policy'] = request.POST[ID+'_Access_policy']
            inputs.append(tmp)

        try:
            obst_api.obst_put_bucket_policy(self,
                                            bucket_name.encode('utf-8'),
                                            inputs)

            messages.success(request,
                             _('Container ACL has been updated successfully.'))
        except Exception:
            response = exceptions.handle(request, ignore=True)
            messages.error(request, _('Unable to update the Container ACL.'))

        return True

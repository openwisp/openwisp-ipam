=============
openwisp-ipam
=============

.. image:: https://github.com/openwisp/openwisp-ipam/actions/workflows/ci.yml/badge.svg?branch=master
  :target: https://github.com/openwisp/openwisp-ipam/actions/workflows/ci.yml?query=workflow%3AOpenWISP+Ipam+CI+Build%22
  :alt: CI Build status

.. image:: https://coveralls.io/repos/openwisp/openwisp-ipam/badge.svg
  :target: https://coveralls.io/r/openwisp/openwisp-ipam
  :alt: Coverage

.. image:: https://img.shields.io/pypi/v/openwisp-ipam
  :target: https://pypi.org/project/openwisp-ipam
  :alt: PyPI

.. image:: https://requires.io/github/openwisp/openwisp-ipam/requirements.svg?branch=master
  :target: https://requires.io/github/openwisp/openwisp-ipam/requirements/?branch=master
  :alt: Requirements Status

.. image:: https://github.com/openwisp/openwisp-ipam/raw/master/docs/subnet_demo.gif
  :alt: Feature Highlights

.. contents:: **Table of Contents**:
   :backlinks: none
   :depth: 2

Available Features
******************

* IPv4 and IPv6 IP address management
* IPv4 and IPv6 Subnet management
* Automatic free space display for all subnets
* Visual display for a specific subnet
* IP request module
* REST API for CRUD operations and main features
* Possibility to search for an IP or subnet
* CSV Import and Export of subnets and their IPs

Project Goals
*************

* provide basic features of IP Address management as a reusable django app
* integrate this module in the rest of the OpenWISP ecosystem
* allow standalone usage (without the rest of OpenWISP)
* provide ways to extended the core features in order to create derivatives

Dependencies
************

* Python 3.6 or higher
* Django 2.2 or higher
* Django REST Framework (for the REST API)
* openwisp-users
* swapper

Install stable version
**********************

.. code-block:: shell

    pip install openwisp-ipam

Install development version
***************************

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-ipam/tarball/master

Alternatively you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-ipam#egg=openwisp-ipam

Installation for development
****************************

Install ``openwisp-ipam`` for development using following commands:

.. code-block:: shell

    git clone https://github.com/openwisp/openwisp-ipam.git
    cd openwisp-ipam
    pip install -e .
    pip install -r requirements-test.txt

Launch the development sever:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver

You can access the admin interface at `http://127.0.0.1:8000/admin/`.

Run Tests
=========

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Then run the test suite:

.. code-block:: shell

    # options "--keepdb" & "--parallel" are optional but
    # improve time required for running tests.
    ./runtests.py --keepdb --parallel
    # Run tests for the sample_app
    SAMPLE_APP=1 ./runtests.py --keepdb --parallel

Visual Display of subnets
*************************

openwisp-ipam provides a graphical representation of a subnet which shows the available free space under any subnet.

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/master/docs/visual-display.png

REST API
********

Live documentation
==================

.. image:: https://github.com/openwisp/openwisp-ipam/raw/master/docs/api-docs.png

A general live API documentation (following the OpenAPI specification) is available at ``/api/v1/docs/``.

Browsable web interface
=======================

.. image:: https://github.com/openwisp/openwisp-ipam/raw/master/docs/api-ui.png

Additionally, opening any of the endpoints `listed below <#list-of-endpoints>`_
directly in the browser will show the `browsable API interface of Django-REST-Framework
<https://www.django-rest-framework.org/topics/browsable-api/>`_,
which makes it even easier to find out the details of each endpoint.

Authentication
==============

See openwisp-users: `authenticating with the user token
<https://github.com/openwisp/openwisp-users#authenticating-with-the-user-token>`_.

When browsing the API via the `Live documentation <#live-documentation>`_
or the `Browsable web page <#browsable-web-interface>`_, you can also use
the session authentication by logging in the django admin.

Pagination
==========

All *list* endpoints support the ``page_size`` parameter that allows paginating
the results in conjunction with the ``page`` parameter.

.. code-block:: text

    GET /api/v1/<api endpoint url>/?page_size=10
    GET /api/v1/<api endpoint url>/?page_size=10&page=2

List of endpoints
=================

Since the detailed explanation is contained in the `Live documentation <#live-documentation>`_
and in the `Browsable web page <#browsable-web-interface>`_ of each endpoint,
here we'll provide just a list of the available endpoints,
for further information please open the URL of the endpoint in your browser.

API Throttling
==============

To override the default API throttling settings, add the following to your ``settings.py`` file:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_THROTTLE_RATES': {
            'ipam': '100/hour',
        }
    }

The rate descriptions used in ``DEFAULT_THROTTLE_RATES`` may include
``second``, ``minute``, ``hour`` or ``day`` as the throttle period.

Get Next Available IP
=====================

A model method to fetch the next available IP address under a specific subnet. This method can also be accessed via a REST API: `openwisp_ipam/base/models.py <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/openwisp_ipam/base/models.py#L80>`_

GET
---

Returns the next available IP address under a subnet.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet_id>/get-next-available-ip/

Request IP
^^^^^^^^^^

A model method to create and fetch the next available IP address record under a subnet.

POST
----

Creates a record for next available IP address and returns JSON data of that record.

.. code-block:: text

    POST /api/v1/ipam/subnet/<subnet_id>/request-ip/

===========    ========================================
Param          Description
===========    ========================================
description    Optional description for the IP address
===========    ========================================

Response
^^^^^^^^

.. code-block:: json


    {
        "ip_address": "ip_address",
        "subnet": "subnet_uuid",
        "description": "optional description"
    }


IpAddress-Subnet List and Create View
=====================================

An api endpoint to retrieve or create IP addresses under a specific subnet.

GET
---

Returns the list of IP addresses under a particular subnet.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet_id>/ip-address/

POST
----

Create a new ``IP Address``.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet_id>/ip-address/

===========    ========================================
Param          Description
===========    ========================================
ip_address     IPv6/IPv4 address value
subnet         Subnet UUID
description    Optional description for the IP address
===========    ========================================

Subnet List/Create View
=======================

An api endpoint to create or retrieve the list of subnet instances.

GET
---

Returns the list of ``Subnet`` instances.

.. code-block:: text

    /api/v1/ipam/subnet/

POST
----

Create a new ``Subnet``.

.. code-block:: text

    /api/v1/ipam/subnet/

=============    ========================================
Param            Description
=============    ========================================
subnet           Subnet value in CIDR format
master_subnet    Master Subnet UUID
description      Optional description for the IP address
=============    ========================================

Subnet View
===========

An api endpoint for retrieving, updating or deleting a subnet instance.

GET
---

Get details of a ``Subnet`` instance

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/

DELETE
------

Delete a ``Subnet`` instance

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/

PUT
---

Update details of a ``Subnet`` instance.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/

=============    ========================================
Param            Description
=============    ========================================
subnet           Subnet value in CIDR format
master_subnet    Master Subnet UUID
description      Optional description for the IP address
=============    ========================================

IP Address View
===============

An api endpoint for retrieving, updating or deleting a IP address instance.

GET
---

Get details of an ``IP address`` instance.

.. code-block:: text

    /api/v1/ipam/ip-address/<ip_address-id>/

DELETE
------

Delete an ``IP address`` instance.

.. code-block:: text

    /api/v1/ipam/ip-address/<ip_address-id>/

PUT
---

Update details of an ``IP address`` instance.

.. code-block:: text

    /api/v1/ipam/ip-address/<ip_address-id>/

===========    ========================================
Param          Description
===========    ========================================
ip_address     IPv6/IPv4 value
subnet         Subnet UUID
description    Optional description for the IP address
===========    ========================================

Export Subnet View
==================

View to export subnet data.

POST
----

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/export/

Import Subnet View
==================

View to import subnet data.

POST
----

.. code-block:: text

    /api/v1/ipam/import-subnet/


Exporting and Importing Subnet
==============================

One can easily import and export `Subnet` data and it's Ip Addresses using `openwisp-ipam`.
This works for both IPv4 and IPv6 types of networks.

Exporting
---------

Data can be exported via the admin interface or by using a management command. The exported data is in `.csv` file format.

From management command
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    ./manage.py export_subnet <subnet value>

This would export the subnet if it exists on the database.

From admin interface
^^^^^^^^^^^^^^^^^^^^

Data can be exported from the admin interface by just clicking on the export button on the subnet's admin change view.

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/master/docs/export.png

Importing
---------

Data can be imported via the admin interface or by using a management command.
The imported data file can be in `.csv`, `.xls` and `.xlsx` format. While importing
data for ip addresses, the system checks if the subnet specified in the import file exists or not.
If the subnet does not exists it will be created while importing data.

From management command
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    ./manage.py import_subnet --file=<file path>

From admin interface
^^^^^^^^^^^^^^^^^^^^

Data can be imported from the admin interface by just clicking on the import button on the subnet view.

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/master/docs/import.png

CSV file format
===============

Follow the following structure while creating `csv` file to import data.

.. code-block:: text

    Subnet Name
    Subnet Value

    ip_address,description
    <ip-address>,<optional-description>
    <ip-address>,<optional-description>
    <ip-address>,<optional-description>

Setup (integrate in an existing Django project)
***********************************************

The ``settings.py`` of your project should contain the following:

.. code-block:: python

    INSTALLED_APPS = [
        # openwisp2 modules
        'openwisp_users',
        'openwisp_ipam',
        # admin
        'django.contrib.admin',
        # rest framework
        'rest_framework',
        'drf_yasg',
    ]

    AUTH_USER_MODEL = 'openwisp_users.User'

Add the URLs to your main ``urls.py``:

.. code-block:: python

    from django.conf.urls import url
    from django.contrib import admin
    from django.urls import include, path
    from openwisp_users.api.urls import get_api_urls as get_users_api_urls

    urlpatterns = [
        # admin URLs
        path('admin/', admin.site.urls),
        # IPAM API
        path('', include('openwisp_ipam.urls')),
        # OpenAPI docs
        path('api/v1/', include('openwisp_utils.api.urls')),
        # Bearer Authentication API URL
        url(r'^api/v1/', include((get_users_api_urls(), 'users'), namespace='users')),
    ]


Then run:

.. code-block:: shell

    ./manage.py migrate

Extending openwisp-ipam
***********************

One of the core values of the OpenWISP project is `Software Reusability <http://openwisp.io/docs/general/values.html#software-reusability-means-long-term-sustainability>`_,
for this reason *openwisp-ipam* provides a set of base classes
which can be imported, extended and reused to create derivative apps.

In order to implement your custom version of *openwisp-ipam*,
you need to perform the steps described in this section.

When in doubt, the code in the `test project <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/>`_ and
the `sample app <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/>`_
will serve you as source of truth:
just replicate and adapt that code to get a basic derivative of
*openwisp-ipam* working.

If you want to add new users fields, please follow the `tutorial to extend the
openwisp-users <https://github.com/openwisp/openwisp-users/#extend-openwisp-users>`_.
As an example, we have extended *openwisp-users* to *sample_users* app and
added a field ``social_security_number`` in the `sample_users/models.py
<https://github.com/openwisp/openwisp-ipam/blob/master/tests/openwisp2/sample_users/models.py>`_.

**Premise**: if you plan on using a customized version of this module,
we suggest to start with it since the beginning, because migrating your data
from the default module to your extended version may be time consuming.

1. Initialize your custom module
================================

The first thing you need to do is to create a new django app which will
contain your custom version of *openwisp-ipam*.

A django app is nothing more than a
`python package <https://docs.python.org/3/tutorial/modules.html#packages>`_
(a directory of python scripts), in the following examples we'll call this django app
``myipam``, but you can name it how you want::

    django-admin startapp myipam

Keep in mind that the command mentioned above must be called from a directory
which is available in your `PYTHON_PATH <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`_
so that you can then import the result into your project.

Now you need to add ``myipam`` to ``INSTALLED_APPS`` in your ``settings.py``,
ensuring also that ``openwisp_ipam`` has been removed:

.. code-block:: python

    INSTALLED_APPS = [
        # ... other apps ...
        'openwisp_utils.admin_theme',
        # all-auth
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # openwisp2 modules
        'openwisp_users',
        # 'myipam',   <-- replace without your app-name here
        # admin
        'django.contrib.admin',
        # rest framework
        'rest_framework',
        # Other dependencies
        'reversion',
    ]

For more information about how to work with django projects and django apps,
please refer to the `django documentation <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

2. Install ``openwisp-ipam``
============================

Install (and add to the requirement of your project) openwisp-ipam::

    pip install openwisp-ipam

3. Add ``EXTENDED_APPS``
========================

Add the following to your ``settings.py``:

.. code-block:: python

    EXTENDED_APPS = ('openwisp_ipam',)

4. Add ``openwisp_utils.staticfiles.DependencyFinder``
======================================================

Add ``openwisp_utils.staticfiles.DependencyFinder`` to
``STATICFILES_FINDERS`` in your ``settings.py``:

.. code-block:: python

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'openwisp_utils.staticfiles.DependencyFinder',
    ]

5. Add ``openwisp_utils.loaders.DependencyLoader``
==================================================

Add ``openwisp_utils.loaders.DependencyLoader`` to ``TEMPLATES``
in your ``settings.py``, but ensure it comes before
``django.template.loaders.app_directories.Loader``:

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'openwisp_utils.loaders.DependencyLoader',
                    'django.template.loaders.app_directories.Loader',
                ],
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }
    ]

6. Inherit the AppConfig class
==============================

Please refer to the following files in the sample app of the test project:

- `sample_ipam/__init__.py <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/__init__.py>`_.
- `sample_ipam/apps.py <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/apps.py>`_.

You have to replicate and adapt that code in your project.

For more information regarding the concept of ``AppConfig`` please refer to
the `"Applications" section in the django documentation <https://docs.djangoproject.com/en/dev/ref/applications/>`_.

7. Create your custom models
============================

For the purpose of showing an example, we added a simple "details" field to the
`models of the sample app in the test project <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/models.py>`_.

You can add fields in a similar way in your ``models.py`` file.

**Note**: for doubts regarding how to use, extend or develop models please refer to
the `"Models" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/db/models/>`_.

8. Add swapper configurations
=============================

Once you have created the models, add the following to your ``settings.py``:

.. code-block:: python

    # Setting models for swapper module
    OPENWISP_IPAM_IPADDRESS_MODEL = 'myipam.IpAddress'
    OPENWISP_IPAM_SUBNET_MODEL = 'myipam.Subnet'

Substitute ``myipam`` with the name you chose in step 1.

9. Create database migrations
=============================

Create and apply database migrations::

    ./manage.py makemigrations
    ./manage.py migrate

For more information, refer to the
`"Migrations" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/migrations/>`_.


10. Create the admin
====================

Refer to the `admin.py file of the sample app <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/admin.py>`_.

To introduce changes to the admin, you can do it in two main ways which are described below.

**Note**: for more information regarding how the django admin works, or how it can be customized,
please refer to `"The django admin site" section in the django documentation <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_.

1. Monkey patching
------------------

If the changes you need to add are relatively small, you can resort to monkey patching.

For example:

.. code-block:: python

    from openwisp_ipam.admin import IpAddressAdmin, SubnetAdmin

    SubnetAdmin.app_label = 'sample_ipam'


2. Inheriting admin classes
---------------------------

If you need to introduce significant changes and/or you don't want to resort to
monkey patching, you can proceed as follows:

.. code-block:: python

    from django.contrib import admin
    from openwisp_ipam.admin import (
        IpAddressAdmin as BaseIpAddressAdmin,
        SubnetAdmin as BaseSubnetAdmin,
    )
    from swapper import load_model

    IpAddress = load_model('openwisp_ipam', 'IpAddress')
    Subnet = load_model('openwisp_ipam', 'Subnet')

    admin.site.unregister(IpAddress)
    admin.site.unregister(Subnet)

    @admin.register(IpAddress)
    class IpAddressAdmin(BaseIpAddressAdmin):
        # add your changes here

    @admin.register(Subnet)
    class SubnetAdmin(BaseSubnetAdmin):
        app_label = 'myipam'
        # add your changes here

Substitute ``myipam`` with the name you chose in step 1.

11. Create root URL configuration
=================================

.. code-block:: python

    from .sample_ipam import views as api_views
    from openwisp_ipam.urls import get_urls

    urlpatterns = [
        # ... other urls in your project ...
        # openwisp-ipam urls
        # url(r'^', include(get_urls(api_views))) <-- Use only when changing API views (dicussed below)
        url(r'^', include('openwisp_ipam.urls')),
    ]

For more information about URL configuration in django, please refer to the
`"URL dispatcher" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_.

12. Import the automated tests
==============================

When developing a custom application based on this module, it's a good
idea to import and run the base tests too, so that you can be sure the changes
you're introducing are not breaking some of the existing features of *openwisp-ipam*.

In case you need to add breaking changes, you can overwrite the tests defined
in the base classes to test your own behavior.

See the `tests of the sample app <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/tests.py>`_
to find out how to do this.

You can then run tests with::

    # the --parallel flag is optional
    ./manage.py test --parallel myipam

Substitute ``myipam`` with the name you chose in step 1.

For more information about automated tests in django, please refer to
`"Testing in Django" <https://docs.djangoproject.com/en/dev/topics/testing/>`_.

Other base classes that can be inherited and extended
=====================================================

The following steps are not required and are intended for more advanced customization.

1. Extending the API Views
--------------------------

The API view classes can be extended into other django applications as well. Note
that it is not required for extending openwisp-ipam to your app and this change
is required only if you plan to make changes to the API views.

Create a view file as done in `views.py <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/views.py>`_.

For more information about django views, please refer to the `views section in the django documentation <https://docs.djangoproject.com/en/dev/topics/http/views/>`_.

Contributing
************

Please refer to the `OpenWISP contributing guidelines <http://openwisp.io/docs/developer/contributing.html>`_.

`Support channels <http://openwisp.org/support.html>`_ |
`Issue Tracker <https://github.com/openwisp/openwisp-ipam/issues>`_ |
`License <https://github.com/openwisp/openwisp-ipam/blob/master/LICENSE>`_

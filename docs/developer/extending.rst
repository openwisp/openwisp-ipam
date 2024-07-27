Extending OpenWISP IPAM
=======================

.. include:: ../partials/developer-docs.rst

One of the core values of the OpenWISP project is :ref:`Software
Reusability <values_software_reusability>`, for this reason
*openwisp-ipam* provides a set of base classes which can be imported,
extended and reused to create derivative apps.

In order to implement your custom version of *openwisp-ipam*, you need to
perform the steps described in this section.

When in doubt, the code in the `test project
<https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/>`_
and the `sample app
<https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/>`_
will serve you as source of truth: just replicate and adapt that code to
get a basic derivative of *openwisp-ipam* working.

If you want to add new users fields, please follow the :doc:`tutorial to
extend the openwisp-users </users/developer/extending>`. As an example, we
have extended *openwisp-users* to *sample_users* app and added a field
``social_security_number`` in the `sample_users/models.py
<https://github.com/openwisp/openwisp-ipam/blob/master/tests/openwisp2/sample_users/models.py>`_.

.. important::

    If you plan on using a customized version of this module, we suggest
    to start with it since the beginning, because migrating your data from
    the default module to your extended version may be time consuming.

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

1. Initialize your Custom Module
--------------------------------

The first thing you need to do is to create a new django app which will
contain your custom version of *openwisp-ipam*.

A django app is nothing more than a `python package
<https://docs.python.org/3/tutorial/modules.html#packages>`_ (a directory
of python scripts), in the following examples we'll call this django app
``myipam``, but you can name it how you want:

.. code-block::

    django-admin startapp myipam

Keep in mind that the command mentioned above must be called from a
directory which is available in your `PYTHON_PATH
<https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`_ so that
you can then import the result into your project.

Now you need to add ``myipam`` to ``INSTALLED_APPS`` in your
``settings.py``, ensuring also that ``openwisp_ipam`` has been removed:

.. code-block:: python

    INSTALLED_APPS = [
        # ... other apps ...
        "openwisp_utils.admin_theme",
        # all-auth
        "django.contrib.sites",
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        # openwisp2 modules
        "openwisp_users",
        # 'myipam',   <-- replace without your app-name here
        # admin
        "admin_auto_filters",
        "django.contrib.admin",
        # rest framework
        "rest_framework",
        # Other dependencies
        "reversion",
    ]

For more information about how to work with django projects and django
apps, please refer to the `django documentation
<https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

2. Install ``openwisp-ipam``
----------------------------

Install (and add to the requirement of your project) openwisp-ipam:

.. code-block::

    pip install openwisp-ipam

3. Add ``EXTENDED_APPS``
------------------------

Add the following to your ``settings.py``:

.. code-block:: python

    EXTENDED_APPS = ("openwisp_ipam",)

4. Add ``openwisp_utils.staticfiles.DependencyFinder``
------------------------------------------------------

Add ``openwisp_utils.staticfiles.DependencyFinder`` to
``STATICFILES_FINDERS`` in your ``settings.py``:

.. code-block:: python

    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "openwisp_utils.staticfiles.DependencyFinder",
    ]

5. Add ``openwisp_utils.loaders.DependencyLoader``
--------------------------------------------------

Add ``openwisp_utils.loaders.DependencyLoader`` to ``TEMPLATES`` in your
``settings.py``, but ensure it comes before
``django.template.loaders.app_directories.Loader``:

.. code-block:: python

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "openwisp_utils.loaders.DependencyLoader",
                    "django.template.loaders.app_directories.Loader",
                ],
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        }
    ]

6. Inherit the AppConfig Class
------------------------------

Please refer to the following files in the sample app of the test project:

- `sample_ipam/__init__.py
  <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/__init__.py>`_.
- `sample_ipam/apps.py
  <https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/apps.py>`_.

You have to replicate and adapt that code in your project.

For more information regarding the concept of ``AppConfig`` please refer
to the `"Applications" section in the django documentation
<https://docs.djangoproject.com/en/dev/ref/applications/>`_.

7. Create your Custom Models
----------------------------

For the purpose of showing an example, we added a simple "details" field
to the `models of the sample app in the test project
<https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/models.py>`_.

You can add fields in a similar way in your ``models.py`` file.

**Note**: for doubts regarding how to use, extend or develop models please
refer to the `"Models" section in the django documentation
<https://docs.djangoproject.com/en/dev/topics/db/models/>`_.

8. Add Swapper Configurations
-----------------------------

Once you have created the models, add the following to your
``settings.py``:

.. code-block:: python

    # Setting models for swapper module
    OPENWISP_IPAM_IPADDRESS_MODEL = "myipam.IpAddress"
    OPENWISP_IPAM_SUBNET_MODEL = "myipam.Subnet"

Substitute ``myipam`` with the name you chose in step 1.

9. Create Database Migrations
-----------------------------

Create and apply database migrations:

.. code-block::

    ./manage.py makemigrations
    ./manage.py migrate

For more information, refer to the `"Migrations" section in the django
documentation
<https://docs.djangoproject.com/en/dev/topics/migrations/>`_.

10. Create the Admin
--------------------

Refer to the `admin.py file of the sample app
<https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/admin.py>`_.

To introduce changes to the admin, you can do it in two main ways which
are described below.

**Note**: for more information regarding how the django admin works, or
how it can be customized, please refer to `"The django admin site" section
in the django documentation
<https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_.

1. Monkey Patching
~~~~~~~~~~~~~~~~~~

If the changes you need to add are relatively small, you can resort to
monkey patching.

For example:

.. code-block:: python

    from openwisp_ipam.admin import IpAddressAdmin, SubnetAdmin

    SubnetAdmin.app_label = "sample_ipam"

2. Inheriting Admin Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to introduce significant changes and/or you don't want to
resort to monkey patching, you can proceed as follows:

.. code-block:: python

    from django.contrib import admin
    from openwisp_ipam.admin import (
        IpAddressAdmin as BaseIpAddressAdmin,
        SubnetAdmin as BaseSubnetAdmin,
    )
    from swapper import load_model

    IpAddress = load_model("openwisp_ipam", "IpAddress")
    Subnet = load_model("openwisp_ipam", "Subnet")

    admin.site.unregister(IpAddress)
    admin.site.unregister(Subnet)


    @admin.register(IpAddress)
    class IpAddressAdmin(BaseIpAddressAdmin):
        # add your changes here
        pass


    @admin.register(Subnet)
    class SubnetAdmin(BaseSubnetAdmin):
        app_label = "myipam"
        # add your changes here

Substitute ``myipam`` with the name you chose in step 1.

11. Create Root URL Configuration
---------------------------------

.. code-block:: python

    from .sample_ipam import views as api_views
    from openwisp_ipam.urls import get_urls

    urlpatterns = [
        # ... other urls in your project ...
        # openwisp-ipam urls
        # path('', include(get_urls(api_views))) <-- Use only when changing API views (dicussed below)
        path("", include("openwisp_ipam.urls")),
    ]

For more information about URL configuration in django, please refer to
the `"URL dispatcher" section in the django documentation
<https://docs.djangoproject.com/en/dev/topics/http/urls/>`_.

12. Import the Automated Tests
------------------------------

When developing a custom application based on this module, it's a good
idea to import and run the base tests too, so that you can be sure the
changes you're introducing are not breaking some of the existing features
of *openwisp-ipam*.

In case you need to add breaking changes, you can overwrite the tests
defined in the base classes to test your own behavior.

See the `tests of the sample app
<https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/tests.py>`_
to find out how to do this.

You can then run tests with:

.. code-block::

    # the --parallel flag is optional
    ./manage.py test --parallel myipam

Substitute ``myipam`` with the name you chose in step 1.

For more information about automated tests in django, please refer to
`"Testing in Django"
<https://docs.djangoproject.com/en/dev/topics/testing/>`_.

Other Base Classes That Can be Inherited and Extended
-----------------------------------------------------

The following steps are not required and are intended for more advanced
customization.

1. Extending the API Views
~~~~~~~~~~~~~~~~~~~~~~~~~~

The API view classes can be extended into other django applications as
well. Note that it is not required for extending openwisp-ipam to your app
and this change is required only if you plan to make changes to the API
views.

Create a view file as done in `views.py
<https://github.com/openwisp/openwisp-ipam/tree/master/tests/openwisp2/sample_ipam/views.py>`_.

For more information about django views, please refer to the `views
section in the django documentation
<https://docs.djangoproject.com/en/dev/topics/http/views/>`_.

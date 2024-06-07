REST API
========

.. _ipam_live_documentation:

Live Documentation
------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/docs/docs/api-docs.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-ipam/docs/docs/api-docs.png

A general live API documentation (following the OpenAPI specification) is
available at ``/api/v1/docs/``.

.. _ipam_browsable_web_interface:

Browsable Web Interface
-----------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/docs/docs/api-ui.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-ipam/docs/docs/api-ui.png

Additionally, opening any of the endpoints :ref:`ipam_list_endpoints`
directly in the browser will show the `browsable API interface of
Django-REST-Framework
<https://www.django-rest-framework.org/topics/browsable-api/>`_, which
makes it even easier to find out the details of each endpoint.

Authentication
--------------

See openwisp-users: :ref:`authenticating_rest_api`.

When browsing the API via the :ref:`ipam_live_documentation` or the
:ref:`ipam_browsable_web_interface`, you can also use the session
authentication by logging in the django admin.

Pagination
----------

All *list* endpoints support the ``page_size`` parameter that allows
paginating the results in conjunction with the ``page`` parameter.

.. code-block:: text

    GET /api/v1/<api endpoint url>/?page_size=10
    GET /api/v1/<api endpoint url>/?page_size=10&page=2

.. _ipam_list_endpoints:

List of Endpoints
-----------------

Since the detailed explanation is contained in the
:ref:`ipam_live_documentation` and in the
:ref:`ipam_browsable_web_interface` of each endpoint, here we'll provide
just a list of the available endpoints, for further information please
open the URL of the endpoint in your browser.

API Throttling
--------------

To override the default API throttling settings, add the following to your
``settings.py`` file:

.. code-block:: python

    REST_FRAMEWORK = {
        "DEFAULT_THROTTLE_RATES": {
            "ipam": "100/hour",
        }
    }

The rate descriptions used in ``DEFAULT_THROTTLE_RATES`` may include
``second``, ``minute``, ``hour`` or ``day`` as the throttle period.

Get Next Available IP
---------------------

Fetch the next available IP address under a specific subnet.

GET
~~~

Returns the next available IP address under a subnet.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet_id>/get-next-available-ip/

Request IP
++++++++++

A model method to create and fetch the next available IP address record
under a subnet.

POST
~~~~

Creates a record for next available IP address and returns JSON data of
that record.

.. code-block:: text

    POST /api/v1/ipam/subnet/<subnet_id>/request-ip/

=========== =======================================
Param       Description
=========== =======================================
description Optional description for the IP address
=========== =======================================

Response
++++++++

.. code-block:: json

    {
        "ip_address": "ip_address",
        "subnet": "subnet_uuid",
        "description": "optional description"
    }

IpAddress-Subnet List and Create View
-------------------------------------

An api endpoint to retrieve or create IP addresses under a specific
subnet.

GET
~~~

Returns the list of IP addresses under a particular subnet.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet_id>/ip-address/

POST
~~~~

Create a new ``IP Address``.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet_id>/ip-address/

=========== =======================================
Param       Description
=========== =======================================
ip_address  IPv6/IPv4 address value
subnet      Subnet UUID
description Optional description for the IP address
=========== =======================================

Subnet List/Create View
-----------------------

An api endpoint to create or retrieve the list of subnet instances.

GET
~~~

Returns the list of ``Subnet`` instances.

.. code-block:: text

    /api/v1/ipam/subnet/

POST
~~~~

Create a new ``Subnet``.

.. code-block:: text

    /api/v1/ipam/subnet/

============= =======================================
Param         Description
============= =======================================
subnet        Subnet value in CIDR format
master_subnet Master Subnet UUID
description   Optional description for the IP address
============= =======================================

Subnet View
-----------

An api endpoint for retrieving, updating or deleting a subnet instance.

GET
~~~

Get details of a ``Subnet`` instance

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/

DELETE
~~~~~~

Delete a ``Subnet`` instance

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/

PUT
~~~

Update details of a ``Subnet`` instance.

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/

============= =======================================
Param         Description
============= =======================================
subnet        Subnet value in CIDR format
master_subnet Master Subnet UUID
description   Optional description for the IP address
============= =======================================

IP Address View
---------------

An api endpoint for retrieving, updating or deleting a IP address
instance.

GET
~~~

Get details of an ``IP address`` instance.

.. code-block:: text

    /api/v1/ipam/ip-address/<ip_address-id>/

DELETE
~~~~~~

Delete an ``IP address`` instance.

.. code-block:: text

    /api/v1/ipam/ip-address/<ip_address-id>/

PUT
~~~

Update details of an ``IP address`` instance.

.. code-block:: text

    /api/v1/ipam/ip-address/<ip_address-id>/

=========== =======================================
Param       Description
=========== =======================================
ip_address  IPv6/IPv4 value
subnet      Subnet UUID
description Optional description for the IP address
=========== =======================================

Export Subnet View
------------------

View to export subnet data.

POST
~~~~

.. code-block:: text

    /api/v1/ipam/subnet/<subnet-id>/export/

Import Subnet View
------------------

View to import subnet data.

POST
~~~~

.. code-block:: text

    /api/v1/ipam/import-subnet/

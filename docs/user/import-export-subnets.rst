Exporting and Importing Subnet
==============================

One can easily import and export `Subnet` data and it's Ip Addresses using
`openwisp-ipam`. This works for both IPv4 and IPv6 types of networks.

Exporting
---------

Data can be exported via the admin interface or by using a management
command. The exported data is in `.csv` file format.

From Management Command
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    ./manage.py export_subnet <subnet value>

This would export the subnet if it exists on the database.

From Admin Interface
~~~~~~~~~~~~~~~~~~~~

Data can be exported from the admin interface by just clicking on the
export button on the subnet's admin change view.

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/docs/docs/export.png

Importing
---------

Data can be imported via the admin interface or by using a management
command. The imported data file can be in `.csv` and `.xlsx` format. While
importing data for ip addresses, the system checks if the subnet specified
in the import file exists or not. If the subnet does not exists it will be
created while importing data.

From Management Command
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    ./manage.py import_subnet --file=<file path>

From Admin Interface
~~~~~~~~~~~~~~~~~~~~

Data can be imported from the admin interface by just clicking on the
import button on the subnet view.

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-ipam/docs/docs/import.png

CSV File Format
===============

Follow the following structure while creating `csv` file to import data.

.. code-block:: text

    Subnet Name
    Subnet Value
    Organization Slug

    ip_address,description
    <ip-address>,<optional-description>
    <ip-address>,<optional-description>
    <ip-address>,<optional-description>

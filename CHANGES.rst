Changelog
=========

Version 1.1.0 [2024-11-21]
--------------------------

Changes
~~~~~~~

Dependencies
++++++++++++

- Bumped ``openwisp-users~=1.1.0``.
- Bumped ``openwisp-utils[rest]~=1.1.1``.
- Bumped ``django-reversion~=5.1.0``.
- Bumped ``openpyxl~=3.1.5``.
- Added support for Python ``3.10``.
- Dropped support for Python ``3.7``.
- Added support for Django ``4.2.x``.
- Dropped support for Django ``4.0``.

Bug Fixes
~~~~~~~~~

- Implemented error handling in Subnet admin change view to fix *HTTP 500
  Internal Server Error* response when attempting to open the change page
  for a non-existent subnet.

Version 1.0.0 [2022-04-28]
--------------------------

Features
~~~~~~~~

- Added go to in subnet UI
- Added support for `django-reversion
  <https://github.com/etianen/django-reversion>`_
- Created default permissions for the default permission groups defined by
  OpenWISP Users
- Added menu items
- Added throttling of API requests
- Implemented multi-tenancy in REST API

Changes
~~~~~~~

Backward incompatible changes
+++++++++++++++++++++++++++++

- Changed API endpoints from ``/api/v1/*`` to ``/api/v1/ipam/*`` for
  consistency with the other openwisp modules

Dependencies
++++++++++++

- Dropped support for Python 3.6
- Dropped support for Django 2.2
- Added support for Django 3.2 and Django 4.0
- Replaced xlrd with openpyxl
- Bumped django-reversion~=4.0.1

Other changes
+++++++++++++

- Allow shared subnets to have non shared child subnets
- Switched to new navigation menu
- Updated tests to use administrator for failing tests

Bugfixes
~~~~~~~~

- Avoid shipping openwisp-users URLs in openwisp-ipam app
- Fixed ``IndexError`` exception in REST API
- Fixed extensibility issues with openwisp-users and added tests for this
  in the sample app
- Fix overlapping shared/non-shared subnet validation
- Excluded child subnets from overlapping validation
- Added organization in import/export subnet
- Validate organization membership when importing subnets
- Ensure import/export subnet views check for user permissions
- Fixed subnet /32 & /128 pie chart error
- Fixed creation of subnet without name
- Fixed API docs errror

Version 0.2.0 [2020-10-16]
--------------------------

Features
~~~~~~~~

- Added organization in list display, possibility to filter by
  organization, and other minor improvements
- Added OpenAPI documentation (a.k.a. REST swagger) for the REST API
- Added bearer token authentication to REST API

Changes
~~~~~~~

- Allow subnets to be shared
- Changed hosts API endpoint for consistency
- Added trailing slash to endpoints for consistency

Bugfixes
~~~~~~~~

- Fixed master subnet multitenant validation
- Fixed master subnet multitenant validation
- Fixed admin multitenancy issue in hierarchical view
- Fixed integration tests with openwisp-users 0.4.1
- Fixed wrong API URL for ``list_create_ip_address``
- Add MANIFEST to fix missing admin templates from python package

Version 0.1.1 [2020-09-03]
--------------------------

- Updated dependencies (django 3.1, openwisp-users 0.4.0, openwisp-utils
  0.6.0)

Version 0.1.0 [2020-05-28]
--------------------------

- IPv4 and IPv6 IP address management
- IPv4 and IPv6 Subnet management
- Automatic free space display for all subnets
- Visual display for a specific subnet
- IP request module
- REST API for CRUD operations and main features
- Possibility to search for an IP or subnet
- CSV Import and Export of subnets and their IPs
- Multi-tenancy
- Swappable models and extensible classes

Changelog
=========

Version 0.2.0 [2020-10-16]
--------------------------

Features
~~~~~~~~

- Added organization in list display, possibility to filter by organization,
  and other minor improvements
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

- Updated dependencies (django 3.1, openwisp-users 0.4.0, openwisp-utils 0.6.0)

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

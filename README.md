# eve-utils
Templates and scripts to rapidly spin up an Eve-based API.
**WIP - usable, but not yet ready!**

This package will provide utilities to create and manage APIs based on [Eve](http://docs.python-eve.org/en/stable/)

`pip install eve-utils`

## Commands
* mkapi - creates a project with the following features
  * feature
  * feature
  
  `mkapi my-api`

* mkresource - adds the resource to the domain
  * feature
  * feature
  
  `mkresource cars`
  
  `mkresource people --no_common`

* mkrel - creates link relation between two resources (works, but needs major refactoring!)
  * feature
  * feature

  mkrel _parent_ _child_
  
  `mkrel people cars`

* mkdocker - adds dev-ready Dockerfile, docker-compose.yml, and image build scripts
  * feature
  * feature
  
  `mkdocker my-api`
  
* command
* command

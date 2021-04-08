eve-utils
=========
Templates and scripts to rapidly spin up a production-ready Eve-based API.

> **Please note**:  although I currently use these tools to create production-ready APIs, the tools themselves are still under development.  Use at your own risk.



## Introduction

[Eve](https://docs.python-eve.org/en/stable/) is amazing.  The full power of Flask/Python, optimized for an API over mongodb.  Nice.

It does take a bit of work to go from the simple example in the docs...

```python
settings = {'DOMAIN': {'people': {}}}

app = Eve(settings=settings)
app.run()
```

...to a production-ready API, with robust exception handling, logging, control endpoints, configurability, (and so much more).

**eve-utils** helps make some of that work easier.

Install eve-utils with pip. 

`pip install eve-utils`

## Getting Started

Get started with three easy steps

1. Create your API (I recommend creating a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) first)

   `mkapi my-api --with_docker`

   *(note: if you don't have docker installed, create the api without `--with-docker`, then later run the API with `python run.py` - assuming you have mongodb running on localhost:27127)*

   

2. Add domain resources

   `cd my-api`

   `mkresource people`

   

3. Build and launch the API

   `cd ..`

   `image-build`

   `docker-compose up -d`

   *(note:* `image-build` *is usually called with a version number so the new docker image is correctly tagged - see more in the docs below)*



Try it out with the following curl commands (or use Postman if you prefer)

`curl http://localhost:2112`

`curl http://localhost:2112/_settings`

`curl -X POST http://localhost:2112/people -H "Content-type: application/json" -d "{\"name\":\"Michael\"}"`

`curl http://localhost:2112/people`



If you followed the above, be sure to clean up after playing around with your new API:

`docker-compose down`

`docker image rm my-api`



## Commands

* `mkvir` <api-name>

  * creates folder named *api-name*
  * creates a skeleton Eve API in that folder

* `mkresource` <resource-name>

  * adds *resource-name* to the domain
  * default fields are name, description
  * add fields by modifying domain/*resource-name*.py - as you would any Eve resource
  * NOTE: resources in Eve are collections, so eve-utils names resources as plural by convention, 
    * i.e. if you enter mkresource dog it will create an endpoint named **dogs**
    * eve-utils rely on the [inflect](https://pypi.org/project/inflect/) library for pluralization, which is very accurate but can make mistakes

* `mkrel` <parent-resource> <child-resource>

  * `-p` `--as_parent_ref`:  field name defaults to `_` *parent-resource* `_ref`, e.g. if the parent name was dogs the field would be `_dog_ref`.  Using this parameter, the field name become literally `_parent_ref`.  Useful to implement generic parent traversals.

* `mkdocker` <api-name> - run this in the folder above the root api folder to create a basic `Dockerfile`, `docker-compose.yml` file, and some useful build scripts (to be further documented later).

  * NOTE: not necessary if you have created the API using `--with_docker`

  * Adds the following files:

    `Dockerfile`

    `docker-compose.yml` (note: by default this file does not use a volume for mongodb, so killing the container also kills your data)

    `.docker-ignore`

    `image-build`

    `image-build.bat`



MORE TO COME!


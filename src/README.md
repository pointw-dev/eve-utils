# eve-utils
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

   *(note: if you don't have docker installed, create the API without `--with-docker`, then later run the API with `python run.py` - assuming you have mongodb running on localhost:27127)*

   

2. Add domain resources

   ```bash
   cd my-api
   mkresource people
   ```

   

3. Build and launch the API

   ```bash
   cd ..
   image-build
   docker-compose up -d
   ```

   *(note:* `image-build` *is usually called with a version number so the new docker image is correctly tagged - see more in the docs below)*



Try it out with the following curl commands (or use Postman if you prefer)

```bash
curl http://localhost:2112
curl http://localhost:2112/_settings
curl -X POST http://localhost:2112/people -H "Content-type: application/json" -d "{\"name\":\"Michael\"}"
curl http://localhost:2112/people
```



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

    * i.e. if you enter mkresource **dog** it will create an endpoint named **/dogs**

    * eve-utils rely on the [inflect](https://pypi.org/project/inflect/) library for pluralization, which is very accurate but can make mistakes

      

* `mkrel` <parent-resource> <child-resource>

  * For example:

    ```bash
    mkresource person
    mkresource cars
    mkrel person car
    ```

    * you could also have typed `mkrel people cars` or `mkrel person cars` - they all are equivalent

  * If you followed the example above, you have already POSTed a person named Michael:

    `curl -X POST http://localhost:2112/people -H "Content-type: application/json" -d "{\"name\":\"Michael\"}"`

  * Normally GET a person by `_id`.   **eve-utils** wires up the name field as an `additonal_lookup`, so you can also GET by name.

    `curl http://localhost:2112/people/Michael?pretty`

    ```json
    {
      _id: '606f5453b43a8f480a1b8fc6',
      name: 'Michael',
      _updated: '2021-04-08T19:06:59',
      _created: '2021-04-08T19:06:59',
      _etag: '6e91d500cbb0a2f6645d9b4dced422d429a69820',
      _links: {
        self: { href: '/people/606f5453b43a8f480a1b8fc6', title: 'person' },
        parent: { title: 'home', href: '/' },
        collection: { title: 'people', href: 'people' },
        cars: { href: '/people/606f5453b43a8f480a1b8fc6/cars', title: 'cars' }
      }
    }
    ```

  * Notice the `_links` field includes a rel named `cars`.  You can POST a car to that `href` (I'll demonstrate with Javascript):

    ```javascript
    const axios = require('axios')
    axios.defaults.baseURL = 'http://localhost:2112'
    
    axios.get('/people/Michael').then((response) => {
        const person = response.data
        const car = {
            name: 'Mustang'
        }
        axios.post(person._links.cars.href, car)
    })
    ```

  * `-p` `--as_parent_ref`:  field name defaults to `_` *parent-resource* `_ref`, e.g. if the parent name was dogs the field would be `_dog_ref`.  Using this parameter, the field name become literally `_parent_ref`.  Useful to implement generic parent traversals.

  

* `add_docker` <api-name> - run this in the folder above the root api folder to create a basic `Dockerfile`, `docker-compose.yml` file, and some useful build scripts (to be further documented later).

  * NOTE: not necessary if you have created the API using `--with_docker`

  * Adds the following files:

    `Dockerfile`

    `docker-compose.yml` (note: by default this file does not use a volume for mongodb, so killing the container also kills your data)

    `.docker-ignore`

    `image-build`

    `image-build.bat`
    
    

*  `add_auth`  - run this in the API folder. It will add a folder named ``auth`` with modules to add authorization to your API (docs to come)

   * NOTE: the only supported IdP is [Auth0](https://auth0.com/) at the moment, but it will be fairly easy to manually tweak to use any OAuth2 JWT issuer. (I have used a forked [Glewlwyd](https://github.com/babelouest/glewlwyd) with very minimal changes)
   
     


MORE TO COME!


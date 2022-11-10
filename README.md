# myapp

**myapp** is a backbone for flask-dash based apps giving you access to the entire flask ecosystem for web development and the simplicy of dash for building Apps in python.

An live example of a **myapp** based deployment can be found on [https://flaski.age.mpg.de](https://flaski.age.mpg.de).

The backbone includes connection to a mysql (optionally Galera) and redis (optionally Sentinel).

You can add Apps by adding route files to the build, ie. having them as part of the main App (eg. [flaski](https://github.com/mpg-age-bioinformatics/flaski) ) or by running them as an independent containter (eg. [myapp-eg-container](https://github.com/mpg-age-bioinformatics/myapp-eg-container)).

User level authentication for running or visualizing each App is built in.

User settings and administrator settings dashboards are included. 

2FA ready. Traefik as reverse proxy with Let's Encrypt as certificate authority for https in production deployments. 

Administrator authorization for each registration built as an option. 

Backups are performed by an independent `backup` container.

Multiple dependent or independent instances/pods/containers can be added under the same domain eg. www.myapp.com ; www.myapp.com/age ; www.myapp.com/genomics (eg. [myapp-eg-container](https://github.com/mpg-age-bioinformatics/myapp-eg-container)).

**myapp** deployments are fully scalable, we run our production environment on kubernetes and local development over docker compose.
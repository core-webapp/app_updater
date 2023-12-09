# app_updater
source code updater


## Local development

For local development and test of the code, could be better to run inside a container, avoiding crashing or destroying anything in your machine.

So, the purpose of the Dockerfile is only to test in locally

```bash
docker build -t updater .

docker run --name updater -p 8000:8000 updater

docker exec -it updater /bin/bash
```

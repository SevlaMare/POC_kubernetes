# Thumbify
> This project consists of a service that creates thumbnails based on an uploaded image.

## Table of Contents

1. [Future Improvements](#future-improvements)
2. [Architecture](#architecture)
3. [To go into production](#to-go-into-production)
4. [Requirements](#requirements)
5. [Running Tests](#running-tests)
6. [Deployment](#deployment)
7. [Usage](#usage)
8. [Author](#author)

# 1 Future Improvements
- Increase test coverage.
- Split the YAML files and build charts individually.
- Resolve the configuration to enable the bucket for object storage to run on Kubernetes.
- Implement pagination in the endpoint that retrieves all jobs.
- Integrate Elasticsearch and Kibana within the API to track errors and keep logs.
- Build a RAG (Retrieval-Augmented Generation) system with a prompt UI to answer questions within the scope of the documentation.
- Implement an NGINX controller on Kubernetes, so the services use it as an ingress. This will also integrate Prometheus for observability, tracking key metrics like the volume of requests.
- Implement a service mesh to abstract certain logic from the application layer, such as retry policies.

# 2 Architecture
### 2.1 Backend
- To build the API, Python with FastAPI was picked, a library for building APIs that supports asynchronous programming and provides good integration with Swagger for API documentation.

### 2.2 Message broker
- Since image processing can be particularly time-consuming, a queue system will be used to avoid deadlocks. The chosen solution is to use Redis to keep the queue in memory and manage it with a FIFO approach to process jobs using background processes. Redis is free to use, open source, and licensed under the RSAL.

### 2.3 Upload
- To store the images initially a bucket with the same API as AWS S3 would be used, called MinIO, due it complexity to be deployed on kubenertes, at moment a simple file system upload will be used, the application is ready to be used with it as soon as the configurations are solved.

### 2.4 Future Optimizations
- To deal with large images, specific libraries that relies on GPU hardware can be used which would required way less time to process, to keep the memory footprint low while handling the large images, also would be necessary some customization to process it in steps rather than loading all the image as most solutions do out of the box.
- If the system is expected to primarily handle small files, using a serverless approach to facilitate auto-scaling setup would allow to processing more files in less time.
- Extra queue to keep track of failed jobs, so the system can retry to process then before marking it as permanent fail.
- If the system is primarily receiving large files, then using a queue for the upload could be necessary to prevent the system from running out of memory. Currently, the system uses a chunk-based approach that loads 1 MB at a time, so roughly estimating, it can handle around 1000 simultaneous large file uploads for every 1 GB of free memory on the server.

# 3 To go into production
- Adjust the volumes to use what is available on-premises, example NFS instead of local storage, redis need a stateful set.
- For small workloads, a single node multi drive must be enough, define the persistent volumes and tweak the resources settings.
- For high data workloads, a scalable object storage solution is necessary, which can be achieved using AWS S3 or an alternative in terms of features and easy to use would be MinIO, allowing the storages to scale through Kubernetes.
- For high throughput of parallel requests, replace Redis with Kafka, due to its built-in concurrency controls.
- Address security protocols, such as compliance and regulatory requirements, demanded by the use case (e.g. encrypt data).
- Implement server routines, like backup and recovery procedures.

# 4 Requirements
-Docker 27.2.0 [install guide](https://docs.docker.com/engine/install/) \
-Kubectl 1.28.9 [install guide](https://kubernetes.io/docs/tasks/tools/#kubectl) \
-Kind 1.28 [install guide](https://kind.sigs.k8s.io/docs/user/quick-start#installation) \
-Helm 3 [install guide](https://helm.sh/docs/intro/install/)

# 5 Running tests
start your docker machine, and get a terminal at project folder to run the command:
```
docker compose -p thumbify -f "compose.api.yaml" up -d --build
```

now run the tests direct from container
```
docker compose -f "compose.api.yaml" exec api python -m pytest src/
```

with compose up, is also possible to do manual testing at:
```
http://localhost/docs
```

after performing the tests, to remove the build:
```
docker compose -p thumbify -f "compose.api.yaml" down
```
to run tests and modify as a developer read docs/dev-readme.md

# 6 Deployment
Start the docker machine.

### 6.1 Create a cluster
```
kind create cluster --name thumb-cluster --image kindest/node:v1.28.9
```

### 6.2 Build the images
from a terminal on project root folder:
```
docker build -t thumbify_api:2.0.0 -f Dockerfile.api .

docker build -t resize_worker:2.0.0 -f Dockerfile.worker .

docker pull redis:7.4.0
```

### 6.3 Send the images to the cluster
```
kind load docker-image thumbify_api:2.0.0 --name thumb-cluster

kind load docker-image resize_worker:2.0.0 --name thumb-cluster

kind load docker-image redis:7.4.0 --name thumb-cluster
```

### 6.4 Deploy the application
from a terminal on project root folder:
```
cd helm

helm install apichart api
```

### 6.5 Forward the API
verify if pod is already running, it can take a few minutes, then get it's name:
```
kubectl get pods -n api-ns
```

to expose the api, replace the the pod name in the command bellow:
```
kubectl port-forward -n api-ns <pod_name> 80:80
```

### 6.6 API documentation available at
```
http://localhost/docs
```

# 7 Usage
- With the server running go to http://host/docs
- Upload an image file, you will get a id to check the job progress
- Using the previous response job_id, check the job status
- Retrieve the thumbnail using the original filename prefixed with "thumb_"

Considerations:
- Images with the same name will be treated as a new version and will replace the previous version.
- The resizing is designed to handle square images, though it allows any shape.
- If no workers are available, jobs will be queued in FIFO order until a worker becomes available.
- A single worker currently handles jobs synchronously.
- The queue is not persistent; shutting down the Redis pod will result in the loss of the queue.

# 8 Author
👤 **Thiago Miranda**
- Github: [SevlaMare](https://github.com/SevlaMare)
- Linkedin: [sevla-mare](https://www.linkedin.com/in/sevla-mare)
- Email: thiagotm@outlook.com
- Phone: +81 070-3112-5851

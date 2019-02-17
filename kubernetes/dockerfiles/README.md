# Dockerfiles for Spark on K8s

This just explains how to use these Dockerfiles. Each one of the four are required for different purposes, explained here:
1. `/dockerfiles/Dockerfile` - this is the Dockerfile specifically used to deploy and run the spark scripts built in this repo. 
The files stored in the `src/` directory is compressed and copied to `dist/` and from there the Dockerfile copies the distribution files.
1. `spark/Dockerfile` - this is the base Spark Dockerfile from which all others are built. NB: this can only be built from within the 
official spark distribution package - v2.4.0. See the repo's README for more information.  
1. `spark/bindings/python/Dockerfile` - this is the first direct extension of the Spark base Docker image. It merely extends the Spark image with 
Python bindings, making it a PySpark image. 
1.  `k8s-operator/Dockerfile` - this Dockerfile also builds from the Spark base Docker image and adds a customer K8s API resource, which
enables us to distribute Spark jobs on K8s using YAML configuration files.

##### Read more about the rest of the folder structure in the repo README.md
This will include source links to the resources I used to put this all together and understand how it all works. As well as a how-to guide on replicating 
this on your own system (as far as possible).
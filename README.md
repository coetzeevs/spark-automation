# Spark Automation WIP
This repository is still a work in progress and will be contributed to over time. 
Watch this space for further developments.

## Requirements
There are a few required components that must be in place for the scaffold to work as intended. The following 
is an attempted exhaustive list and what the usage is. 
1. The custom Spark images available on a Docker repository of some kind (the Dockerfiles for these are available under 
`kubernetes/dockerfiles`): 
    The Spark-base image is built as-is from the official Spark distributions
    1. Spark-base (`kubernetes/dockerfiles/spark/`)
    1. Spark-PY (`kubernetes/dockerfiles/spark/bindings/python/`)
    1. Spark-DS (`kubernetes/dockerfiles/`)
    1. Spark-Operator (`kubernetes/dockerfiles/spark/k8s-operator`)
1. A running Kubernetes cluster with a minimum 2 VCPU cores and 8GB RAM allocatable to the Spark distribution.
1. A GCP service account that has been granted access to Storage (Admin) and BigQuery (Data Owner and Jobs User)
1. A Kubernetes secret with the JSON key associated with the service account mentioned above
1. Cluster role bindings associated with the user that will be setting up the Spark Application architecture
1. A namespace dedicated to the Spark operations, just for cleanliness and organisation/separation of the environments.
It also makes things easier to handle permissions and access
1. A dedicated Kubernetes service account that will be bound to role bindings to execute the Spark applications
1. A custom API deployment for Google Cloud Platform's SparkApplication Operator (see the first link under _Necessary Links_)
1. A configured SparkApplication YAML file that deploys the spark job, similar to manually firing a `spark-submit` from 
a terminal where Spark has been installed. This can also be replaced with a YAML file to deploy a ScheduledSparkApplication.   

## Necessary links and further reading
It's imperative to read through source docs and code to understand how this is put together, so I'll link two resources I've used to get here:
1. [Spark-on-k8s-operator](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator) - this is a Google Git repo, though the repo
expresses that this is not officially supported by Google (yet). This is the base on which the automation deployment in K8s is built. 
1. [Best Practices Writing Production-Grade PySpark Jobs](https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f) - this was 
my inspiration for the project structure and how to package and ship the application files to each of the different executors on Spark. (A lot of credit
is due here, since I basically copied the logic exactly - I just changed some things since it has been about 18months since this article was written)
1. [Accompanying GitRepo for the Article above](https://github.com/ekampf/PySpark-Boilerplate)
1. [First resource for commandline spark-submit](https://github.com/GoogleCloudPlatform/spark-on-k8s-gcp-examples) - this repo contains some examples 
to submit spark jobs from your command line using native Spark, specifically to a K8s cluster, be it Minikube or an actual cluster in GCP.

## Let's get stuck in
It's all good and well to have a list of links and resources and what the requirements are, but often it's still all shrouded
in a cloak of ambiguity and confusion. So let's attempt to clear the air and get you on your way to using Spark on K8s like a (semi) pro.

The first step is to understand how it all fits together. Of course, GCP is the vehicle for this application since we'll be using quite a few of the products available (and because Google is nice 
enough to give new users $300 worth of resource usage over 12months to try out its products). The main products we'll be using are Kubernetes, Container Registry, Storage,
and BigQuery. Make sure you've [created an account with Google Cloud Platform](https://console.cloud.google.com/freetrial/signup/tos) if you haven't already and be sure to 
[create a new project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) and [activate the necessary APIs](https://cloud.google.com/endpoints/docs/openapi/enable-api) that we'll be using.
As last preparatory steps, make sure to [install the Google Cloud SDK](https://cloud.google.com/sdk/) as well as the [Kubernetes Commandline Tool](https://kubernetes.io/docs/tasks/tools/install-kubectl/).
For brevity I'll omit the details of those steps from this guide, although the links are provided (for the most part) on how to get started using GCP. It's all really just a quick Google search away.   

Once that's all set up we're ready to start building the architecture for our demo Spark application to: 1) run in Kubernetes, 
2) write data to GCS, and finally 3) fire a job on BigQuery that saves the data from GCS to a BigQuery table. Along the way I'll try and give some extra tips and tricks I've picked up
regarding Spark configs and how to optimise for GCP use.

### How it works 
Figure 1 below shows the architecture slightly abstracted to demonstrate how each component is used to make the magic happen. Take note that a base Docker image of native Spark v2.4.0 is used to
produce both the Spark Operator image as well as the PySpark image. As a last step the PySpark image is used to create the final Job image that gets used during the 'pseudo'
call to `spark-submit` (remember that we're deploying an operator that reads a YAML file and does the `spark-submit` step for us).

```image
Add new image here.
```

```text
Side note: One could argue that all these Docker images could be consolidated into one file, and you'd be right, although I chose to split this out for one simple reason: to build the Spark base, 
PySpark, and Spark Operator images you need to have the different files/repository contents for Spark and SparkOperatorOnK8s available since the build calls are issued from the 
root directory in each of the projects. Having to track those files directly in my own projects seems silly and infeasible so I opt to build a stable version of my base images and
simply adjust according to stable releases.
```

So once the images are built and available for use (I prefer to use [Google's Container Registry](https://cloud.google.com/container-registry/) for remote access when deploying images to a Kubernetes Pod), 
the Kubernetes Cluster is configured to
host the Spark Operator deployment. As mentioned, the Spark Operator serves as the interpreter that 'decodes' our YAML file and submits the Spark job. The PySpark image that was used to create the 
Job image submitted in the SparkApplication YAML file provides the necessary Python bindings to run our PySpark code in. The Job image provides the actual files that are to 
be executed during runtime. Kubernetes serves as the environment for orchestrating the Driver and Executor processes once the Spark job is fired off, and of course provides the necessary 
machine resources that the Job will run on. This explanation obviously only scratches the surface, so do some more digging on your own to understand the different components.

### You've seen the picture - Now let's draw it
So assuming you've got everything set up (the account, the project, the APIs, and the SDK) we can proceed with some basic command to get this project up and running. 
First clone this repo and `cd` into the repo directory on your local machine. THen we'll need to do the following (all of these commands are run in terminal):
1. Create a new Kubernetes cluster that has at least 1 node, 4 virtual CPU cores, and 15GB RAM. In [GCP Machine Type](https://cloud.google.com/compute/docs/machine-types) terminology that would be a `n1-standard-4` machine.
    ```bash
    gcloud config set compute/zone europe-west1-b
    gcloud container clusters create spark-on-gke --machine-type n1-standard-32 --num-nodes 1
    ```
    The first command just sets the default compute zone to Europe West, region 1 B. I'd suggest reading more about this in your spare time. The second actually creates the cluster.
1. Create a new GCP service account that will be granted access to both BigQuery and Cloud Storage (this is to ensure a valid application is accessing your resources).
    ```bash
    gcloud iam service-accounts create spark-bq --display-name spark-bq
    ```
    The command creates a new service account called _spark-bq_ having the same display name.
1. Assign the necessary permissions to the new service account.
    ```bash
    export SA_EMAIL=$(gcloud iam service-accounts list --filter="displayName:spark-bq" --format='value(email)')
    export PROJECT=$(gcloud info --format='value(config.project)')
    
    gcloud projects add-iam-policy-binding $PROJECT --member serviceAccount:$SA_EMAIL --role roles/storage.admin
    gcloud projects add-iam-policy-binding $PROJECT --member serviceAccount:$SA_EMAIL --role roles/bigquery.dataOwner
    gcloud projects add-iam-policy-binding $PROJECT --member serviceAccount:$SA_EMAIL --role roles/bigquery.jobUser
    ```
    The export commands reads some details from your GCloud SDK configurations and sets them as environment variables. The subsequent commands leverages
    the add-iam-policy-binding command in the GCloud SDK to alter the permissions for the service account we've created and sets access to Storage on admin level, and access to
    BigQuery on DataOwner level as well as JobsUser level.
1. Create a new service account key (in _JSON_ format) associated with the service account.
    ```bash
    gcloud iam service-accounts keys create spark-sa.json --iam-account $SA_EMAIL
    ```
    The new service account key will be created and associated with the email address linked to our _spark-bq_ service account, and downloaded to your machine. 
1. Create a Kubernetes Secret using the key file we've downloaded.
    ```bash
    kubectl create secret generic spark-sa --from-file=spark-sa.json
    ```
    This uses the Kubernetes Commandline Tool to create a resource called a _secret_ on your new cluster that has the service account key value stored and makes it accessible to your applications.
1. Grant yourself `cluster-admin` cluster role binding for the newly created Kubernetes cluster. This will allow your own profile to create new bindings required for the application to run smoothly.
    ```bash
    kubectl create clusterrolebinding user-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value account)
    ```
1. Apply specific configurations required to grant different levels of [Role-Based access control](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) across your cluster, to enable safe execution of your applications.
    ```bash
    kubectl apply -f kubernetes/once-off/spark-operator-rbac.yml
    ```
    This command uses a file called `spark-operator-rbac.yml` to apply the YAML configurations contained within - more on this a little later. In short it creates a new namespace
    in the cluster, it creates a new Kubernetes service account (not the same as the GCP service account), and it creates customer cluster role bindings and binds them to the 
    new K8s service account.
1. Create the SparkOperator deployment.
    ```bash
    kubectl apply -f kubernetes/once-off/spark-operator.yml
    ```
    The applies the deployment configuration in the `spark-operator.yml` which uses the Spark Operator image to deploy the [Custom Resource](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/), 
    for Kubernetes to be able to run our Spark application.

Up to this point, if you've been able to run each command without error, you should be able to run the following command and have it return three things: 1) a spark-operator Pod,
2) a spark-operator Deployment, and 3) a spark-operator Replica Set. 
```bash
kubectl get all
```
If their statuses all reflect "green" (i.e. everything is in a Ready state), we can move on. If not, see the _Debugging Your Deployment_ part at the end. 

### The Makefile and what it's for
A Makefile, from my limited understanding, is used to wrap commands and procedures that run in bash, into a single command. I.e. aliasing to a certain extent. There are two commands
in the Makefile for this project that are quite important to know. 1) `make build` and 2) `make pips`. The build command is the primary one to be used when developing a new application.
It copy's the files and folders from the `src` directory to a folder called `dist` and zips the files and folders which will be submitted to the application. Of course, if you make 
any changes to your application and run `make build` you'll need to rebuild your Job image using Docker again, and re-upload it to the cloud repository. 

```text
Side note: I've noticed that the right overwrite actions aren't always adhered when pushing a Docker image to the Container Registry, using the same version tag. I suggest either changing
the version tag -- you would then need to change it in the YAML file too -- or simply deleting the current version in the Container Registry before uploading it again. 

```

The pips command is something I rarely use since I try and resolve my dependencies within the Dockerfiles instead of submitting dependencies through the job submission step.
In short, it installs the specified dependencies (listed in the `requirements.txt` file) into a specified directory, in this case `src/libs`. This then gets compressed and copied along with the other
files and folders in the `make build` command.

### What we're trying to run (and how it fits together)
So we've got the scaffold in place and it's all ready to go. But first you need to understand how the job is set up and how it works.

We start with the `main.py` file and some important lines from it. 

# Spark Automation WIP
This repository is still a work in progress and will be finalised soon. Watch this space for further developments.

## Necessary links and further reading
It's imperative to read through source docs and code to understand how this is put together, so I'll link two resources I've used to get here:
1. [Spark-on-k8s-operator](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator) - this is a Google Git repo, though the repo
expresses that this is not officially supported by Google (yet). This is the base on which the automation deployment in K8s is built. 
1. [Best Practices Writing Production-Grade PySpark Jobs](https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f) - this was 
my inspiration for the project structure and how to package and ship the application files to each of the different executors on Spark. (A lot of credit
is due here, since I basically copied the logic exactly - I just changed some things since it has been about 18months since this article was written)
1. [Accompanying GitRepo for the Article above](https://github.com/ekampf/PySpark-Boilerplate)
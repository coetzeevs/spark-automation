#!/usr/bin/python
import argparse
import importlib
import time
import os
import sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

if os.path.exists('libs.zip'):
    sys.path.insert(0, 'libs.zip')
else:
    sys.path.insert(0, './libs')

if os.path.exists('jobs.zip'):
    sys.path.insert(0, 'jobs.zip')
else:
    sys.path.insert(0, './jobs')

try:
    import pyspark
except Exception as e:
    import findspark

    findspark.init()
    import pyspark

    raise

__author__ = 'data-science'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a PySpark job')
    parser.add_argument('--job', type=str, required=True, dest='job_name',
                        help="The name of the job module you want to run. (ex: poc will run job on jobs.poc package)")
    parser.add_argument('--job-args', nargs='*',
                        help="Extra arguments to send to the PySpark job "
                             "(example: --job-args template=manual-email1 foo=bar")

    args = parser.parse_args()
    logger.info(f'Called with arguments: {args}')

    environment = {
        'PYSPARK_JOB_ARGS': ' '.join(args.job_args) if args.job_args else ''
    }

    job_args = dict()
    if args.job_args:
        job_args_tuples = [arg_str.split('=') for arg_str in args.job_args]
        logger.info(f'job_args_tuples: {job_args_tuples}')
        job_args = {a[0]: a[1] for a in job_args_tuples}

    logger.info(f'\nRunning job {args.job_name}...\nenvironment is {environment}\n')

    os.environ.update(environment)
    sc = pyspark.SparkContext(appName=args.job_name, environment=environment)

    if os.path.exists('dist/jobs.zip'):
        sc.addPyFile('dist/jobs.zip')
    if os.path.exists('dist/libs.zip'):
        sc.addPyFile('dist/libs.zip')

    job_module = importlib.import_module(f'jobs.{args.job_name}')

    start = time.time()
    job_module.analyze(sc, **job_args)
    end = time.time()

    logger.info(f'\nExecution of job {args.job_name} took {end-start} seconds')

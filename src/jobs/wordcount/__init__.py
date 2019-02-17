import re
from functools import partial
import logging
from shared.context import JobContext

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

__author__ = 'data-science'


class WordCountJobContext(JobContext):
    def _init_accumulators(self, sc):
        self.initialize_counter(sc, 'words')


strip_regexp = re.compile(r"[^\w]*")


def to_pairs(context, word):
    context.inc_counter('words')
    return word, 1


def analyze(sc):
    logger.info('Running wordcount')
    context = WordCountJobContext(sc)

    text = """
    Sample text: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum at condimentum augue. 
    Sed a massa convallis, rhoncus felis sed, fringilla lacus. Sed tristique nulla sem, ut egestas erat consequat sed.
    """

    to_pairs_transform = partial(to_pairs, context)

    words = sc.parallelize(text.split())
    pairs = words.map(to_pairs_transform)
    counts = pairs.reduceByKey(lambda a, b: a + b)
    ordered = counts.sortBy(lambda pair: pair[1], ascending=False)

    result = ordered.collect()
    logging.info(result)
    context.print_accumulators()

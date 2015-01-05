from __future__ import absolute_import

import os

from .viz.domain import Domain
from .viz.harvest import Harvest
from .viz.termite import Termite    
from .models import DataSource
from .config import CRAWLS_PATH

from .db_api import (get_plot, get_data_source)

PLOT_NAMES = ('Domain Relevance',
              'Domain Crawled',
              'Domain Frontier',
              'Harvest',
              'Harvest Rate',
              'Termite')

PLOT_TYPES = ('domain_by_relevance',
              'domain_by_crawled',
              'domain_by_frontier',
              'harvest',
              'harvest_rate',
              'termite')

class PlotsNotReadyException(Exception):
    pass 

def plot_builder(crawl, plot):

    assert plot.plot in PLOT_TYPES, 'Unrecognized plot type.'
    data = MonitorData.query.filter_by(crawl_id=crawl.id)

    if "domain" in plot.plot:
        crawled_uri = data.filter_by(name='crawledpages').first().data_uri
        relevant_uri = data.filter_by(name='relevantpages').first().data_uri
        frontier_uri = data.filter_by(name='frontierpages').first().data_uri
        d = Domain(crawled=crawled_uri, relevant=relevant_uri, frontier=frontier_uri)

        if plot.plot == 'domain_by_relevance':
            script, div = d.create_plot_relevant()        

        if plot.plot == 'domain_by_crawled':
            script, div = d.create_plot_crawled()

        if plot.plot == 'domain_by_frontier':
            script, div = d.create_plot_frontier()

    if plot.plot == 'harvest':
        harvest = data.filter_by(name='harvest').first().data_uri
        d = Harvest(harvest)
        script, div = d.create_plot_harvest()

    if plot.plot == 'harvest_rate':
        harvest = data.filter_by(name='harvest').first().data_uri
        d = Harvest(harvest)
        script, div = d.create_plot_harvest_rate()

    if plot.name == 'termite':
        termite = data.filter_by(name='termite').first().data_uri
        t =  Termite(termite)
        script, div = t.create_plot()

    return script, div


def default_ache_dash(project, crawl):


    ### Domain
    domain_plot = get_plot(crawl.name + "-domain")

    crawled = get_data_source(project.id, crawl.name + "-crawledpages")
    relevant = get_data_source(project.id, crawl.name + "-relevantpages")
    domain_sources = dict(crawled=crawled, relevant=relevant)

    print [CRAWLS_PATH + x.data_uri for x in domain_sources.values()]
    print [os.path.exists(CRAWLS_PATH + x.data_uri) for x in domain_sources.values()]

    if not all(os.path.exists(CRAWLS_PATH + x.data_uri) for x in domain_sources.values()):
        raise PlotsNotReadyException("Domain sources are not initialized.")

    domain = Domain(domain_sources, domain_plot)
    domain_script, domain_div = domain.create()
    ###


    ### Harvest
    harvest_plot = get_plot(crawl.name + "-harvest")

    harvest_source = get_data_source(project.id, crawl.name + "-harvest")
    if not os.path.exists(CRAWLS_PATH + harvest_source.data_uri):
        raise PlotsNotReadyException("Harvest source is not initialized.")

    harvest = Harvest(harvest_source, harvest_plot)
    harvest_script, harvest_div  = harvest.create()
    ###

    scripts = (domain_script, harvest_script)
    divs = (domain_div, harvest_div)

    return scripts, divs

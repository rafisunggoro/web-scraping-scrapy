from rafi_job_scraping.utils import job_list
import scrapy
import json
import logging

class JWA(scrapy.Spider):
    name = 'jwa'

    def __init__(self, name=None, *args, **kwargs):
        super(JWA, self).__init__(*args, **kwargs)
            
        job_keyword = getattr(self, 'job', None)
        if job_keyword is None: raise ValueError('No job specified!')

        if job_keyword == 'job_list':
            self.job_targets = job_list['purple_jobs'] + job_list['pink_jobs']
        elif job_keyword in job_list:
            self.job_targets = job_list[job_keyword]
        else:
            self.job_targets = [job_keyword] 

        logging.debug('Target Jobs:' + ', '.join([str(elem) for elem in self.job_targets]))

    def start_requests(self):
        yield scrapy.Request(f'https://jobs.workable.com/search?remote=false', callback=self.start_requests_2,
        meta={
                'count':0,
                'page':1,
        })    

    def start_requests_2(self, response):
        yield scrapy.Request(f'https://jobs.workable.com/api/v1/jobs?remote=false&offset=0', callback=self.parse,
        meta={
                'count':0,
                'page':1,
        })         

    def parse(self, response):
        result = json.loads(response.text)
        for job in result['jobs']:
            job_parsed = {
                'Title' : job['title']
            }
            yield job_parsed
                    
        meta = response.meta
        meta['count'] += 10
        meta['page'] += 1
        if meta['count'] < result['totalSize']:
            yield scrapy.Request(f"https://jobs.workable.com/api/v1/jobs?remote=false&offset={meta['page']}",
            callback=self.parse,
            meta=meta)
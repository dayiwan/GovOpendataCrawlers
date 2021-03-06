# -*- coding: utf-8 -*-
import os, json
import requests
from scrapy.conf import settings
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
from .util.FileSummary import FilesSummary
from .util.LastCrawl import LastCrawl


class KaiFangGuangDongPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        """重写请求生成函数"""
        file_urls = item['file_urls']
        file_name = item['file_names']
        for index in range(len(file_urls)):
            yield Request(file_urls[index], meta={"dataset_name": item['title'], "file_name": file_name[index]})

    def file_path(self, request, response=None, info=None):
        """重写保存路径函数"""
        return '%s/%s' % (request.meta['dataset_name'], request.meta.get('file_name', 'file'))

    def item_completed(self, results, item, info):
        """重写下载完成钩子函数"""

        dir_name = 'files/%s' % item['title']
        metadata_json_file = '%s/metadata.json' % dir_name
        # 写入元数据json
        with open(metadata_json_file, 'w', encoding='utf8') as f:
            json.dump(item['metadata'], f, ensure_ascii=False)

    def close_spider(self, spider):
        dataset_count = FilesSummary.dataset_count()
        size_mb = FilesSummary.size_mb()

        # data = {
        #     'address': '172.16.119.3',
        #     'project_name': settings.get('BOT_NAME'),
        #     'file_number': dataset_count - LastCrawl.dataset_count(),
        #     'file_size': size_mb - LastCrawl.total_file_size_mb(),
        # }
        # res = requests.post(
        #     url=settings.get('DATARECORDADDRESS'),
        #     data=data)
        # if not res.status_code == 200:
        #     logging.info('关闭爬虫时错误，保存数据记录出错！')

        LastCrawl.write(dataset_count=dataset_count, total_file_size_mb=size_mb)

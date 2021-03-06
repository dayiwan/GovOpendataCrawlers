# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from scrapy.pipelines.files import FilesPipeline
from scrapy import FormRequest, Request
from ChengDuOpendata.settings import BOT_NAME
from ChengDuOpendata.utils import toolkit
from ChengDuOpendata.utils.FileSummary import FilesSummary
from ChengDuOpendata.utils.LastCrawl import LastCrawl

class ChengduopendataPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        """重写请求生成函数"""
        Host = 'http://www.cddata.gov.cn/odweb/catalog/CatalogDetailDownload.do?method=getFileDownloadAddr&fileId='
        yield Request(url=Host + item['fileId'], meta={
            "dataset_name": item['metadata']['数据目录名称'],
            "file_name": item['fileName']
        })

    def file_path(self, request, response=None, info=None):
        """重写保存路径函数"""
        return '%s/%s' % (request.meta['dataset_name'], request.meta['file_name'])

    def item_completed(self, results, item, info):
        """重写下载完成钩子函数"""
        dir_name = 'files/%s' % item['metadata']['数据目录名称']
        metadata_json_file = '%s/metadata.json' % dir_name
        datafield_json_file = '%s/datafield.json' % dir_name
        # # 解压文件并删除安装包
        # toolkit.un_zip(file_name=zip_file, dir_name=dir_name)
        # os.remove(zip_file)
        # 写入元数据json
        with open(metadata_json_file, 'w', encoding='utf8') as f:
            json.dump(item['metadata'], f, ensure_ascii=False)

        with open(datafield_json_file, 'w', encoding='utf8') as f:
            json.dump(item['datafield'], f, ensure_ascii=False)

        # return item

    def close_spider(self, spider):
        dataset_count = FilesSummary.dataset_count()
        size_mb = FilesSummary.size_mb()

        data = {
            'address': '172.16.119.3',
            'project_name': BOT_NAME,
            'file_number': dataset_count - LastCrawl.dataset_count(),
            'file_size': size_mb - LastCrawl.total_file_size_mb(),
        }
        print(data)
    #     # res = requests.post(
    #     #     url=settings.get('DATARECORDADDRESS'),
    #     #     data=data)
    #     # if not res.status_code == 200:
    #     #     logging.info('关闭爬虫时错误，保存数据记录出错！')
    #
        LastCrawl.write(dataset_count=dataset_count, total_file_size_mb=size_mb)
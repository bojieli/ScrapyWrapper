#!/usr/bin/python3
import sys
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

table_name = sys.argv[1]
column_name = sys.argv[2]
output_folder = sys.argv[3]

config = ScrapyWrapperConfig()
config.file_basedir = output_folder
myspider = SpiderFactory(config, __name__)()
myspider.prepare_db()
myspider.download_images_from_db_table(table_name, column_name)

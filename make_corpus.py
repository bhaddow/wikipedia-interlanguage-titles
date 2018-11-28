#!/usr/bin/env python3

import argparse
import logging
import os
import os.path
import re
import wget

import wikititles

LOG = logging.getLogger(__name__)

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s:  %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--source-language", required=True, help="Source language - langlinks file for this language will be downloaded")
  parser.add_argument("-r", "--refresh", action="store_true", help="Re-download wikidumps")
  parser.add_argument("-t", "--target-language", default="en")
  parser.add_argument("-w", "--working-directory", default=".")
  parser.add_argument("-o", "--output-stem", default="wikititles")
  args = parser.parse_args()

  # Check for wiki dumps and download if necessary
  #eswiki-latest-langlinks.sql  eswiki-latest-page.sql
  page_file = "{}/{}wiki-latest-page.sql.gz".format(args.working_directory, args.source_language)
  langlinks_file = "{}/{}wiki-latest-langlinks.sql.gz".format(args.working_directory, args.source_language)

  if args.refresh or not os.path.exists(page_file):
    if os.path.exists(page_file): os.unlink(page_file)
    url = "https://dumps.wikimedia.org/{0}wiki/latest/{0}wiki-latest-page.sql.gz".format(args.source_language)
    LOG.debug("Downloading from " + url)
    wget.download(url, out=page_file)
  else:
    LOG.debug("Using existing page file")

  if args.refresh or not os.path.exists(langlinks_file):
    if os.path.exists(langlinks_file): os.unlink(langlinks_file)
    url = "https://dumps.wikimedia.org/{0}wiki/latest/{0}wiki-latest-langlinks.sql.gz".format(args.source_language)
    LOG.debug("Downloading from " + url)
    wget.download(url, out=langlinks_file)
  else:
    LOG.debug("Using existing langlinks file")

  output_file = "{0}/wikititles.{1}-{2}.tsv".format(args.working_directory, args.source_language, args.target_language)
  LOG.debug("Writing corpus to " + output_file)
  brackets = re.compile(r"\([^\)]*\)")
  with open(output_file, "w") as ofh:
    for (page_id, ori_title, tar_title) in wikititles.match_titles(page_file, langlinks_file, args.target_language, None):
      tar_title = tar_title.split(":")
      if len(tar_title) > 1:
        tar_title = tar_title[-1]
      else:
        tar_title = tar_title[0]
      ori_title = ori_title.replace("_", " ")
      tar_title = tar_title.replace("_", " ")
      ori_title = re.sub(brackets,"",ori_title)
      tar_title = re.sub(brackets,"",tar_title)
      print("{}\t{}".format(ori_title,tar_title), file=ofh)


if __name__ == "__main__":
  main()




cd /root/ig/ig_crawler/ig_crawler
for i in {1..12};
do
  nohup scrapy crawl ig >/dev/null &
done

cp -f proxy_api.service /etc/systemd/system/
cp -f proxy_crawler.service /etc/systemd/system/
systemctl enable proxy_api.service
systemctl enable proxy_crawler.service
systemctl start proxy_api.service
systemctl start proxy_crawler.service

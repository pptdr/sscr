sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl enable nginx
sudo service nginx restart

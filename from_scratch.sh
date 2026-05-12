sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile


git clone https://github.com/tugberko/app-analytics.git

apt install docker.io

cd app-analytics/

docker build -t "app-analytics" .

docker run -d -p 5000:5000 app-analytics

sudo apt install nginx
sudo systemctl enable nginx
sudo systemctl start nginx


sudo nano /etc/nginx/sites-available/levrek.tugberk.cloud


server {
    listen 80;
    server_name levrek.tugberk.cloud;

    location / {
        proxy_pass http://127.0.0.1:5000;  # your docker port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}


sudo ln -s /etc/nginx/sites-available/levrek.tugberk.cloud /etc/nginx/sites-enabled/

sudo nginx -t

sudo systemctl reload nginx

sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d levrek.tugberk.cloud


git clone https://github.com/tugberko/app-analytics.git

apt install docker.io

cd app-analytics/

docker build -t "app-analytics" .

docker run -d -p 5000:5000 app-analytics
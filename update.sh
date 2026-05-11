APP_NAME="practivo-analytics-service"

git pull

CONTAINERS=$(sudo docker ps -q --filter ancestor="$APP_NAME")

if [ ! -z "$CONTAINERS" ]; then
  sudo docker stop $CONTAINERS
  sudo docker rm $CONTAINERS
fi

sudo docker build -t "$APP_NAME" .

sudo docker run -d \
  --name "$APP_NAME" \
  --restart unless-stopped \
  -p 5000:5000 \
  "$APP_NAME"
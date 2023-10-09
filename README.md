# Runbot-bridge

Bridge Bitget x Runbot

## Usage
Stop, resume or start the bot via CLI :
Attach the docker console.
```bash
docker attach runbot-bridge-cli-1
```
CTRL-P + CTRL-Q to detach console.

## Deployment
### Production
```bash
git checkout production
docker compose -p runbot-bridge-production down
docker-compose -f compose.production.yml build --no-cache #If updated code
docker-compose -f compose.production.yml -p runbot-bridge-production up -d 
```


### Staging 
Run the tests (There are some tests passing real orders and mock ones).
```bash
git checkout staging
docker compose -p runbot-bridge-staging down
docker-compose -f compose.staging.yml build --no-cache #If updated code
docker-compose -f compose.staging.yml -p runbot-bridge-staging up -d
```
Go on Runbot, use the staging bot to test live.




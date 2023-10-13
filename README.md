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
docker-compose -f compose.production.yml build  #If updated code
docker-compose -f compose.production.yml -p runbot-bridge-production up -d 
```


### Staging 
Run the tests (There are some tests passing real orders and mock ones).
```bash
git checkout <RELEASE NAME>
docker compose -p runbot-bridge-staging down
docker-compose -f compose.staging.yml build  #If updated code
docker-compose -f compose.staging.yml -p runbot-bridge-staging up -d
```
Go on Runbot, use the staging bot to test live.

## Logging
Logging is done via stdout and stderr from docker containers.
You can fetch max 1GB of log per container.
```bash
docker compose -p runbot-bridge-STAGE logs 
```
Or if you want to analyze it from your local and download it as a file in your Downloads folder, use the custom script.
Automatically open VSCODE as well.
```bash
fetch_logs -p runbot-bridge-STAGE -h SERVER_SSH_NAME
```


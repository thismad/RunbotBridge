# Runbot-bridge

Bridge Bitget x Runbot

## Usage

Check the correct branch is used (main for production or staging for development).
```bash
docker compose -p runbot-bridge-production down
docker-compose -f compose.production.yml build --no-cache #If updated code
docker-compose -f compose.production.yml -p runbot-bridge-production up -d 

```

Attach console if you want to interact :

```bash
docker attach runbot-bridge-cli-1
```

CTRL-P + CTRL-Q to detach console.

## For staging testing 
Run the tests (There are some tests passing real orders and mock ones).
```bash
docker compose -p runbot-bridge-staging down
docker-compose -f compose.staging.yml build --no-cache #If updated code
docker-compose -f compose.staging.yml -p runbot-bridge-staging up -d
```
Go on Postman and run local/staging/prod curl requests.
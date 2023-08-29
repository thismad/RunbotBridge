# Runbot-bridge

Bridge Bitget x Runbot

## Usage

Check the correct branch is used (main for production or staging for development).
```bash
docker-compose build --no-cache #If updated code
docker-compose up -d
```

Attach console if you want to interact :

```bash
docker attach runbot-bridge-cli-1
```

CTRL-P + CTRL-Q to detach console.

## For local testing 
Run the tests (There are some tests passing real orders and mock ones).
```bash
docker-compose build --no-cache #If updated code
docker-compose up -d
```
Go on Postman and run local/staging/prod curl requests.
# dragonpottery-bot
Telegram bot [@dragonpottery_bot](https://t.me/dragonpottery_bot).

## Build
```shell
podman manifest create poofeg/dragonpottery-bot:latest
podman build --target=main --platform=linux/amd64,linux/arm64 --manifest=poofeg/dragonpottery-bot:latest .
podman manifest push poofeg/dragonpottery-bot:latest
```
Pre-built images available on Docker Hub: https://hub.docker.com/r/poofeg/dragonpottery-bot

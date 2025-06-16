# Squobert

Squobert is a conversational AI agent built with [Pipecat](https://pipecat.ai) and running on [Pipecat Cloud](https://pipecat.daily.co). He was featured at the [2025 AI Engineer World's Fair](https://www.ai.engineer/) in San Francisco.

![squobert](./squobert.jpeg)

Squobert is powered by a Raspberry Pi and a Jabra 410 USB speaker/microphone. His face is a React app that runs in a fullscreen browser.

## Running the bot

```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
LOCAL_RUN=1 python bot.py
```

To deploy it to Pipecat Cloud, edit `bot/build.sh` and `bot/pcc-deploy.toml` and run:

```bash
cd bot
./build.sh
pcc deploy
```

## Running the client UI

```
cd client
npm i
npm run dev
```

Then add a Pipecat Cloud public key to `client/src/providers/RTVIProvider.tsx`.

The client code is a bit of a mess to make the touch interactions work the way I wanted them to, but you should be able to understand it well enough to do something useful with it if you want. Claude wrote most of it, after all. :)

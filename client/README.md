# Voice UI Kit with Next.js

A simple voice chatbot using [@pipecat-ai/voice-ui-kit](https://www.npmjs.com/package/@pipecat-ai/voice-ui-kit) and Next.js.

## Getting Started

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Start the dev server:**

   ```bash
   npm run dev
   ```

3. **Start your Pipecat bot** (in a separate terminal):

   ```bash
   cd ../server

   # For SmallWebRTC
   uv run bot.py

   # or Daily
   uv run bot.py -t daily
   ```

4. Open http://localhost:3000, select a matching transport, and click **Connect** to start talking to your bot.

## Transport Options

### SmallWebRTC (Local Development only)

Direct peer-to-peer WebRTC connection via `/api/offer`.

**Limitations:** Requires both client and bot to be network-accessible to each other. Not recommended for production deployments.

### Daily (Local or Production deployment)

Uses a Next.js API route (`/api/start`) to create a Daily room and connect to your bot.

**Local Development:**

- Works out of the box with `http://localhost:7860/start`
- No configuration needed

**Production:**
Set environment variables:

```bash
BOT_START_URL=https://api.pipecat.daily.co/v1/public/{agentName}/start
BOT_START_PUBLIC_API_KEY=your-secret-key # Your Pipecat Cloud public API key
```

See `src/app/api/start/route.ts` for the implementation.

## Customization

See the [voice-ui-kit docs](https://voiceuikit.pipecat.ai/) to learn how to style and customize your voice AI app.

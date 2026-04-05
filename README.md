# OpenClaw Configuration Backup

This repository contains my OpenClaw configuration with secrets redacted.

## Restoring to a New Machine

### Prerequisites
- Docker installed
- Git

### Step 1: Clone this repository
```bash
git clone https://github.com/codingalpha368/openclaw-config.git
cd openclaw-config
```

### Step 2: Run OpenClaw Docker container
```bash
# Create directories for persistence
mkdir -p ~/.openclaw

# Copy config (secrets redacted - see Step 3)
cp openclaw.json ~/.openclaw/
cp jobs.json ~/.openclaw/
mkdir -p ~/.openclaw/agents/main/agent
cp agents/main/agent/auth-profiles.json ~/.openclaw/agents/main/agent/
cp agents/main/agent/models.json ~/.openclaw/agents/main/agent/

# Run OpenClaw
docker run -d \
  --name openclaw \
  -v ~/.openclaw:/home/node/.openclaw \
  -v /home/node/.openclaw/workspace:/home/node/.openclaw/workspace \
  -p 18789:18789 \
  openclai/openclaw
```

### Step 3: Add your secrets
Edit `~/.openclaw/openclaw.json` and replace `<REDACTED>` with your actual tokens:

```json
{
  "channels": {
    "discord": {
      "token": "YOUR_ACTUAL_DISCORD_BOT_TOKEN"
    }
  },
  "gateway": {
    "auth": {
      "token": "YOUR_GATEWAY_AUTH_TOKEN"
    }
  },
  "auth": {
    "profiles": {
      "minimax-portal:default": {
        "provider": "minimax-portal",
        "apiKey": "YOUR_MINIMAX_API_KEY"
      }
    }
  }
}
```

### Step 4: Restart the container
```bash
docker restart openclaw
```

## Getting Tokens

### Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Select your bot → Bot → Reset Token

### MiniMax API Key
1. Go to https://platform.minimax.io/
2. API Keys → Create API Key

## Files Reference

| File | Description |
|------|-------------|
| `openclaw.json` | Main configuration (secrets redacted) |
| `jobs.json` | Cron jobs for automation |
| `agents/main/agent/auth-profiles.json` | Auth profile configurations |
| `agents/main/agent/models.json` | Model configurations |

## Updating Config

After making config changes:
```bash
# Pull latest
git pull

# After editing config
git add .
git commit -m "Update config"
git push
```

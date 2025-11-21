# Italian Vocabulary Practice - Windows + ngrok Setup

## Share Your Vocabulary Tool via Internet

### Step 1: Download ngrok for Windows

1. Visit: https://ngrok.com/download
2. Click **Windows (64-bit)** to download `ngrok-v3-stable-windows-amd64.zip`
3. Extract the zip file to a folder (e.g., `C:\ngrok\`)

### Step 2: Start Your Vocabulary Server

Open PowerShell in your `italian-trainer` folder and run:

```powershell
python vocab.py web
```

Keep this window open - the server is running on port 5000.

### Step 3: Start ngrok Tunnel

Open a **second** PowerShell window and navigate to where you extracted ngrok:

```powershell
cd C:\ngrok
.\ngrok http 5000
```

You'll see output like:

```
Session Status                online
Account                       <your account>
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000
```

### Step 4: Share the URL

Copy the `https://abc123.ngrok-free.app` URL and share it with anyone!

They can access your vocabulary tool from anywhere in the world through that link.

**Important Notes:**
- The URL changes each time you restart ngrok (unless you have a paid account)
- Both PowerShell windows must stay open
- Free ngrok has a connection limit (~40 connections/minute)
- Your vocabulary file will be served from your computer

### Optional: Get a Persistent URL

Create a free ngrok account:
1. Visit: https://dashboard.ngrok.com/signup
2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure it once:

```powershell
.\ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

Then you can use reserved domains (optional paid feature) or just get better limits on the free tier.

### Stop Sharing

Press `Ctrl+C` in the ngrok window to stop the tunnel.
Press `Ctrl+C` in the Python window to stop the server.

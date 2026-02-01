# Morssenger

Morssenger is a Morse-code messageg app with a flashing UI. It can run with or without AI (Amazon Bedrock) for Morse conversion.

## Requirements
- Python 3.9+
- Tkinter (usually included with Python on Windows)
- Optional: AWS credentials for Bedrock

## Install dependencies

```
pip install boto3
```

## Configure AWS (optional)
Create `aws_credentials.ini` in the project root:

```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1
```

Then enable Bedrock model access in AWS Console for the model you choose.

## Run the UI app

```
python UI.py
```

### UI Controls
- **Target IP / Port**: connection settings
- **AI Model**: choose a Bedrock model or **None (Local Dictionary)** to avoid AI usage/billing
- **Flash Color**: set the flash color for incoming Morse
- **Start Server (Listen)**: wait for a connection
- **Connect (Client)**: connect to a server
- **Disconnect**: close the current connection

## Run the CLI app (optional)
The original CLI version is still available:

```
python ptp.py server 5000
python ptp.py client <server-ip> 5000
```

## Notes
- If no AI model is selected, conversion uses the local Morse dictionary.
- Bedrock errors will automatically fall back to the local dictionary.

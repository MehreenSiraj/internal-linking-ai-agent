# Deployment Guide

This guide covers deploying the Internal Linking AI Agent to a VPS and integrating with n8n.

---

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ (or similar Linux)
- Python 3.8+
- Git
- n8n instance (local or hosted)
- Basic terminal/SSH knowledge

---

## 🚀 Step 1: VPS Setup

### 1.1 SSH into your VPS
```bash
ssh user@your-vps-ip
```

### 1.2 Update system
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Install Python and Git
```bash
sudo apt install -y python3.9 python3.9-venv python3-pip git
```

### 1.4 Create application directory
```bash
sudo mkdir -p /var/www/internal-linking-agent
sudo chown $USER:$USER /var/www/internal-linking-agent
cd /var/www/internal-linking-agent
```

---

## 📦 Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/internal-linking-ai-agent.git .
```

---

## 🔧 Step 3: Python Environment

```bash
# Create virtual environment
python3.9 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 Step 4: Verify Installation

```bash
# Run test suite
python test_internal_linking.py
```

Expected output:
```
Ran 17 tests in 2.101s
OK
```

---

## 📁 Step 5: Directory Structure

```bash
# Create output directory for reports
mkdir -p /var/www/internal-linking-agent/output

# Set permissions
chmod 755 /var/www/internal-linking-agent/output
```

---

## 🔗 Step 6: n8n Integration

### 6.1 Create wrapper script

Create `/var/www/internal-linking-agent/agent_wrapper.sh`:

```bash
#!/bin/bash
# Wrapper script for n8n integration

SCRIPT_DIR=/var/www/internal-linking-agent
VENV_DIR=$SCRIPT_DIR/venv
SITE_URL=$1
OUTPUT_DIR=$SCRIPT_DIR/output

# Exit if no URL provided
if [ -z "$SITE_URL" ]; then
  echo '{"status":"error","errors":["No site URL provided"]}'
  exit 1
fi

# Activate venv and run agent
source $VENV_DIR/bin/activate
cd $SCRIPT_DIR

# Run agent with JSON output
python run_agent.py --site "$SITE_URL" --json-output

# Deactivate venv
deactivate
```

Make it executable:
```bash
chmod +x /var/www/internal-linking-agent/agent_wrapper.sh
```

### 6.2 Configure n8n

In n8n, create a workflow:

**1. Webhook trigger (HTTP POST)**
- Path: `/internal-linking`
- Accept: JSON body with `site` field

Example JSON:
```json
{
  "site": "https://example.com"
}
```

**2. Execute command node**
```bash
/var/www/internal-linking-agent/agent_wrapper.sh {{$node["Webhook"].json.site}}
```

**3. Parse JSON output**
- Set output type: JSON

**4. Send response**
- Return JSON from previous step

---

## 📊 Step 7: Output Management

### 7.1 Archive old reports (cron job)

Create `/var/www/internal-linking-agent/cleanup.sh`:

```bash
#!/bin/bash
# Archive outputs older than 30 days

OUTPUT_DIR="/var/www/internal-linking-agent/output"
ARCHIVE_DIR="$OUTPUT_DIR/archive"
DAYS=30

# Create archive directory if it doesn't exist
mkdir -p $ARCHIVE_DIR

# Find and gzip old files
find $OUTPUT_DIR -maxdepth 1 -type f \( -name "*_links.csv" -o -name "*_report.pdf" \) -mtime +$DAYS -exec gzip {} \; -exec mv {}.gz $ARCHIVE_DIR \;

echo "Archived outputs older than $DAYS days"
```

Make executable and add to crontab:
```bash
chmod +x /var/www/internal-linking-agent/cleanup.sh

# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * /var/www/internal-linking-agent/cleanup.sh
```

---

## 🔒 Step 8: Security Configuration

### 8.1 Firewall (if applicable)

Only allow necessary ports:
```bash
# If using UFW
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 8.2 User permissions

Create dedicated user (optional but recommended):
```bash
sudo useradd -m -s /bin/bash agent-user
sudo chown -R agent-user:agent-user /var/www/internal-linking-agent
```

### 8.3 Environment variables

Create `.env` file (if needed for future config):
```bash
cd /var/www/internal-linking-agent
touch .env
chmod 600 .env
```

Example `.env`:
```
MAX_PAGES_CRAWL=200
CLUSTER_MIN=2
CLUSTER_MAX=15
OUTPUT_DIR=/var/www/internal-linking-agent/output
```

---

## 📝 Step 9: Logging Setup

Create log directory:
```bash
mkdir -p /var/www/internal-linking-agent/logs
chmod 755 /var/www/internal-linking-agent/logs
```

Update `run_agent.py` logging to write to file:
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/internal-linking-agent/logs/agent.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🔄 Step 10: systemd Service (Optional)

For automatic startup on reboot, create `/etc/systemd/system/internal-linking-agent.service`:

```ini
[Unit]
Description=Internal Linking AI Agent
After=network.target

[Service]
Type=simple
User=agent-user
WorkingDirectory=/var/www/internal-linking-agent
ExecStart=/var/www/internal-linking-agent/venv/bin/python /var/www/internal-linking-agent/run_agent.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable internal-linking-agent
sudo systemctl start internal-linking-agent
```

---

## 📈 Monitoring & Maintenance

### Monitor logs
```bash
tail -f /var/www/internal-linking-agent/logs/agent.log
```

### Check disk usage
```bash
du -sh /var/www/internal-linking-agent/output
```

### Update code
```bash
cd /var/www/internal-linking-agent
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python test_internal_linking.py
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|---|---|
| `Permission denied` on wrapper script | Run `chmod +x agent_wrapper.sh` |
| `Module not found` errors | Verify venv is activated: `source venv/bin/activate` |
| n8n webhook timeout | Increase timeout in n8n; crawling can take 5-10 minutes |
| Disk space issues | Run cleanup script manually: `/var/www/internal-linking-agent/cleanup.sh` |
| High CPU usage | Crawling is CPU-intensive. Schedule non-peak hours. |

---

## 📊 Performance Optimization

### For large sites:

1. **Increase timeouts** in crawler.py:
   ```python
   r = requests.get(url, timeout=30)  # Increase from 10
   ```

2. **Batch by sections**: Crawl `/blog/*` separately from `/products/*`

3. **Use caching**: Store embeddings locally to skip recomputation

4. **Database**: Store results in PostgreSQL instead of CSV

---

## ✅ Deployment Checklist

- [ ] VPS has Python 3.8+
- [ ] Git repo cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Test suite passes (17/17)
- [ ] Wrapper script created and executable
- [ ] n8n webhook configured
- [ ] Output directory created
- [ ] Cron job for cleanup added
- [ ] Firewall rules configured
- [ ] Logs directory created
- [ ] First test run successful

---

## 🎉 Next Steps

1. Test with a real website: `/var/www/internal-linking-agent/agent_wrapper.sh https://yoursite.com`
2. Verify CSV, PDF, and JSON outputs in `output/` directory
3. Configure n8n workflow
4. Set up monitoring/alerting

---

## 📞 Support

For issues during deployment:
1. Check logs: `tail -f /var/www/internal-linking-agent/logs/agent.log`
2. Run tests: `python test_internal_linking.py`
3. Verify environment: `python -c "import nltk; print('OK')"`

---

**Happy deploying! 🚀**

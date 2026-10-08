# Ubuntu headless deployment

Copy the project source files to `/opt/pepe-collector` on the Ubuntu host, excluding the Windows `.venv` directory. Then run these commands:

```bash
sudo apt update
sudo apt install -y python3-venv
cd /opt/pepe-collector
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Confirm `.env` contains `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and optionally `BINANCE_SYMBOL=PEPEUSDT`. Keep `.env` private.

## Run manually

```bash
.venv/bin/python pepe_collector.py
```

## Run continuously with systemd

The included `pepe-collector.service` assumes the project is installed at `/opt/pepe-collector` and runs as the `pepecollector` user:

```bash
sudo useradd --system --home /opt/pepe-collector --shell /usr/sbin/nologin pepecollector
sudo mkdir -p /opt/pepe-collector
sudo chown -R pepecollector:pepecollector /opt/pepe-collector
sudo chmod 600 /opt/pepe-collector/.env
sudo cp pepe-collector.service /etc/systemd/system/pepe-collector.service
sudo systemctl daemon-reload
sudo systemctl enable --now pepe-collector
```

Check status and logs:

```bash
sudo systemctl status pepe-collector
sudo journalctl -u pepe-collector -f
```

Owl deployment guide for fist time
==================================

Preparation
-----------

### Prerequicites:

```bash
sudo apt-get install build-essential python3-pip postgresql libpq-dev
```

### Virtual env

```bash
sudo pip3 install -U pip setuptools wheel
sudo pip3 install virtualenvwrapper
``` 

##### Create and login as `dev` user

```bash
sudo adduser dev
su - dev
mkdir ~/workspace
echo "export VIRTUALENVWRAPPER_PYTHON=`which python3.6`" >> ~/.bashrc
echo "alias v.activate=\"source $(which virtualenvwrapper.sh)\"" >> ~/.bashrc
source ~/.bashrc
v.activate
mkvirtualenv --python=$(which python3.6) --no-site-packages dolphin

```

##### Setup Database

```bash
echo 'CREATE USER dev' | sudo -u postgres psql
echo 'CREATE DATABASE dolphin' | sudo -u postgres psql
echo 'GRANT ALL PRIVILEGES ON DATABASE dolphin TO dev' | sudo -u postgres psql
echo "ALTER USER dev WITH PASSWORD 'password'" | sudo -u postgres psql
```

##### Config file

Create a file `/etc/maestro/dolphin.yml` with this contents:

```yaml
db:
  url: postgresql://dev:password@localhost/dolphin
  echo: false

logging:

  handlers:
    main:
      filename: /var/log/dolphin/dolphin.log
      
    error:
      filename: /var/log/dolphin/error.log
    
    worker:
      filename: /var/log/dolphin/worker.log
    
  loggers:
    worker:
      handlers: [worker, error]
      level: info

```

### Install

#### dolphin:
```bash
su - dev
cd ~/workspace/dolphin
v.activate && workon dolphin
pip install -e .
```

##### Database objects

```bash
v.activate && workon dolphin
dolphin -c /etc/maestro/dolphin.yml db schema
```

##### wsgi

/etc/maestro/dolphin_wsgi.py
```python
from dolphin import dolphin as app


app.configure(files='/etc/maestro/dolphin.yml')
app.initialize_orm()

```

##### Systemd

/etc/systemd/system/dolphin.service:

```ini
[Unit]
Description=dolphin API daemon
Requires=dolphin.socket
After=network.target

[Service]
PIDFile=/run/dolphin/pid
User=dev
Group=dev
WorkingDirectory=/home/dev/workspace/dolphin/
ExecStart=/home/dev/.virtualenvs/dolphin/bin/gunicorn --pid /run/dolphin/pid --chdir /etc/maestro dolphin_wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target


```

/etc/systemd/system/dolphin.socket:

```ini
[Unit]
Description=dolphin socket

[Socket]
ListenStream=/run/dolphin.socket

[Install]
WantedBy=sockets.target
```

/usr/lib/tmpfiles.d/dolphin.conf:

```
d /run/dolphin 0755 dev dev -
```

Next enable the services so they autostart at boot:

```bash
systemd-tmpfiles --create
systemctl daemon-reload
systemctl enable dolphin.socket
```

Either reboot, or start the services manually:

```bash
systemctl start dolphin.socket
```

### NGINX

/etc/nginx/sites-available/maestro.carrene.com

```
upstream dolphin_webapi {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response
    server unix:/var/run/dolphin.socket fail_timeout=0;
}

server {
    listen 80;

    server_name maestro.carrene.com;

    root /home/dev/workspace/otter;
    index index.html;


    location /apiv1/ {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_redirect off;
      proxy_pass http://dolphin_webapi;
    }
}

```

```bash
ln -s /etc/nginx/sites-available/maestro.carrene.com /etc/nginx/sites-enabled/
```

### Restart service

```bash
service nginx restart
service dolphin restart
```

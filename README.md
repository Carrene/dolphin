
dolphin
===
branches
---
### master
[![Build Status](https://travis-ci.com/Carrene/dolphin.svg?token=6WpJ2w8ex7Mp4ndx7xs2&branch=master)](https://travis-ci.com/Carrene/dolphin) 
[![Coverage Status](https://coveralls.io/repos/github/Carrene/dolphin/badge.svg?t=fWXT5d)](https://coveralls.io/github/Carrene/dolphin)

![dolphin](https://www.wildquest.com/wp-content/gallery/wallpapers-2014/September-2017.jpg)

### Installing Dependencies

    $ sudo apt-get install libass-dev libpq-dev postgresql \
      build-essential redis-server redis-tools


### Setup Python environment

    $ sudo apt-get install python3-pip python3-dev
    $ sudo pip3 install virtualenvwrapper
    $ echo "export VIRTUALENVWRAPPER_PYTHON=`which python3.6`" >> ~/.bashrc
    $ echo "alias v.activate=\"source $(which virtualenvwrapper.sh)\"" >> ~/.bashrc
    $ source ~/.bashrc
    $ v.activate
    $ mkvirtualenv --python=$(which python3.6) --no-site-packages dolphin


#### Activating virtual environment

      $ workon dolphin

#### Upgrade pip, setuptools and wheel to the latest version

      $ pip install -U pip setuptools wheel


### Installing Project by pip
        
You can install by 'pip install' and use https by the following way:
      
      $ pip install git+https://github.com/Carrene/dolphin.git

Or you can use SSH:
      
      $ pip install git+git@github.com:Carrene/dolphin.git 


### Installing Project (edit mode)

So, your changes will affect instantly on the installed version

#### dolphin

      $ cd /path/to/workspace
      $ git clone git@git.carrene.com:web/dolphin.git
      $ cd dolphin
      $ pip install -e .

#### Enabling the bash autocompletion for dolphin

      $ echo "eval \"\$(register-python-argcomplete dolphin)\"" >> $VIRTUAL_ENV/bin/postactivate    
      $ deactivate && workon dolphin\
      
### Setup Database

#### Configuration

Dolphin is zero configuration application and there is no extra configuration file needed, but if you want to have your own 
configuration file, you can make a `dolphin.yml` in the following  path: `~/.config/dolphin.yml`

#### Remove old abd create a new database **TAKE CARE ABOUT USING THAT**

    $ dolphin db create --drop --basedata [or instead of --basedata, --mockup]

#### Drop old database: **TAKE CARE ABOUT USING THAT**

    $ dolphin [-c path/to/config.yml] db drop

#### Create database

    $ dolphin [-c path/to/config.yml] db create

Or, you can add `--drop` to drop the previously created database: **TAKE CARE ABOUT USING THAT**

    $ dolphin [-c path/to/config.yml] db create --drop
    
#### Create schema

    $ dolphin [-c path/to/config.yml] db schema      
      
### Serving

- Using python builtin http server

```bash
$ dolphin serve
```    

- Gunicorn

```bash
$ ./gunicorn
```

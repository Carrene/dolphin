# dolphin


![dolphin](https://www.wildquest.com/wp-content/gallery/wallpapers-2014/July-2017.jpg)


### Installing Dependencies

    $ sudo apt-get install libass-dev libpq-dev postgresql \
      build-essential redis-server redis-tools


### Setup Python environment

      $ sudo apt-get install python3-pip python3-dev
      $ sudo pip3.6 install virtualenvwrapper
      $ echo "export VIRTUALENVWRAPPER_PYTHON=`which python3.6`" >~/.bashrc
      $ echo "alias v.activate=\"source $(whicvirtualenvwrapper.sh)\"" >> ~/.bashrc
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

#### nanohttp

    $ cd /path/to/workspace
    $ git clone git@github.com:Carrene/nanohttp.git
    $ cd nanohttp
    $ pip install -e .
    
#### restfulpy
    
    $ cd /path/to/workspace
    $ git clone git@github.com:Carrene/restfulpy.git
    $ cd restfulpy
    $ pip install -e .

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

Create a file named `~/.config/dolphin.yml`

```yaml
db:
  url: postgresql://postgres:postgres@localhost/dolphin_dev
  test_url: postgresql://postgres:postgres@localhost/dolphin_test
  administrative_url: postgresql://postgres:postgres@localhost/postgres

```


### Serving

- Using python builtin http server

```bash
$ dolphin [-c path/to/config.yml] serve
```    

- Gunicorn

```bash
$ ./gunicorn
```

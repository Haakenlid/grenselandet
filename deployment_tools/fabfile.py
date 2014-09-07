""" Deployment of Django website using pyvenv-3.4 and git """
import os
from os.path import join, dirname
from fabric.contrib.files import append, exists, put
from fabric.context_managers import shell_env
from fabric.api import local, env, run, sudo, settings, task
from generate_postactivate import make_postactivate_file

REPO_URL = 'https://github.com/user/reponame.git'  # github repo used for deploying the site
PYVENV = 'pyvenv-3.4'  # using python 3.4
LINUXGROUP = 'www-data'  # linux user group on the webserver
WEBSERVER_ROOT = '/srv'  # root folder for all websites on the webserver
SITE_DOMAIN = 'example.com'


@task(alias='local')
def localhost():
    env.sudo = local
    env.run = local
    env.hosts = ['local.{}'.format(SITE_DOMAIN)]


@task(alias='dev')
def development_server():
    env.run = run
    env.sudo = sudo
    env.hosts = ['dev.{}'.format(SITE_DOMAIN)]


def _get_folders(site_url):
    """ Return a dictionary containing pathnames of named project folders. """
    folders = {
        'site': '{site_folder}',                   # project root folder
        'source': '{site_folder}/source',          # django source code
        'bin': '{site_folder}/bin',                # bash scripts
        'static': '{site_folder}/static',          # static files served by nginx
        'media': '{site_folder}/static/media',     # user uploaded files
        'venv': '{site_folder}/venv/{venv_name}',  # python virtual environment
        'logs': '{site_folder}/logs',              # contians logfiles
        'venvs': '/home/{user}/.venvs',            # global folder with symlinks to all virtual environments
    }
    for folder in folders:
        folders[folder] = folders[folder].format(
            venv_name=site_url,
            site_folder='{root}/{url}'.format(root=WEBSERVER_ROOT, url=site_url,),
            user=env.user,
        )

    return folders


def _get_configs(site_url, user_name=None, bin_folder=None, config_folder=None,):
    """ Return a dictionary containing configuration for webserver programs and services. """
    # user name for database and linux
    user_name = user_name or site_url.replace('.', '_')
    # folder to put shell scripts
    bin_folder = bin_folder or '{root}/{url}/bin'.format(root=WEBSERVER_ROOT, url=site_url)
    # parent folder of config file templates.
    config_folder = config_folder or dirname(__file__)

    configs = {
        # 'service': { # name of program or service that need configuration files.
        # 'template': # template for configuration file
        # 'filename': # what to call the config file made from template
        # 'target folder': # where to put the config file
        # 'install': # bash command to prepare and activate the config file.
        # 'start': # bash command to start the service
        # 'stop': # bash command to stop the service
        # },
        'gunicorn': {  # python wsgi env.runner for django
            'template': '{config}/gunicorn/template'.format(config=config_folder,),
            'filename': '{user}_gunicorn.sh'.format(user=user_name,),
            'target folder': bin_folder,
            # make bash file executable by the supervisor user.
            'install': 'sudo chmod 774 $FILENAME && env.sudo chown {user} $FILENAME'.format(user=user_name,),
            'start': '',
            'stop': '',
        },
        'supervisor': {  # keeps gunicorn env.running
            'template': '{config}/supervisor/template'.format(config=config_folder,),
            'filename': '{user}.conf'.format(user=user_name,),
            'target folder': '/etc/supervisor/conf.d',
            # read all config files in conf.d folder
            'install': 'sudo supervisorctl reread && env.sudo supervisorctl update',
            'start': 'sudo supervisorctl start {url}'.format(url=site_url,),
            'stop': 'sudo supervisorctl stop {url}'.format(url=site_url,),
        },
        'nginx': {  # webserver
            'template': '{config}/nginx/template'.format(config=config_folder,),
            'filename': '{url}'.format(url=site_url,),
            'target folder': '/etc/nginx/sites-available',
            'install': '',
            'start': (
                # create symbolic link from config file to sites-enabled
                'sudo ln -sf /etc/nginx/sites-available/{url} /etc/nginx/sites-enabled/{url} '
                # reload nginx service
                '&& env.sudo nginx -s reload').format(url=site_url),
            # remove symbolic link
            'stop': 'sudo rm /etc/nginx/sites-enabled/{url} && env.sudo nginx -s reload'.format(url=site_url,),
        },
    }
    return configs


@task:
def deploy():
    """ create database, make folders, install django, create linux user, make virtualenv. """
    # Folders are named something like www.example.com
    # or www.staging.example.com for production or staging
    site_url = env.host
    folders = _get_folders(site_url)

    postactivate_file, project_settings = make_postactivate_file(site_url, )

    _create_postgres_db(project_settings)
    _create_linux_user(project_settings['user'], site_url, LINUXGROUP)

    _create_directory_structure_if_necessary(folders)
    _create_virtualenv(folders['venv'], folders['venvs'])
    _upload_postactivate(postactivate_file, folders['venv'], folders['bin'])
    _deploy_configs(site_url)
    _update_deployment(site_url, folders)


@task:
def update():
    """ update repo from github, install pip reqirements, collect staticfiles and env.run database migrations. """
    site_url = env.host
    folders = _get_folders(site_url)

    _update_deployment(site_url, folders)


def _update_deployment(site_url, folders):

    _get_latest_source(folders['source'])
    _update_virtualenv(folders['source'], folders['venv'],)
    _update_static_files(folders['venv'])
    _update_database(folders['venv'])
    stop()
    start()


@task
def start():
    """ Start webserver for site """
    site_url = env.host
    _enable_site(site_url)


@task
def stop():
    """ Stop webserver from serving site """
    site_url = env.host
    with settings(warn_only=True):
        _enable_site(site_url, start=False)


@task
def dropdb():
    """ Delete the site database """
    site_url = env.host
    db_name = site_url.replace('.', '_')
    _drop_postgres_db(db_name)


@task
def reboot():
    """ Restart all services connected to website """
    site_url = env.host
    _enable_site(site_url, start=False)
    env.sudo('service nginx restart; service supervisorctl restart')
    _enable_site(site_url)

# def make_local_config():
#     """ Create configuration files for env.running the site on localhost """
#     site_url = 'local.example.com'
#     _deploy_configs(site_url, upload=False)


@task
def update_config():
    """ Update the configuration files for services and restart site. """
    site_url = env.host
    stop()
    _deploy_configs(site_url)
    start()


def _deploy_configs(site_url, user_name=None, user_group=None, upload=True):
    """
    Creates new configs for webserver and services and uploads them to webserver.
    If a custom version of config exists locally that is newer than the template config,
    a new config file will not be created from template.
    """
    user_name = user_name or site_url.replace('.', '_')
    user_group = user_group or LINUXGROUP
    configs = _get_configs(site_url)
    for service in configs:  # services are webserver, wsgi service and so on.
        config = configs[service]
        template = config['template']  # template config file
        target = join(dirname(template), config['filename'])  # name for parsed config file
        # server filepath to place config file. Outside git repo.
        destination = join(config['target folder'], config['filename'])
        if not os.path.exists(target) or os.path.getctime(target) < os.path.getctime(template):
            # Generate config file from template if a newer custom file does not exist.
            # use sed to change variable names that will differ between deployments and sites.
            local((
                'cat "{template}" | '
                'sed "s / SITEURL / {url} / g" | '
                'sed "s / USERNAME / {user} / g" | '
                'sed "s / USERGROUP / {group} / g" > '
                '"{filename}"'
            ).format(
                template=template,
                url=site_url,
                user=user_name,
                group=user_group,
                filename=target,
            ))
        if upload:
            # upload config file
            put(target, destination, use_sudo=True)
            with shell_env(FILENAME=destination):
                # env.run command to make service register new config and restart if needed.
                env.run(config['install'])


def _enable_site(site_url, start=True):
    """
    Start webserver and enable configuration and services to serve the site.
    if start=False, stops the wsgi-server and deactivates nginx config for the site.
    """
    command = 'start' if start else 'stop'
    configs = _get_configs(site_url)
    for service in configs.values():
        env.run(service[command])


def _upload_postactivate(postactivate_file, venv_folder, bin_folder):
    """ Uploads postactivate shell script file to server. """
    # full filepath for the uploaded file.
    postactivate_path = '{bin}/postactivate'.format(bin=bin_folder,)
    # full filepath for python virtual environment activation shellscript on the server.
    activate_path = '{venv}/bin/activate'.format(venv=venv_folder,)
    # add bash command to activate shellscript to source (run) postactivate
    # script when the virtualenvironment is activated.
    append(activate_path, 'source {postactivate}'.format(postactivate=postactivate_path,))
    # upload file.
    put(postactivate_file, postactivate_path)


def _create_directory_structure_if_necessary(folders):
    """ Ensure basic file structure in project. """
    site_folder = folders['site']
    if not exists(site_folder):
        # base deployment folder
        env.run('mkdir -p {site_folder}'.format(site_folder=site_folder,))
        # set linux user group.
        env.run('chown :{group} {site_folder}'.format(group=LINUXGROUP, site_folder=site_folder))
        # set folder priveleges - 6*** means group and user sticky bits are set, and subfolders and files.
        # will inherit parent folder's group and user.
        # 770 means read, write and execute for folder is enabled for owner and group.
        env.run('chmod 6770 {site_folder}'.format(site_folder=site_folder,))

    # Make folders for static files, virtual environment and so on.
    # -p flag means that folder is only created if it doesn't exist,
    # and parent directories are also created if needed.
    env.run('mkdir -p {folder_paths}'.format(folder_paths=' '.join(folders.values())))


def _create_linux_user(username, site_url, group):
    """ Create a new linux user to env.run programs and own project files and folders on the webserver. """
    # Bash command id user returns error code 1 if user does not exist and code 0 if user exists.
    # To avoid Fabric raising an exception on an expected shell error,
    # return code ($?) is echoded to stdout and passed to python as a string.
    user_exists = env.run('id {linux_user}; echo $?'.format(linux_user=username,)).split()[-1] == '0'
    if not user_exists:
        # Create user and add to the default linux user group.
        env.sudo('useradd --shell /bin/bash -g {linux_group} -M -c "runs gunicorn for {site_url}" {linux_user}'.format(
            linux_group=group, site_url=site_url, linux_user=username)
        )


def _drop_postgres_db(db_name, backup=True):
    """ Delete database and user. Dumps the database to file before deleting """
    if backup:
        env.run('pg_dump -Fc {db_name} > {db_name}_$(date +" % Y - %m - %d").sql'.format(db_name=db_name,))
    env.run('psql -c "DROP DATABASE {db_name}"'.format(db_name=db_name,))
    env.run('psql -c "DROP USER {db_user}"'.format(db_user=db_name,))


def _create_postgres_db(project_settings):
    """ Create postgres database and user for the django deployment. Will also change that user's postgres password. """
    username = project_settings['user']
    password = project_settings['db password']
    db_name = project_settings['db name']
    databases = env.run(r'psql -l | grep --color=never -o " ^ \w\+ "').split()
    if db_name not in databases:
        print(db_name, databases)
        # create user
        env.run('psql -c "CREATE ROLE {user} NOSUPERUSER CREATEDB NOCREATEROLE LOGIN"'.format(user=username, ))
        # create database
        env.run('psql -c "CREATE DATABASE {db} WITH OWNER={user}  ENCODING=\'utf-8\';"'.format(user=username, db=db_name, ))
    # change password. This will happen even if user already exists.
    # this is because a new password is created every time the postactivate file has to be changed.
    env.run('psql -c "ALTER ROLE {user} WITH PASSWORD \'{password}\';"'.format(user=username, password=password, ))


def _get_latest_source(source_folder):
    """ Updates files on staging server with current git commit on dev branch. """
    if exists(source_folder + '/.git'):
        env.run('cd {source_folder} && git fetch'.format(source_folder=source_folder,))
    else:
        env.run('git clone {github_url} {source_folder}'.format(github_url=REPO_URL, source_folder=source_folder))
    current_commit = local('git log -n 1 --format=%H', capture=True)
    env.run('cd {source_folder} && git reset --hard {commit}'.format(source_folder=source_folder, commit=current_commit))


def _create_virtualenv(venv_folder, global_venv_folder):
    """ Create python virtual environment. """
    if not exists(venv_folder + '/bin/pip'):
        env.run('{python_venv_version} {venv_folder}'.format(python_venv_version=PYVENV, venv_folder=venv_folder,))
        # link to global folder to enable virtualenvwrapper 'workon' command.
        env.run('ln -fs {venv_folder} {venvs}'.format(venv_folder=venv_folder, venvs=global_venv_folder))


def _update_virtualenv(source_folder, venv_folder):
    """ Install required python packages from pip requirements file. """
    env.run('{venv}/bin/pip install -r {source}/requirements.txt'.format(venv=venv_folder, source=source_folder, )
        )


def _update_static_files(venv_folder):
    """ Move images, js and css to staticfolder to be served directly by nginx. """
    env.run('source {venv}/bin/activate && django-admin collectstatic --noinput'.format(venv=venv_folder,))


def _update_database(venv_folder):
    """ Run database migrations if required by changed apps. """
    env.run('source {venv}/bin/activate && django-admin migrate --noinput'.format(venv=venv_folder,))

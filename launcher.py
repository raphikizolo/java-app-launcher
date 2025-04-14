# get currently running app.
# load environment variables into memory
# load them into the current shell
# start boot jar.

import json
import os
from pathlib import Path

current_app_file_name = os.path.join(os.getcwd(), 'current_app_config.txt')

def get_app_config(name):
    for dir, dirs, files in os.walk(os.getcwd()):
        for f in files:
            if f == f'app_{name}.txt':
                with open(os.path.join(dir, f)) as configfile:
                    return json.loads(configfile.read())
    return None

def save_as_current_config(cfg):
    j = json.dumps(cfg, indent=4)
    with open(current_app_file_name, 'wb') as f:
        f.write(j.encode())

def add_new_app():
    while True:
        name = input('Enter name of spring app. q to quit>> ')
        if name.strip() == 'q':
            return (None, name)
        if name:
            fn = input("Enter full path to the spring app jar's jar. q to quit>> ")
            if Path.is_file(Path(fn)):
                with open(os.path.join(os.getcwd(), f'app_{name}.txt'), 'wb') as f:
                    cfg = { "name": name, "jar": fn }
                    f.write(json.dumps(cfg, indent=4).encode())
                return (cfg, None)
            else:
                print('Invalid path to jar')
                continue
        print('Invalid name.')


def ask_set_current_app_config(name = None):
    name = name if name else input('Enter name of spring app to run >> ')
    appconfig = get_app_config(name)
    if appconfig:
        save_as_current_config(appconfig)
        return (appconfig, None)
    d = input('No app with that name. Add a new app and set as current app?Y/n>> ')
    if d.strip() in ['y', 'Y']:
        cfg, command = add_new_app()
        if command == 'q':
            return (None, command)
        save_as_current_config(cfg)
        return (cfg, None)
    return (None, 'q')
    


def get_current_app():
    with open(current_app_file_name, 'rb') as f:
        data = f.read().decode()
        if not data:
            return ask_set_current_app_config()
        return (json.loads(data), None)
    
def add_to_current_env(prop, val):
    if prop in os.environ:
        raise Exception('Environment property already exists.')
    os.environ[prop] = val
    
def run_app(cfg):

    if Path(cfg['jar']).is_file():
        # Set env vars and exec Spring Boot app (replaces current process)
        if 'envs' in cfg:
            [add_to_current_env(key, value) for key, value in cfg['envs'].items()]
        os.execvpe("java", ["java", "-jar", cfg['jar']], os.environ)
        print(f'running app...environment ==> {os.environ}')
    else:
        print(f'\033[31mThis is not a valid jar file ==> {cfg['jar']}. \n\nAborting attempt to run it as a java app.\033[0m')

def get_env():
    env = input('Enter property name and value separated by an equal sign. Value and name will be trimmed(prepended appended spaces will be'
                ' removed). Enter ok to go back. >>')
    env = env.strip()
    if env == 'ok':
        return (None, 'ok')
    name, value = tuple([v.strip() for v in env.split('=')])
    return ({ name: value }, None)

def get_envs(cfg):
    if 'envs' in cfg:
        return cfg['envs']
    else:
        cfg['envs'] = dict()
    return cfg['envs']

def save_config(cfg):
    with open(os.path.join(os.getcwd(), f'app_{cfg['name']}.txt'), 'wb') as f:
        f.write(json.dumps(cfg, indent=4).encode())
    curr, _ = get_current_app()
    if cfg['name'] == curr['name']:
        save_as_current_config(cfg)

def add_envs(cfg):
    while True:
        envv, command = get_env()
        if command and command == 'q':
            save_config(cfg)
            return (None, command)
        elif command and command == 'ok':
            save_config(cfg)
            return (None, None)
        envs = get_envs(cfg)
        envs.update(envv)

def get_actions():
    return ['1. run app', 
            '2. add environment variable',
            '3. show environment variables',
            '4. quit',
            ]


def main():
    while True:
        current_app, command = get_current_app()
        if command and command.strip() == 'q':
            break
        print(f'Current app ==> {str({ 'name': current_app['name'], 'jar': current_app['jar']})}')
        i = input('Enter the next thing to do.\n' + '\n'.join(get_actions()) + '\n>> ')
        i = int(i.strip())
        if i == 1:
            run_app(current_app)
        elif i == 2:
            i = add_envs(current_app)
        elif i == 3:
            print('If the app has environment variables there should be a property called envs')
            current_app, _ = get_current_app()
            print(json.dumps(current_app, indent=4))
        elif i == 4:
            print('Bye.....')
            break

            

        


if __name__ == "__main__":
    main()

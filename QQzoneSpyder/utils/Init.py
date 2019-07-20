import configparser

class Global_Var:
    webdriver_path=""
    qqzone_url=""
    username=""
    password=""
    
    
def __init__():
    config=configparser.ConfigParser()
    config.read("value.ini")
    Global_Var.webdriver_path=config['Message']['webdriver_path']
    Global_Var.qqzone_url=config['Message']['qqzone_url']
    Global_Var.username=config['Message']['username']
    Global_Var.password=config['Message']['password']
    
    
def get_webdriver_path():
    return Global_Var.webdriver_path

def get_qqzone_url():
    return Global_Var.qqzone_url

def get_username():
    return Global_Var.username

def get_password():
    return Global_Var.password
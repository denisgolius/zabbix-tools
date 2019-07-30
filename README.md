# zabbix-tools

**How to use**

**Example from Ubuntu 18.04**

Install needed packages

`sudo apt install python3-pip python3-dev virtualenv `


Clone repository

` git clone https://github.com/denisgolius/zabbix-tools.git && cd zabbix-tools`


Create virtualenv instead installation packages in system 

` python3 -m venv zabbix-tools-env`


Activate virtualenv and install needed libs for script

`source zabbix-tools-env/bin/activate && pip install -r requirements.txt`


Add dirrectory fro saving Thempaltes

`mkdir templates_dir && ls -l `


Running script

`(zabbix-tools-env) python Export_Templates_from_Zabbix.py --zabbix-host "https://your_server_address" --zabbix-user "username" --zabbix-password "password!" --dir templates_dir --e`



# Get help for script
` python3 Export_Templates_from_Zabbix.py --h`

```bash
usage: python3 script_name.py {ARGS}

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --t TEMPLATE [TEMPLATE ...], --template TEMPLATE [TEMPLATE ...]
                        Indicate a template(s)
  --d folder, --dir folder
                        Indicate a folder for template(s)
  --zabbix-host ZABBIX_HOST
                        Zabbix host
  --zabbix-user ZABBIX_USER
                        Zabbix user
  --zabbix-password ZABBIX_PASSWORD
                        Zabbix password of user
  --i                   Import function
  --import              Import function
  --e                   Export function
  --export              Export function
```

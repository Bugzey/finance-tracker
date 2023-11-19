#	Finance tracker

##  Description
Lightweight command-line program to manage personal finances with added support for reading receipt
QR codes.

Features:

* Transactional backend
* CLI input
* Import from / export to a free compatible spreadsheet template


##  Installation
Download the repository and install it using pip:

```
git clone <URL> finance-tracker
cd finance-tracker
pip install .
```


##  Usage
The project provides a command-line script called `finance_tracker`. When calling the script,
provide an action and an object to apply the action to:

```
usage: finance_tracker [-h] [-d DATABASE]
                       {create,c,update,u,delete,d,get,g,query,q,help,h} ...

positional arguments:
  {create,c,update,u,delete,d,get,g,query,q,help,h}

options:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Path to database file
```

When you have selected an action, provide an object and optionally data for the action in the form
of `KEY=VALUE` pairs separated by space:

```

usage: finance_tracker create [-h]
                              {transaction,category,subcategory,account,business,period,t,c,s,a,b,p}
                              [data ...]

positional arguments:
  {transaction,category,subcategory,account,business,period,t,c,s,a,b,p}
  data                  Key-value pairs in the form KEY=VALUE

options:
  -h, --help            show this help message and exit
```

Upon initial setup you will be asked whether you want to use a predefined database location or you
can provide your own location. When creating a new file you can also opt to pre-populate the
database with a standard set of categories and subcategories along with a default account.


##  Contributing
Any features or bug fixes should be provided in a pull request to the master branch. Any new
features should be accompanied by tests written in the `unittest` framework.


##  Authors and Acknowledgement
* Lead Developer: Radoslav Dimitrov

README based on <https://www.makeareadme.com/>

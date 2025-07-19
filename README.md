#	Finance tracker

##  Description

Lightweight command-line program to manage personal finances with added support for reading receipt
QR codes.

Features:

* Transactional backend
* CLI input
* Import from / export to a free compatible spreadsheet template
* A basic report view


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
usage: finance_tracker [-h] [-d DATABASE] [-v]
                       {create,c,update,u,delete,d,get,g,query,q,help,h,report} ...

positional arguments:
  {create,c,update,u,delete,d,get,g,query,q,help,h,report}
    report              Run report server

options:
  -h, --help            show this help message and exit
  -d, --database DATABASE
                        Path to database file
  -v, --verbose         Print verbose messages

```

When you have selected an action, provide an object and optionally data for the action in the form
of `KEY=VALUE` pairs separated by space:

```
usage: finance_tracker c [-h] [-q]
                         {transaction,t,category,c,subcategory,s,account,a,business,b,period,p}
                         [data ...]

positional arguments:
  {transaction,t,category,c,subcategory,s,account,a,business,b,period,p}
  data                  Key-value pairs in the form KEY=VALUE

options:
  -h, --help            show this help message and exit
  -q, --qr-code         Create from QR code
```

Upon initial setup you will be asked whether you want to use a predefined database location or you
can provide your own location. When creating a new file you can also opt to pre-populate the
database with a standard set of categories and subcategories along with a default account.


###	Reporting

Calling the `report` command opens a web browser pointing to a simple reporting interface:

```
finance_tracker report
```

By default the server is available under [https://localhost:5000/](http://localhost:5000/).


##  Contributing

Any features or bug fixes should be provided in a pull request to the master branch. Any new
features should be accompanied by tests written in the `unittest` framework.


##  Authors and Acknowledgement

* Lead Developer: Radoslav Dimitrov

README based on <https://www.makeareadme.com/>

Boxer
=======================================

Boxer is a directory bruteforcing tool. It was designed primarily for a red team and for a large network of systems to scan. 
Not only can it run a directory bruteforce, but it can save the results and allow you to query them locally or from a HTTPS server that Boxer provides.

(5/11/2019) Some testing has indicated results of finishing in roughly a fourth of the time as Gobuster on one URL with the same wordlist. 

- There is no recursion currently implemented. There is some code commented out to possibly allow this in the future.

Why another directory bruteforce tool?

- I put this tool together to implement and work with OOP and polymorphism.
- I also wanted to implement concurrency and coroutines.
- This should aid in process improvements for my job.
- As a security professional and hobbyist, I like putting helpful software together for this domain.

Requirements
------------

This code was created with Python 3.7.3. Other versions of Python 3 might also work. 

Make sure to install all requirements:

    $ pip3 install -r requirements.txt


Quick start
-----------

Run a scan:

    $ python3 boxer.py -u https://www.google.com -w common.txt 

Run a scan and setup a database for persistent results:

    $ python3 boxer.py -u https://www.google.com -w common.txt -d database

Run a scan with a 'urls.txt' file (with or without a database).

    $ python3 boxer.py -u urls.txt -w common.txt -d database

Query the local database for available urls:

    $ python3 boxer.py -urlsavailable -d database.json

Query the local database for the url's directories:

    $ python3 boxer.py -u https://www.google.com -d database.json

Setup server to serve up the urls' database:

    $ python3 boxer.py -server -d database.json

Query the server for available urls:

    $ python3 boxer.py -urlsavailable -s 0.0.0.0

Query the server for the url's directories:

    $ python3 boxer.py -u https://www.google.com -s 0.0.0.0


License
-------

This code is licensed under the terms of the MIT License (see the file
LICENSE).

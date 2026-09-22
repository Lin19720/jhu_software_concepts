Overview & Setup
================

This application scrapes GradCafe admissions data, cleans it, loads it into a database, and provides analytical queries alongside a Flask web app.

Installation
------------
.. code-block:: bash

   pip install -r requirements.txt

Environment Variables
---------------------
* ``DATABASE_URL``: Database connection string (e.g., ``sqlite:///gradcafe.db``).

Running the Application
-----------------------
.. code-block:: bash

   python src/app.py

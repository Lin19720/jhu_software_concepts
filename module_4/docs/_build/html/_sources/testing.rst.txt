Testing Guide
=============

Running Tests
-------------
.. code-block:: bash

   pytest --cov=src tests/

Marked Tests & Selectors
------------------------
.. code-block:: bash

   pytest -m "not slow"

Test Doubles & Fixtures
-----------------------
* **Mocks**: Database/Selenium mocked with ``unittest.mock.patch``.
* **Fixtures**: ``tmp_path`` used for isolated file operations.

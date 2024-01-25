Script that generates combinations of passwords according to a predefined pattern and tests them for a 7z file.

The pattern is as follows: ``^(123|456|789)(_|)([aA]bc|[dD]ef|[gG]hi)(_|)(123|456|789)(_|)([aA]bc|[dD]ef|[gG]hi)(_|)(123|456|789)(_|)([aA]bc|[dD]ef|[gG]hi)$``

With the caveat that a numbers string or a letters string can't be repeated within the same combination.

Examples of **valid** combinations:

- 123_Abc_456_Def_789_ghi
- 789_ghi_123_abc_456_Def
- 789ghi_123_abc456_Def

Examples of **invalid** combinations:

- 123_abc_123_Def_456_ghi
- 456_def_789_Def_123_Abc

.. contents:: **Contents**
   :depth: 3
   :local:
   :backlinks: top

Dependencies
============
* **Platforms:** Linux, macOS
* **Python** >=3.8
* `7-Zip`_

Script usage
============
To display the script's list of options and their descriptions::

    $ python script.py -h
    usage: script.py [OPTIONS] {7z_filepath}

    Script that generates combinations of passwords according to a predefined pattern and tests them for a 7z file.
   
    Optional arguments:
      -h, --help                           Show this help message and exit.
      -t NB_THREADS, --threads NB_THREADS  Number of threads to use for processing the whole list of password combinations. (default: 10)
   
    Input file:
      7z_filepath                          Path of the 7z file upon which password combinations will be tested.

To generate and test all possible password combinations satisfying the predefined pattern using **20 threads** 
(by default, the script uses 10 threads to test all passwords)::

   $ python script.py my_doc.7z -t 20

At any moment, you can stop the program with ``Ctrl`` + ``C``::

   $ python script.py my_doc.7z
   855 combinations were rejected because they were already processed in previous runs
   Total number of passwords to test: 8361
   Number of threads used to test passwords: 10
   [thread_0] Processing password='123Abc789_Ghi456_def' [0/837]
   [thread_1] Processing password='123_Abc_789_ghi_456_def' [0/836]
   [thread_2] Processing password='123_def_456Ghi789_abc' [0/836]
   [thread_3] Processing password='123ghi456Abc_789def' [0/836]
   [thread_4] Processing password='456Ghi_123_def789Abc' [0/836]
   [thread_5] Processing password='456_abc789_Def123ghi' [0/836]
   [thread_6] Processing password='456abc_789_ghi_123_def' [0/836]
   [thread_7] Processing password='789Def456_ghi_123_Abc' [0/836]
   [thread_8] Processing password='789_Ghi123_abc_456Def' [0/836]
   [thread_9] Processing password='789_ghi_123abc_456Def' [0/836]
   ^C
   Warning: Program stopped!
   10 passwords were tested
   Saving file
   Program exited with 2

`:information_source:` 

  - The script saves in a pickle file all the password combinations that were tried so far. Hence, if you 
    stop the program and re-run it, the script will skip all the passwords that were already tested.
  - The name of the pickle file is the MD5 hash of the 7z file.

| 

`:star:` If the script finds the password, all threads are stopped and the password is saved in the pickle file
along with all the passwords that were tested so far::

   $ python script.py my_doc.7z
   Total number of passwords to test: 9216
   Number of threads used to test passwords: 10
   [thread_0] Processing password='123Abc456Def789Ghi' [0/922]
   [thread_1] Processing password='123_Abc_456_Ghi789_def' [0/922]
   [thread_2] Processing password='123_def456abc_789Ghi' [0/922]
   [thread_3] Processing password='123def_789Ghi_456_abc' [0/922]
   [thread_4] Processing password='456Ghi789_def123Abc' [0/922]
   [thread_5] Processing password='456_abc123Def789_ghi' [0/922]
   [thread_6] Processing password='456abc_123_Ghi_789Def' [0/921]
   [thread_7] Processing password='789Def123abc_456_Ghi' [0/921]
   [thread_8] Processing password='789_Def_456Ghi_123_abc' [0/921]
   [thread_9] Processing password='789_ghi456_abc_123def' [0/921]
   
   **** Found the password: 123Abc456Def789Ghi ****
   
   10 passwords were tested
   Saving file
   Program exited with 0

If you re-run the script after the password was found::

   $ python script.py my_doc.7z
   Password was already found: 123Abc456Def789Ghi
   Program exited with 0

License
=======
This program is licensed under the MIT License. For more details see the `LICENSE`_ file in the repository.

.. URLs
.. _7-Zip: https://www.7-zip.org/
.. _LICENSE: ./LICENSE

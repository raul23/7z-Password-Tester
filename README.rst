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

License
=======
This program is licensed under the MIT License. For more details see the `LICENSE`_ file in the repository.

.. URLs
.. _7-Zip: https://www.7-zip.org/
.. _LICENSE: ./LICENSE

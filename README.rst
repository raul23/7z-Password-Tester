Script that generates combinations of passwords according to a predefined pattern and tests them for a 7z file.

The pattern is as follows: ``^(123|456|789)(_|)([aA]bc|[dD]ef|[gG]hi)(_|)(123|456|789)(_|)([aA]bc|[dD]ef|[gG]hi)$``

With the caveat that a numbers string or a letters string can't be repeated within the same combination.

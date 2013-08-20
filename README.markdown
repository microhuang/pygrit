## pygrit

pygrit intends to provide a minimal [ruby grit](https://github.com/mojombo/grit) like functions into python world.

currently working on diff and commit objects.

## usage

```python
from pygrit.repo import Repo

# specify repos root path
Repo.repos_path

# Repo.repos_path + 'path/to/repository'
repo = Repo('path/to/repository')

commit = Repo.commit(':commit_id') # currently only support sha1

for diff in commit.diffs:
    print diff.__dict__ # check properties
```

+ `diff_with_lineno`, old_lineno, new_lineno, and line text now available.

```
>>> diff.diff_with_lineno

(2, 2, u'bbbbbbbbbbbbbbb')
(3, 3, u'ccccccccccccccc')
(4, 4, u'eeeeeeeeeeeeeee')
(5, '', u'-fffffffffffffff')
('', 5, u'+111111111111111')
(6, '', u'-ggggggggggggggg')
('', 6, u'+222222222222222')
(7, 7, u'hhhhhhhhhhhhhhh')
```

## TODO

+ Git objects wrapped in python
+ write reasonable tests

## LICENSE

[The MIT License (MIT)](http://opensource.org/licenses/MIT)

Copyright (c) 2013 AR (a.k.a AleiPhoenix)

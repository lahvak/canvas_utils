"""
Some utility functions for reading course configuration from YAML files.

Course config file should be a YAML file (default name `course.yaml`) residing
in the course top directory containing information about the course.  It can
use the `!include` directive to include other files. The purpose of that is to
have a common information shared by all courses to reduce duplication.
Example:

```yaml
---
course:
  name: Advanced Numerology
  number: Math 666
sections:
  621:
    days: MW
    start_time: 10:30 am
    end_time: 12:20 pm
office_hours: !include ../ohs.yaml
```

The `ohs.yaml` can look like this:

```yaml
  Monday:
    - from: 2:20 pm
      to: 3:10 pm
    - from: 4:20 pm
      to: 4:21 pm
  Tuesday:
    - from: 2:30 pm
      to: 3:15 pm
  Wednesday:
    - from: 2:20 pm
      to: 3:10 pm
    - from: 4:20 pm
      to: 4:21 pm
    - from: 4:22 pm
      to: 9:16 pm
```
"""

import yaml
from yaml.loader import SafeLoader
from yamlinclude import YamlIncludeConstructor
from pathlib import Path


def find_config_file(fname, root=None):
    """
    Search in the current directory and all parent directories all the way up
    to `root` for file with name `fname`.  Returns a Path, throws
    FileNotFoundError exception if it does not find it.
    If `root` is not provided, search goes all the way up to user's home
    directory.
    """

    if root is None:
        root_path = Path.home()
    else:
        root_path = Path(root)

    wd = Path.cwd().resolve()

    for p in (wd / "dummy").parents:
        fpath = p / fname
        if fpath.exists():
            return fpath

        if p.samefile(root_path):
            break

    raise FileNotFoundError("Could not find the config file " + fname)


def read_config_file(fpath):
    """
    Read configuration from a YAML file at path `fpath`.  The file
    can include other files using the `!include` directive.
    """

    basedir = fpath.parent
    YamlIncludeConstructor.add_to_loader_class(
        loader_class=SafeLoader, base_dir=basedir)

    with open(fpath, 'r') as class_conf:
        config = yaml.load(class_conf, Loader=SafeLoader)

    return config


def get_course_config(fname="course.yaml", root=None):
    """
    Find and read course configuration YAML file.

    The parameter `root` limits which part of directory tree to search.
    Defaults to the user home dir.

    Throws a fit^w^wan exception when file not found.
    """

    fpath = find_config_file(fname, root)
    return read_config_file(fpath)


def comma(items):
    """
    Takes a list of strings and joins them into an English list,
    separated by commas, with 'and' before the last element.
    """

    if not items:
        return ""

    start, last = items[:-1], items[-1]

    if start:
        form = "{}, and {}" if len(start) > 1 else "{} and {}"
        return form.format(", ".join(start), last)
    else:
        return last


def format_time_list(ls):
    """
    Take a list of dicts, each having keys 'from' and 'to'.
    Returns a list of English time interval specifications.
    """

    return ["from {from} to {to}".format(**times) for times in ls]


def markdown_from_hours(d):
    """
    Gets a dict where keys are names of weekdays and values are
    lists of time intervals. Returns a markdown formatted list of lines.
    """

    return ["*   __{}__: {}".format(day, comma(format_time_list(times)))
            for day, times in d.items()]

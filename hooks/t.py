#!/usr/bin/python

import json
from jinja2 import Template
import yaml

jstr = '''
{'101': ['host1.domain:1/1', 'host2.domain:1/2'], '102':['host3.domain:1/4']}
'''

jstr = '''
{'101': ['fab11-srv2:1/26', 'fab11-srv3:1/27']}
'''
xx = yaml.safe_load(jstr.replace("'", "\""))

xy = 'ext1:ext1epg, ext2:ext2epg'
templ = Template('''
{{ xx }}
        {% for sw in xx %}
        [apic_switch:{{ sw }}]
        {% for pstr in xx[sw] %}
        {{ pstr|replace(":","=") }}
        {% endfor %}
        {% endfor %}
''')
print(templ.render(xx = xx))

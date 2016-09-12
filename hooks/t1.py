#!/usr/bin/python

import json
from jinja2 import Template
import yaml

xx = "{'101': ['host1.domain:1/1', 'host2.domain:1/2'], '102':['host3.domain:1/4']}"

#xx = yaml.safe_load(jstr.replace("'", "\""))

templ = Template('''
{{ xx }}
        {% for sw in xx %}
        [apic_switch:{{ sw }}]
        {% for pstr in xx[sw] %}
        {{ pstr|replace(":","=") }}
        {% endfor %}
        {% endfor %}
''')
ctxt = {}
ctxt['xx'] = xx
print(templ.render(ctxt))

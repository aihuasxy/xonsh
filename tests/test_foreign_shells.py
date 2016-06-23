# -*- coding: utf-8 -*-
"""Tests foreign shells."""
from __future__ import unicode_literals, print_function
import os
import subprocess

import pytest

from xonsh.tools import ON_WINDOWS
from xonsh.foreign_shells import foreign_shell_data, parse_env, parse_aliases

def test_parse_env():
    exp = {'X': 'YES', 'Y': 'NO'}
    s = ('some garbage\n'
         '__XONSH_ENV_BEG__\n'
         'Y=NO\n'
         'X=YES\n'
         '__XONSH_ENV_END__\n'
         'more filth')
    obs = parse_env(s)
    assert exp ==  obs


def test_parse_aliases():
    exp = {'x': ['yes', '-1'], 'y': ['echo', 'no']}
    s = ('some garbage\n'
         '__XONSH_ALIAS_BEG__\n'
         "alias x='yes -1'\n"
         "alias y='echo    no'\n"
         '__XONSH_ALIAS_END__\n'
         'more filth')
    obs = parse_aliases(s)
    assert exp ==  obs


@pytest.mark.skipif(ON_WINDOWS, reason='Unix stuff')
def test_foreign_bash_data():
    expenv = {"EMERALD": "SWORD", 'MIGHTY': 'WARRIOR'}
    expaliases = {
        'l': ['ls', '-CF'],
        'la': ['ls', '-A'],
        'll': ['ls', '-a', '-lF'],
        }
    rcfile = os.path.join(os.path.dirname(__file__), 'bashrc.sh')
    try:
        obsenv, obsaliases = foreign_shell_data('bash', currenv=(),
                                                extra_args=('--rcfile', rcfile),
                                                safe=False)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return
    for key, expval in expenv.items():
        assert expval == obsenv.get(key, False)
    for key, expval in expaliases.items():
        assert expval == obsaliases.get(key, False)


def test_foreign_cmd_data():
    env = (('ENV_TO_BE_REMOVED','test'),)
    batchfile = os.path.join(os.path.dirname(__file__), 'batch.bat')
    source_cmd ='call "{}"\necho off'.format(batchfile)
    try:
        obsenv, _ = foreign_shell_data('cmd',prevcmd=source_cmd, 
                                        currenv=env,
                                        interactive =False,
                                        sourcer='call',envcmd='set',
                                        use_tmpfile=True,
                                        safe=False)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return

    assert 'ENV_TO_BE_ADDED' in obsenv 
    assert obsenv['ENV_TO_BE_ADDED']=='Hallo world'
    assert 'ENV_TO_BE_REMOVED' not in obsenv

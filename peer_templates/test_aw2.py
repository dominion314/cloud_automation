import sys
import pytest
import pprint as pp

# from .aw2 import identify_name, get_info, Arguments
from . import aw2

parser = aw2.Arguments('Called from pytest')


def test_identify_name():
    info = {}
    sys.argv = ['aw2', '-p172.17.0.1', '-rus-east-1', '-caws', '-s127.0.0.1']
    args = parser.get()
    pp.pprint(args)

    print(aw2.banner)  ## Print the banner that is defined at the top of this program.

    aw2.identify(args, info)  ## print peer info, and ask whether or not to proceed.

    aw2.create_peer_tf(info) ## Creates a Terraform Config File with peer_name.

    ## Creates a Terraform Config File and Applies plan
    # terraform(path   = info['peer_name'],
    #        secret = info['cloud_secret'])

    ### Updates a Terraform Config File with peer_name and info.
    # add_info(peer = info['peer_name'],
    #        id = info['peer_id'],
    #        subnet = info['peer_subnet'])

    ## update file permissions of directory tree that was created for peer_name to '-rwxr--r--'.
    # update_permissions(info['peer_name'])

    ## call git() to add/commit/push the current directory as the given repo
    # git(name = info['peer_name'])
    assert True




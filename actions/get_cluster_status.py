import requests, json, sys, ConfigParser
from st2actions.runners.pythonrunner import Action
from lib.ceph_admin_tools import CephAdmin


class GetStatusAction(Action):
    def run(self, cluster_id):
        config_path = '/opt/stackstorm/packs/ceph/actions/cluster_config.cnf'
        config = ConfigParser.ConfigParser()
        config.read(config_path)

        try:
            admin_host = config.get(cluster_id, 'admin_host')
            admin_port = config.get(cluster_id, 'admin_port')
        except Exception as e:
            print(e)
            return (False, 'cluster_id doest not exists')

        ceph_admin = CephAdmin(admin_host, admin_port)

        return (True, ceph_admin.get_cluster_status())



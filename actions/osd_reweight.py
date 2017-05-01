import requests, json, sys, ConfigParser
from st2actions.runners.pythonrunner import Action
from lib.ceph_admin_tools import CephAdmin


class GetStatusAction(Action):
    def run(self, cluster_id, osd_id, reweight):

        ceph_admin = CephAdmin(cluster_id)

        return (True, ceph_admin.osd_reweight(osd_id, reweight))

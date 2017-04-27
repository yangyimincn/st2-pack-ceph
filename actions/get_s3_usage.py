#-*- coding: UTF-8 -*-

from awsauth import S3Auth
import requests, json, sys
from st2actions.runners.pythonrunner import Action
from lib.s3_tools import s3_admin

class MyEchoAction(Action):
    def run(self, cluster_id, uid):
        if cluster_id == 'infra.ceph.c1':
            cluster_endpoint = 'http://10.0.71.72'
            access_key = 'Y9Z8WC3MXYGU4XV66BD1'
            secret_key = '5UtrlvLCqKjHycUBokt3sY7ZiCGHbawaNXrtV16h'
        elif cluster_id == 'infra.ceph.c4':
            cluster_endpoint = 'http://10.200.51.204'
            access_key = 'VA612G91IC8191F52UQW'
            secret_key = 'rB56vABOnH4AGaRVPY4XLUO4RD1Pkg9qpjvQN6cy'
        elif cluster_id == 'test':
            cluster_endpoint = 'http://10.12.10.26:7480'
            access_key = '5CCOFLUS10VJ31E71DOZ'
            secret_key = 'F8dH35JwaPPrN4YowkQfvDROkAdNn3LD6zcZlJj3'
        else:
            return(False, 'cluster_id doest not exists')
        cluster = s3_admin(endpoint=cluster_endpoint, access_key=access_key,
                  secret_key=secret_key)
        cluster.get_user_info(uid=uid)
        return(True, cluster.get_user_report(uid=uid))
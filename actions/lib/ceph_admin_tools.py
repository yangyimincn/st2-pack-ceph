import requests, json

class CephAdmin:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_cluster_status(self):
        endpoint = '/api/v0.1/status'
        url = 'http://' + self.host + ':' + str(self.port) + endpoint

        current_status = self.__http_get(url)

        cluster_status = {
            'overall_status': '',
            'mon_num': 0,
            #'mon_leader': '',
            'issue_summary': {},
            'num_osds': 0,
            'num_up_osds': 0,
            'num_in_osds': 0,
            'num_remapped_pgs': 0,
            'pgs_by_state': {},
            'num_pgs': 0,
            'bytes_total': 0,
            'bytes_used': 0
        }

        try:
            # Overall status
            cluster_status['overall_status'] = current_status['health']['overall_status']

            # MON in quorum num
            for rank in current_status['quorum']:
                cluster_status['mon_num'] += 1

            # Get all issue
            for issue in current_status['health']['summary']:
                cluster_status['issue_summary'][issue['summary']] = issue['severity']

            # OSDS
            cluster_status['num_osds'] = current_status['osdmap']['osdmap']['num_osds']
            cluster_status['num_up_osds'] = current_status['osdmap']['osdmap']['num_up_osds']
            cluster_status['num_in_osds'] = current_status['osdmap']['osdmap']['num_in_osds']
            cluster_status['num_remapped_pgs'] = current_status['osdmap']['osdmap']['num_remapped_pgs']

            # PGS
            cluster_status['num_pgs'] = current_status['pgmap']['num_pgs']

            for pgsstat in current_status['pgmap']['pgs_by_state']:
                cluster_status['pgs_by_state'][pgsstat['state_name']] = pgsstat['count']

            # Uasge
            cluster_status['bytes_total'] = current_status['pgmap']['bytes_total']
            cluster_status['bytes_used'] = current_status['pgmap']['bytes_used']

        except KeyError as e:
            print(e)

        return cluster_status

    def __http_get(self, url):
        try:
            headers = {'Accept': 'application/json'}
            r = requests.get(url=url, headers=headers)

            if r.status_code == 200:
                if r.json()['status'] == 'OK':
                    return r.json()['output']

        except Exception as e:
            print(e)

if __name__ == '__main__':
    host = '10.12.10.26'
    port = 5000
    test_ceph = CephAdmin(host, port)

    s = test_ceph.get_cluster_status()
    print(s)

import requests, json, ConfigParser

class CephAdmin:
    def __init__(self, cluster_id):
        config = ConfigParser.ConfigParser()
        config_file = config_path = '/opt/stackstorm/packs/ceph/actions/lib/cluster_config.cnf'

        try:
            config.read(config_file)
            self.host = config.get(cluster_id, 'admin_host')
            self.port = config.get(cluster_id, 'admin_port')
        except Exception as e:
            print('Cluster id not exists!')
            exit(1)

    def osd_df(self):
        endpoint = '/api/v0.1/osd/df'
        url = 'http://' + self.host + ':' + str(self.port) + endpoint

        # /osd/df endpoint does not support convert into json
        # current_status = self.__http_get(url)
        r = requests.get(url)
        current_status_str = r.text

        osd_df = {}

        for line in current_status_str.split('\n'):
            # Remove unuse line
            if 'TOTAL' in line or 'MAX' in line or 'ID' in line:
                continue
            elif len(line) < 2:
                continue
            else:
                line = line.split()
                osd_info = {}
                osd_id = line[0]
                osd_info['crush_weight'] = line[1]
                osd_info['reweight'] = line[2]
                osd_info['capacity'] = line[3]
                osd_info['utilization'] = line[6]
                osd_info['pgs'] = line[8]
                osd_df[osd_id] = osd_info
        return osd_df

    def osd_reweight(self, osd_id=None, weight=None):
        '''
        :param osd_id: The osd id(must)
        :param weight: THe osd weight
        :return: None
        '''

        try:
            osd_id = int(osd_id)
            weight = float(weight)
        except Exception as e:
            print(e)
            exit(1)

        endpoint = '/api/v0.1/osd/reweight?id=%d&weight=%f' % \
                   (osd_id, weight)

        url = 'http://' + self.host + ':' + str(self.port) + endpoint

        r = requests.put(url)

        if r.status_code == 200:
            return 1
        else:
            return 0

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

    # s = test_ceph.osd_reweight(11, 0.98)
    # print(s)

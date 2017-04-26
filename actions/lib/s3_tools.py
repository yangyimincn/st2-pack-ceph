#-*- coding: UTF-8 -*-

from awsauth import S3Auth
import requests, json, sys

class UidException(Exception):
    '''
     Uid does not exit!
    '''
    def __init__(self, uid):
        err = 'Uid %s is not exist' % uid
        Exception.__init__(self, err)

class s3_admin:

    def __init__(self, endpoint, access_key, secret_key):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def get_bucket_info(self, bucketname=''):
        '''
            Get bucket info for on bucket
        '''

        url = self.endpoint + '/admin/bucket?format=json' + '&bucket=' + \
              bucketname

        bucket_info = self.__http_get(url)
        bucket_info_json = json.loads(bucket_info)

        result_dict = {
            'bucket': bucketname,
            'owner': '',
            'size_kb': 0,
            'size_kb_actual': 0,
            'num_objects': 0
        }

        try:

            result_dict['bucket'] = bucket_info_json['bucket']
            result_dict['owner'] = bucket_info_json['owner']
            result_dict['size_kb'] = bucket_info_json['usage']['rgw.main']['size_kb']
            result_dict['size_kb_actual'] = bucket_info_json['usage']['rgw.main']['size_kb_actual']
            result_dict['num_objects'] = bucket_info_json['usage']['rgw.main']['num_objects']

        except KeyError:
            pass

        return result_dict

    def list_bucket(self, uid=None):
        '''
        List bucket for user
        :param uid: if uid is provide, get all bucket for this uid
        :return: A list with bucket
        '''

        url = self.endpoint + '/admin/bucket?format=json'

        if uid:
            url = self.endpoint + '/admin/bucket?format=json' + '&uid=' + \
                  uid

        bucket_list_str = self.__http_get(url)

        if bucket_list_str == '[]':
            bucket_list = []

        else:

            bucket_list_tmp = bucket_list_str.strip('[').strip(']').split(',')
            bucket_list = []
            for b in bucket_list_tmp:
                bucket_list.append(b.strip('"'))
        return bucket_list

    def get_user_info(self, uid=None):
        url = self.endpoint + '/admin/user?format=json' + '&uid=' + uid

        user_info = self.__http_get(url)

        if 'NoSuchKey' in user_info:
            raise UidException(uid=uid)
            # print('Uid: %s is not exist!' % uid)
        return user_info

    def get_user_quota(self, uid=None):
        url = self.endpoint + '/admin/user?quota&uid=' + uid + '&quota-type=user'

        quota_info = self.__http_get(url)
        quota_info = json.loads(quota_info)
        return quota_info

    def get_user_report(self, uid):

        user_report = {
            'uid': uid,
            'bucket_num': 0,
            'object_num': 0,
            'size_kb_actual': 0,
            'quota_size': 0,
            'quota_status': 0
        }

        user_bucket_list = self.list_bucket(uid=uid)

        user_report['bucket_num'] = len(user_bucket_list)

        if user_report['bucket_num'] > 0:
            for b in user_bucket_list:
                bucket_info = self.get_bucket_info(b)
                user_report['object_num'] += bucket_info['num_objects']
                user_report['size_kb_actual'] += bucket_info['size_kb_actual'] / 1024 / 1024

        quoat_info = self.get_user_quota(uid=uid)
        if quoat_info['enabled'] == True:
            user_report['quota_status'] = 1

        if quoat_info['max_size_kb'] != -1:
            user_report['quota_size'] = quoat_info['max_size_kb'] / 1024 / 1024
        else:
            user_report['quota_size'] = quoat_info['max_size_kb']

        return user_report

    def __http_get(self, url):
        try:
            req = requests.get(url, auth=S3Auth(self.access_key, self.secret_key))
            return req.text

        except Exception as e:
            print(e)

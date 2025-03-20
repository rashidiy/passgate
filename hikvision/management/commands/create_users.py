from django.core.management import BaseCommand

from hikvision.models import Employee
from hikvision.plugins.DS_K1T671MF.camera import send_acs_request


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         print('Creating users')
#         path = '/ISAPI/AccessControl/UserInfo/Search'
#         current_steak = 0
#         data = {"UserInfoSearchCond":{"searchID":"0","maxResults":30,"searchResultPosition":current_steak}}
#         get_total_count = lambda x: x.json().get('UserInfoSearch').get('totalMatches')
#         while current_steak < get_total_count(rsp:=send_acs_request(path, data)):
#             user_info = rsp.json().get('UserInfoSearch').get('UserInfo')
#             if user_info:
#                 for user in user_info:
#                     Employee.objects.create(rfid=)
#             current_steak += 30
#             break

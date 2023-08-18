from django.test import TestCase,Client
from django.contrib.auth import get_user_model,get_user
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserExtended,Files,Requests,Comments
import json
# Create your tests here.
TEST_USER_NAME = 'TESTUSER1'
TEST_USER_PASSWORD = 'password123'
TEST_USER_NEW_PASSWORD = 'Password345'

TEST_USER2_NAME = 'TESTUSER2'
TEST_USER2_PASSWORD = 'password123'

class IndexTestView(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username=TEST_USER_NAME,password=TEST_USER_PASSWORD)
        self.user1_settings = UserExtended.objects.create(user=self.user1)
        self.user2 = User.objects.create_user(username=TEST_USER2_NAME,password=TEST_USER2_PASSWORD)
        self.user2_settings = UserExtended.objects.create(user=self.user2)
        self.file = Files.objects.create(file='100012',name='file.txt',description='blank',user=self.user1,acces='Public')
    def test_blacklist_add(self):
        client = Client()
        client.login(username=TEST_USER_NAME,password=TEST_USER_PASSWORD)
        response = client.get('/blacklist/2/add')
        self.assertEqual(self.user2 in self.user1_settings.blacklist.all(),True)

    def test_file_view_blacklist(self):
        client=Client()
        client.login(username=TEST_USER2_NAME,password=TEST_USER2_PASSWORD)
        self.user1_settings.blacklist.add(get_user(client))
        self.user1_settings.save()
        response = client.get(f'/files/{self.file.id}')
        self.assertContains(response,'Доступ',status_code=200)

    def test_storage_view_blacklist(self):
        client=Client()
        client.login(username=TEST_USER2_NAME,password=TEST_USER2_PASSWORD)
        self.user1_settings.blacklist.add(self.user2)
        self.user1_settings.save()
        response = client.get(f'/files/{self.file.id}')
        self.assertContains(response,'Доступ',status_code=200)

    def test_file_upload(self):
        client = Client()
        client.login(username=TEST_USER_NAME,password=TEST_USER_PASSWORD)
        file = SimpleUploadedFile('file.txt',b'1120012012')
        client.post(reverse('upload'),{'name':'filename','description':'filedescription','file':file,'acces':'Public'})
        self.assertEqual(Files.objects.filter(user=get_user(client)).count(),2)

    def test_blacklist_remove(self):
        self.user1_settings.blacklist.add(self.user2)
        self.user1_settings.save()
        client = Client()
        client.login(username=TEST_USER_NAME,password=TEST_USER_PASSWORD)
        client.get(reverse('blacklist',kwargs={'pk':2,'operation':'remove'}))
        self.assertEqual(self.user1_settings.blacklist.all().count(),0)

    def test_whitelist_accept(self):
        client=Client()
        client.login(username=TEST_USER2_NAME,password=TEST_USER2_PASSWORD)
        client.get(reverse('invite',kwargs={'user':self.user1}))
        client.logout()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        client.get(reverse('accept', kwargs={'pk':1,'operation':'accept'}))
        self.assertEqual(self.user1_settings.whitelist.all().count(),1)

    def test_whitelist_decline(self):
        client=Client()
        client.login(username=TEST_USER2_NAME,password=TEST_USER2_PASSWORD)
        client.get(reverse('invite',kwargs={'user':self.user1}))
        client.logout()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        client.get(reverse('accept', kwargs={'pk':1,'operation':'decline'}))
        self.assertEqual(self.user1_settings.whitelist.all().count(),0)
        self.assertEqual(Requests.objects.all().count(), 0)

    def test_whitelist_delete(self):
        client=Client()
        client.login(username=TEST_USER2_NAME,password=TEST_USER2_PASSWORD)
        client.get(reverse('invite',kwargs={'user':self.user1}))
        client.logout()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        client.get(reverse('accept', kwargs={'pk':1,'operation':'accept'}))
        self.assertEqual(self.user1_settings.whitelist.all().count(),1)
        client.get(reverse('remove', kwargs={'pk': 2, 'redirect_to': 'profile'}))
        self.assertEqual(self.user1_settings.whitelist.all().count(), 0)
        self.assertEqual(self.user2_settings.whitelist.all().count(), 0)

    def test_comment_delete(self):
        comment = Comments.objects.create(user=self.user1,text='Тестовый коммент',file=self.file)
        comment2 = Comments.objects.create(user=self.user2, text='Тестовый коммент', file=self.file)
        client = Client()
        client.login(username=TEST_USER2_NAME, password=TEST_USER2_PASSWORD)
        client.get(reverse('delete_comment',kwargs={'pk':comment.id}))
        self.assertEqual(Comments.objects.all().count(),2)
        client.get(reverse('delete_comment', kwargs={'pk': comment2.id}))
        self.assertEqual(Comments.objects.all().count(), 1)
        client.logout()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        client.get(reverse('delete_comment', kwargs={'pk': comment.id}))
        self.assertEqual(Comments.objects.all().count(), 0)

    def test_settings_change(self):
        client= Client()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        client.post(reverse('my_storage'),{'acces':'Limited'})
        self.assertEqual(UserExtended.objects.get(user=get_user(client)).storage_status,'Limited')
        client.post(reverse('my_storage'),{'acces':'Public'})
        self.assertEqual(UserExtended.objects.get(user=get_user(client)).storage_status, 'Public')

    def test_file_update(self):
        client = Client()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        file = SimpleUploadedFile('file.txt', b'1120012012')
        client.post(reverse('edit',kwargs={'pk':1}),{'name':'z','description':'1','file':file,'acces':'Limited'})
        self.assertEqual(Files.objects.get(pk=1).name,'z')

    def test_file_delete(self):
        client = Client()
        client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        client.post(reverse('delete',kwargs={'pk':1}))
        self.assertEqual(Files.objects.count(),0)

    def test_file_delete_no_permission(self):
        client = Client()
        client.login(username=TEST_USER2_NAME, password=TEST_USER2_PASSWORD)
        client.post(reverse('delete',kwargs={'pk':1}))
        self.assertEqual(Files.objects.count(),1)
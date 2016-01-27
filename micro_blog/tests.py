from django.test import TestCase
from django.test import Client
from micro_blog.forms import BlogpostForm, BlogCategoryForm
from micro_blog.models import Category, Post, Tags
from micro_admin.models import User
import unittest
from microsite.settings import BASE_DIR
from django.core.files import File


class micro_blog_forms_test(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            'mp@mp.com', 'micro-test', 'mp')
        self.category = Category.objects.create(
            name='django', description='django desc')
        self.blogppost = Post.objects.create(
            title='python introduction', user=self.user, content='This is content', category=self.category, status='D', meta_description='meta')

    def test_blogpostform(self):
        form = BlogpostForm(data={'title': 'python introduction', 'content': 'This is content', 'category': self.category.id,
                                  'status': 'D', 'meta_description': 'meta', 'is_superuser': 'True', 'slug': 'python-introduction'})
        self.assertTrue(form.is_valid())

    def test_BlogCategoryForm(self):
        form = BlogCategoryForm(
            data={'name': 'django form', 'description': 'django'})
        self.assertTrue(form.is_valid())


# models test
class category_models_test(TestCase):

    def create_category(self, name="simple page", description="simple page content"):
        return Category.objects.create(name=name, description=description)

    def test_category_creation(self):
        w = self.create_category()
        self.assertTrue(isinstance(w, Category))
        self.assertEqual(w.__unicode__(), w.name)
        # category_url = settings.SITE_BLOG_URL + "category/" + w.slug
        # self.assertEquals(w.get_url(), category_url)


# models test
class tags_models_test(TestCase):

    def create_tags(self, name="simple page"):
        return Tags.objects.create(name=name)

    def test_category_creation(self):
        w = self.create_tags()
        self.assertTrue(isinstance(w, Tags))
        self.assertEqual(w.__unicode__(), w.name)


# models test
class post_models_test(TestCase):

    def create_post(self, tag="simple page", category="simple page", description="simple page content", meta_description='meta_description', title="post", content="content", status="D"):
        category = Category.objects.create(name=category, description=description)
        tag = Tags.objects.create(name=tag)
        user = User.objects.create_superuser('mp@mp.com', 'micro-test', 'mp')

        return Post.objects.create(category=category, user=user, content=content, title=title, status=status, meta_description=meta_description)

    def test_category_creation(self):
        w = self.create_post()
        self.assertTrue(isinstance(w, Post))
        self.assertEqual(w.__unicode__(), w.title)



class micro_blog_views_test_with_employee(TestCase):

    def setUp(self):
        self.client = Client()
        self.employee = User.objects.create_user(
            'testemployee', "testemployee@micropyramid.com", 'pwd')
        self.user = User.objects.create_user(
            'testuser', "testuser@micropyramid.com", 'userpws')
        self.category = Category.objects.create(
            name='category', description='category desc')
        self.django_category = Category.objects.create(
            name='django', description='category desc')
        self.blogpost = Post.objects.create(
            title='python blog', user=self.user, content='This is content', category=self.category, status='D', slug='python-blog')

    def test_views_with_employee_login(self):
        user_login = self.client.login(
            username='testemployee@micropyramid.com', password='pwd')
        self.assertTrue(user_login)

        response = self.client.get('/blog/new-category/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/blog/edit-category/django/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/blog/delete-category/category/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/blog/edit-post/python-blog/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accessdenied.html')

        response = self.client.get('/blog/delete-post/python-blog/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Admin or Owner can delete blog post' in response.content)

        # Testcase for report
        response = self.client.post('/report/', {'envelope': [{'from': 'testuser@micropyramid.com'}], 'text': '</p>This is a report text</p>'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Report has been created Sucessfully.' in response.content)

        # Testcase for contact with get
        response = self.client.get('/contact-us/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/pages/contact-us.html')

        # Testcase for contact with post request simple
        response = self.client.post('/contact-us/', {'full_name': 'client name', 'message': 'test message', 'email': 'testclient@mp.com', 'phone': '1234567890'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Contact submitted successfully' in response.content)

        # Testcase for contact with post request advanced
        response = self.client.post('/contact-us/', {'full_name': 'client name', 'message': 'test message', 'email': 'testclient@mp.com', 'phone': '1234567890', 'enquery_type': 'general', 'domain': 'micropyramid.com', 'domain_url': 'https://micropyramid.com', 'country': 'india'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Contact submitted successfully' in response.content)

        # Testcase for contact advanced wrong data
        response = self.client.post('/contact-us/', {'full_name': '', 'message': 'test message', 'email': 'testclient@mp.com', 'phone': '1234567890'})
        self.assertEqual(response.status_code, 200)

        # Testcase for contact simple wrong data
        response = self.client.post('/contact-us/', {'full_name': '', 'message': 'test message', 'email': 'testclient@mp.com', 'phone': '1234567890', 'enquery_type': 'general', 'domain': 'micropyramid.com', 'domain_url': 'https://micropyramid.com', 'country': 'india'})
        self.assertEqual(response.status_code, 200)

        # Testcase for subscribe with get request
        response = self.client.get('/subscribe/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/pages/subscribe.html')

        # Testcase for subscribe
        response = self.client.post('/subscribe/', {'email': '', 'is_blog': '', 'is_category': ''})
        self.assertEqual(response.status_code, 200)

        # Testcase for subscribe on site
        response = self.client.post('/subscribe/', {'email': 'testsubscriber@mp.com', 'is_blog': 'False', 'is_category': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Your email has been successfully subscribed.' in response.content)

        # Testcase for subscribe on blog
        response = self.client.post('/subscribe/', {'email': 'testsubscriber@mp.com', 'is_blog': 'True', 'is_category': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Your email has been successfully subscribed.' in response.content)

        # Testcase for subscribe on blog category
        response = self.client.post('/subscribe/', {'email': 'testsubscriber@mp.com', 'is_blog': 'True', 'is_category': str(self.category.id)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Your email has been successfully subscribed.' in response.content)


class micro_blogviews_get(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('mp@mp.com', 'micro', 'mp')
        self.category = Category.objects.create(
            name='django', description='django desc')
        self.blogppost = Post.objects.create(
            title='other python introduction', user=self.user, content='This is content', category=self.category, status='P', slug="other-python-introduction")
        self.tag = Tags.objects.create(name='testtag')
        self.blogppost.tags.add(self.tag)
        print self.blogppost.updated_on

    def test_blog_get(self):
        user_login = self.client.login(username='micro', password='mp')
        self.assertTrue(user_login)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/blog/index.html')

        response = self.client.get('/blog/list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/blog/blog-posts.html')

        response = self.client.get('/blog/new-post/')
        self.assertTemplateUsed(response, 'admin/blog/blog-new.html')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/edit-post/other-python-introduction/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/blog/blog-edit.html')

        response = self.client.post('/blog/view-post/other-python-introduction/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/blog/2016/01/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/category-list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/blog/blog-category-list.html')

        response = self.client.get('/blog/new-category/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/blog/blog-category.html')

        response = self.client.get('/blog/category/django/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/blog/index.html')

        response = self.client.get('/blog/tag/'+str(self.tag.slug)+'/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/category/django/?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/blog/index.html')

        response = self.client.get('/blog/' + self.blogppost.slug + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/blog/article.html')

        response = self.client.get('/blog/2016/01/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/blog/index.html')

        response = self.client.get('/blog/2016/01/?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'site/blog/index.html')

        response = self.client.get('/blog/edit-category/django/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/blog/blog-category-edit.html')

        response = self.client.get('/blog/delete-post/other-python-introduction/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/delete-category/django/')
        self.assertEqual(response.status_code, 302)


class micro_blog_post_data(TestCase):

    '''
        Saving(POST data) data to the database in django
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('mp@mp.com', 'micro', 'mp')
        self.category = Category.objects.create(
            name='django', description='django desc')
        self.blogppost = Post.objects.create(
            title='django introduction', user=self.user, content='This is content', category=self.category, status='D', slug='django-introduction')

    def test_blog_post(self):
        user_login = self.client.login(username='micro', password='mp')
        self.assertTrue(user_login)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/?page=1')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/?page=s')
        self.assertEqual(response.status_code, 404)

        # with correct input
        response = self.client.post('/blog/new-post/', {'title': 'python introduction', 'content': 'This is content', 'category':
                                                        self.category.id, 'status': 'D', 'tags': 'django', 'meta_description': 'meta', 'is_superuser': 'True', 'slug': 'python-introduction-1'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post created' in response.content)

        response = self.client.post('/blog/new-post/', {'title': 'introduction', 'content': 'This is content', 'category':
                                                        self.category.id, 'status': 'D', 'tags': 'django', 'meta_description': 'meta', 'is_superuser': 'False', 'slug': 'introduction'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post created' in response.content)

        response = self.client.post('/blog/new-post/', {'title': 'python', 'content': 'This is content', 'category':
                                                        self.category.id, 'status': 'P', 'tags': 'python', 'meta_description': 'meta', 'slug': 'python', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post created' in response.content)

        response = self.client.post('/blog/new-post/', {'title': 'Django', 'content': 'This is content', 'category':
                                                        self.category.id, 'status': 'T', 'tags': 'django', 'meta_description': 'meta', 'slug': 'django', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post created' in response.content)

        # with wrong input
        response = self.client.post(
            '/blog/new-post/', {'content': 'This is content', 'category': self.category.id, 'status': 'D', 'meta_description': 'meta', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('Blog Post created' in response.content)

        response = self.client.post('/blog/edit-post/python-introduction-1/', {
                                    'title': 'python introduction', 'content': 'This is content', 'category': self.category.id, 'status': 'D', 'meta_description': 'meta', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post edited' in response.content)

        response = self.client.post('/blog/edit-post/python-introduction-1/', {
                                    'title': 'python introduction', 'content': 'This is content', 'category': self.category.id, 'status': 'P', 'meta_description': 'meta', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post edited' in response.content)

        response = self.client.post('/blog/edit-post/python-introduction-1/', {
                                    'title': 'python introduction', 'content': 'This is content', 'category': self.category.id, 'status': 'T', 'tags': 'django python', 'meta_description': 'meta', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog Post edited' in response.content)

        response = self.client.post('/blog/edit-post/python-introduction-1/', {
                                    'content': 'This is content', 'category': self.category.id, 'status': 'D', 'tags': 'python', 'meta_description': 'meta', 'is_superuser': 'False'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('Blog Post edited' in response.content)

        response = self.client.post(
            '/blog/new-category/', {'name': 'django form', 'description': 'django'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog category created' in response.content)

        response = self.client.post(
            '/blog/new-category/', {'description': 'django'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('Blog category created' in response.content)

        response = self.client.get('/blog/edit-category/django/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/blog/edit-category/django-form/', {'name': 'django new', 'description': 'django'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Blog category updated' in response.content)

        response = self.client.post(
            '/blog/edit-category/django-new/', {'description': 'django'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse('Blog category updated' in response.content)

        response = self.client.get('/blog/tag/django/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/blog/tag/django/?page=1')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/blog/tag/django/?page=e')
        self.assertEqual(response.status_code, 404)

        # img = open(BASE_DIR + '/static/site/images/1-c-n.png')
        # img = File(img)

        # response = self.client.get('/blog/ajax/photos/upload/')
        # self.assertEqual(response.status_code,200)

        # response = self.client.post('/blog/ajax/photos/upload/',{'upload':img})
        # self.assertEqual(response.status_code,200)

        # response = self.client.get('/blog/ajax/photos/recent/')
        # self.assertEqual(response.status_code,200)


# class image_upload(unittest.TestCase):
#   def setUp(self):
#       img = open(BASE_DIR + '/static/site/images/1-c-n.png')
#       img = File(img)

#   def test_img(self):
#       img = open(BASE_DIR + '/static/site/images/1-c-n.png')
#       img = File(img)
        # resp=store_image(img,'')
        # self.assertTrue(resp)

    # def test_upload(self):
    #   img = upload_photos('')
    #   print img


class micro_user_test(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'test@micropyramid.com', 'testuser', 'test')
        self.category = Category.objects.create(
            name='django', description='django desc')
        self.blogppost = Post.objects.create(
            title='new python introduction', user=self.user, content='This is content', category=self.category, status='D', slug="new-python-introduction")

    def test_blog_without_user(self):

        user_login = self.client.login(username='testuser', password='test')
        self.assertTrue(user_login)

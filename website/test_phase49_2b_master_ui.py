from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

class Phase492BMasterUIContractTests(TestCase):
    def setUp(self): self.root=Path(settings.BASE_DIR)
    def read(self,p): return (self.root/p).read_text(encoding='utf-8',errors='replace')
    def test_master_only_admin_contract(self):
        base=self.read('templates/admin/base.html'); site=self.read('templates/admin/base_site.html')
        self.assertIn('velzon_master/css/bootstrap-rtl.min.css',base); self.assertIn('velzon_master/css/app-rtl.min.css',base); self.assertIn('phase49_2b-admin.css',site); self.assertNotIn('interactive',site.lower())
    def test_exact_logo_contract(self):
        for p in ('templates/website/customer/account_base.html','templates/admin/login.html','static/css/brand-mark-contract.css'):
            self.assertIn('3dprinthublogo.png',self.read(p))
    def test_iransans_fanum_weights(self):
        css=self.read('static/css/phase49_2b-design-system.css')
        for w in (200,300,400,500,700,900): self.assertIn(f'font-weight:{w}',css)
    def test_customer_drawer_contract(self):
        self.assertIn('data-p49-customer-toggle',self.read('templates/website/customer/account_base.html'))
        self.assertIn('.customer-sidebar.is-open',self.read('static/css/phase49_2b-customer.css'))
    def test_admin_login_smoke(self):
        r=self.client.get('/admin/login/'); self.assertEqual(r.status_code,200); self.assertContains(r,'3dprinthublogo.png')
    def test_admin_index_smoke(self):
        U=get_user_model(); u=U.objects.create_superuser(username='phase492b',email='phase492b@example.test',password='StrongPass123!'); self.client.force_login(u)
        r=self.client.get('/admin/'); self.assertEqual(r.status_code,200); self.assertContains(r,'phase49_2b-admin.css')

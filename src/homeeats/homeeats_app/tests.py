from django.test import TestCase, Client
from django.urls import reverse
import json 
from django.shortcuts import render, get_object_or_404
from django.test import RequestFactory
from . import views
from homeeats_app.models import Cook, Cuisine, Dish, Dish_Review, Address, User, Customer, Order, ShoppingCart, CartItem
from .forms import DishSearchForm, DishCreateForm, CustomerCreateForm, DishReviewForm, UserEditForm, PhoneEditForm

class CookHomeTest(TestCase):
    fixtures = ['test_data.json']
    def test_cuisines_on_cook_manage(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('cook_manage'))
        cuisines = response.context['cuisines']
        self.assertEquals(cuisines[0]['name'], "Italian")
        self.assertEquals(cuisines[1]['name'], "Mexican")
        self.client.logout()
    def test_not_logged_in_causes_redirect_to_login_for_cook_home(self):
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)
    def test_orders_work(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       orders = response.context['pending_orders']
       self.assertEquals(len(orders), 1)
    def test_orders_page_works(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.assertEquals(response.status_code, 200)
    def test_correct_pending_order_renders(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.assertEquals(response.context['pending_orders'][0]['id'], 1)
       self.assertEquals(response.context['pending_orders'][0]['status'], 'p')
    def test_correct_in_progress_order_renders(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.assertEquals(response.context['in_progress_orders'][0]['id'], 2)
       self.assertEquals(response.context['in_progress_orders'][0]['status'], 'c')
    def test_cook_online_has_orders_so_cant_go_offline(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       response = self.client.get(reverse('available'))
       self.assertEquals(response.status_code, 302)
       self.assertEquals(response.url, '/cook/home/')
    def test_cook_online_no_orders_so_can_logout(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.client.get(reverse('reject_order', args=[1,1]))
       self.client.get(reverse('cooking_to_delivery', args=[2]))
       self.client.get(reverse('completed_delivery', args=[2]))
       response = self.client.get(reverse('logout_view'))
       self.assertEquals(response.status_code, 302)
       self.assertEquals(response.url, '/')
    def test_reject_order_changes_status(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.client.get(reverse('reject_order', args=[1,1]))
       order = Order.objects.get(id=1)
       self.assertEquals(order.status, 'r')
    def test_accept_order_changes_status(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.client.get(reverse('accept_order', args=[1]))
       order = Order.objects.get(id=1)
       self.assertEquals(order.status, 'c')
    def test_change_status_from_cooking_to_delivery(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.client.get(reverse('cooking_to_delivery', args=[2]))
       order = Order.objects.get(id=2)
       self.assertEquals(order.status, 'o')

class CookManageTest(TestCase):
    fixtures = ['test_data.json']
    def test_delete_dish(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        self.client.get(reverse('delete_dish', args=[2]))
        response = self.client.get(reverse('cook_cuisine_dishes', args=[1]))
        dishes = response.context['dishes']
        self.assertEquals(len(dishes),1)
    def test_delete_dish_redirects_to_cook_cuisine_dishes(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('delete_dish', args=[2]))
       self.assertEquals(response.status_code, 302)
       self.assertEquals(response.url, "/cook/cuisine/1/dishes")

class CustomerCheckoutTest(TestCase):
    def test_checkout_access(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('checkout'))
        self.assertEquals(response.status_code, 302)
    def test_checkout_redirect(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('checkout'))
        self.assertEquals(response.url, "/?next=/customer/checkout/")
    def test_checkout_home_redirect(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.get(reverse('checkout'))
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.url, "/?next=/customer/home/")
    def test_checkout_home_access(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.get(reverse('checkout'))
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_valid_payment(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1}, content_type='application/x-www-form-urlencoded')
        data = {
            "cardNumber": "4242424242424242",
            "expDate": 12/20,
            "cvc": "314",
            "payment_option": "card",
        }
        response = self.client.post(reverse('checkout'), data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(response.status_code, 302)
    def test_invalid_payment(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1}, content_type='application/x-www-form-urlencoded')
        data = {
            "cardNumber": "5242424242424242",
            "expDate": 12/20,
            "cvc": "314",
            "payment_option": "card",
        }
        response = self.client.post(reverse('checkout'), data, content_type='application/x-www-form-urlencoded', follow=True)
        self.assertEquals(response.status_code, 200)
    def test_invalid_date(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1}, content_type='application/x-www-form-urlencoded')
        data = {
            "cardNumber": "4242424242424242",
            "expDate": 12/18,
            "cvc": "314",
            "payment_option": "card",
        }
        response = self.client.post(reverse('checkout'), data, content_type='application/x-www-form-urlencoded', follow=True)
        self.assertEquals(response.status_code, 200)
    def test_invalid_cvv(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1}, content_type='application/x-www-form-urlencoded')
        data = {
            "cardNumber": "4242424242424242",
            "expDate": 12/20,
            "cvc": "34",
            "payment_option": "card",
        }
        response = self.client.post(reverse('checkout'), data, content_type='application/x-www-form-urlencoded', follow=True)
        self.assertEquals(response.status_code, 200)
    def test_cash(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1}, content_type='application/x-www-form-urlencoded')
        data = {
            "payment_option": "cash",
        }
        response = self.client.post(reverse('checkout'), data, content_type='application/x-www-form-urlencoded', follow=True)
        self.assertEquals(response.status_code, 200)
    def test_skip_checkout(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1}, content_type='application/x-www-form-urlencoded')
        response = self.client.get(reverse('checkout'), follow=True)
        self.assertEquals(response.status_code, 200)

class CustomerCartTest(TestCase):
    def test_cart_access(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('cart'))
        self.assertEquals(response.status_code, 302)
    def test_cart_redirect(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('cart'))
        self.assertEquals(response.url, "/?next=/customer/cart/")
    def test_checkout_home_redirect(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.get(reverse('cart'))
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.url, "/?next=/customer/home/")
    def cart_order(self):
        ShoppingCart.objects.create(total = 12.99, empty=False)
        self.assertTrue(empty = False)
    def cart_items(self):
        CartItems.objects.create(quantity = 3)
        self.assertTrue(quantity > 0)
    def test_remove(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1})
        response = self.client.post(reverse('removeItem'), {'cart_id': 3, 'item_id': 1})
        self.assertEquals(response.status_code, 302)
    def test_remove_multiple(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1})
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 2})
        response = self.client.post(reverse('removeItem'), {'cart_id': 3, 'item_id': 1})
        response = self.client.post(reverse('removeItem'), {'cart_id': 3, 'item_id': 2})
        self.assertEquals(response.status_code, 302)
    def test_remove_multiple_none(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1})
        response = self.client.post(reverse('removeItem'), {'cart_id': 3, 'item_id': 1})
        response = self.client.post(reverse('removeItem'), {'cart_id': 3, 'item_id': 1})
        self.assertEquals(response.status_code, 302)
    def test_remove_none(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.post(reverse('removeItem'), {'cart_id': 3, 'item_id': 1})
        self.assertEquals(response.status_code, 302)
    def test_payment(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1})
        response = self.client.get(reverse('payment'))
        self.assertEquals(response.status_code, 202)
    def test_payment(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.post(reverse('addtocart'), {'quantity': 1, 'dish_id': 1})
        response = self.client.get(reverse('payment'))
        self.assertEquals(response.status_code, 302)

class CustomerHomeTest(TestCase):
    def test_not_logged_in_causes_redirect_to_login_for_cook_home(self):
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_search_form_is_valid(self):
        form = DishSearchForm(data={'search':'', 'sort':'rating', 'cuisine':'none'})
        self.assertTrue(form.is_valid())
    def test_search_form_not_valid(self):
        form = DishSearchForm()
        self.assertFalse(form.is_valid())

class CustomerAddToCartTest(TestCase):
    def test_addtocart_redirects(self):
        response = self.client.post(reverse('addtocart'), {})
        self.assertEquals(response.status_code, 302)
    def test_addtocart_returns(self):
        response = self.client.post(reverse('addtocart'), {'dish_id':1})
        self.assertEqual(str(response.content, encoding='utf8'),'')
    
        
class CustomerAddToFavoritesTest(TestCase):
    def test_addtofavorites_redirects(self):
        response = self.client.post(reverse('togglefav'), {})
        self.assertEquals(response.status_code, 302)
    def test_addtofavorites_returns(self):
        response = self.client.post(reverse('togglefav'), {})
        self.assertEqual(str(response.content, encoding='utf8'),'')

class CustomerRemoveFromFavoritesTest(TestCase):
    def test_removefromfavorites_redirects(self):
        response = self.client.post(reverse('togglefav'), {})
        self.assertEquals(response.status_code, 302)
    def test_removefromfavorites_returns(self):
        response = self.client.post(reverse('togglefav'), {})
        self.assertEqual(str(response.content, encoding='utf8'),'')

class CustomerCancelOrderTest(TestCase):
    fixtures = ['test_data.json']
    def test_cancelorder_success(self):
        response = self.client.post(reverse('cancel_order'), {'order_id':'1'})
        self.assertEquals(response.status_code, 302)
    def test_cancelorder_failure(self):
        response = self.client.post(reverse('cancel_order'), {'order_id':'5'})
        self.assertEquals(response.status_code, 302)

class CustomAdminInterfaceTest(TestCase):
    def test_cook_applications(self):
        response = self.client.get(reverse('admin_applications'))
        self.assertEquals(response.status_code, 200)
    def test_cook_changerequests(self):
        response = self.client.get(reverse('admin_changerequests'))
        self.assertEquals(response.status_code, 200)
    def test_reported_reviews(self):
        response = self.client.get(reverse('admin_reportedreviews'))
        self.assertEquals(response.status_code, 200)


class CustomerDishReviewTest(TestCase):
    def test_review_form_is_valid(self):
        form = DishReviewForm(data={'dish_rating':5, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid()) #change when fixed
    def test_review_form_not_valid(self):
        form = DishReviewForm(data={'dish_rating':5, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid())
    def test_review_form_rating_too_high(self):
        form = DishReviewForm(data={'dish_rating':6, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid())
    def test_review_form_rating_too_low(self):
        form = DishReviewForm(data={'dish_rating':-1, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid())
    
class SearchTest(TestCase):
    def test_search_empty(self):
        form = DishSearchForm(data={'search':'', 'sort':'rating', 'cuisine':'none'})
        self.assertTrue(form.is_valid())

class AccountCreationTest(TestCase):
    # def test_cook_create_with_valid_data(self):
    #     response = self.client.post(reverse('cookcreate'), {'first_name': 'Bob', 'last_name': 'Saget', 'email': 'bob@bob.com', 'password': 'sagetsaget', 'government_id':'cook_government_ids/id.png', 'kitchen_license': 'asdfasdfasdf', 'phone_number': '7777777777', 'delivery_distance_miles': '30', 'delivery_fee': '3.44', 'street': '3775 Mazewood Lane', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22033'})
        # self.assertEquals(response.status_code, 302)
        # self.assertEquals(response.url, "/")
    def test_customer_create_with_valid_data(self):
        response = self.client.post(reverse('customercreate'), {'first_name': 'Dave', 'last_name': 'Chapelle', 'street': '221 Baker Street', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22000', 'email': 'dave@dave.com', 'password': 'chapchap', 'phone_number': '8888888888'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")
        
class AddressCreationTest(TestCase):
     def setUp(self):
         Address.objects.create(street_name='2132 someStreet Ln', city="Chantilly", state="VA", zipcode="20151")
         Address.objects.create(street_name='123 Jefferson Park Av', city="Herndon", state="VA", zipcode="20166")
         cook_user = User.objects.create(is_cook=True)
         self.cook = Cook.objects.create(user=cook_user)
         self.cook_address = Address.objects.create(street_name='733 Summer Grove Terr', city="Ashburn", state="MD", zipcode="12333", cook=self.cook)

class UserGroupTest(TestCase):
    # def test_cook_create(self):
    #     response = self.client.post(reverse('cookcreate'), {'first_name': 'Bob', 'last_name': 'Saget', 'email': 'bob@bob.com', 'password': 'sagetsaget', 'government_id':'', 'kitchen_license': 'asdfasdfasdf', 'phone_number': '7777777777', 'delivery_distance_miles': '30', 'delivery_fee': '3.44', 'street': '3775 Mazewood Lane', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22033'})
    #     user = User.objects.get(username="bob@bob.com")
    #     self.assertTrue(user.is_cook)
    def test_redirect_cook(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_redirect(self):
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_redirect_cook_checkout(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('checkout'))
        self.assertEquals(response.status_code, 302)
    def test_customer_create(self):
        response = self.client.post(reverse('customercreate'), {'first_name': 'Dave', 'last_name': 'Chapelle', 'street': '221 Baker Street', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22000', 'email': 'dave@dave.com', 'password': 'chapchap', 'phone_number': '8888888888'})
        user = User.objects.get(username="dave@dave.com")
        self.assertTrue(user.is_customer)
    def test_redirect_customer(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)
    def test_redirect_customer_home(self):
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)

class CookReportDishReviewTest(TestCase):
    fixtures = ['test_data.json']
    def test_cook_report_redirects_right(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('report_dish_review', args=[1, 'o']))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/cook/dish/1/reviews')
    def test_cook_report_offensive(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        self.client.get(reverse('report_dish_review', args=[1, 'o']))
        review = Dish_Review.objects.get(id=1)
        self.assertEquals(review.report_flag, True)
        self.assertEquals(review.report_reason, 'o')
    def test_cook_report_not_relevant(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        self.client.get(reverse('report_dish_review', args=[1, 'n']))
        review = Dish_Review.objects.get(id=1)
        self.assertEquals(review.report_flag, True)
        self.assertEquals(review.report_reason, 'n')
    def test_cook_report_threatening(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        self.client.get(reverse('report_dish_review', args=[1, 't']))
        review = Dish_Review.objects.get(id=1)
        self.assertEquals(review.report_flag, True)
        self.assertEquals(review.report_reason, 't')
    def test_cook_report_spam(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        self.client.get(reverse('report_dish_review', args=[1, 's']))
        review = Dish_Review.objects.get(id=1)
        self.assertEquals(review.report_flag, True)
        self.assertEquals(review.report_reason, 's')

class AddressCreationTest(TestCase):
     def setUp(self):
         Address.objects.create(street_name='2132 someStreet Ln', city="Chantilly", state="VA", zipcode="20151")
         Address.objects.create(street_name='123 Jefferson Park Av', city="Herndon", state="VA", zipcode="20166")
         cook_user = User.objects.create(is_cook=True)
         self.cook = Cook.objects.create(user=cook_user)
         self.cook_address = Address.objects.create(street_name='733 Summer Grove Terr', city="Ashburn", state="MD", zipcode="12333", cook=self.cook)

     def test_fetch_all_correct_streets_names(self):
         addresses = Address.objects.values_list('street_name', flat=True)
         self.assertTrue(addresses[0] == ('2132 someStreet Ln'))
         self.assertTrue(addresses[1] == ('123 Jefferson Park Av'))
         self.assertTrue(addresses[2] == ('733 Summer Grove Terr'))

     def test_fetch_all_correct_cities(self):
         addresses = Address.objects.values_list('city', flat=True)
         self.assertTrue(addresses[0] == ('Chantilly'))
         self.assertTrue(addresses[1] == ('Herndon'))
         self.assertTrue(addresses[2] == ('Ashburn'))

     def test_fetch_all_correct_states(self):
         addresses = Address.objects.values_list('state', flat=True)
         self.assertTrue(addresses[0] == ('VA'))
         self.assertTrue(addresses[1] == ('VA'))
         self.assertTrue(addresses[2] == ('MD'))

     def test_fetch_all_correct_zipcodes(self):
         addresses = Address.objects.values_list('zipcode', flat=True)
         self.assertTrue(addresses[0] == ('20151'))
         self.assertTrue(addresses[1] == ('20166'))
         self.assertTrue(addresses[2] == ('12333'))

     def test_correctly_saves_address_cook(self):
         self.assertTrue(self.cook.id == self.cook_address.cook.id)

class CustomerCreateFormTest(TestCase):
    def test_valid_data(self):
        form = CustomerCreateForm({
            'first_name': "First",
            'last_name': "Last",
            'password': "password",
            'email': "first@email.com",
            'street': "123 rotunda",
            'town': "Charlottesville",
            'state': "VA",
            'zipcode': "22903",
            'phone_number': "0123456789"
        })
        self.assertTrue(form.is_valid())

    '''
    Tests that invalid emails are not accepted
    '''
    def test_invalid_email(self):
        form = CustomerCreateForm({
            'first_name': "First",
            'last_name': "Last",
            'password': "password",
            'email': "first",
            'street': "123 rotunda",
            'town': "Charlottesville",
            'state': "VA",
            'zipcode': "22903",
            'phone_number': "0123456789"
        })      
        self.assertFalse(form.is_valid())
    
    
    '''
    Tests that data will not saved if required information is missing
    '''
    def test_missing_required_firstname(self):
        form = CustomerCreateForm({
            'first_name': "",
            'last_name': "Last",
            'password': "password",
            'email': "first",
            'street': "123 rotunda",
            'town': "Charlottesville",
            'state': "VA",
            'zipcode': "22903",
            'phone_number': "0123456789"
        })
        self.assertFalse(form.is_valid())
    

class CustomerEditProfileTest(TestCase):
    '''
    Cannot submit a form with an empty first name
    '''
    def test_no_firstname(self):
        form = UserEditForm({'first_name': "",'last_name': "Last"})
        self.assertFalse(form.is_valid())
    
    '''
    Cannot submit an edit form without last name
    '''
    def test_no_lastname(self):
        form = UserEditForm({'first_name': "first",'last_name': ""})
        self.assertFalse(form.is_valid())
    
    '''
    Cannot change the the user's username
    '''
    def test_change_email(self):
        form = UserEditForm({'first_name': "first",'last_name': "last", 'email': "abc@gmail.com"})
        self.assertFalse(form.is_valid())
    
    '''
    Can change the firstname, lastname, and phonenumber
    '''
    def test_change_phonenumber(self):
        form = PhoneEditForm({'phone_number':'0123456789'})
        self.assertTrue(form.is_valid())

class DishRestrictionsTest(TestCase):
    def test_vegan_true(self):
         cook_user = User.objects.create(is_cook=True)
         cook = Cook.objects.create(user=cook_user)
         cuisine = Cuisine.objects.create(name='mexican')
         new_dish = Dish.objects.create(cook_id= cook.id, cuisine_id=cuisine.id, vegan=True)
         self.assertTrue(new_dish.vegan == True)

    def test_vegan_false(self):
         cook_user = User.objects.create(is_cook=True)
         cook = Cook.objects.create(user=cook_user)
         cuisine = Cuisine.objects.create(name='italian')
         new_dish = Dish.objects.create(cook_id= cook.id, cuisine_id=cuisine.id, vegan=False)
         self.assertTrue(new_dish.vegan == False)

    def test_valid_allergies(self):
         cook_user = User.objects.create(is_cook=True)
         cook = Cook.objects.create(user=cook_user)
         cuisine = Cuisine.objects.create(name='italian')
         new_dish = Dish.objects.create(cook_id= cook.id, cuisine_id=cuisine.id, allergies="Peanuts")
         self.assertTrue(new_dish.allergies == "Peanuts")

    def test_no_allergies(self):
         cook_user = User.objects.create(is_cook=True)
         cook = Cook.objects.create(user=cook_user)
         cuisine = Cuisine.objects.create(name='italian')
         new_dish = Dish.objects.create(cook_id= cook.id, cuisine_id=cuisine.id) 
         self.assertFalse(new_dish.allergies)
    
    def test_dish_create_form(self):
        dishForm = DishCreateForm({'vegan': True, 'allergies': 'Peanuts'})
        self.assertFalse(dishForm.is_valid())

class CustomerProfileRedirectTest(TestCase):
    def test_customer_profile_navigation(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('myaccount'))
        self.assertEquals(response.status_code, 302)

class CookProfileRedirectTest(TestCase):
    def test_cook_profile_navigation(self):
        self.client.login(username='test@cook.com', password='capstone')
        response = self.client.get(reverse('myaccount'))
        self.assertEquals(response.status_code, 302)


class DishReviewModelTest(TestCase):

    def test_dish_review_dish_relationship(self):
         customer_user = User.objects.create(username="customer_user", is_customer=True)
         cook_user= User.objects.create(username="cook_user", is_cook=True)
         customer = Customer.objects.create(user=customer_user)
         cook = Cook.objects.create(user=cook_user)
         cuisine = Cuisine.objects.create()
         dish = Dish.objects.create(cuisine=cuisine, cook=cook)
         dish_review = Dish_Review.objects.create(dish=dish, customer=customer)
         self.assertEquals(dish_review.dish.id, dish.id)

    def test_dish_review_customer_relationship(self):
         customer_user = User.objects.create(username="customer_user", is_customer=True)
         cook_user= User.objects.create(username="cook_user", is_cook=True)
         customer = Customer.objects.create(user=customer_user)
         cook = Cook.objects.create(user=cook_user)
         cuisine = Cuisine.objects.create()
         dish = Dish.objects.create(cuisine=cuisine, cook=cook)
         dish_review = Dish_Review.objects.create(dish=dish, customer=customer)
         self.assertEquals(dish_review.customer.id, customer.id)
  
    def test_dish_description(self):
        cook_user= User.objects.create(username="cook_user", is_cook=True)
        customer_user = User.objects.create(username="customer_user", is_customer=True)
        customer = Customer.objects.create(user=customer_user)
        cook = Cook.objects.create(user=cook_user)
        cuisine = Cuisine.objects.create()
        dish = Dish.objects.create(cuisine=cuisine, cook=cook)
        dish_review = Dish_Review.objects.create(description="This was a nice dish", dish=dish, customer=customer)
        self.assertEquals(dish_review.description, "This was a nice dish")

    def test_dish_rating(self):
        cook_user= User.objects.create(username="cook_user", is_cook=True)
        customer_user = User.objects.create(username="customer_user", is_customer=True)
        customer = Customer.objects.create(user=customer_user)
        cook = Cook.objects.create(user=cook_user)
        cuisine = Cuisine.objects.create()
        dish = Dish.objects.create(cuisine=cuisine, cook=cook)
        dish_review = Dish_Review.objects.create(dish_rating=3, dish=dish, customer=customer)
        self.assertEquals(dish_review.dish_rating, 3) 

    def test_dish_report_flag(self):
        cook_user= User.objects.create(username="cook_user", is_cook=True)
        customer_user = User.objects.create(username="customer_user", is_customer=True)
        customer = Customer.objects.create(user=customer_user)
        cook = Cook.objects.create(user=cook_user)
        cuisine = Cuisine.objects.create()
        dish = Dish.objects.create(cuisine=cuisine, cook=cook)
        dish_review = Dish_Review.objects.create(report_flag=True, dish=dish, customer=customer)
        self.assertEquals(dish_review.report_flag, True) 
      
class AddressCreateFormTest(TestCase):
    def test_missing_street(self):
        form = UserEditForm({'street': "",'town': "Charlottesville", 'state':'VA', 'zipcode':22903})
        self.assertFalse(form.is_valid())
    
    def test_missing_town(self):
        form = UserEditForm({'street': "street",'town': "", 'state':'VA', 'zipcode':22903})
        self.assertFalse(form.is_valid())
    
    def test_missing_state(self):
        form = UserEditForm({'street': "street",'town': "cville", 'state':'', 'zipcode':22903})
        self.assertFalse(form.is_valid())

class CustomerAddressManageTest(TestCase):
    def setUp(self):
        self.client.post(reverse('customercreate'), {'first_name': 'Dave', 'last_name': 'Chapelle', 'street': '221 Baker Street', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22000', 'email': 'dave@dave.com', 'password': 'chapchap', 'phone_number': '8888888888'})
        self.client.login(username='dave@dave.com', password='chapchap')
        self.client.post(reverse('add_address'), {'street': '111 X Street', 'town': 'Harrisonburg', 'state': 'CA', 'zipcode': '33333'})
    def test_current_address_set_upon_customer_creation(self):
        add = Address.objects.get(street_name='221 Baker Street')
        self.assertTrue(add.current_customer_address)
    def test_add_address_pass(self):
        cust = Customer.objects.get(phone_number='8888888888')
        add = Address.objects.get(street_name='111 X Street')
        self.assertEqual(cust, add.customer)
    def test_change_current_address(self):
        add = Address.objects.get(street_name='111 X Street')
        self.client.get(reverse('change_current_address', args=[add.id]))
        add = Address.objects.get(street_name='111 X Street')
        self.assertTrue(add.current_customer_address)
    def test_remove_address(self):
        add = Address.objects.get(street_name='111 X Street')
        self.client.get(reverse('delete_address', args=[add.id]))
        customer = Customer.objects.get(phone_number='8888888888')
        addresses = Address.objects.filter(customer=customer)
        self.assertEqual(len(addresses), 1)
    



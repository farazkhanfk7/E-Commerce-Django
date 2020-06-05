from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .models import Item, Orderitem, Order, Address, Payment
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from .forms import CheckoutForm
from django.conf import settings

import stripe
stripe.api_key = 'sk_test_51GqdShDXThita7nzArJ3jK8wDJFz2gXTMcYkXne6mpmwt17ufDJwST8g2iPCilMIvvkN3EslL8Iri5ii5t5lgSgw00LIT6EFxu'


# Create your views here.
class CheckoutView(View):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'object': order
            }
        except Exception:
            form = CheckoutForm()
            context = {
                'form': form
            }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('street_address')
                country = form.cleaned_data.get('country')
                zipc = form.cleaned_data.get('zipc')
                payment_option = form.cleaned_data.get('payment_option')
                address = Address(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zipc=zipc
                )
                address.save()
                order.address = address
                order.save()
                return redirect('core:payment')
            messages.warning(self.request, "Failed Checkout")
            return redirect('core:payment')
        except ObjectDoesNotExist:
            messages.error(request, "You don't have an active order")
            return redirect('core:order-summary')


class PaymentView(View):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'object': order
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_total() * 100)
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source="token"
            )

            # payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # link payment to order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful")
            return redirect("/")
        except Exception:
            order = Order.objects.get(user=self.request.user, ordered=False)
            amount = int(order.get_total() * 100)
            # payment
            payment = Payment()
            payment.stripe_charge_id = 'dghd45454hjgfdhgf'
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # link payment to order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful")
            return redirect("/")


class HomeView(ListView):
    model = Item
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ordersummary.html', context)
        except Exception:
            return render(self.request, 'ordersummary.html')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = Orderitem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_query = Order.objects.filter(user=request.user, ordered=False)
    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item's quantity was updated")
        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_query = Order.objects.filter(user=request.user, ordered=False)
    # checking if order exists
    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = Orderitem.objects.filter(
                item=item, user=request.user, ordered=False)
            order_item.delete()
            messages.info(request, "This item was removed your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item isn't in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You don't have any active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = Orderitem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_query = Order.objects.filter(user=request.user, ordered=False)
    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity -= 1
            order_item.save()
            messages.info(request, "This item's quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item isn't in your cart")
            return redirect("core:order-summary")
    else:
        messages.info(request, "You don't have any active order")
        return redirect("core:order-summary")


@login_required
def add_single_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = Orderitem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_query = Order.objects.filter(user=request.user, ordered=False)
    if order_query.exists():
        order = order_query[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item's quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item isn't in your cart")
            return redirect("core:order-summary")
    else:
        messages.info(request, "You don't have any active order")
        return redirect("core:order-summary")

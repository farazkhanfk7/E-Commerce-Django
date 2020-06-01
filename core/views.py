from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .models import Item, Orderitem, Order
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages

# Create your views here.


def checkout(request):
    return render(request, "checkout.html")


class HomeView(ListView):
    model = Item
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ordersummary.html', context)
        except ObjectDoesNotExist:
            messages.error(request, "You don't have an active order")
            return redirect('/')


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

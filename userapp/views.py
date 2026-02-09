from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from main.models import Category, Order, OrderItem, Product

from .forms import CheckoutForm

TAX_RATE = Decimal('0.07')


def _get_cart(request) -> dict[str, int]:
	cart = request.session.get('cart', {})
	request.session.setdefault('cart', cart)
	return cart


def _persist_cart(request, cart):
	request.session['cart'] = cart
	request.session.modified = True


def _cart_items(cart):
	product_ids = [int(pk) for pk in cart.keys()]
	products = Product.objects.filter(id__in=product_ids, is_active=True)
	items = []
	for product in products:
		quantity = cart.get(str(product.id), 0)
		if quantity:
			line_total = product.price * quantity
			items.append({'product': product, 'quantity': quantity, 'line_total': line_total})
	return items


def _cart_totals(items):
	subtotal = sum(item['line_total'] for item in items)
	tax = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
	total = subtotal + tax
	return {'subtotal': subtotal, 'tax': tax, 'total': total}


def home(request):
	cart = _get_cart(request)
	categories = Category.objects.all()
	products = Product.objects.filter(is_active=True)

	category_id = request.GET.get('category')
	if category_id:
		products = products.filter(category__id=category_id)

	query = request.GET.get('q')
	if query:
		products = products.filter(name__icontains=query)

	featured = products.filter(featured=True)[:4]

	context = {
		'categories': categories,
		'products': products,
		'featured_products': featured,
		'selected_category': category_id,
		'search_query': query or '',
		'cart_count': sum(cart.values()),
	}
	return render(request, 'userapp/home.html', context)


def product_detail(request, slug):
	product = get_object_or_404(Product, slug=slug, is_active=True)
	related = (
		Product.objects.filter(category=product.category, is_active=True)
		.exclude(pk=product.pk)
		[:4]
	)
	context = {
		'product': product,
		'related_products': related,
	}
	return render(request, 'userapp/product_detail.html', context)


def add_to_cart(request, pk):
	if request.method != 'POST':
		return redirect('userapp:view_cart')
	product = get_object_or_404(Product, pk=pk, is_active=True)
	quantity = max(int(request.POST.get('quantity', 1)), 1)
	cart = _get_cart(request)
	cart[str(product.id)] = cart.get(str(product.id), 0) + quantity
	_persist_cart(request, cart)
	messages.success(request, f"Added {product.name} to your bag.")
	return redirect('userapp:view_cart')


def view_cart(request):
	cart = _get_cart(request)
	items = _cart_items(cart)
	totals = _cart_totals(items)
	return render(
		request,
		'userapp/cart.html',
		{
			'items': items,
			'totals': totals,
		},
	)


def update_cart(request, pk):
	if request.method != 'POST':
		return redirect('userapp:view_cart')
	cart = _get_cart(request)
	product = get_object_or_404(Product, pk=pk)
	quantity = int(request.POST.get('quantity', 1))
	if quantity <= 0:
		cart.pop(str(product.id), None)
	else:
		cart[str(product.id)] = quantity
	_persist_cart(request, cart)
	messages.info(request, 'Cart updated.')
	return redirect('userapp:view_cart')


def remove_from_cart(request, pk):
	if request.method != 'POST':
		return redirect('userapp:view_cart')
	cart = _get_cart(request)
	cart.pop(str(pk), None)
	_persist_cart(request, cart)
	messages.info(request, 'Item removed from cart.')
	return redirect('userapp:view_cart')


def clear_cart(request):
	if request.method == 'POST':
		request.session['cart'] = {}
		request.session.modified = True
		messages.success(request, 'Cart cleared.')
	return redirect('userapp:view_cart')


def checkout(request):
	cart = _get_cart(request)
	items = _cart_items(cart)
	if not items:
		messages.warning(request, 'Your cart is empty. Add a few styles first!')
		return redirect('userapp:home')

	totals = _cart_totals(items)

	if request.method == 'POST':
		form = CheckoutForm(request.POST)
		if form.is_valid():
			order = Order.objects.create(
				customer_name=form.cleaned_data['customer_name'],
				email=form.cleaned_data['email'],
				phone=form.cleaned_data['phone'],
				address=form.cleaned_data['address'],
				city=form.cleaned_data['city'],
				state=form.cleaned_data['state'],
				postal_code=form.cleaned_data['postal_code'],
				notes=form.cleaned_data.get('notes', ''),
				subtotal=totals['subtotal'],
				tax=totals['tax'],
				total=totals['total'],
			)

			for item in items:
				product = item['product']
				OrderItem.objects.create(
					order=order,
					product=product,
					quantity=item['quantity'],
					price=product.price,
				)
				product.stock = max(product.stock - item['quantity'], 0)
				product.save(update_fields=['stock'])

			request.session['cart'] = {}
			request.session.modified = True
			messages.success(request, 'Order placed! We will keep you posted on the delivery.')
			return redirect('userapp:checkout_success', order_id=order.pk)
	else:
		form = CheckoutForm()

	return render(
		request,
		'userapp/checkout.html',
		{
			'items': items,
			'totals': totals,
			'form': form,
		},
	)


def checkout_success(request, order_id):
	order = get_object_or_404(Order.objects.prefetch_related('items__product'), pk=order_id)
	return render(request, 'userapp/checkout_success.html', {'order': order})

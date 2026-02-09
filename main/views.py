from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrderStatusForm, ProductForm
from .models import Order, Product


staff_only = user_passes_test(lambda user: user.is_staff, login_url='/admin/login/')


@staff_only
def dashboard(request):
	revenue_qs = Order.objects.exclude(status=Order.STATUS_CANCELLED)
	total_revenue = revenue_qs.aggregate(total=Sum('total'))['total'] or 0
	pending_orders = Order.objects.filter(status=Order.STATUS_PENDING).count()
	low_stock_products = Product.objects.filter(is_active=True, stock__lt=5)
	featured_products = Product.objects.filter(featured=True, is_active=True)[:6]
	latest_orders = Order.objects.prefetch_related('items__product')[:5]

	context = {
		'total_revenue': total_revenue,
		'pending_orders': pending_orders,
		'low_stock_products': low_stock_products,
		'featured_products': featured_products,
		'latest_orders': latest_orders,
	}
	return render(request, 'main/dashboard.html', context)


@staff_only
def product_create(request):
	if request.method == 'POST':
		form = ProductForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Product created successfully.')
			return redirect('main:dashboard')
	else:
		form = ProductForm()
	return render(request, 'main/product_form.html', {'form': form, 'title': 'Add Product'})


@staff_only
def product_edit(request, pk):
	product = get_object_or_404(Product, pk=pk)
	if request.method == 'POST':
		form = ProductForm(request.POST, instance=product)
		if form.is_valid():
			form.save()
			messages.success(request, 'Product updated successfully.')
			return redirect('main:dashboard')
	else:
		form = ProductForm(instance=product)
	return render(request, 'main/product_form.html', {'form': form, 'title': 'Edit Product'})


@staff_only
def order_list(request):
	status_filter = request.GET.get('status')
	orders = Order.objects.all()
	if status_filter:
		orders = orders.filter(status=status_filter)
	return render(
		request,
		'main/order_list.html',
		{
			'orders': orders,
			'selected_status': status_filter,
			'status_choices': Order.STATUS_CHOICES,
		},
	)


@staff_only
def order_detail(request, pk):
	order = get_object_or_404(Order.objects.prefetch_related('items__product'), pk=pk)
	if request.method == 'POST':
		form = OrderStatusForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			messages.success(request, 'Order updated successfully.')
			return redirect('main:order_detail', pk=order.pk)
	else:
		form = OrderStatusForm(instance=order)

	return render(
		request,
		'main/order_detail.html',
		{
			'order': order,
			'form': form,
		},
	)

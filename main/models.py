from decimal import Decimal

from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Category(TimeStampedModel):
	name = models.CharField(max_length=120, unique=True)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['name']

	def __str__(self) -> str:
		return self.name


class Product(TimeStampedModel):
	category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True, blank=True)
	description = models.TextField()
	price = models.DecimalField(max_digits=8, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	image_url = models.URLField(blank=True)
	is_active = models.BooleanField(default=True)
	featured = models.BooleanField(default=False)
	colorway = models.CharField(max_length=100, blank=True)
	sizes = models.CharField(
		max_length=120,
		blank=True,
		help_text='Comma separated sizes such as XS,S,M,L,XL',
	)

	class Meta:
		ordering = ['name']

	def __str__(self) -> str:
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		else:
			self.slug = slugify(self.slug)
		super().save(*args, **kwargs)

	@property
	def available_sizes(self) -> list[str]:
		return [size.strip() for size in self.sizes.split(',') if size.strip()]


class Order(TimeStampedModel):
	STATUS_PENDING = 'pending'
	STATUS_PROCESSING = 'processing'
	STATUS_SHIPPED = 'shipped'
	STATUS_DELIVERED = 'delivered'
	STATUS_CANCELLED = 'cancelled'

	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_PROCESSING, 'Processing'),
		(STATUS_SHIPPED, 'Shipped'),
		(STATUS_DELIVERED, 'Delivered'),
		(STATUS_CANCELLED, 'Cancelled'),
	]

	customer_name = models.CharField(max_length=150)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	postal_code = models.CharField(max_length=20)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
	tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
	total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return f'Order #{self.pk} - {self.customer_name}'


class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField(default=1)
	price = models.DecimalField(max_digits=8, decimal_places=2)

	class Meta:
		ordering = ['product__name']

	def __str__(self) -> str:
		return f'{self.product.name} x{self.quantity}'

	@property
	def line_total(self) -> Decimal:
		return self.price * self.quantity

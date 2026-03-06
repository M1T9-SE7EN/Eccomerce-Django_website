from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Category, Product, Brand, Order, OrderItem
from .forms import CategoryForm, BrandForm, ProductForm, OrderForm
from django.contrib.admin.models import LogEntry


# --- shopping cart helpers --------------------------------------------------
def _get_cart(request):
    return request.session.setdefault('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def build_cart_items(request):
    cart = _get_cart(request)
    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            continue
        subtotal = product.price * qty
        items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
        total += subtotal
    return items, total


@login_required
def cart_detail(request):
    items, total = build_cart_items(request)
    return render(request, 'shop/cart.html', {'cart_items': items, 'total': total})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)
    messages.success(request, f"Added {product.name} to cart.")
    return redirect('product_list')


@login_required
def cart_remove(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = _get_cart(request)
    items, total = build_cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect('product_list')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price_snapshot=item['product'].price,
                    quantity=item['quantity'],
                    subtotal=item['subtotal'],
                )
                # reduce stock if available
                prod = item['product']
                if prod.stock >= item['quantity']:
                    prod.stock -= item['quantity']
                    prod.save()
            # clear cart
            request.session['cart'] = {}
            messages.success(request, "Order placed successfully!")
            return redirect('order_list')
    else:
        form = OrderForm(initial={
            'full_name': request.user.get_full_name(),
            'email': request.user.email
        })
    return render(request, 'shop/checkout.html', {'form': form, 'cart_items': items, 'total': total})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, ProductImage
from .forms import ProductImageForm


@staff_member_required
def product_image_list(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    images = product.images.all()

    return render(request, 'product_images/image_list.html', {
        'product': product,
        'images': images
    })


@staff_member_required
def product_image_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_obj = form.save(commit=False)
            image_obj.product = product

            # Ensure only one main image
            if image_obj.is_main:
                ProductImage.objects.filter(
                    product=product,
                    is_main=True
                ).update(is_main=False)

            image_obj.save()
            return redirect('product_image_list', product_id=product.id)
    else:
        form = ProductImageForm()

    return render(request, 'product_images/image_form.html', {
        'form': form,
        'product': product
    })

@staff_member_required
def product_image_update(request, pk):
    image_obj = get_object_or_404(ProductImage, pk=pk)
    product = image_obj.product

    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES, instance=image_obj)
        if form.is_valid():

            if form.cleaned_data.get('is_main'):
                ProductImage.objects.filter(
                    product=product,
                    is_main=True
                ).exclude(id=image_obj.id).update(is_main=False)

            form.save()
            return redirect('product_image_list', product_id=product.id)
    else:
        form = ProductImageForm(instance=image_obj)

    return render(request, 'product_images/image_form.html', {
        'form': form,
        'product': product
    })


@staff_member_required
def product_image_delete(request, pk):
    image_obj = get_object_or_404(ProductImage, pk=pk)
    product_id = image_obj.product.id

    image_obj.delete()
    return redirect('product_image_list', product_id=product_id)



@staff_member_required
def admin_dashboard(request):
    # Gathering some sample metrics
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10)
    total_users = User.objects.count()
    total_brands = Brand.objects.count()

    # include products for the products tab
    products = Product.objects.filter(is_active=True)

    # data for categories/brands/users tabs
    categories = Category.objects.all()
    brands = Brand.objects.all()
    category_form = CategoryForm()
    brand_form = BrandForm()

    # include users for users tab (import form inside to avoid circular imports)
    from django.contrib.auth.models import User as AuthUser
    from users.forms import AdminUserCreateForm
    users = AuthUser.objects.order_by('id')
    user_form = AdminUserCreateForm()

    context = {
        'total_products': total_products,
        'total_brands': total_brands,
        'low_stock_count': low_stock_products.count(),
        'low_stock_list': low_stock_products[:5], # Show first 5 items
        'total_users': total_users,
        'recent_logs': LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:20],
        'products': products,
        'categories': categories,
        'brands': brands,
        'category_form': category_form,
        'brand_form': brand_form,
        'users': users,
        'user_form': user_form,
    }
    return render(request, 'Dashboard/admin_dashboard.html', context)

@login_required
def login_success(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    else:
        return redirect('product_list')
    



@staff_member_required
def category_list_create(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # return to dashboard brands tab
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#categories')
    else:
        form = CategoryForm()

    return render(request, 'category/category_list.html', {
        'categories': categories,
        'form': form
    })

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'category/category_form.html', {
        'form': form,
        'category': category,
    })

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    from django.urls import reverse
    return redirect(reverse('admin_dashboard') + '#categories')

# BRAND CRUD

@staff_member_required
def brand_list_create(request):
    brands = Brand.objects.all()

    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#brands')
    else:
        form = BrandForm()

    return render(request, 'brand/brand_list.html', {
        'brands': brands,
        'form': form
    })

@staff_member_required
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#brands')
    else:
        form = BrandForm(instance=brand)

    return render(request, 'brand/brand_edit.html', {
        'form': form
    })

@staff_member_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    from django.urls import reverse
    return redirect(reverse('admin_dashboard') + '#brands')

def product_list(request):
    products = Product.objects.filter(is_active=True)
    # render customer-facing product list (includes add-to-cart button)
    return render(request, 'shop/product_list.html', {
        'products': products
    })

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#products')
    else:
        form = ProductForm()

    return render(request, 'product/product_form.html', {
        'form': form
    })

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            from django.urls import reverse
            return redirect(reverse('admin_dashboard') + '#products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'product/product_form.html', {
        'form': form
    })

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    from django.urls import reverse
    return redirect(reverse('admin_dashboard') + '#products')











# def product_list(request):
#     products = Product.objects.filter(available=True)
#     return render(request, 'shop/product_list.html', {'products': products})


# @staff_member_required
# def category_create(request):
#     if request.method == "POST":
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Category created successfully.")
#             return redirect('category_list')
#     else:
#         form = CategoryForm()

#     return render(request, 'Category/category_form.html', {
#         'form': form,
#         'title': 'Create Category'
#     })

# @staff_member_required
# def category_list(request):
#     categories = Category.objects.all()
#     return render(request, 'Category/category_list.html', {
#         'categories': categories
#     })

# @staff_member_required
# def category_update(request, pk):
#     category = get_object_or_404(Category, pk=pk)

#     if request.method == "POST":
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Category updated successfully.")
#             return redirect('category_list')
#     else:
#         form = CategoryForm(instance=category)

#     return render(request, 'Category/category_form.html', {
#         'form': form,
#         'title': 'Update Category'
#     })


# @staff_member_required
# def category_delete(request, pk):
#     category = get_object_or_404(Category, pk=pk)

#     if request.method == "POST":
#         category.delete()
#         messages.success(request, "Category deleted successfully.")
#         return redirect('category_list')

#     return render(request, 'Category/category_confirm_delete.html', {
#         'category': category
#     })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.models import User
from .models import Product, Transfer, Store, Inventory
from .forms import CreateTransferForm
from .services import *
from django.contrib import messages


def home(request):
    if request.user.is_authenticated:
        return redirect('stores')
    else:
        return render(request, 'home.html')

@login_required
def stores(request):
    user_id = request.user.id
    if User.objects.get(id=user_id).is_staff:
        stores = Store.objects.all().order_by('name')
        
        return render(request, 'stores.html', {'stores': stores})
    else:
        store_id = Store.objects.get(head_of_store=user_id).id

        return redirect(f'/stores_detail/{store_id}')

    
@login_required
def stores_detail(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    search_result = request.GET.get('searchProduct')
    context = {'search_result' : search_result,
               'store_name' : store.name,
               'inventory' : []
               }
    if search_result:
        products = Product.objects.filter(name__icontains=search_result).order_by('name')
    else:
        products = Product.objects.order_by('name')
    for product in products:
        try:
            item = Inventory.objects.get(product=product, store=store)
            product_id = Product.objects.get(name=product.name).id
            quantity = item.quantity
            minimum_quantity = item.minimum_quantity
            if minimum_quantity != 0 and minimum_quantity/quantity < 0.8:
                ready_to_order = True
            else:
                ready_to_order = False
            request.session['store_id'] = store.id
            context['inventory'].append({'product_id': product_id, 'product_name': product.name, 'quantity': quantity, 'minimum_quantity': minimum_quantity, 'ready_to_order': ready_to_order})
        except Exception as e:
            print(e)
    return render(request, 'stores_detail.html',  context)

@login_required
def product_detail(request, product_id):
    store = request.session.get('store_id', {})
    product_obj = Product.objects.get(id=product_id)
    product_inventory = get_object_or_404(Inventory, product=product_obj, store=store)
    store_name = product_inventory.store
    transfers = Transfer.objects.filter(product=product_obj).order_by('-date')
    context = {'product_inventory': product_inventory,'product_id': product_obj.id , 'transfers': transfers, 'store_name': store_name}
    
    return render(request, 'product_detail.html', context)

@login_required
def create_transfer(request, product_id):
    product_obj = Product.objects.get(id=product_id)
    store = request.session.get('store_id', {})
    product_inventory = get_object_or_404(Inventory, product=product_obj, store=store)
    store_name = product_inventory.store
    form = CreateTransferForm(request.POST)
    if form.is_valid():
        transfer = form.save(commit=False)
        transfer.user = request.user
        transfer.store = store_name
        transfer.product = product_obj
        transfer.starting_quantity = product_inventory.quantity
        transfer.save()
        quantity = product_inventory.quantity + transfer.difference
        product_inventory.quantity = quantity
        product_inventory.save()
        return redirect(f'../../product_detail/{product_obj.id}')
    else:
        form = CreateTransferForm()
        
    return render(request, 'create_transfer.html', {'product': product_obj, 'store_name': store_name, 'form': form})

@login_required
def upload_sales(request):
    user_id = request.user.id
    user_role = request.user.is_staff
    if user_role:
        stores_query_set = Store.objects.all()
        stores = [obj.name for obj in stores_query_set]
    else:
        default_store = Store.objects.filter(head_of_store=user_id).first()
        stores = [default_store]

    context = {'user_id' : user_id,
               'stores' : stores,
               }

    if request.method == 'POST':
        try:
            sales_file = request.FILES['sales_file']
            if str(sales_file).endswith('.csv'):
                store = request.POST.get('store')
                sales_data = get_sales_data_from_csv(sales_file)
                sales_changes = get_sales_changes(sales_data, store)
                permission = get_permission_sales(sales_changes)
                
                context = {'store' : store,
                            'sales_changes' : sales_changes,
                            'permission' : permission
                        }
                request.session['sales_report'] = context
                
                return redirect('report_sales')

        except:
            messages.error(request, 'Необходимо загрузить файл')
        else:
            messages.error(request, 'Не правильный формат файла!')

    
    return render(request, 'upload_sales.html', context)

@login_required
def report_sales(request):
    context = request.session.get('sales_report', {})
    if request.method == 'POST':
        user = request.user
        message = write_sales_to_db(context, user)
        return render(request, 'stores.html', {'message': message})


    return render(request, 'report_sales.html', context)

@login_required
def upload_receipt(request):
    user_id = request.user.id
    user_role = request.user.is_staff
    if user_role:
        stores_query_set = Store.objects.all()
        stores = [obj.name for obj in stores_query_set]
    else:
        default_store = Store.objects.filter(head_of_store=user_id).first().name
        stores = [default_store]

    context = {'user_id' : user_id,
               'stores' : stores,
               }
    try:
        if request.method == 'POST':
            receipt_file = request.FILES['receipt_file']


        if str(receipt_file).endswith('.xlsx'):
            store = request.POST.get('store')
            receipt_data = get_receipt_data_from_xlsx(receipt_file)
            receipt_changes = get_receipt_changes(receipt_data, store)
            permission = get_permission_receipt(receipt_changes)
            context = {'store' : store,
                        'receipt_changes' : receipt_changes,
                        'permission' : permission
                    }
            request.session['receipt_report'] = context
            
            return redirect('report_receipt')
        else:
            messages.error(request, 'Не правильный формат файла!')
            
    except:
        messages.error(request, 'Необходимо загрузить файл')

    return render(request, 'upload_receipt.html', context)

@login_required
def report_receipt(request):
    context = request.session.get('receipt_report', {})
    if request.method == 'POST':
        user = request.user
        message = write_receipt_to_db(context, user)

        return render(request, 'stores.html', {'message': message})


    return render(request, 'report_receipt.html', context)

@user_passes_test(lambda user: user.is_staff, login_url='/login/')
def upload_stock_products(request):
    user_id = request.user.id
    stores_query_set = Store.objects.all()
    stores = [obj.name for obj in stores_query_set]
    context = {'user_id' : user_id,
               'stores' : stores,
               }
    
    if request.method == 'POST':
        try:
            stock_products_file = request.FILES['stock_products_file']
            store = request.POST.get('store')
            if str(stock_products_file).endswith('.xlsx'):
                stock_products_data = get_stock_products_data(stock_products_file)
                if not stock_products_data:
                    permission = 404
                else:
                    permission = get_permission_stock_products(stock_products_data, store)
                context = {'store' : store,
                            'stock_products_data' : stock_products_data,
                            'permission' : permission
                        }
                request.session['stock_products_report'] = context
            
                return redirect('report_stock_products')
            else:
                messages.error(request, 'Не правильный формат файла!')
        except:
            messages.error(request, 'Необходимо загрузить файл')

    return render(request, 'upload_stock_products.html', context)

@user_passes_test(lambda user: user.is_staff, login_url='/login/')
def report_stock_products(request):
    context = request.session.get('stock_products_report', {})
    if request.method == 'POST':
        user = request.user
        message = write_stock_products_to_db(context, user)
        
        return render(request, 'stores.html', {'message': message})


    return render(request, 'report_stock_products.html', context)

def compare_products(request):
    user_id = request.user.id
    stores_query_set = Store.objects.all()
    stores = [obj.name for obj in stores_query_set]
    context = {'user_id' : user_id,
               'stores' : stores,
               }
    
    if request.method == 'POST':
        try:
            stock_products_file = request.FILES['stock_products_file']
            store = request.POST.get('store')
            if str(stock_products_file).endswith('.xlsx'):
                stock_products_data = get_stock_products_data(stock_products_file)
                if not stock_products_data:
                    permission = 404
                else:
                    permission = 200
                context = {'store' : store,
                            'stock_products_data' : stock_products_data,
                            'permission' : permission
                        }
                request.session['compare_products'] = context
            
                return redirect('report_compare_products')
            else:
                messages.error(request, 'Не правильный формат файла!')
        except:
            messages.error(request, 'Необходимо загрузить файл')

    return render(request, 'compare_products.html', context)

def report_compare_products(request):
    context = request.session.get('compare_products', {})
    diff_products = compare_products_db(context)

    return render(request, 'report_compare_products.html', {'diff_products':diff_products})

import csv
from .models import Product, Store, Transfer, Inventory
from django.db.models import F, Count
import pandas as pd

def get_sales_data_from_csv(sales_file):
    sales_data = {}
    sales_file_str = sales_file.file.read().decode('utf-8')
    reader = csv.reader(sales_file_str.splitlines(), delimiter=';')
    for row in reader:
        if reader.line_num > 8:
            product_name = row[1]
            expense_amount = int(row[4])
            sales_data[product_name] = expense_amount
            
    return sales_data

def get_sales_changes(sales_data, store):
    sales_data_for_preview = []
    store_id = Store.objects.filter(name=store).first().id
    for key, value in sales_data.items():
        product = Inventory.objects.filter(product__name=key, store__id=store_id).first()
        if product != None:
            amount_in_db = int(product.quantity)
            sales_data_for_preview.append({'product_name' : key,
                                       'amount_in_db': amount_in_db,
                                       'expanse': value,
                                       'result': amount_in_db - value
                                       })
        else:
            sales_data_for_preview.append({'product_name': key,
                                           'amount_in_db': 0,
                                           'expanse': value,
                                           'result': None
                                           })

    return sales_data_for_preview

def get_permission_sales(sales_changes):
    for sales in sales_changes:
        if sales['result'] == None:
            permission_sales = 403
            break
        elif sales['result'] < 0:
            permission_sales = 400
            break
        else:
            permission_sales = 200
        
    return permission_sales

def write_sales_to_db(context, user):
    store_name = context['store']
    store = Store.objects.get(name=store_name)
    sales_data = context['sales_changes']
    change_product_amount(store, sales_data)
    add_transactions(store, sales_data, user)
    message = f'Изменений записано -  {len(sales_data)} шт. для точки "{store_name}"'
    
    return message
    
def change_product_amount(store, sales_data):
    store_id = store
    for sale_data in sales_data:
        product_name = sale_data['product_name']
        product_id = Product.objects.filter(name=product_name).first().id
        expanse = sale_data['expanse']
        product = Inventory.objects.get(product=product_id, store=store_id)
        product.quantity = F('quantity') - expanse
        product.save()

def add_transactions(store, sales_data, user):
    comment = f'Добавленно из файла продаж {user.last_name} {user.first_name}'
    for sale_data in sales_data:
        product_name = sale_data['product_name']
        product_id = Product.objects.filter(name=product_name).first()
        expanse = -int(sale_data['expanse'])
        starting_quantity = int(sale_data['amount_in_db'])
        transaction = Transfer.objects.create(
        store=store,
        product=product_id,
        starting_quantity=starting_quantity,
        difference=expanse,
        user=user,
        comment=comment
        )
        transaction.save()

def get_receipt_data_from_xlsx(receipt_file):
    df = pd.read_excel(receipt_file, skiprows=10, skipfooter=8, header=None)
    receipt_data = {}
    for index, row in df.iterrows():
        if not pd.isna(row[3]) and not pd.isna(row[13]):
            product_name = row[3][:-2]
            quantity = int(row[13])
            receipt_data[product_name] = quantity

    return receipt_data

def get_receipt_changes(receipt_data, store):
    receipt_data_for_preview = []
    store_id = Store.objects.filter(name=store).first().id
    for key, value in receipt_data.items():
        product = Inventory.objects.filter(product__name=key, store__id=store_id).first()
        if product != None:
            amount_in_db = int(product.quantity)
            receipt_data_for_preview.append({'product_name' : key,
                                       'amount_in_db': amount_in_db,
                                       'income': value,
                                       'result': amount_in_db + value
                                       })
        else:
            receipt_data_for_preview.append({'product_name': key,
                                           'amount_in_db': 0,
                                           'income': value,
                                           'result': value,
                                           })

    return receipt_data_for_preview

def get_permission_receipt(receipt_changes):
    if receipt_changes == []:
        permission_receipt = 404
    else:
        for receipt in receipt_changes:
            if receipt['income'] == receipt['result']:
                permission_receipt = 204
                break
            else:
                permission_receipt = 200
        
    return permission_receipt

def write_receipt_to_db(context, user):
    store_name = context['store']
    store = Store.objects.get(name=store_name)
    receipt_data = context['receipt_changes']
    change_product_amount_receipt(store, receipt_data)
    add_receipt_transactions(store, receipt_data, user)
    message = f'Изменений записано -  {len(receipt_data)} шт. для точки "{store_name}"'
    
    return message

def change_product_amount_receipt(store, receipt_data):
    store_id = store
    for receipt in receipt_data:
        product_name = receipt['product_name']
        income = receipt['income']
        try:
            product = Inventory.objects.select_related('product').get(product__name=product_name, store=store_id)
            product.quantity = F('quantity') + income
        except Inventory.DoesNotExist:
            product = Inventory(product=Product.objects.create(name=product_name), quantity=income, store=store_id)
        product.save()
        
def add_receipt_transactions(store, receipt_data, user):
    comment = f'Добавленно из файла прихода {user.last_name} {user.first_name}'
    for receipt in receipt_data:
        product_name = receipt['product_name']
        product_id = Product.objects.filter(name=product_name).first()
        starting_quantity = receipt['amount_in_db']
        income = int(receipt['income'])
        transaction = Transfer.objects.create(
        store=store,
        product=product_id,
        starting_quantity=starting_quantity,
        difference=income,
        user=user,
        comment=comment
        )
        transaction.save()

def get_stock_products_data(stock_products_file):
    df = pd.read_excel(stock_products_file, skiprows=10, header=None, skipfooter=8)
    stock_products_data = []

    for index, row in df.iterrows():
        if not pd.isna(row[5]) and not pd.isna(row[16]):
            product_name = row[5][:-2]
            amount = int(row[16])
            stock_products_data.append({'product_name': product_name,
                                     'amount': amount
            })

    return stock_products_data

def get_permission_stock_products(stock_products_data, store):
    store_obj = Store.objects.get(name=store)
    inventory_count = Inventory.objects.filter(store=store_obj).count()
    if inventory_count > 0:
        permission_stock_products = 204
    else:
        permission_stock_products = 200
            
    return permission_stock_products

def write_stock_products_to_db(context, user):
    store_name = context['store']
    store = Store.objects.get(name=store_name)
    stock_products_data = context['stock_products_data']
    add_product_amount_stock(store, stock_products_data)
    add_product_stock_transactions(store, stock_products_data, user)
    message = f'Изменений записано -  {len(stock_products_data)} шт. для точки "{store_name}"'
    
    return message

def add_product_amount_stock(store, stock_products_data):
    store_obj = Store.objects.filter(name=store).first()
    for product_stock in stock_products_data:
        product_name = product_stock['product_name']
        product_quantity = int(product_stock['amount'])
        if product_quantity < 0:
            minimum_product_quantity = 0
        else:
            minimum_product_quantity = product_quantity
        product_obj, created = Product.objects.get_or_create(name=product_name)
        inventory_obj, created = Inventory.objects.get_or_create(
            product=product_obj,
            store=store_obj,
            quantity = product_quantity,
            minimum_quantity=minimum_product_quantity
        )

        
def add_product_stock_transactions(store, stock_products_data, user):
    comment = f'Добавленно из файла с начальными остатками товара {user.last_name} {user.first_name}'
    for product_stock in stock_products_data:
        product_name = product_stock['product_name']
        product_obj = Product.objects.filter(name=product_name).first()
        income = int(product_stock['amount'])
        transfer = Transfer.objects.create(
        store=store,
        product=product_obj,
        starting_quantity=0,
        difference=income,
        user=user,
        comment=comment
        )
        transfer.save()

def compare_products_db(context):
    diff_products = []
    store_name = context['store']
    store = Store.objects.get(name=store_name)
    stock_products_data = context['stock_products_data']
    for product in stock_products_data:
        product_name = product['product_name']
        product_obj = Product.objects.get(name=product_name)
        product_amount = product['amount']
        try:
            amount_in_db = Inventory.objects.filter(product=product_obj, store=store).first().quantity
            if amount_in_db != product_amount:
                diff_products.append({'product_name': product_name,
                               'reason': 'Различие в количестве',
                               'product_amount_db': amount_in_db,
                               'product_amount_file': product_amount
                })
        except Exception as e:
            print(e)
            diff_products.append({'product_name': product_name,
                               'reason': 'Нет товара в базе',
                               'product_amount_db': 0,
                               'product_amount_file': product_amount
                })

    
    return diff_products

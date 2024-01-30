from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_pos.wsgi import *
from django_pos import settings
from django.template.loader import get_template
from customers.models import Customer
from products.models import Product
from weasyprint import HTML, CSS
from .models import Sale, SaleDetail
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET

def get_customers_ajax(request):
    customers = Customer.objects.all()
    data = [{'value': customer.id, 'label': customer.first_name} for customer in customers]
    return JsonResponse(data, safe=False)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def SalesListView(request):
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.all()
    }
    return render(request, "sales/sales.html", context=context)


@login_required(login_url="/accounts/login/")
def SalesAddView(request):
    hold_sales = Sale.objects.filter(payment_status='hold')
    context = {
        "active_icon": "sales",
        "customers": [c.to_select2() for c in Customer.objects.all()],
        "hold_sales":hold_sales
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            # Save the POST arguements
            data = json.load(request)
            customer = data.get('customer', '')
            dicount = data.get('discount', '')
            payment_status = data.get('payment_status', '')
            if customer == 'walking_customer':
                customer = None
            else:
                customer = Customer.objects.get(id=int(customer)) 
            if dicount == '':
                dicount = 0
            else:
                dicount = dicount           
            sale_attributes = {
                "customer": customer,
                "discount": dicount,
                "grand_total": float(data["grand_total"]),
                "payment_status":payment_status,                
                "amount_payed": float(data["amount_payed"]),
                "sub_total": float(data["sub_total"]),
                "amount_change": float(data["amount_change"]),
            }
            try:
                # Create the sale
                new_sale = Sale.objects.create(**sale_attributes)
                new_sale.save()
                # Create the sale details
                products = data["products"]
                for product in products:
                    detail_attributes = {
                        "sale": Sale.objects.get(id=new_sale.id),
                        "product": Product.objects.get(id=int(product["id"])),
                        "sell_price": product["sell_price"],
                        "quantity": product["quantity"],
                        "total_detail": product["total_product"]
                    }
                    sale_detail_new = SaleDetail.objects.create(
                        **detail_attributes)
                    sale_detail_new.save()
                messages.success(
                    request, 'Sale created succesfully!', extra_tags="success")

            except Exception as e:
                messages.success(
                    request, 'There was an error during the creation!', extra_tags="danger")

        return redirect('sales:sales_list')

    return render(request, "sales/sales_add.html", context=context)


@login_required(login_url="/accounts/login/")
def SalesDetailsView(request, sale_id):
    """
    Args:
        sale_id: ID of the sale to view
    """
    try:
        # Get tthe sale
        sale = Sale.objects.get(id=sale_id)

        # Get the sale details
        details = SaleDetail.objects.filter(sale=sale)

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "sales/sales_details.html", context=context)
    except Exception as e:
        messages.success(
            request, 'There was an error getting the sale!', extra_tags="danger")
        print(e)
        return redirect('sales:sales_list')


@login_required(login_url="/accounts/login/")
def ReceiptPDFView(request, sale_id):
    """
    Args:
        sale_id: ID of the sale to view the receipt
    """
    # Get tthe sale
    sale = Sale.objects.get(id=sale_id)

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    template = get_template("sales/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details
    }
    html_template = template.render(context)

    # CSS Boostrap
    css_url = os.path.join(
        settings.BASE_DIR, 'static/css/receipt_pdf/bootstrap.min.css')

    # Create the pdf
    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])

    return HttpResponse(pdf, content_type="application/pdf")

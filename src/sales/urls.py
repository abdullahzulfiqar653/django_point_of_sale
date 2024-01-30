from django.urls import path

from . import views
from .views import get_customers_ajax
app_name = "sales"
urlpatterns = [
    # List sales
     path('get_customers_ajax', views.get_customers_ajax, name='get_customers_ajax'),
    path('', views.SalesListView, name='sales_list'),
    # Add sale
    path('add', views.SalesAddView, name='sales_add'),
    # Details sale
    path('details/<str:sale_id>',
         views.SalesDetailsView, name='sales_details'),
    # Sale receipt PDF
    path("pdf/<str:sale_id>",
         views.ReceiptPDFView, name="sales_receipt_pdf"),
]

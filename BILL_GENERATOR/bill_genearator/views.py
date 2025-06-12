from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import InvoiceForm
from .models import Invoice, InvoiceItem
from datetime import datetime

"""def invoice_form(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)

        if form.is_valid():
            print("Form is valid")  # Debugging line
            try:
                with transaction.atomic():  # Ensures atomicity
                    # Save the invoice
                    invoice = form.save()

                    # Extract item data from POST request
                    item_names = request.POST.getlist('item_name')
                    hsn_codes = request.POST.getlist('hsn_code')
                    gst_percentages = request.POST.getlist('gst_percentage')
                    uoms = request.POST.getlist('uom')
                    quantities = request.POST.getlist('quantity')
                    rates = request.POST.getlist('rate')

                    # Validate item data
                    if not item_names or not any(item_names):
                        raise ValueError("At least one item must be provided.")

                    for i in range(len(item_names)):
                        # Ensure all fields are properly filled
                        if not all([item_names[i], hsn_codes[i], gst_percentages[i], uoms[i], quantities[i], rates[i]]):
                            raise ValueError(f"Missing data for item {i + 1}.")

                        # Save InvoiceItems
                        InvoiceItem.objects.create(
                            invoice=invoice,
                            item_name=item_names[i],
                            hsn_code=hsn_codes[i],
                            gst_percentage=float(gst_percentages[i]),
                            uom=uoms[i],
                            quantity=int(quantities[i]),
                            rate=float(rates[i]),
                        )

                    messages.success(request, "Invoice and items saved successfully!")
                    return redirect('invoice_list')
            except ValueError as ve:
                messages.error(request, f"Error: {ve}")
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
        else:
            print("Form is not valid:", form.errors)  # Debugging line
            messages.error(request, "Invalid form data. Please correct the errors below.")
    else:
        form = InvoiceForm()

    return render(request, 'invoice_form.html', {'form': form})"""


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm
import uuid

def invoice_form(request):
    print("✅ View accessed")

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            print("✅ Form is valid")
            try:
                with transaction.atomic():
                    invoice = form.save(commit=False)

                    # 🔐 Generate unique code if missing
                    if not invoice.code:
                        invoice.code = str(uuid.uuid4())[:8]

                    # ✅ Save Terms & Conditions (newly added logic)
                    invoice.terms_conditions = request.POST.get('terms_conditions', '')

                    invoice.save()

                    # 🔄 Fetch all invoice items from POST data
                    item_names = request.POST.getlist('item_name')
                    hsn_codes = request.POST.getlist('hsn_code')
                    gst_percentages = request.POST.getlist('gst_percentage')
                    uoms = request.POST.getlist('uom')
                    quantities = request.POST.getlist('quantity')
                    rates = request.POST.getlist('rate')

                    if not item_names or not any(item_names):
                        raise ValueError("At least one item must be provided.")

                    supplier_state_code = invoice.gstn[:2]
                    buyer_state_code = invoice.buyer_gstn[:2]

                    for i in range(len(item_names)):
                        if not all([item_names[i], hsn_codes[i], gst_percentages[i], uoms[i], quantities[i], rates[i]]):
                            raise ValueError(f"Missing data for item {i + 1}.")

                        taxable_amount = float(rates[i]) * int(quantities[i])
                        gst_percentage = float(gst_percentages[i])

                        if supplier_state_code == buyer_state_code:
                            cgst = sgst = (gst_percentage / 2) * taxable_amount / 100
                            ugst = 0
                        else:
                            cgst = sgst = 0
                            ugst = gst_percentage * taxable_amount / 100

                        total = taxable_amount + cgst + sgst + ugst

                        InvoiceItem.objects.create(
                            invoice=invoice,
                            item_name=item_names[i],
                            hsn_code=hsn_codes[i],
                            gst_percentage=gst_percentage,
                            uom=uoms[i],
                            quantity=int(quantities[i]),
                            rate=float(rates[i]),
                            taxable_amount=taxable_amount,
                            cgst=cgst,
                            sgst=sgst,
                            ugst=ugst,
                            total=total,
                        )

                    messages.success(request, "Invoice and items saved successfully!")
                    return redirect('invoice_list')

            except ValueError as ve:
                messages.error(request, f"Error: {ve}")
            except Exception as e:
                messages.error(request, f"🔥 Unexpected error: {e}")
                print(f"🔥 Unexpected error: {e}")
        else:
            print(form.errors)
            messages.error(request, "Invalid form data. Please correct the errors below.")
    else:
        form = InvoiceForm()

    latest_invoice = Invoice.objects.order_by('-id').first()

    # 🔄 Send Terms & Conditions to template (if available)
    context = {
        'form': form,
        'invoice': latest_invoice,
    }

    return render(request, 'invoice_form.html', context) 



def invoice_list(request):
    invoices = Invoice.objects.prefetch_related('invoice_items').all()
    for invoice in invoices:
        # Calculate total amount for the invoice
        total_amount = sum(item.total if item.total is not None else 0 for item in invoice.invoice_items.all())  # Sum of all item totals, fallback to 0 if None
        invoice.total_amount = total_amount  # Add total_amount as an attribute for easy access
    return render(request, 'invoice_list.html', {'invoices': invoices})

from django.shortcuts import render, get_object_or_404
from .models import Invoice

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = invoice.invoice_items.all()  # Fetch related items
    return render(request, 'invoice_detail.html', {'invoice': invoice, 'items': items})


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Invoice, InvoiceItem
from .forms import InvoiceItemForm  # Assuming you have a form for InvoiceItem

def edit_items(request, invoice_id):
    # 🔄 Fetch the Invoice and its Items
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_items = invoice.invoice_items.all()
    
    # ✅ Fetch the Terms & Conditions from the database
    terms_conditions = invoice.terms_conditions  

    if request.method == "POST":
        # 🔄 Update Terms & Conditions
        invoice.terms_conditions = request.POST.get('terms_conditions', '')
        invoice.save()

        # 🔄 Update existing invoice items
        for item in invoice_items:
            item_name = request.POST.get(f'item_name_{item.id}', item.item_name)
            hsn_code = request.POST.get(f'hsn_code_{item.id}', item.hsn_code)
            gst_percentage = request.POST.get(f'gst_percentage_{item.id}', item.gst_percentage)
            uom = request.POST.get(f'uom_{item.id}', item.uom)
            quantity = float(request.POST.get(f'quantity_{item.id}', item.quantity))
            rate = float(request.POST.get(f'rate_{item.id}', item.rate))

            # ✅ Calculate new totals
            taxable_amount = quantity * rate
            cgst = (taxable_amount * float(gst_percentage) / 100) / 2
            sgst = cgst
            ugst = 0  # Update based on GST rules if needed
            total = taxable_amount + cgst + sgst + ugst

            # ✅ Save updated values
            item.item_name = item_name
            item.hsn_code = hsn_code
            item.gst_percentage = gst_percentage
            item.uom = uom
            item.quantity = quantity
            item.rate = rate
            item.taxable_amount = taxable_amount
            item.cgst = cgst
            item.sgst = sgst
            item.ugst = ugst
            item.total = total
            item.save()

        # 🔄 Recalculate the total invoice amount
        invoice.total_amount = invoice.invoice_items.aggregate(Sum('total'))['total__sum'] or 0
        invoice.save()

        return redirect('invoice_list')  # Redirect to invoice list after update

    # 🔄 Send the Terms & Conditions to the template
    return render(request, 'edit_items.html', {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'terms_conditions': terms_conditions
    })



from django.db.models import Sum
from django.db.models import DecimalField

def invoice_list(request):
    invoices = Invoice.objects.annotate(
        total_amount=Sum('invoice_items__total', output_field=DecimalField())
    ).order_by('-invoice_date')

    return render(request, 'invoice_list.html', {'invoices': invoices})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm

def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()

            # Handling invoice items update
            item_ids = request.POST.getlist('item_id')
            item_names = request.POST.getlist('item_name')
            hsn_codes = request.POST.getlist('hsn_code')
            gst_percentages = request.POST.getlist('gst_percentage')
            uoms = request.POST.getlist('uom')
            quantities = request.POST.getlist('quantity')
            rates = request.POST.getlist('rate')

            removed_items = request.POST.get("deleted_items", "").split(",")
            removed_items = [int(item_id) for item_id in removed_items if item_id.isdigit()]
            InvoiceItem.objects.filter(id__in=removed_items).delete()

            for i in range(len(item_names)):
                item_id = item_ids[i] if i < len(item_ids) and item_ids[i].strip() else None
                quantity = int(quantities[i]) if quantities[i].strip() else 0
                rate = float(rates[i]) if rates[i].strip() else 0
                gst_percentage = float(gst_percentages[i]) if gst_percentages[i].strip() else 0

                if item_id:
                    item = InvoiceItem.objects.get(id=item_id)
                    item.item_name = item_names[i]
                    item.hsn_code = hsn_codes[i]
                    item.gst_percentage = gst_percentage
                    item.uom = uoms[i]
                    item.quantity = quantity
                    item.rate = rate
                    item.save()
                else:
                    item = InvoiceItem(
                        invoice=invoice,
                        item_name=item_names[i],
                        hsn_code=hsn_codes[i],
                        gst_percentage=gst_percentage,
                        uom=uoms[i],
                        quantity=quantity,
                        rate=rate
                    )
                    item.save()

            return redirect('invoice_list')
        else:
            print("Form is not valid:", form.errors)  # 🔍 Form is defined here — safe to print

    else:
        form = InvoiceForm(instance=invoice)

    return render(request, 'edit_items.html', {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'form': form
    })





from django.http import JsonResponse
from .models import Invoice
from django.views.decorators.csrf import csrf_exempt


def fetch_supplier_details(request):
    query = request.GET.get('q', '')
    data = []

    if query:
        # Get distinct matching supplier names
        suppliers = Invoice.objects.filter(name_of_supplier__icontains=query).values(
            'name_of_supplier', 'state', 'gstn', 'pan', 'address'
        ).distinct()

        for supplier in suppliers:
            data.append(supplier)

    return JsonResponse(data, safe=False)


def fetch_buyer_details(request):
    query = request.GET.get('q', '')
    data = []

    if query:
        buyers = Invoice.objects.filter(name_of_buyer__icontains=query).values(
            'name_of_buyer', 'buyer_state', 'buyer_gstn', 'buyer_pan', 'buyer_address'
        ).distinct()

        for buyer in buyers:
            data.append(buyer)

    return JsonResponse(data, safe=False)


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from decimal import Decimal
from num2words import num2words  # Add this
from .models import Invoice

def download_invoice_pdf(request, invoice_id):
    # Get the invoice and related invoice items
    invoice = Invoice.objects.get(id=invoice_id)
    invoice_items = invoice.invoice_items.all()

    # Calculate totals for each item
    total_taxable = sum(item.taxable_amount for item in invoice_items)
    total_cgst = sum(item.cgst for item in invoice_items)
    total_sgst = sum(item.sgst for item in invoice_items)
    total_ugst = sum(item.ugst for item in invoice_items)
    total_amount = sum(item.total for item in invoice_items)

    # Group the invoice items by gst_percentage
    gst_totals = {}
    for item in invoice_items:
        gst_rate = item.gst_percentage
        if gst_rate not in gst_totals:
            gst_totals[gst_rate] = {
                'taxable_value': Decimal(0),
                'cgst': Decimal(0),
                'sgst': Decimal(0),
                'ugst': Decimal(0),
                'total': Decimal(0)
            }
        gst_totals[gst_rate]['taxable_value'] += item.taxable_amount
        gst_totals[gst_rate]['cgst'] += item.cgst
        gst_totals[gst_rate]['sgst'] += item.sgst
        gst_totals[gst_rate]['ugst'] += item.ugst
        gst_totals[gst_rate]['total'] += item.total

    # Calculate the overall totals for GST
    gst_totals_total = {
        'taxable_value': sum(gst['taxable_value'] for gst in gst_totals.values()),
        'cgst': sum(gst['cgst'] for gst in gst_totals.values()),
        'sgst': sum(gst['sgst'] for gst in gst_totals.values()),
        'ugst': sum(gst['ugst'] for gst in gst_totals.values()),
        'total': sum(gst['total'] for gst in gst_totals.values())
    }

    # Convert invoice.total_amount to words
    total_amount_words = num2words(invoice.total_amount, lang='en_IN').title() + " Only"

    # Prepare the context for the PDF template
    template_path = 'pdf_template.html'
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'total_taxable': total_taxable,
        'total_cgst': total_cgst,
        'total_sgst': total_sgst,
        'total_ugst': total_ugst,
        'total_amount': total_amount,
        'gst_totals': gst_totals,
        'gst_totals_total': gst_totals_total,
        'total_amount_words': total_amount_words,  # Pass to template
    }

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.code}.pdf"'

    # Render the template with the context and generate the PDF
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    
    return response





from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Invoice

def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-invoice_date')
    paginator = Paginator(invoices, 5)  # Show 5 invoices per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'invoice_list.html', {'page_obj': page_obj})


# views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Invoice

def invoice_list(request):
    query = request.GET.get('search', '')
    invoices = Invoice.objects.all()

    if query:
        invoices = invoices.filter(
            name_of_supplier__icontains=query
        ) | invoices.filter(
            name_of_buyer__icontains=query
        )

    paginator = Paginator(invoices.order_by('-invoice_date'), 10)  # Optional: paginate 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'invoice_list.html', {'page_obj': page_obj, 'search_query': query})








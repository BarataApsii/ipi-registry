from django.shortcuts import render, get_object_or_404, redirect
from .models import Shareholder, ShareLedger
from django.http import HttpResponse
from django.db.models import Sum

def home(request):
    return render(request, 'shareholders/home.html')

def search_shareholder(request):
    query = request.GET.get('q', '')
    shareholder = None
    total_shares = 0
    if query:
        try:
            shareholder = Shareholder.objects.get(id_number=query)
            total_shares = shareholder.ledger_entries.aggregate(Sum('shares'))['shares__sum'] or 0
        except Shareholder.DoesNotExist:
            shareholder = None
    return render(request, 'shareholders/search.html', {
        'shareholder': shareholder,
        'total_shares': total_shares,
        'query': query
    })

def update_shares(request, shareholder_id):
    shareholder = get_object_or_404(Shareholder, pk=shareholder_id)
    if request.method == 'POST':
        shares = int(request.POST.get('shares'))
        transaction_type = request.POST.get('transaction_type')
        ShareLedger.objects.create(
            shareholder=shareholder,
            shares=shares,
            transaction_type=transaction_type,
            updated_by=request.user if request.user.is_authenticated else None
        )
        return redirect('shareholders:search_shareholder')
    return render(request, 'shareholders/update_shares.html', {'shareholder': shareholder})

def shareholder_report(request, shareholder_id):
    shareholder = get_object_or_404(Shareholder, pk=shareholder_id)
    total_shares = shareholder.ledger_entries.aggregate(Sum('shares'))['shares__sum'] or 0
    return render(request, 'shareholders/report.html', {
        'shareholder': shareholder,
        'total_shares': total_shares
    })

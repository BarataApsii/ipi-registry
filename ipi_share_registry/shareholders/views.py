from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Sum
from .models import Shareholder, Transaction


def home(request):
    """Render the home page."""
    return render(request, 'shareholders/home.html')


def search_shareholder(request):
    """Search a shareholder by ID number."""
    query = request.GET.get('q', '').strip()
    shareholder = None
    total_shares = 0

    if query:
        try:
            shareholder = Shareholder.objects.get(id_number=query)
            # Use related_name from Transaction model
            total_shares = shareholder.transactions.aggregate(Sum('shares'))['shares__sum'] or 0
        except Shareholder.DoesNotExist:
            shareholder = None

    context = {
        'shareholder': shareholder,
        'total_shares': total_shares,
        'query': query
    }
    return render(request, 'shareholders/search.html', context)


def update_shares(request, shareholder_id):
    """Update shares of a shareholder by creating a transaction."""
    shareholder = get_object_or_404(Shareholder, pk=shareholder_id)

    if request.method == 'POST':
        shares = int(request.POST.get('shares', 0))
        transaction_type = request.POST.get('transaction_type', 'ISSUE')

        Transaction.objects.create(
            shareholder=shareholder,
            shares=shares,
            transaction_type=transaction_type,
            created_by=request.user if request.user.is_authenticated else None
        )

        # Optionally update Shareholder's total_shares
        shareholder.total_shares = shareholder.transactions.aggregate(Sum('shares'))['shares__sum'] or 0
        shareholder.save(update_fields=['total_shares'])

        return redirect('shareholders:search_shareholder')

    context = {
        'shareholder': shareholder
    }
    return render(request, 'shareholders/update_shares.html', context)


def shareholder_report(request, shareholder_id):
    """Generate a report for a shareholder."""
    shareholder = get_object_or_404(Shareholder, pk=shareholder_id)
    total_shares = shareholder.transactions.aggregate(Sum('shares'))['shares__sum'] or 0

    context = {
        'shareholder': shareholder,
        'total_shares': total_shares
    }
    return render(request, 'shareholders/report.html', context)

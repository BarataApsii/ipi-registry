from django.shortcuts import render
from shareholders.models import Shareholder, ShareLedger, Director
from django.db.models import Sum, Count
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    total_shareholders = Shareholder.objects.count()
    total_shares = ShareLedger.objects.aggregate(Sum('shares'))['shares__sum'] or 0
    total_directors = Director.objects.count()

    thirty_days_ago = now() - timedelta(days=30)
    new_shareholders = Shareholder.objects.filter(created_at__gte=thirty_days_ago).count()

    shares_distribution = Shareholder.objects.annotate(
        total_shares=Sum('ledger_entries__shares')
    ).values('full_name', 'total_shares')

    context = {
        'total_shareholders': total_shareholders,
        'total_shares': total_shares,
        'total_directors': total_directors,
        'new_shareholders': new_shareholders,
        'shares_distribution': shares_distribution,
    }
    return render(request, 'dashboard/dashboard.html', context)

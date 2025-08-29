from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from devices.models import Event
from employees.models import Employee
from orders.models import Order


class Statistics:
    @classmethod
    def percentage_comparison(cls, x: int, y: int) -> float:
        if y == 0:
            return float('inf')
        return round((x - y) / y * 100, 2)

    @classmethod
    def get_entrance_count(cls):
        return Event.objects.filter(type__startswith='valid', timestamp__gt=now().replace(hour=0, minute=0)).count()

    @classmethod
    def get_employee_count(cls):
        return Employee.objects.count()

    @classmethod
    def get_orders_count(cls):
        today = now().astimezone()
        return Order.objects.filter(created_at__date=today).aggregate(
            daily_orders=Count("id", filter=Q(is_cancelled=False)),
            daily_cancelled_orders=Count("id", filter=Q(is_cancelled=True)),
        )

    @classmethod
    def get_orders_weekly_chart_labels(cls):
        today = now().astimezone()
        day_before = lambda x: ((a := (today - timedelta(days=x))).strftime('%d.%m') + ' ' + _(a.strftime('%a')))
        return [day_before(day) for day in range(6, -1, -1)]

    @classmethod
    def get_orders_weekly_chart(cls):
        today = now().astimezone()
        start_date = today - timedelta(days=13)
        qs = (
            Order.objects.filter(created_at__date__range=[start_date, today], is_cancelled=False)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        date_map = {(i['day']).day: i['count'] for i in qs}
        this_week, last_week = {}, {}
        for i in range(13, -1, -1):
            day_ = (today - timedelta(days=i)).day
            if i < 7:
                this_week[day_] = date_map.get(day_, 0)
            else:
                last_week[day_] = date_map.get(day_, 0)
        return {
            'sum': sum(this_week.values()),
            'labels': cls.get_orders_weekly_chart_labels(),
            'this_week': this_week.values(),
            'last_week': last_week.values(),
            'top_number': max(*this_week.values(), *last_week.values()) + 30,
            'difference': cls.percentage_comparison(sum(this_week.values()), sum(last_week.values())),
        }

    @classmethod
    def get_orders_yearly_chart_labels(cls):
        today = now().astimezone()
        month_before = lambda x: _((today - relativedelta(months=x)).strftime('%B'))
        return [month_before(month) for month in range(11, -1, -1)]

    @classmethod
    def get_orders_yearly_chart(cls):
        today = now().astimezone()
        start_date = today.replace(day=1) - relativedelta(months=11)

        qs = (
            Order.objects.filter(created_at__gte=start_date, is_cancelled=False)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        month_map = {i['month'].month: i['count'] for i in qs}
        yearly_orders = [month_map.get((today - relativedelta(months=month)).month, 0) for month in range(11, -1, -1)]
        return {
            'sum': sum(yearly_orders),
            'labels': cls.get_orders_yearly_chart_labels(),
            'yearly_orders': yearly_orders,
            'difference': cls.percentage_comparison(yearly_orders[-1], yearly_orders[-2]),
        }

    @classmethod
    def get_food_size_consume(cls):
        today = now()
        qs = (
            Order.objects.filter(
                created_at__year=today.year,
                created_at__month=today.month,
                is_cancelled=False,
            )
            .values("food_size")
            .annotate(count=Count("id"))
            .order_by("food_size")
        )
        food_size = {'0.5': 0, '1': 0, '1.5': 0}
        for order in qs:
            food_size[order['food_size']] = order['count']
        return food_size.values()

    @classmethod
    def get_index_context(cls, request: WSGIRequest):
        context = {
            'entrance_count': cls.get_entrance_count(),
            'employee_count': cls.get_employee_count(),
            'orders_weekly_chart': cls.get_orders_weekly_chart(),
            'orders_yearly_chart': cls.get_orders_yearly_chart(),
            'orders_food_size_consume': cls.get_food_size_consume()
        }
        context.update(**cls.get_orders_count())
        return context


def context_manager(request: WSGIRequest):
    if request.path in ('/uz/', '/ru/', '/en/'):
        return Statistics.get_index_context(request)
    return {}

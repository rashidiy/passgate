# from django.views.generic.edit import FormView
# from django.urls import reverse_lazy
#
# from .forms import OrderForm
# from camera import check_face, switch_cam
# from .models import Employee, Order
#
# from django.views.generic.edit import FormView
# from django.urls import reverse_lazy
#
# from .forms import OrderForm
# from camera import check_face, switch_cam
# from .models import Employee, Order
#
# from django.http import JsonResponse
#
# from django.http import JsonResponse
#
# class OrderFoodView(FormView):
#     template_name = 'order_food.html'
#     form_class = OrderForm
#     success_url = reverse_lazy('order_food')
#
#     def form_valid(self, form):
#         food_size = form.cleaned_data['food_size']
#
#         switch_cam(True)
#         face_result = check_face(timeout=10)
#         switch_cam(False)
#
#         if face_result == 'unknown':
#             error_message = 'Yuz ro\'yxatga olinmagan.'
#             if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'message': error_message})
#             else:
#                 form = self.form_class()
#                 return self.render_to_response(self.get_context_data(form=form, error_message=error_message))
#         elif face_result == 'error' or face_result == 'timeout':
#             error_message = 'Yuz aniqlanmadi.'
#             if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({'success': False, 'message': error_message})
#             else:
#                 form = self.form_class()
#                 return self.render_to_response(self.get_context_data(form=form, error_message=error_message))
#         else:
#             employee = Employee.objects.get(id=face_result)
#             Order.objects.create(employee=employee, food_size=food_size)
#
#             success_message = 'Buyurtma qabul qilindi!'
#             if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({'success': True, 'message': success_message})
#             else:
#                 form = self.form_class()
#                 return self.render_to_response(self.get_context_data(form=form, success_message=success_message))
#
#     def form_invalid(self, form):
#         error_message = 'Noto‘g‘ri ma‘lumot kiritildi.'
#         if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({'success': False, 'message': error_message})
#         else:
#             return self.render_to_response(self.get_context_data(form=form, error_message=error_message))


from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import OrderForm
from .models import Employee, Order
from django.http import JsonResponse
from .middleware_client import check_face, switch_cam

class OrderFoodView(FormView):
    template_name = 'order_food.html'
    form_class = OrderForm
    success_url = reverse_lazy('order_food')

    def form_valid(self, form):
        food_size = form.cleaned_data['food_size']

        switch_cam(True)
        face_result = check_face(timeout=10)
        switch_cam(False)

        if face_result == 'unknown':
            error_message = 'Yuz ro\'yxatga olinmagan.'
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            else:
                form = self.form_class()
                return self.render_to_response(self.get_context_data(form=form, error_message=error_message))
        elif face_result == 'error' or face_result == 'timeout':
            error_message = 'Yuz aniqlanmadi.'
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})
            else:
                form = self.form_class()
                return self.render_to_response(self.get_context_data(form=form, error_message=error_message))
        else:
            try:
                employee = Employee.objects.get(id=face_result)
                Order.objects.create(employee=employee, food_size=food_size)
                success_message = 'Buyurtma qabul qilindi!'
                if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': success_message})
                else:
                    form = self.form_class()
                    return self.render_to_response(self.get_context_data(form=form, success_message=success_message))
            except Employee.DoesNotExist:
                error_message = 'Xodim topilmadi.'
                if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_message})
                else:
                    form = self.form_class()
                    return self.render_to_response(self.get_context_data(form=form, error_message=error_message))

    def form_invalid(self, form):
        error_message = 'Noto‘g‘ri ma‘lumot kiritildi.'
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_message})
        else:
            return self.render_to_response(self.get_context_data(form=form, error_message=error_message))

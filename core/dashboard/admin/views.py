from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import AdminProductForm, AdminProductImageForm, AdminCouponForm, AdminReviewForm
from dashboard.permissions import StaffDashboardRequiredMixin

from shop.models import ProductCategoryModel, ProductModel, ProductImageModel
from order.models import OrderModel, OrderStatusType, CouponModel
from review.models import ReviewModel, ReviewStatusType


class AdminDashboardHomeView(LoginRequiredMixin, StaffDashboardRequiredMixin, TemplateView):
    template_name = "dashboard/admin/home.html"


class AdminProductListView(LoginRequiredMixin, StaffDashboardRequiredMixin, ListView):
    template_name = "dashboard/admin/products/product-list.html"
    context_object_name = "products"
    paginate_by = 10

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "price_asc": "price",
        "price_desc": "-price",
        "title_asc": "title",
        "title_desc": "-title",
    }

    def get_queryset(self):
        queryset = (
            ProductModel.objects
            .select_related("user")
            .prefetch_related("category")
        )

        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        category_id = self.request.GET.get("category_id")

        if category_id:
            try:
                queryset = queryset.filter(category__id=int(category_id))
            except (TypeError, ValueError):
                pass

        order_by = self.request.GET.get("order_by")

        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(self.ALLOWED_ORDERINGS[order_by])

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProductCategoryModel.objects.all()
        context["total_items"] = context["paginator"].count

        return context


class AdminProductCreateView(LoginRequiredMixin, StaffDashboardRequiredMixin, CreateView):
    template_name = "dashboard/admin/products/product-create.html"
    form_class = AdminProductForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "محصول جدید با موفقیت ایجاد شد.")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product-edit",
            kwargs={"pk": self.object.pk},
        )


class AdminProductUpdateView(LoginRequiredMixin, StaffDashboardRequiredMixin, UpdateView):
    model = ProductModel
    form_class = AdminProductForm
    template_name = "dashboard/admin/products/product-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = AdminProductImageForm()
        context["extra_images"] = self.object.product_images.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات محصول با موفقیت بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product-edit",
            kwargs={"pk": self.object.pk},
        )


class AdminProductDeleteView(LoginRequiredMixin, StaffDashboardRequiredMixin, DeleteView):
    model = ProductModel
    template_name = "dashboard/admin/products/product-delete.html"
    success_url = reverse_lazy("dashboard:admin:product-list")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)

        except ProtectedError:
            messages.error(
                request,
                "این محصول در سفارش ثبت شده و قابل حذف نیست. "
                "می‌توانید وضعیت آن را به Draft تغییر دهید.",
            )

            return redirect("dashboard:admin:product-edit", pk=kwargs["pk"])


class AdminProductAddImageView(LoginRequiredMixin, StaffDashboardRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(ProductModel, pk=kwargs["pk"])

        form = AdminProductImageForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            product_image = form.save(commit=False)
            product_image.product = product
            product_image.save()
            messages.success(request, "تصویر محصول با موفقیت اضافه شد.")

        else:
            messages.error(request, "فایل تصویر معتبر نیست.")

        return redirect("dashboard:admin:product-edit", pk=product.pk)


class AdminProductRemoveImageView(LoginRequiredMixin, StaffDashboardRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(ProductModel, pk=kwargs["pk"])
        product_image = get_object_or_404(ProductImageModel, pk=kwargs["image_id"], product=product)
        product_image.delete()
        messages.success(request, "تصویر محصول حذف شد.")

        return redirect("dashboard:admin:product-edit", pk=product.pk)


class AdminOrderListView(LoginRequiredMixin, StaffDashboardRequiredMixin, ListView):
    template_name = "dashboard/admin/orders/order-list.html"
    context_object_name = "orders"
    paginate_by = 10

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "price_asc": "total_price",
        "price_desc": "-total_price",
    }

    def get_queryset(self):
        queryset = (
            OrderModel.objects
            .select_related("user", "coupon", "payment")
            .prefetch_related("order_items__product")
        )

        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            filters = Q(user__email__icontains=search_query)

            if search_query.isdigit():
                filters |= Q(id=int(search_query))

            queryset = queryset.filter(filters)

        status = self.request.GET.get("status")

        valid_statuses = {
            str(status_id)
            for status_id, _ in OrderStatusType.choices
        }

        if status in valid_statuses:
            queryset = queryset.filter(status=int(status))

        order_by = self.request.GET.get("order_by")

        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(self.ALLOWED_ORDERINGS[order_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["paginator"].count
        context["status_types"] = OrderStatusType.choices

        return context


class AdminOrderDetailView(LoginRequiredMixin, StaffDashboardRequiredMixin, DetailView):
    template_name = "dashboard/admin/orders/order-detail.html"
    context_object_name = "order"
    queryset = (
        OrderModel.objects
        .select_related("user", "coupon", "payment")
        .prefetch_related("order_items__product")
    )


class AdminOrderInvoiceView(LoginRequiredMixin, StaffDashboardRequiredMixin, DetailView):
    template_name = "dashboard/admin/orders/order-invoice.html"
    context_object_name = "order"
    queryset = (
        OrderModel.objects
        .filter( status=OrderStatusType.success.value)
        .select_related("user", "coupon", "payment")
        .prefetch_related("order_items__product")
    )


class AdminCouponListView(LoginRequiredMixin, StaffDashboardRequiredMixin, ListView):
    template_name = "dashboard/admin/coupons/coupon-list.html"
    context_object_name = "coupons"
    paginate_by = 10

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "discount_asc": "discount_percent",
        "discount_desc": "-discount_percent",
        "expiration_asc": "expiration_date",
        "expiration_desc": "-expiration_date",
    }

    def get_queryset(self):
        queryset = CouponModel.objects.prefetch_related("used_by")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(code__icontains=search_query)

        order_by = self.request.GET.get("order_by")

        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(self.ALLOWED_ORDERINGS[order_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["paginator"].count

        return context


class AdminCouponCreateView(LoginRequiredMixin, StaffDashboardRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/coupons/coupon-create.html"
    form_class = AdminCouponForm
    success_message = "کد تخفیف با موفقیت ایجاد شد."

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:coupon-list")


class AdminCouponUpdateView(LoginRequiredMixin, StaffDashboardRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CouponModel
    form_class = AdminCouponForm
    template_name = "dashboard/admin/coupons/coupon-edit.html"
    success_message = "کد تخفیف با موفقیت بروزرسانی شد."

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:coupon-edit", kwargs={"pk": self.object.pk})
        

class AdminCouponDeleteView(LoginRequiredMixin, StaffDashboardRequiredMixin, DeleteView):
    model = CouponModel
    template_name = "dashboard/admin/coupons/coupon-delete.html"
    success_url = reverse_lazy("dashboard:admin:coupon-list")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        
        except ProtectedError:
            messages.error(request, "این کد تخفیف در سفارش ثبت شده و قابل حذف نیست.")

            return redirect("dashboard:admin:coupon-edit", pk=kwargs["pk"])


class AdminReviewListView(LoginRequiredMixin, StaffDashboardRequiredMixin, ListView):
    template_name = "dashboard/admin/reviews/review-list.html"
    context_object_name = "reviews"
    paginate_by = 10

    ALLOWED_ORDERINGS = {
        "newest": "-created_date",
        "oldest": "created_date",
        "rate_asc": "rate",
        "rate_desc": "-rate",
    }

    def get_queryset(self):
        queryset = ReviewModel.objects.select_related("user", "product")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(user__email__icontains=search_query)
                | 
                Q(product__title__icontains=search_query)
                | 
                Q(description__icontains=search_query)
            )

        status = self.request.GET.get("status")

        valid_statuses = {
            str(status_id)
            for status_id, _ in ReviewStatusType.choices
        }

        if status in valid_statuses:
            queryset = queryset.filter(status=int(status))

        order_by = self.request.GET.get("order_by")

        if order_by in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by( self.ALLOWED_ORDERINGS[order_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = context["paginator"].count
        context["status_types"] = ReviewStatusType.choices

        return context


class AdminReviewUpdateView(LoginRequiredMixin, StaffDashboardRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ReviewModel
    form_class = AdminReviewForm
    template_name = "dashboard/admin/reviews/review-edit.html"
    success_message = "نظر مشتری با موفقیت بروزرسانی شد."
 
    def get_success_url(self):
        return reverse_lazy("dashboard:admin:review-edit", kwargs={"pk": self.object.pk})
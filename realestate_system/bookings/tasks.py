from celery import shared_task


@shared_task
def send_booking_confirmation(booking_id):
    from .models import Booking

    try:
        booking = Booking.objects.get(id=booking_id)
        print(f"Booking confirmation prepared for booking #{booking.id}")
        return f"Booking confirmation prepared for booking #{booking.id}"
    except Booking.DoesNotExist:
        return f"Booking #{booking_id} does not exist"
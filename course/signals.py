from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AddStudTask, Notification
from django.contrib.auth import get_user_model


@receiver(post_save, sender=AddStudTask)
def create_notification(sender, instance, created, **kwargs):
    print('Сигнал сработал !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(f'{sender=}')
    if created:
        print('Прошли иф')
        # Получаем модель пользователя
        User = get_user_model()
        
        # Проверяем, является ли пользователь лектором и создал ли он новую запись
        if instance.lecturer.is_lecturer or instance.lecturer.is_superuser:
            print('Преподаватель')
            notif_user_id = instance.lecturer.id
            for_user_id = instance.student.id
            message = f'Вам назвначено новое задание: {instance.exercise.title}'

            # Создаем запись уведомления
            Notification.objects.create(
                notif_user_id=notif_user_id,
                for_user_id=for_user_id,
                exercise_notif=instance,
                messages=message
            )
    else:
    
        notif_user_id = instance.student.id
        for_user_id = instance.lecturer.id
        message = f'Подгружен ответ на задание: "{instance.exercise.title}"'
    
        print('Создаем')
        # Создаем запись уведомления
        Notification.objects.create(
            notif_user_id=notif_user_id,
            for_user_id=for_user_id,
            exercise_notif=instance,
            messages=message
        )
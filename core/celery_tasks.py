from celery import shared_task


@shared_task
def test_task(test_value):
    print(f'Task working, test_value: {test_value}')


# celery -A django_microservice worker -l info
# from core.celery_tasks import create_random_user_accounts
# create_random_user_accounts.delay('my_test_value')

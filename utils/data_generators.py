from faker import Faker

from models.comments.comms_create_and_response_dbc import ExpectedCommModel
from models.posts.post_create_and_response_dbc import ExpectedPostModel


faker = Faker('ru_RU')


class GenerateRandomTexts:
    """
    Генерирует случайные последовательности русских слов.
    """
    @staticmethod
    def generate_short_text():
        return faker.sentence(nb_words=5)

    @staticmethod
    def generate_long_text():
        return faker.paragraph(nb_sentences=5)


class GenerateExpectedItem:
    @staticmethod
    def generate_posts(
            amount: int = 1, status: str = 'publish'
    ) -> list[ExpectedPostModel]:
        """
        Создаёт список с заданным количеством постов с данными для полей
        title, content и status. Заполнение полей title и content производится
        набором случайных русских слов.

        Args:
            amount (int): количество создаваемых постов (по умолчанию 1)
            status (str): Значение поля status(по умолчанию 'publish')

        Returns:
            list[ExpectedPostModel]: Список созданных постов
        """
        posts = [
            ExpectedPostModel(
                title=f'Пост {i}. {GenerateRandomTexts.generate_short_text()}',
                content=GenerateRandomTexts.generate_long_text(),
                status=status
            ) for i in range(amount)
        ]
        return posts

    @staticmethod
    def generate_comms(
            post_id: int, amount: int = 5, status: str = 'approved',
    ) -> list[ExpectedCommModel]:
        """
        Создаёт список с заданным количеством комментариев для указанного \
        поста.
        Заполнение поля content производится набором случайных русских слов.

        Args:
            post_id (int): ID поста, к которому относится комментарий.
            amount (int): количество создаваемых комментариев (по умолчанию 5)
            status (str): Статус комментария (по умолчанию 'approved')

        Returns:
            list[ExpectedCommModel]: Список созданных комментариев
        """
        comms = [
            ExpectedCommModel(
                post_id=post_id,
                content=(
                    f'Каммент {i}. {GenerateRandomTexts.generate_long_text()}'
                ),
                status=status
            ) for i in range(amount)
        ]
        return comms

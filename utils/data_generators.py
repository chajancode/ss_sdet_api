from faker import Faker

from models.posts.post_create_and_response_dbc import ExpectedPostModel


faker = Faker('ru_RU')


class GenerateRandomTexts:
    @staticmethod
    def generate_short_text():
        return faker.sentence(nb_words=5)

    @staticmethod
    def generate_long_text():
        return faker.paragraph(nb_sentences=5)


class GenerateExpectedPosts:
    @staticmethod
    def generate_posts(
            amount: int, status: str = 'publish') -> list[ExpectedPostModel]:
        print(f'GENERATOR POSTOV 👀 ststus {status}')
        posts = [
            ExpectedPostModel(
                title=f'Пост {i}. {GenerateRandomTexts.generate_short_text()}',
                content=GenerateRandomTexts.generate_long_text(),
                status=status
            ) for i in range(amount)
        ]
        return posts

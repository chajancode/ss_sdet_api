from models.comments.comms_create_and_response_dbc import ExpectedCommModel
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from utils.data_generators import GenerateExpectedItem


class TestGeneratePosts:
    def test_count_status_and_types(self):
        posts = GenerateExpectedItem.generate_posts(amount=3, status="draft")
        assert len(posts) == 3
        assert all(isinstance(p, ExpectedPostModel) for p in posts)
        assert all(p.status == "draft" for p in posts)
        assert all(p.title and p.content for p in posts)

    def test_title_has_index_prefix(self):
        posts = GenerateExpectedItem.generate_posts(amount=2)
        assert posts[0].title.startswith("Пост 0.")
        assert posts[1].title.startswith("Пост 1.")

    def test_defaults(self):
        posts = GenerateExpectedItem.generate_posts()
        assert len(posts) == 1
        assert posts[0].status == "publish"


class TestGenerateComms:
    def test_count_status_and_post_id(self):
        comms = GenerateExpectedItem.generate_comms(
            post_id=14, amount=2, status="trash"
        )
        assert len(comms) == 2
        assert all(isinstance(c, ExpectedCommModel) for c in comms)
        assert all(c.post_id == 14 for c in comms)
        assert all(c.status == "trash" for c in comms)
        assert all(c.content for c in comms)

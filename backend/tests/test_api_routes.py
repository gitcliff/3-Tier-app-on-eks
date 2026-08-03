import pytest

from app import create_app
from app.models import db
from app.models.models import Question, Topic


class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True


@pytest.fixture()
def app():
    flask_app = create_app(TestConfig)

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_get_topics_returns_empty_list(client):
    response = client.get("/api/topics")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_topic_and_list_it(client):
    payload = {
        "name": "Linux",
        "description": "Basic Linux interview questions",
        "slug": "linux"
    }

    create_response = client.post("/api/topics", json=payload)
    assert create_response.status_code == 201

    created_topic = create_response.get_json()
    assert created_topic["title"] == "Linux"
    assert created_topic["description"] == "Basic Linux interview questions"
    assert created_topic["id"] == "linux"

    list_response = client.get("/api/topics")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) == 1


def test_quiz_endpoint_returns_questions_for_topic(client):
    topic = Topic(name="Docker", description="Docker questions", slug="docker")
    db.session.add(topic)
    db.session.commit()

    question = Question(
        topic_id=topic.id,
        question_text="What does docker build do?",
        options=["Builds an image", "Runs a container", "Deletes a volume", "Lists services"],
        correct_answer=0,
    )
    db.session.add(question)
    db.session.commit()

    response = client.get("/api/quiz/docker")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["title"] == "Docker"
    assert payload["total_questions"] == 1
    assert payload["selected_questions"] == 1
    assert len(payload["questions"]) == 1
    assert payload["questions"][0]["question"] == "What does docker build do?"


def test_submit_quiz_returns_score(client):
    topic = Topic(name="Kubernetes", description="K8s questions", slug="kubernetes")
    db.session.add(topic)
    db.session.commit()

    first_question = Question(
        topic_id=topic.id,
        question_text="What is a pod?",
        options=["A deployment", "The smallest deployable unit", "A service", "A namespace"],
        correct_answer=1,
    )
    second_question = Question(
        topic_id=topic.id,
        question_text="What does kubectl apply do?",
        options=["Deletes resources", "Applies configuration from a file", "Lists nodes", "Builds images"],
        correct_answer=1,
    )
    db.session.add_all([first_question, second_question])
    db.session.commit()

    response = client.post(
        "/api/quiz/submit",
        json={
            "topic": "kubernetes",
            "answers": {
                str(first_question.id): 1,
                str(second_question.id): 2,
            },
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["correct"] == 1
    assert payload["total"] == 2
    assert payload["score"] == 50.0


def test_bulk_upload_questions_returns_success_counts(client):
    topic = Topic(name="AWS", description="AWS interview questions", slug="aws")
    db.session.add(topic)
    db.session.commit()

    payload = [
        {
            "topic_slug": "aws",
            "question_text": "What does EC2 stand for?",
            "options": ["Elastic Compute Cloud", "Elastic Container Cloud", "Elastic Configuration Cloud", "Elastic Cache Cloud"],
            "correct_answer": 0,
        },
        {
            "topic_slug": "aws",
            "question_text": "What is S3?",
            "options": ["Storage service", "Compute service", "Database service", "Queue service"],
            "correct_answer": 0,
        },
    ]

    response = client.post("/api/quiz/questions/bulk", json=payload)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] == 2
    assert payload["failed"] == 0
    assert payload["errors"] is None

    questions = Question.query.all()
    assert len(questions) == 2

from __future__ import annotations

from fastapi.testclient import TestClient


def test_question_and_answer_flow(fastapi_app):
    client = TestClient(fastapi_app)
    with client:
        response = client.get("/api/question", params={"difficulty": "make_model_year", "timer": 25})
        assert response.status_code == 200
        question = response.json()
        assert question["timeout"] == 25
        assert question["difficulty"] == "make_model_year"
        assert len(question["options"]) == 10

        answer_payload = {
            "qid": question["qid"],
            "difficulty": question["difficulty"],
            "answer": question["correct"],
            "player": "테스터",
            "timeout": False,
        }
        answer_response = client.post("/api/answer", json=answer_payload)
        assert answer_response.status_code == 200
        answer_data = answer_response.json()
        assert answer_data["correct"] is True
        assert answer_data["score"]["player"] == "테스터"

        leaderboard_response = client.get("/api/leaderboard")
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()
        assert leaderboard["entries"]

import os

def test_transit_partner_submission_doc_exists():
    assert os.path.exists("docs/TRANSIT_PARTNER_SUBMISSION.md")

def test_transit_partner_submission_doc_content():
    with open("docs/TRANSIT_PARTNER_SUBMISSION.md", "r") as f:
        content = f.read()
    assert "authorization" in content.lower()
    assert "kocaeli" in content.lower()

import pytest
from screenflow_processor import ScreenFlowProcessor

# Mock responses for the AURA API
MOCK_PARSE_RESPONSE = {
    "quality_assessment": {
        "overall_score": 85
    },
    "document_metrics": {
        "word_count": 5000,
        "estimated_pages": 20
    }
}

MOCK_ANALYSIS_RESPONSE = {
    "insights": {
        "narrative_structure": {
            "act_breakdown": {
                "act1": "25%",
                "act2": "50%",
                "act3": "25%"
            }
        },
        "character_analysis": {
            "main_characters": 3
        },
        "commercial_viability": {
            "market_potential": "high"
        }
    }
}

MOCK_VALIDATION_RESPONSE = {
    "compliance_report": {
        "industry_standards": {
            "hollywood_format": "95%"
        }
    },
    "overall_score": 90,
    "issues_found": 0
}

def test_process_submission(monkeypatch):
    # Mock the _make_request method to return predefined responses
    def mock_make_request(self, endpoint, data):
        if endpoint == '/api/parse':
            return MOCK_PARSE_RESPONSE
        elif endpoint == '/api/analyze':
            return MOCK_ANALYSIS_RESPONSE
        elif endpoint == '/api/validate':
            return MOCK_VALIDATION_RESPONSE

    processor = ScreenFlowProcessor('https://test.api', 'test_key')
    monkeypatch.setattr(ScreenFlowProcessor, '_make_request', mock_make_request)

    writer_info = {"name": "Test Writer"}
    assessment = processor.process_submission("Test screenplay", writer_info)

    assert assessment['quick_assessment']['commercial_score'] == 85
    assert assessment['quick_assessment']['recommendation'] == "Advance to next round"
    assert assessment['quick_assessment']['priority_level'] == "high"

# ... more tests
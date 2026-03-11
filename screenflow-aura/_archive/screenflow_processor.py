import requests
import json
from datetime import datetime
from typing import Dict, List, Any

class ScreenFlowProcessor:
    """
    A wrapper class for the AURA Enterprise API tailored for ScreenFlow Studios.
    """

    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.api_key = api_key

    def _make_request(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """
        Helper method to make authenticated requests to the AURA API.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Client-ID': 'screenflow_studios'
        }

        response = requests.post(
            f"{self.api_base}{endpoint}",
            json=data,
            headers=headers,
            timeout=30
        )

        # Raise an exception for bad status codes
        response.raise_for_status()

        return response.json()

    def process_submission(self, screenplay_content: str, writer_info: Dict) -> Dict[str, Any]:
        """
        Process a single screenplay submission through the AURA Enterprise API.

        Args:
            screenplay_content (str): The screenplay text.
            writer_info (Dict): Information about the writer.

        Returns:
            Dict: A comprehensive assessment report.
        """

        # Step 1: Basic parsing and metrics
        parse_response = self._make_request('/api/parse', {
            'screenplay': screenplay_content,
            'options': {'enhance': True}
        })

        # Step 2: Advanced AI analysis
        analysis_response = self._make_request('/api/analyze', {
            'screenplay': screenplay_content,
            'analysis_type': 'comprehensive'
        })

        # Step 3: Industry validation
        validation_response = self._make_request('/api/validate', {
            'screenplay': screenplay_content
        })

        # Compile the assessment
        assessment = self._compile_assessment(parse_response, analysis_response, validation_response, writer_info)

        return assessment

    def process_batch_submissions(self, submissions: List[Dict]) -> Dict[str, List]:
        """
        Process a batch of screenplays.

        Args:
            submissions: List of dictionaries, each containing 'screenplay' and 'writer_info'

        Returns:
            Dict: Categorized submissions (high_potential, needs_development, not_suitable)
        """

        # Extract the screenplay contents for batch processing
        screenplays = [sub['screenplay'] for sub in submissions]

        batch_response = self._make_request('/api/batch/parse', {
            'screenplays': screenplays
        })

        # Categorize each result
        categorized = {
            'high_potential': [],
            'needs_development': [],
            'not_suitable': []
        }

        for i, result in enumerate(batch_response['results']):
            # Each result corresponds to the submission at the same index
            writer_info = submissions[i]['writer_info']

            # Compile assessment for this submission
            # Note: We are using the batch result, so we don't call the other endpoints again.
            # However, note that the batch endpoint may not return as much detail as the individual ones.
            # In a real scenario, we might have to adjust. For now, we use what we have.

            # We'll create a simplified assessment from the batch result
            assessment = {
                'submission_id': f"SF-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{i}",
                'writer': writer_info,
                'timestamp': datetime.now().isoformat(),
                'quick_assessment': {
                    'commercial_score': result.get('quality_assessment', {}).get('overall_score', 0),
                    'word_count': result.get('document_metrics', {}).get('word_count', 0),
                    'estimated_pages': result.get('document_metrics', {}).get('estimated_pages', 0)
                },
                # ... we could add more fields from the batch result if available
            }

            score = assessment['quick_assessment']['commercial_score']
            if score >= 85:
                categorized['high_potential'].append(assessment)
            elif score >= 70:
                categorized['needs_development'].append(assessment)
            else:
                categorized['not_suitable'].append(assessment)

        return categorized

    def _compile_assessment(self, parse_data: Dict, analysis_data: Dict, validation_data: Dict, writer_info: Dict) -> Dict[str, Any]:
        """
        Compile a comprehensive assessment report from the AURA API responses.

        Args:
            parse_data: Response from /api/parse
            analysis_data: Response from /api/analyze
            validation_data: Response from /api/validate
            writer_info: Writer information

        Returns:
            Dict: Comprehensive assessment
        """

        return {
            'submission_id': f"SF-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'writer': writer_info,
            'timestamp': datetime.now().isoformat(),
            'quick_assessment': {
                'commercial_score': parse_data['quality_assessment']['overall_score'],
                'recommendation': self._generate_recommendation(parse_data),
                'priority_level': self._calculate_priority(parse_data, validation_data)
            },
            'detailed_analysis': {
                'structural_breakdown': analysis_data['insights']['narrative_structure'],
                'character_analysis': analysis_data['insights']['character_analysis'],
                'market_potential': analysis_data['insights']['commercial_viability']
            },
            'technical_validation': {
                'industry_compliance': validation_data['compliance_report'],
                'quality_metrics': validation_data['overall_score'],
                'identified_issues': validation_data['issues_found']
            },
            'next_steps': self._generate_next_steps(analysis_data, validation_data)
        }

    def _generate_recommendation(self, parse_data: Dict) -> str:
        """
        Generate a recommendation based on the parse data.

        Args:
            parse_data: Response from /api/parse

        Returns:
            str: Recommendation (e.g., "Advance to next round", "Request revisions", "Reject")
        """

        score = parse_data['quality_assessment']['overall_score']

        if score >= 85:
            return "Advance to next round"
        elif score >= 70:
            return "Request revisions"
        else:
            return "Reject"

    def _calculate_priority(self, parse_data: Dict, validation_data: Dict) -> str:
        """
        Calculate the priority level for the submission.

        Args:
            parse_data: Response from /api/parse
            validation_data: Response from /api/validate

        Returns:
            str: Priority level (e.g., "high", "medium", "low")
        """

        score = parse_data['quality_assessment']['overall_score']
        issues = validation_data['issues_found']

        if score >= 85 and issues == 0:
            return "high"
        elif score >= 70 and issues <= 2:
            return "medium"
        else:
            return "low"

    def _generate_next_steps(self, analysis_data: Dict, validation_data: Dict) -> List[str]:
        """
        Generate next steps based on the analysis and validation.

        Args:
            analysis_data: Response from /api/analyze
            validation_data: Response from /api/validate

        Returns:
            List[str]: List of next steps
        """

        next_steps = []

        # Example logic for next steps
        if validation_data['issues_found'] > 0:
            next_steps.append("Address validation issues")

        if analysis_data['insights']['narrative_structure']['act_breakdown']['act2'] < 40:
            next_steps.append("Consider expanding the second act")

        # Add more business logic here

        return next_steps

# Example usage
if __name__ == "__main__":
    # Initialize the processor
    processor = ScreenFlowProcessor(
        api_base="https://api.aura-enterprise.com",
        api_key="your_api_key_here"
    )

    # Example submission
    screenplay_content = """
    INT. OFFICE - DAY

    ALEX sits at a computer, typing furiously.

    ALEX
    (muttering)
    This API is going to change everything.

    He smiles, then continues typing.
    """

    writer_info = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "experience": "emerging"
    }

    # Process a single submission
    assessment = processor.process_submission(screenplay_content, writer_info)
    print(json.dumps(assessment, indent=2))

    # Process a batch of submissions
    submissions = [
        {
            'screenplay': screenplay_content,
            'writer_info': writer_info
        },
        # ... more submissions
    ]

    batch_results = processor.process_batch_submissions(submissions)
    print(json.dumps(batch_results, indent=2))
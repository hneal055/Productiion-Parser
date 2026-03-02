"""
Step 4: Batch Processing with AURA
Process multiple screenplays efficiently
"""

from aura_processor import ScreenFlowAURAProcessor
import json
from datetime import datetime

class AURABatchProcessor:
    """Batch processor for multiple screenplays"""
    
    def __init__(self):
        self.aura_processor = ScreenFlowAURAProcessor()
        self.batch_results = []
    
    def process_batch(self, submissions):
        """Process a batch of submissions"""
        print(f"📦 Processing batch of {len(submissions)} submissions...")
        
        for i, submission in enumerate(submissions, 1):
            print(f"   Analyzing submission {i}/{len(submissions)}...")
            screenplay_content = submission.get('content', '')
            writer_info = submission.get('writer_info', {})
            
            # Analyze with AURA
            result = self.aura_processor.analyze_screenplay(screenplay_content, writer_info)
            self.batch_results.append(result)
        
        return self.batch_results
    
    def categorize_results(self):
        """Categorize results by recommendation"""
        categorized = {
            'advance': [],
            'revise': [],
            'reject': []
        }
        
        for result in self.batch_results:
            recommendation = result['quick_verdict']['recommendation']
            if recommendation == "Advance to Development":
                categorized['advance'].append(result)
            elif recommendation == "Request Revisions":
                categorized['revise'].append(result)
            else:
                categorized['reject'].append(result)
        
        return categorized
    
    def generate_batch_report(self):
        """Generate a summary report for the batch"""
        categorized = self.categorize_results()
        
        report = {
            'batch_id': f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'processed_at': datetime.now().isoformat(),
            'total_processed': len(self.batch_results),
            'summary': {
                'advance': len(categorized['advance']),
                'revise': len(categorized['revise']),
                'reject': len(categorized['reject'])
            },
            'advance_rate': f"{(len(categorized['advance']) / len(self.batch_results)) * 100:.1f}%",
            'results': categorized
        }
        
        return report

# Demo the batch processor
if __name__ == "__main__":
    print("🚀 Initializing AURA Batch Processor...")
    print("=" * 50)
    
    batch_processor = AURABatchProcessor()
    
    # Create sample batch of submissions
    sample_batch = [
        {
            'content': """
            INT. SPACESHIP - DAY

            CAPTAIN KIRA looks at the alien artifact.

            KIRA
            This could change everything we know
            about the universe.

            The artifact glows with an unearthly light.
            """,
            'writer_info': {'name': 'Alice Sci-Fi', 'experience': 'professional'}
        },
        {
            'content': """
            INT. OFFICE - DAY

            MARK sits at his desk, staring at a photo.

            MARK
            I never thought it would end like this.

            He sighs, then starts typing his resignation.
            """,
            'writer_info': {'name': 'Bob Drama', 'experience': 'emerging'}
        },
        {
            'content': """
            EXT. PARK - DAY

            Two lovers, EMILY and JACK, walk hand in hand.

            EMILY
            I've never felt this way before.

            JACK
            Me either.

            They kiss as the sun sets.
            """,
            'writer_info': {'name': 'Carol Romance', 'experience': 'emerging'}
        }
    ]
    
    # Process the batch
    results = batch_processor.process_batch(sample_batch)
    
    # Generate report
    report = batch_processor.generate_batch_report()
    
    print(f"\n📊 BATCH PROCESSING COMPLETE!")
    print(f"   Total Processed: {report['total_processed']}")
    print(f"   Advance: {report['summary']['advance']}")
    print(f"   Revise: {report['summary']['revise']}")
    print(f"   Reject: {report['summary']['reject']}")
    print(f"   Advance Rate: {report['advance_rate']}")
    
    # Show individual results
    print(f"\n🎬 INDIVIDUAL RESULTS:")
    for i, result in enumerate(results, 1):
        verdict = result['quick_verdict']
        print(f"   {i}. Score: {verdict['commercial_score']}/100 - {verdict['recommendation']}")

    # Display overall statistics
    batch_processor.aura_processor.display_stats()
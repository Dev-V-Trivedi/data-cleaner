#!/usr/bin/env python3
"""
Test script for the Enhanced Column Classifier
"""

import pandas as pd
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_column_classifier import EnhancedColumnClassifier
    print("✅ Enhanced Column Classifier imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import Enhanced Column Classifier: {e}")
    sys.exit(1)

def test_enhanced_classifier():
    """Test the enhanced classifier with sample data."""
    
    # Create sample data
    sample_data = {
        'business_name': [
            "Joe's Pizza Palace",
            "The Coffee Bean & Tea Leaf",
            "McDonald's",
            "Starbucks Corporation",
            "Local Pharmacy LLC"
        ],
        'contact_phone': [
            '555-123-4567',
            '(555) 987-6543',
            '5551234567',
            '+1-555-444-3333',
            '555.111.2222'
        ],
        'email_address': [
            'info@joespizza.com',
            'contact@coffeebean.com',
            'support@mcdonalds.com',
            'hello@starbucks.com',
            'pharmacy@local.com'
        ],
        'business_type': [
            'Restaurant',
            'Cafe',
            'Fast Food',
            'Coffee Shop',
            'Pharmacy'
        ],
        'full_address': [
            '123 Main St, New York, NY 10001',
            '456 Oak Ave, Los Angeles, CA 90210',
            '789 Pine Rd, Chicago, IL 60601',
            '321 Elm Dr, Houston, TX 77001',
            '654 Maple Ln, Phoenix, AZ 85001'
        ],
        'website': [
            'https://www.joespizza.com',
            'www.coffeebean.com',
            'https://mcdonalds.com',
            'starbucks.com',
            'localpharmacy.net'
        ],
        'customer_review': [
            'Great pizza, excellent service!',
            'Love their coffee, very friendly staff',
            'Fast service, good value for money',
            'Best coffee in town, highly recommend',
            'Helpful pharmacist, clean store'
        ],
        'operating_hours': [
            'Mon-Sun 11:00 AM - 10:00 PM',
            'Monday-Friday 6:00 AM - 9:00 PM',
            '24/7',
            'Mon-Fri 5:30 AM - 10:00 PM',
            'Mon-Sat 8:00 AM - 8:00 PM'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    print("\n📊 Sample Data:")
    print(df.head())
    
    # Initialize classifier
    classifier = EnhancedColumnClassifier()
    
    print("\n🔍 Running Enhanced Classification...")
    
    # Classify columns
    results = classifier.classify_columns(df)
    
    print("\n📋 Classification Results:")
    print("=" * 80)
    
    expected_results = {
        'business_name': 'Business Name',
        'contact_phone': 'Phone Number',
        'email_address': 'Email',
        'business_type': 'Category',
        'full_address': 'Location',
        'website': 'Social Links',
        'customer_review': 'Review',
        'operating_hours': 'Hours'
    }
    
    correct_predictions = 0
    total_predictions = len(results)
    
    for column, result in results.items():
        predicted = result['suggested_category']
        expected = expected_results.get(column, 'Unknown')
        confidence = result['confidence']
        
        is_correct = predicted == expected
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct else "❌"
        
        print(f"{status} {column:<15} | Predicted: {predicted:<15} | Expected: {expected:<15} | Confidence: {confidence:.3f}")
        
        if 'analysis_details' in result:
            details = result['analysis_details']
            print(f"    └─ Name Score: {details.get('column_name_score', {}).get(predicted, 0):.3f} | "
                  f"Content Score: {details.get('content_score', {}).get(predicted, 0):.3f}")
    
    accuracy = correct_predictions / total_predictions
    print("=" * 80)
    print(f"🎯 Accuracy: {correct_predictions}/{total_predictions} ({accuracy:.2%})")
    
    if accuracy >= 0.8:
        print("🎉 Excellent! The enhanced classifier is working great!")
    elif accuracy >= 0.6:
        print("👍 Good! The classifier is working well with room for improvement.")
    else:
        print("⚠️  The classifier needs improvement.")
    
    return accuracy

def test_edge_cases():
    """Test edge cases and challenging data."""
    
    print("\n🧪 Testing Edge Cases...")
    
    edge_case_data = {
        'mixed_data': [
            'John Doe',
            '555-1234',
            'Restaurant',
            'john@email.com',
            '123 Main St'
        ],
        'numbers_only': [
            '12345',
            '67890',
            '11111',
            '22222',
            '33333'
        ],
        'empty_column': [
            '',
            None,
            '',
            '',
            ''
        ]
    }
    
    df = pd.DataFrame(edge_case_data)
    classifier = EnhancedColumnClassifier()
    results = classifier.classify_columns(df)
    
    print("\n📋 Edge Case Results:")
    for column, result in results.items():
        print(f"Column: {column} | Category: {result['suggested_category']} | Confidence: {result['confidence']:.3f}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Column Classifier")
    print("=" * 50)
    
    try:
        accuracy = test_enhanced_classifier()
        test_edge_cases()
        
        print("\n✨ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

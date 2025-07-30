import re
import pandas as pd
from typing import Dict, List, Tuple, Any
import numpy as np

class ColumnClassifier:
    """
    A class to classify columns in a dataset based on their content patterns.
    """
    
    def __init__(self):
        self.categories = {
            'Business Name': self._classify_business_name,
            'Phone Number': self._classify_phone,
            'Email': self._classify_email,
            'Category': self._classify_category,
            'Location': self._classify_location,
            'Social Links': self._classify_social_links,
            'Review': self._classify_review,
            'Hours': self._classify_hours,
            'Price': self._classify_price,
            'Unknown / Junk': lambda col: 0.0  # Default fallback
        }
        
        # Common location keywords
        self.location_keywords = [
            'delhi', 'mumbai', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
            'pune', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur',
            'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri',
            'street', 'road', 'avenue', 'boulevard', 'lane', 'drive',
            'address', 'city', 'state', 'country', 'zipcode', 'pincode'
        ]
        
        # Expanded business category keywords
        self.category_keywords = [
            # Food & Dining
            'restaurant', 'cafe', 'bar', 'bakery', 'pizzeria', 'bistro', 'diner', 'buffet',
            'fast food', 'food truck', 'catering', 'brewery', 'winery', 'steakhouse',
            'sushi', 'chinese', 'italian', 'mexican', 'indian', 'thai', 'japanese',
            
            # Retail
            'shop', 'store', 'boutique', 'mall', 'outlet', 'supermarket', 'grocery',
            'convenience store', 'department store', 'electronics', 'clothing', 'shoes',
            'jewelry', 'books', 'music', 'sports goods', 'toys', 'furniture', 'hardware',
            
            # Services
            'salon', 'spa', 'barber', 'beauty', 'wellness', 'massage', 'nails',
            'dry cleaning', 'laundry', 'repair', 'maintenance', 'plumbing', 'electrical',
            'cleaning service', 'pest control', 'security', 'moving', 'storage',
            
            # Healthcare
            'hospital', 'clinic', 'pharmacy', 'dental', 'veterinary', 'medical',
            'doctor', 'dentist', 'optometry', 'physical therapy', 'mental health',
            
            # Education
            'school', 'college', 'university', 'daycare', 'preschool', 'tutoring',
            'training center', 'library', 'museum',
            
            # Professional Services
            'office', 'bank', 'insurance', 'legal', 'accounting', 'consulting',
            'real estate', 'marketing', 'advertising', 'it services', 'technology',
            
            # Entertainment & Recreation
            'gym', 'fitness', 'yoga', 'dance', 'theater', 'cinema', 'bowling',
            'golf', 'swimming', 'park', 'recreation', 'entertainment',
            
            # Automotive
            'gas station', 'auto repair', 'car wash', 'dealership', 'automotive',
            'tire shop', 'oil change', 'parking',
            
            # Accommodation
            'hotel', 'motel', 'hostel', 'bed and breakfast', 'resort', 'lodge'
        ]
        
        # Common amenities keywords
        self.amenity_keywords = [
            'wifi', 'parking', 'wheelchair accessible', 'air conditioning', 'heating',
            'pet friendly', 'outdoor seating', 'delivery', 'takeout', 'drive through',
            'credit cards accepted', 'cash only', 'reservations', 'walk-ins welcome',
            'valet parking', 'free parking', 'paid parking', 'restrooms', 'family friendly',
            'live music', 'happy hour', 'breakfast', 'lunch', 'dinner', 'late night',
            'open 24 hours', 'weekend hours', 'appointment only', 'online booking'
        ]
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Classify all columns in the dataframe and return suggestions.
        
        Args:
            df: pandas DataFrame to analyze
            
        Returns:
            Dictionary with column analysis results
        """
        results = {}
        
        for column in df.columns:
            # Get non-null values for analysis
            non_null_values = df[column].dropna()
            
            if len(non_null_values) == 0:
                results[column] = {
                    'original_name': column,
                    'suggested_category': 'Unknown / Junk',
                    'confidence': 0.0,
                    'sample_values': [],
                    'total_values': 0,
                    'non_null_values': 0
                }
                continue
            
            # Check column name for hints first
            column_name_lower = column.lower()
            column_name_bonus = self._get_column_name_bonus(column_name_lower)
            
            # Calculate confidence scores for each category
            scores = {}
            for category, classifier_func in self.categories.items():
                if category != 'Unknown / Junk':
                    base_score = classifier_func(non_null_values)
                    # Add bonus from column name
                    scores[category] = min(1.0, base_score + column_name_bonus.get(category, 0))
            
            # Find the best category
            best_category = max(scores.items(), key=lambda x: x[1])
            
            # If no category has sufficient confidence, mark as Unknown
            if best_category[1] < 0.3:
                suggested_category = 'Unknown / Junk'
                confidence = 0.0
            else:
                suggested_category = best_category[0]
                confidence = best_category[1]
            
            # Get sample values (first 5 non-null values)
            sample_values = non_null_values.head(5).tolist()
            
            results[column] = {
                'original_name': column,
                'suggested_category': suggested_category,
                'confidence': round(confidence, 2),
                'sample_values': sample_values,
                'total_values': len(df[column]),
                'non_null_values': len(non_null_values),
                'all_scores': {k: round(v, 2) for k, v in scores.items()}
            }
        
        return results
    
    def _get_column_name_bonus(self, column_name: str) -> Dict[str, float]:
        """Get bonus scores based on column name patterns."""
        bonuses = {}
        
        # Business Name indicators
        business_name_words = ['business_name', 'company_name', 'name', 'business', 'company', 'establishment']
        if any(word in column_name for word in business_name_words):
            if not any(word in column_name for word in ['type', 'category', 'kind']):
                bonuses['Business Name'] = 0.8
        
        # Phone indicators
        phone_words = ['phone', 'mobile', 'contact_phone', 'tel', 'telephone', 'cell', 'contact_number']
        if any(word in column_name for word in phone_words):
            if not any(word in column_name for word in ['rating', 'score', 'count', 'id', 'fax']):
                bonuses['Phone Number'] = 0.8
        
        # Email indicators
        email_words = ['email', 'mail', 'e_mail', 'email_address', 'contact_email']
        if any(word in column_name for word in email_words):
            bonuses['Email'] = 0.9
        
        # Category indicators
        category_words = ['type', 'category', 'kind', 'business_type', 'amenity', 'amenities', 
                         'service', 'feature', 'classification', 'genre', 'tag', 'tags']
        if any(word in column_name for word in category_words):
            bonuses['Category'] = 0.9
        
        # Location indicators
        location_words = ['address', 'location', 'city', 'state', 'country', 'zip', 'postal', 
                         'full_address', 'street', 'coordinates', 'lat', 'lng', 'longitude', 'latitude']
        if any(word in column_name for word in location_words):
            bonuses['Location'] = 0.8
        
        # Social Links indicators
        social_words = ['website', 'url', 'link', 'social', 'facebook', 'instagram', 'twitter', 
                       'website_url', 'homepage', 'web', 'site']
        if any(word in column_name for word in social_words):
            bonuses['Social Links'] = 0.8
        
        # Review indicators
        review_words = ['review', 'rating', 'feedback', 'comment', 'score', 'customer_review', 
                       'rating_score', 'stars', 'satisfaction']
        if any(word in column_name for word in review_words):
            bonuses['Review'] = 0.8
        
        # Hours indicators
        hours_words = ['hours', 'time', 'schedule', 'operating_hours', 'business_hours', 'open', 'close']
        if any(word in column_name for word in hours_words):
            bonuses['Hours'] = 0.8
        
        # Price indicators
        price_words = ['price', 'cost', 'fee', 'charge', 'rate', 'pricing', 'budget', 'expense']
        if any(word in column_name for word in price_words):
            bonuses['Price'] = 0.8
        
        return bonuses
    
    def _classify_business_name(self, series: pd.Series) -> float:
        """Classify if column contains business names."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        
        # Keywords that strongly indicate it's NOT a business name
        exclude_keywords = set(self.category_keywords + self.amenity_keywords + [
            'email', 'phone', 'address', 'location', 'city', 'state', 'zip',
            'review', 'rating', 'comment', 'feedback', 'description',
            'hours', 'open', 'closed', 'schedule', 'time',
            'price', 'cost', 'fee', 'rate', 'charge', '$', 'dollar',
            'website', 'url', 'link', 'http', 'www', '.com', '.org', '.net'
        ])
        
        # Business name indicators (proper nouns, specific patterns)
        business_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Title Case Names
            r'\b[A-Z][a-z]+\'s\b',  # Possessive names (Joe's, Mary's)
            r'\b(LLC|Inc|Corp|Ltd|Company)\b',  # Business suffixes
            r'\b(The\s+[A-Z][a-z]+)\b',  # "The Something"
            r'\b[A-Z]+\s+[A-Z]+\b'  # All caps business names
        ]
        
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip()
            value_lower = value_str.lower()
            
            # Exclude if it contains category/amenity keywords
            if any(keyword in value_lower for keyword in exclude_keywords):
                continue
            
            # Check for business name patterns
            if any(re.search(pattern, value_str) for pattern in business_patterns):
                matches += 1
            # Check for proper noun characteristics
            elif (len(value_str.split()) >= 2 and 
                  value_str[0].isupper() and 
                  not value_lower in self.category_keywords and
                  not any(amenity in value_lower for amenity in self.amenity_keywords)):
                matches += 0.8
            # Check for unique names (not common words)
            elif (len(value_str) > 3 and 
                  not value_lower in ['restaurant', 'store', 'shop', 'cafe', 'bar', 'hotel'] and
                  not any(keyword in value_lower for keyword in ['type', 'category', 'service'])):
                matches += 0.6
        
        return matches / total_count if total_count > 0 else 0.0
    
    def _classify_phone(self, series: pd.Series) -> float:
        """Classify if column contains phone numbers."""
        if series.dtype == 'object':
            str_series = series.astype(str)
        else:
            str_series = series
        
        phone_patterns = [
            r'^\+?1[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',  # US format
            r'^\+?91[-.\s]?[0-9]{10}$',  # Indian format
            r'^\+?44[-.\s]?[0-9]{10,11}$',  # UK format
            r'^\+?49[-.\s]?[0-9]{10,12}$',  # German format
            r'^\+?33[-.\s]?[0-9]{9,10}$',  # French format
            r'^\+?86[-.\s]?[0-9]{11}$',  # Chinese format
            r'^[0-9]{10}$',  # Simple 10 digit
            r'^\([0-9]{3}\)\s?[0-9]{3}-[0-9]{4}$',  # (123) 456-7890
            r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$',  # 123-456-7890
            r'^[0-9]{3}\.[0-9]{3}\.[0-9]{4}$',  # 123.456.7890
            r'^\+?[0-9]{1,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}$'  # International
        ]
        
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip()
            
            # Clean the value for digit counting
            cleaned_value = re.sub(r'[^\d+]', '', value_str)
            
            # Check if it's in valid phone number length range
            if 7 <= len(cleaned_value) <= 15:
                # Check against patterns
                if any(re.match(pattern, value_str) for pattern in phone_patterns):
                    matches += 1
                # Check for common phone indicators
                elif re.search(r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', value_str):
                    matches += 1
                # Simple digit check with common separators
                elif re.search(r'^\+?[\d\s\-\.\(\)]{7,15}$', value_str) and len(cleaned_value) >= 7:
                    matches += 0.8
        
        return matches / total_count if total_count > 0 else 0.0
    
    def _classify_email(self, series: pd.Series) -> float:
        """Classify if column contains email addresses."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        
        # Comprehensive email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Common email domains for additional validation
        common_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'icloud.com', 'mail.com', 'protonmail.com', 'zoho.com', 'yandex.com',
            'msn.com', 'live.com', 'comcast.net', 'verizon.net', 'sbcglobal.net'
        ]
        
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip().lower()
            
            # Primary email pattern match
            if re.match(email_pattern, value_str):
                matches += 1
            # Check for @ symbol and basic structure
            elif '@' in value_str and '.' in value_str:
                # Additional validation for partial matches
                parts = value_str.split('@')
                if len(parts) == 2 and len(parts[0]) > 0 and '.' in parts[1]:
                    domain = parts[1].strip()
                    # Bonus points for common domains
                    if domain in common_domains:
                        matches += 0.9
                    elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
                        matches += 0.7
        
        return matches / total_count if total_count > 0 else 0.0
    
    def _classify_category(self, series: pd.Series) -> float:
        """Classify if column contains business categories."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str).str.lower()
        
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip()
            
            # Direct keyword match
            if any(keyword in value_str for keyword in self.category_keywords):
                matches += 1
            # Check for amenity keywords (strong indicator of category)
            elif any(amenity in value_str for amenity in self.amenity_keywords):
                matches += 0.9
            # Check for category indicators
            elif any(indicator in value_str for indicator in ['type', 'service', 'cuisine', 'style', 'category']):
                matches += 0.7
            # Check for common business descriptors
            elif any(descriptor in value_str for descriptor in ['local', 'chain', 'franchise', 'independent', 'organic', 'premium']):
                matches += 0.5
        
        return matches / total_count if total_count > 0 else 0.0

    def _classify_hours(self, series: pd.Series) -> float:
        """Classify if column contains business hours."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str).str.lower()
        
        hour_patterns = [
            r'\b\d{1,2}:\d{2}\s?(am|pm|AM|PM)\b',  # 9:00 AM, 5:30 PM
            r'\b\d{1,2}(am|pm|AM|PM)\b',  # 9AM, 5PM
            r'\b\d{1,2}:\d{2}\s?-\s?\d{1,2}:\d{2}\b',  # 9:00 - 17:00
            r'\b(mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(open|closed|hours?|schedule)\b',
            r'\b24/7\b',
            r'\b\d{1,2}-\d{1,2}\b'  # 9-5
        ]
        
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
                
            total_count += 1
            value_str = str(value)
            
            if any(re.search(pattern, value_str, re.IGNORECASE) for pattern in hour_patterns):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _classify_price(self, series: pd.Series) -> float:
        """Classify if column contains price information."""
        if series.dtype == 'object':
            str_series = series.astype(str).str.lower()
        else:
            str_series = series.astype(str)
        
        price_patterns = [
            r'\$\d+(\.\d{2})?',  # $10, $10.99
            r'\b\d+\.\d{2}\b',  # 10.99
            r'\b(free|cheap|expensive|affordable|budget|premium|luxury)\b',
            r'\$+',  # $, $$, $$$, $$$$
            r'\b(price|cost|fee|rate|charge)\b'
        ]
        
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
                
            total_count += 1
            value_str = str(value)
            
            if any(re.search(pattern, value_str, re.IGNORECASE) for pattern in price_patterns):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0
    
    def _classify_location(self, series: pd.Series) -> float:
        """Classify if column contains location information."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str).str.lower()
        
        matches = 0
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
            
            # Check for location keywords
            if any(keyword in str(value) for keyword in self.location_keywords):
                matches += 1
            # Check for address patterns
            elif re.search(r'\d+.*(?:street|road|avenue|lane|drive)', str(value)):
                matches += 1
            # Check for postal code patterns
            elif re.search(r'\b\d{5,6}\b', str(value)):
                matches += 0.5
        
        return matches / len(str_series) if len(str_series) > 0 else 0.0
    
    def _classify_social_links(self, series: pd.Series) -> float:
        """Classify if column contains social media links."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str).str.lower()
        
        social_patterns = [
            r'facebook\.com',
            r'instagram\.com',
            r'twitter\.com',
            r'linkedin\.com',
            r'youtube\.com',
            r'tiktok\.com',
            r'@[a-zA-Z0-9_]+',  # Handle format
            r'https?://',  # General URL pattern
        ]
        
        matches = 0
        for value in str_series:
            if pd.isna(value) or value == 'nan':
                continue
            
            if any(re.search(pattern, str(value)) for pattern in social_patterns):
                matches += 1
        
        return matches / len(str_series) if len(str_series) > 0 else 0.0
    
    def _classify_review(self, series: pd.Series) -> float:
        """Classify if column contains reviews or ratings."""
        # Check for numeric ratings first
        if pd.api.types.is_numeric_dtype(series):
            # Check if values are in typical rating ranges
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_series) == 0:
                return 0.0
                
            min_val, max_val = numeric_series.min(), numeric_series.max()
            
            # Common rating scales
            if (0 <= min_val <= 5 and 0 <= max_val <= 5):
                return 0.9  # High confidence for 0-5 scale
            elif (1 <= min_val <= 10 and 1 <= max_val <= 10):
                return 0.8  # Good confidence for 1-10 scale
            else:
                return 0.0
        
        # Text-based reviews
        elif series.dtype == 'object':
            str_series = series.astype(str).str.lower()
            
            review_keywords = [
                'review', 'rating', 'feedback', 'comment', 'opinion',
                'good', 'bad', 'excellent', 'poor', 'great', 'terrible',
                'recommend', 'satisfied', 'disappointed', 'star', 'amazing',
                'awesome', 'fantastic', 'horrible', 'love', 'hate'
            ]
            
            matches = 0
            total_count = 0
            
            for value in str_series:
                if pd.isna(value) or value == 'nan':
                    continue
                
                total_count += 1
                value_str = str(value)
                
                # Check for review keywords
                if any(keyword in value_str for keyword in review_keywords):
                    matches += 1
                # Check for rating patterns (1-5 stars, 1-10 ratings)
                elif re.search(r'\b[1-5]\s*(?:star|out of)', value_str):
                    matches += 1
                # Long text might be reviews (more than 6 words)
                elif len(value_str.split()) > 6:
                    matches += 0.8
                # Check for numeric ratings in text
                elif re.search(r'\b[0-5]\.[0-9]\b', value_str):
                    matches += 0.9
            
            return matches / total_count if total_count > 0 else 0.0
        
        return 0.0

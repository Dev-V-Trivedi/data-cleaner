import re
import pandas as pd
from typing import Dict, List, Tuple, Any
import numpy as np
from collections import Counter
import string

class EnhancedColumnClassifier:
    """
    Enhanced column classifier with improved pattern recognition and machine learning-like features.
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
            'Unknown / Junk': lambda col: 0.0
        }
        
        # Enhanced patterns and keywords
        self._load_enhanced_patterns()
        
    def _load_enhanced_patterns(self):
        """Load enhanced patterns and keywords for better classification."""
        
        # Business name patterns
        self.business_name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Title Case Names
            r'\b[A-Z][a-z]+\'s\b',  # Possessive names
            r'\b(LLC|Inc|Corp|Ltd|Company|Co\.)\b',  # Business suffixes
            r'\b(The\s+[A-Z][a-z]+)\b',  # "The Something"
            r'\b[A-Z]{2,}\s+[A-Z][a-z]+\b',  # ACME Corp
            r'\b[A-Z][a-z]+\s+(Restaurant|Cafe|Bar|Store|Shop|Hotel)\b',  # Name + Type
            r'\b[A-Z][a-z]+\s+(& Co|and Co|Bros|Brothers)\b',  # Business partnerships
        ]
        
        # Enhanced phone patterns
        self.phone_patterns = [
            r'^\+?1[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',  # US
            r'^\+?91[-.\s]?[6-9][0-9]{9}$',  # Indian mobile
            r'^\+?44[-.\s]?[0-9]{10,11}$',  # UK
            r'^\+?49[-.\s]?[0-9]{10,12}$',  # German
            r'^\+?33[-.\s]?[0-9]{9,10}$',  # French
            r'^\+?86[-.\s]?1[0-9]{10}$',  # Chinese mobile
            r'^[6-9][0-9]{9}$',  # Indian mobile without code
            r'^\([0-9]{3}\)\s?[0-9]{3}-[0-9]{4}$',  # (123) 456-7890
            r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$',  # 123-456-7890
            r'^[0-9]{3}\.[0-9]{3}\.[0-9]{4}$',  # 123.456.7890
            r'^\+?[0-9]{1,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}$'
        ]
        
        # Enhanced email patterns
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.common_email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'icloud.com', 'mail.com', 'protonmail.com', 'zoho.com', 'yandex.com',
            'msn.com', 'live.com', 'comcast.net', 'verizon.net', 'sbcglobal.net',
            'rediffmail.com', 'indiatimes.com', 'sify.com'  # Indian domains
        ]
        
        # Enhanced location keywords
        self.location_keywords = [
            # Indian cities
            'delhi', 'mumbai', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
            'pune', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur',
            'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri',
            'vadodara', 'nashik', 'rajkot', 'varanasi', 'agra', 'gurgaon',
            # Global cities
            'new york', 'london', 'paris', 'tokyo', 'sydney', 'toronto',
            'los angeles', 'chicago', 'berlin', 'madrid', 'rome', 'moscow',
            # Address components
            'street', 'road', 'avenue', 'boulevard', 'lane', 'drive', 'circle',
            'plaza', 'square', 'court', 'way', 'place', 'terrace', 'park',
            'address', 'city', 'state', 'country', 'zipcode', 'pincode',
            'zip', 'postal', 'area', 'sector', 'block', 'plot', 'house',
            # Indian address terms
            'nagar', 'colony', 'society', 'apartment', 'complex', 'tower',
            'phase', 'extension', 'main road', 'cross', 'layout'
        ]
        
        # Enhanced category keywords with weights
        self.category_keywords = {
            # Food & Dining (high confidence)
            'restaurant': 0.95, 'cafe': 0.95, 'bar': 0.95, 'bakery': 0.9,
            'pizzeria': 0.9, 'bistro': 0.9, 'diner': 0.9, 'buffet': 0.9,
            'fast food': 0.95, 'food truck': 0.9, 'catering': 0.9,
            'brewery': 0.9, 'winery': 0.9, 'steakhouse': 0.9,
            
            # Cuisine types
            'sushi': 0.85, 'chinese': 0.8, 'italian': 0.8, 'mexican': 0.8,
            'indian': 0.8, 'thai': 0.8, 'japanese': 0.8, 'american': 0.7,
            
            # Retail
            'shop': 0.9, 'store': 0.9, 'boutique': 0.9, 'mall': 0.95,
            'outlet': 0.9, 'supermarket': 0.95, 'grocery': 0.9,
            'convenience store': 0.95, 'department store': 0.95,
            
            # Services
            'salon': 0.95, 'spa': 0.95, 'barber': 0.95, 'beauty': 0.85,
            'wellness': 0.8, 'massage': 0.9, 'nails': 0.9,
            'dry cleaning': 0.95, 'laundry': 0.9, 'repair': 0.8,
            
            # Healthcare
            'hospital': 0.95, 'clinic': 0.95, 'pharmacy': 0.95,
            'dental': 0.95, 'veterinary': 0.95, 'medical': 0.85,
            'doctor': 0.9, 'dentist': 0.95,
            
            # Professional Services
            'bank': 0.95, 'atm': 0.95, 'insurance': 0.9, 'legal': 0.9,
            'accounting': 0.9, 'consulting': 0.85, 'real estate': 0.9,
            
            # Entertainment
            'gym': 0.95, 'fitness': 0.9, 'yoga': 0.9, 'theater': 0.95,
            'cinema': 0.95, 'movie': 0.9, 'bowling': 0.95, 'golf': 0.95,
            
            # Automotive
            'gas station': 0.95, 'petrol pump': 0.95, 'auto repair': 0.95,
            'car wash': 0.95, 'dealership': 0.9, 'parking': 0.9,
            
            # Accommodation
            'hotel': 0.95, 'motel': 0.95, 'hostel': 0.9, 'resort': 0.95
        }
        
        # Social media patterns
        self.social_patterns = [
            r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?twitter\.com/[a-zA-Z0-9._-]+',
            r'https?://(?:www\.)?linkedin\.com/[a-zA-Z0-9._/-]+',
            r'https?://(?:www\.)?youtube\.com/[a-zA-Z0-9._/-]+',
            r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[/a-zA-Z0-9._-]*',
            r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9.-]+\.(com|org|net|in|co\.in|edu|gov)'
        ]
        
        # Column name indicators (enhanced)
        self.column_name_indicators = {
            'Business Name': {
                'strong': ['business_name', 'company_name', 'establishment_name', 'shop_name'],
                'medium': ['name', 'business', 'company', 'establishment', 'title'],
                'weak': ['store', 'shop']
            },
            'Phone Number': {
                'strong': ['phone', 'mobile', 'contact_phone', 'telephone', 'phone_number'],
                'medium': ['tel', 'cell', 'contact_number', 'contact'],
                'weak': ['number']
            },
            'Email': {
                'strong': ['email', 'email_address', 'contact_email', 'e_mail'],
                'medium': ['mail', 'contact_mail'],
                'weak': []
            },
            'Category': {
                'strong': ['category', 'type', 'business_type', 'classification'],
                'medium': ['kind', 'genre', 'service_type', 'amenity'],
                'weak': ['tag', 'tags', 'feature']
            },
            'Location': {
                'strong': ['address', 'location', 'full_address', 'street_address'],
                'medium': ['city', 'state', 'country', 'zip', 'postal', 'coordinates'],
                'weak': ['area', 'region', 'place']
            },
            'Social Links': {
                'strong': ['website', 'website_url', 'homepage', 'social_media'],
                'medium': ['url', 'link', 'web', 'site'],
                'weak': ['facebook', 'instagram', 'twitter']
            },
            'Review': {
                'strong': ['review', 'rating', 'customer_review', 'feedback'],
                'medium': ['comment', 'score', 'rating_score', 'stars'],
                'weak': ['satisfaction']
            }
        }

    def classify_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Enhanced column classification with improved accuracy."""
        results = {}
        
        for column in df.columns:
            non_null_values = df[column].dropna()
            
            if len(non_null_values) == 0:
                results[column] = self._create_empty_result(column, len(df[column]))
                continue
            
            # Multi-factor analysis
            column_name_score = self._analyze_column_name(column.lower())
            content_scores = self._analyze_column_content(non_null_values)
            pattern_scores = self._analyze_patterns(non_null_values)
            statistical_scores = self._analyze_statistics(non_null_values)
            
            # Combine scores with weights
            final_scores = {}
            for category in self.categories.keys():
                if category != 'Unknown / Junk':
                    final_scores[category] = (
                        column_name_score.get(category, 0) * 0.4 +  # Column name is important
                        content_scores.get(category, 0) * 0.3 +     # Content analysis
                        pattern_scores.get(category, 0) * 0.2 +     # Pattern matching
                        statistical_scores.get(category, 0) * 0.1   # Statistical features
                    )
            
            # Find best category with confidence threshold
            best_category = max(final_scores.items(), key=lambda x: x[1])
            
            if best_category[1] < 0.25:  # Lower threshold for better sensitivity
                suggested_category = 'Unknown / Junk'
                confidence = 0.0
            else:
                suggested_category = best_category[0]
                confidence = min(1.0, best_category[1])
            
            # Enhanced sample values
            sample_values = self._get_enhanced_samples(non_null_values, suggested_category)
            
            results[column] = {
                'original_name': column,
                'suggested_category': suggested_category,
                'confidence': round(confidence, 3),
                'sample_values': sample_values,
                'total_values': len(df[column]),
                'non_null_values': len(non_null_values),
                'all_scores': {k: round(v, 3) for k, v in final_scores.items()},
                'analysis_details': {
                    'column_name_score': {k: round(v, 3) for k, v in column_name_score.items()},
                    'content_score': {k: round(v, 3) for k, v in content_scores.items()},
                    'pattern_score': {k: round(v, 3) for k, v in pattern_scores.items()},
                    'statistical_score': {k: round(v, 3) for k, v in statistical_scores.items()}
                }
            }
        
        return results

    def _analyze_column_name(self, column_name: str) -> Dict[str, float]:
        """Enhanced column name analysis."""
        scores = {}
        
        for category, indicators in self.column_name_indicators.items():
            score = 0.0
            
            # Strong indicators
            for indicator in indicators['strong']:
                if indicator in column_name:
                    score = max(score, 0.9)
            
            # Medium indicators
            for indicator in indicators['medium']:
                if indicator in column_name:
                    score = max(score, 0.6)
            
            # Weak indicators
            for indicator in indicators['weak']:
                if indicator in column_name:
                    score = max(score, 0.3)
            
            scores[category] = score
        
        return scores

    def _analyze_column_content(self, series: pd.Series) -> Dict[str, float]:
        """Analyze actual content of the column."""
        scores = {}
        
        for category, classifier_func in self.categories.items():
            if category != 'Unknown / Junk':
                scores[category] = classifier_func(series)
        
        return scores

    def _analyze_patterns(self, series: pd.Series) -> Dict[str, float]:
        """Enhanced pattern analysis."""
        scores = {category: 0.0 for category in self.categories.keys() if category != 'Unknown / Junk'}
        
        if series.dtype != 'object':
            return scores
        
        str_series = series.astype(str)
        total_count = len(str_series)
        
        for category in scores.keys():
            if category == 'Phone Number':
                scores[category] = self._pattern_score_phone(str_series)
            elif category == 'Email':
                scores[category] = self._pattern_score_email(str_series)
            elif category == 'Social Links':
                scores[category] = self._pattern_score_social(str_series)
            elif category == 'Business Name':
                scores[category] = self._pattern_score_business_name(str_series)
        
        return scores

    def _analyze_statistics(self, series: pd.Series) -> Dict[str, float]:
        """Statistical analysis of column data."""
        scores = {category: 0.0 for category in self.categories.keys() if category != 'Unknown / Junk'}
        
        if len(series) == 0:
            return scores
        
        # Length statistics
        if series.dtype == 'object':
            str_series = series.astype(str)
            lengths = [len(str(x)) for x in str_series if str(x) != 'nan']
            
            if lengths:
                avg_length = np.mean(lengths)
                std_length = np.std(lengths)
                
                # Phone numbers typically 10-15 characters
                if 8 <= avg_length <= 16 and std_length < 5:
                    scores['Phone Number'] += 0.3
                
                # Emails typically 15-30 characters
                if 10 <= avg_length <= 40 and std_length < 15:
                    scores['Email'] += 0.2
                
                # Business names typically 10-50 characters
                if 5 <= avg_length <= 60:
                    scores['Business Name'] += 0.1
        
        # Uniqueness ratio
        unique_ratio = len(series.unique()) / len(series)
        
        # High uniqueness suggests names, emails, phones
        if unique_ratio > 0.8:
            scores['Business Name'] += 0.2
            scores['Email'] += 0.2
            scores['Phone Number'] += 0.2
        
        # Low uniqueness suggests categories
        if unique_ratio < 0.3:
            scores['Category'] += 0.3
        
        return scores

    def _pattern_score_phone(self, str_series: pd.Series) -> float:
        """Enhanced phone number pattern scoring."""
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip()
            
            # Enhanced phone validation
            if self._is_valid_phone(value_str):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _pattern_score_email(self, str_series: pd.Series) -> float:
        """Enhanced email pattern scoring."""
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip().lower()
            
            if self._is_valid_email(value_str):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _pattern_score_social(self, str_series: pd.Series) -> float:
        """Social media/website pattern scoring."""
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip().lower()
            
            if any(re.search(pattern, value_str, re.IGNORECASE) for pattern in self.social_patterns):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _pattern_score_business_name(self, str_series: pd.Series) -> float:
        """Enhanced business name pattern scoring."""
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip()
            
            if self._is_likely_business_name(value_str):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _is_valid_phone(self, phone_str: str) -> bool:
        """Enhanced phone validation."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_str)
        
        # Check length
        if not (7 <= len(cleaned.replace('+', '')) <= 15):
            return False
        
        # Check against patterns
        return any(re.match(pattern, phone_str) for pattern in self.phone_patterns)

    def _is_valid_email(self, email_str: str) -> bool:
        """Enhanced email validation."""
        if not re.match(self.email_pattern, email_str):
            return False
        
        # Additional validation
        if email_str.count('@') != 1:
            return False
        
        local, domain = email_str.split('@')
        if len(local) == 0 or len(domain) < 3:
            return False
        
        return True

    def _is_likely_business_name(self, name_str: str) -> bool:
        """Enhanced business name detection."""
        name_lower = name_str.lower()
        
        # Exclude obvious non-business names
        exclude_keywords = set(self.category_keywords.keys()) | {
            'email', 'phone', 'address', 'location', 'review', 'rating',
            'website', 'url', 'hours', 'price', 'cost'
        }
        
        if any(keyword in name_lower for keyword in exclude_keywords):
            return False
        
        # Check for business name patterns
        return any(re.search(pattern, name_str) for pattern in self.business_name_patterns)

    def _get_enhanced_samples(self, series: pd.Series, category: str) -> List[str]:
        """Get representative sample values."""
        samples = []
        unique_values = series.unique()
        
        # Get diverse samples
        for i, value in enumerate(unique_values[:5]):
            if pd.notna(value):
                samples.append(str(value))
        
        return samples

    def _create_empty_result(self, column: str, total_values: int) -> Dict[str, Any]:
        """Create result for empty columns."""
        return {
            'original_name': column,
            'suggested_category': 'Unknown / Junk',
            'confidence': 0.0,
            'sample_values': [],
            'total_values': total_values,
            'non_null_values': 0,
            'all_scores': {},
            'analysis_details': {}
        }

    # Include the original classification methods with enhancements
    def _classify_business_name(self, series: pd.Series) -> float:
        """Enhanced business name classification."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            if self._is_likely_business_name(str(value)):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _classify_phone(self, series: pd.Series) -> float:
        """Enhanced phone classification."""
        return self._pattern_score_phone(series.astype(str) if series.dtype == 'object' else series)

    def _classify_email(self, series: pd.Series) -> float:
        """Enhanced email classification."""
        if series.dtype != 'object':
            return 0.0
        return self._pattern_score_email(series.astype(str))

    def _classify_category(self, series: pd.Series) -> float:
        """Enhanced category classification."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_lower = str(value).lower().strip()
            
            # Check against category keywords with weights
            for keyword, weight in self.category_keywords.items():
                if keyword in value_lower:
                    matches += weight
                    break
        
        return min(1.0, matches / total_count) if total_count > 0 else 0.0

    def _classify_location(self, series: pd.Series) -> float:
        """Enhanced location classification."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        matches = 0
        total_count = 0
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_lower = str(value).lower().strip()
            
            # Address patterns
            if any(keyword in value_lower for keyword in self.location_keywords):
                matches += 1
            # ZIP/Postal code patterns
            elif re.search(r'\b\d{5,6}\b', value_lower):
                matches += 0.8
            # Coordinate patterns
            elif re.search(r'-?\d+\.\d+', value_lower):
                matches += 0.7
        
        return matches / total_count if total_count > 0 else 0.0

    def _classify_social_links(self, series: pd.Series) -> float:
        """Enhanced social links classification."""
        if series.dtype != 'object':
            return 0.0
        return self._pattern_score_social(series.astype(str))

    def _classify_review(self, series: pd.Series) -> float:
        """Enhanced review classification."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        matches = 0
        total_count = 0
        
        review_indicators = [
            'good', 'bad', 'excellent', 'poor', 'great', 'terrible',
            'recommend', 'satisfied', 'disappointed', 'amazing',
            'awful', 'fantastic', 'horrible', 'wonderful', 'disgusting',
            'stars', 'rating', 'review', 'feedback', 'comment'
        ]
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_lower = str(value).lower().strip()
            
            # Check for review indicators
            if any(indicator in value_lower for indicator in review_indicators):
                matches += 1
            # Check for rating patterns (1-5 stars, 1-10 ratings)
            elif re.search(r'\b[1-5]\s*star', value_lower) or re.search(r'\b[1-9]\.?\d*/10\b', value_lower):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _classify_hours(self, series: pd.Series) -> float:
        """Enhanced hours classification."""
        if series.dtype != 'object':
            return 0.0
        
        str_series = series.astype(str)
        matches = 0
        total_count = 0
        
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)\b',  # 9:00 AM
            r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)\s*-\s*\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)\b',  # 9 AM - 5 PM
            r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\b(Open|Closed|24/7|24 hours)\b',
            r'\b\d{1,2}-\d{1,2}\b'  # 9-5
        ]
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_str = str(value).strip()
            
            if any(re.search(pattern, value_str, re.IGNORECASE) for pattern in time_patterns):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

    def _classify_price(self, series: pd.Series) -> float:
        """Enhanced price classification."""
        str_series = series.astype(str)
        matches = 0
        total_count = 0
        
        price_patterns = [
            r'\$\d+(\.\d{2})?',  # $10.99
            r'₹\d+(\.\d{2})?',   # ₹100.50
            r'\b\d+\s*dollars?\b',
            r'\b\d+\s*rupees?\b',
            r'\b(cheap|expensive|affordable|budget|premium|luxury)\b',
            r'\b\$+\b'  # $ symbols
        ]
        
        for value in str_series:
            if pd.isna(value) or str(value) == 'nan':
                continue
                
            total_count += 1
            value_lower = str(value).lower().strip()
            
            if any(re.search(pattern, value_lower, re.IGNORECASE) for pattern in price_patterns):
                matches += 1
        
        return matches / total_count if total_count > 0 else 0.0

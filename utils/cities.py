from __future__ import annotations

# Top US cities for autocomplete — covers major metros and popular trip origins
US_CITIES = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
    "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
    "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL",
    "Fort Worth, TX", "Columbus, OH", "Charlotte, NC", "Indianapolis, IN",
    "San Francisco, CA", "Seattle, WA", "Denver, CO", "Nashville, TN",
    "Oklahoma City, OK", "El Paso, TX", "Washington, DC", "Boston, MA",
    "Las Vegas, NV", "Louisville, KY", "Memphis, TN", "Portland, OR",
    "Baltimore, MD", "Milwaukee, WI", "Albuquerque, NM", "Tucson, AZ",
    "Fresno, CA", "Sacramento, CA", "Kansas City, MO", "Mesa, AZ",
    "Atlanta, GA", "Omaha, NE", "Colorado Springs, CO", "Raleigh, NC",
    "Miami, FL", "Long Beach, CA", "Virginia Beach, VA", "Oakland, CA",
    "Minneapolis, MN", "Tampa, FL", "New Orleans, LA", "Arlington, TX",
    "Bakersfield, CA", "Honolulu, HI", "Anchorage, AK", "Salt Lake City, UT",
    "Pittsburgh, PA", "Cincinnati, OH", "Cleveland, OH", "Orlando, FL",
    "St. Louis, MO", "Riverside, CA", "Lexington, KY", "Buffalo, NY",
    "Corpus Christi, TX", "St. Paul, MN", "Newark, NJ", "Detroit, MI",
    "Madison, WI", "Toledo, OH", "Greensboro, NC", "Chandler, AZ",
    "Scottsdale, AZ", "Boise, ID", "Birmingham, AL", "Rochester, NY",
    "Richmond, VA", "Spokane, WA", "Des Moines, IA", "Tacoma, WA",
    "San Bernardino, CA", "Modesto, CA", "Fontana, CA", "Moreno Valley, CA",
    "Glendale, AZ", "Fayetteville, NC", "Akron, OH", "Yonkers, NY",
    "Huntington Beach, CA", "Columbus, GA", "Durham, NC", "Garland, TX",
    "Shreveport, LA", "Tempe, AZ", "Knoxville, TN", "Fort Wayne, IN",
    "Providence, RI", "Chattanooga, TN", "Oxnard, CA", "Eugene, OR",
    "Hartford, CT", "Bridgeport, CT", "Little Rock, AR", "Jackson, MS",
]

def search_cities(query: str) -> list:
    """Filter cities by query string — case insensitive."""
    if not query:
        return US_CITIES[:10]
    q = query.lower()
    return [c for c in US_CITIES if q in c.lower()][:10]
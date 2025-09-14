-- Create a test restaurant for integration testing
-- This restaurant will be used by test scripts

INSERT INTO restaurants (
    id,
    name,
    cuisine,
    description,
    address,
    price_level,
    rating,
    review_count
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    'Test Restaurant',
    'Test Cuisine',
    'A test restaurant for integration testing',
    '123 Test Street, Test City, TC 12345',
    2,
    4.5,
    100
) ON CONFLICT (id) DO NOTHING;

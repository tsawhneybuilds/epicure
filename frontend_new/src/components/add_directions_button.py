import re

# Read the SwipeCard.tsx file
with open('SwipeCard.tsx', 'r') as f:
    content = f.read()

# Add the directions button after the restaurant info section
directions_button = '''
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-green-500" />
                <span className="text-sm">{menuItem.restaurant.distance}</span>
              </div>
              {(menuItem.restaurant.lat && menuItem.restaurant.lng) || menuItem.restaurant.address ? (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openDirections();
                  }}
                  className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-md text-sm hover:bg-blue-600 transition-colors"
                >
                  <Navigation className="w-4 h-4" />
                  Directions
                </button>
              ) : null}
'''

# Find the MapPin section and replace it with the enhanced version
pattern = r'(              <div className="flex items-center gap-2">\n                <MapPin className="w-4 h-4 text-green-500" />\n                <span className="text-sm">\{menuItem\.restaurant\.distance\}</span>\n              </div>)'
replacement = directions_button

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the updated content back
with open('SwipeCard.tsx', 'w') as f:
    f.write(content)

print("Added directions button to SwipeCard.tsx")

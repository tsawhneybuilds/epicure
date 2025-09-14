import re

# Read the SwipeCard.tsx file
with open('SwipeCard.tsx', 'r') as f:
    content = f.read()

# Add the directions function after the getHighlightInfo function
directions_function = '''
  const openDirections = () => {
    if (menuItem.restaurant.lat && menuItem.restaurant.lng) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${menuItem.restaurant.lat},${menuItem.restaurant.lng}`;
      window.open(url, '_blank');
    } else if (menuItem.restaurant.address) {
      const url = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(menuItem.restaurant.address)}`;
      window.open(url, '_blank');
    }
  };
'''

# Find the end of getHighlightInfo function and add the directions function
pattern = r'(  const getHighlightInfo = \(\) => \{[^}]*\};\n)'
replacement = r'\1' + directions_function

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the updated content back
with open('SwipeCard.tsx', 'w') as f:
    f.write(content)

print("Added directions function to SwipeCard.tsx")

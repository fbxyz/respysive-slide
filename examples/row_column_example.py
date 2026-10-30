"""Example demonstrating Row and Column layout functionality.

This example shows how to use the new Row and Column classes to create
complex nested Bootstrap grid layouts in respysive presentations.
"""

import os
import sys

# Add parent directory to path to use local respysive instead of installed version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from respysive import Column, Presentation, Row, Slide

# Create presentation
pres = Presentation()

# Example 1: Simple two-column layout
slide1 = Slide()
slide1.add_title("Example 1: Simple Two-Column Layout")

layout1 = Row([Column(8, "Main content area (8 columns wide)"), Column(4, "Sidebar content (4 columns wide)")])
slide1.add_layout(layout1)
pres.add_slide(slide1)

# Example 2: Nested layout - chart with stacked sidebar
slide2 = Slide()
slide2.add_title("Example 2: Nested Layout")

layout2 = Row(
    [
        Column(8, "Large chart or visualization would go here"),
        Column(
            4,
            [
                Row("Header text for sidebar"),
                Row("First sidebar item"),
                Row("Second sidebar item"),
                Row("Third sidebar item"),
            ],
        ),
    ]
)
slide2.add_layout(layout2)
pres.add_slide(slide2)

# Example 3: Layout with gap and alignment
slide3 = Slide()
slide3.add_title("Example 3: Gap and Alignment")

layout3 = Row(
    [Column(4, "Column 1"), Column(4, "Column 2"), Column(4, "Column 3")],
    gap=3,
    align_items="center",
    justify_content="between",
)
slide3.add_layout(layout3)
pres.add_slide(slide3)

# Example 4: Responsive layout (desktop vs mobile)
slide4 = Slide()
slide4.add_title("Example 4: Responsive Layout")

layout4 = Row(
    [
        Column({"md": 8, "sm": 12}, "8 columns on desktop, full width on mobile"),
        Column({"md": 4, "sm": 12}, "4 columns on desktop, full width on mobile"),
    ]
)
slide4.add_layout(layout4)
pres.add_slide(slide4)

# Example 5: Complex nested layout
slide5 = Slide()
slide5.add_title("Example 5: Complex Nested Layout")

layout5 = Row(
    [
        Column(6, [Row("Title section"), Row([Column(6, "Sub-column 1"), Column(6, "Sub-column 2")])]),
        Column(6, "Right side content"),
    ],
    gap=3,
)
slide5.add_layout(layout5)
pres.add_slide(slide5)

# Example 6: Layout with custom styling
slide6 = Slide()
slide6.add_title("Example 6: Custom Styling")

layout6 = Row(
    [
        Column(6, "Bordered column", **{"class": "border rounded", "padding": "20px", "background_color": "#f8f9fa"}),
        Column(
            6, "Another styled column", **{"class": "border rounded", "padding": "20px", "background_color": "#e9ecef"}
        ),
    ],
    gap=2,
)
slide6.add_layout(layout6)
pres.add_slide(slide6)

# Example 7: Using offset and order
slide7 = Slide()
slide7.add_title("Example 7: Offset and Order")

layout7 = Row(
    [Column(4, "Displayed second (order=2)", offset=2, order=2), Column(4, "Displayed first (order=1)", order=1)]
)
slide7.add_layout(layout7)
pres.add_slide(slide7)

# Example 8: Backward compatibility - old and new system together
slide8 = Slide()
slide8.add_title("Example 8: Backward Compatibility")

# Old system still works
slide8.add_content(["Using old add_content()", "Still works perfectly!"], columns=[6, 6])

# New system works alongside it
layout8 = Row([Column(12, "And you can use Row/Column on the same slide!")])
slide8.add_layout(layout8)
pres.add_slide(slide8)

# Save presentation
pres.save_html("row_column_example.html", theme="black")
print("✅ Example presentation created: row_column_example.html")
print("\nThe presentation demonstrates:")
print("- Simple two-column layouts")
print("- Nested rows and columns")
print("- Gap and alignment utilities")
print("- Responsive column widths")
print("- Complex nested structures")
print("- Custom styling with kwargs")
print("- Offset and order features")
print("- Backward compatibility with add_content()")

# GCP Project Selector Container Specifications

**Document Type**: UI/UX Design Specification
**Component**: Project Selector Container (Excluding Dropdown Arrow)
**Author**: Senior UI/UX Designer - Google Cloud Platform
**Date**: December 16, 2024

---

## IMPORTANT NOTE

This specification covers ONLY the rectangular container around the project name. The dropdown arrow/chevron is explicitly EXCLUDED from this documentation.

---

## 1. EXACT DIMENSIONS

### Container Measurements

- **Width**:
  - Type: Flexible width
  - Min-width: Not explicitly set in GCP (relies on content)
  - Max-width: Approximately 280px
  - Actual rendered width: Varies based on project name length
- **Height**: 32px (exact)
- **Box Model**: Border-box sizing

---

## 2. POSITIONING

### Distance Measurements

- **From Logo/Brand Text**:
  - Left margin: 16px
- **From Search Bar**:
  - Right margin: Variable (search bar is centered in remaining space)
- **Vertical Alignment**:
  - Centered within 48px header height
  - 8px from top and bottom of header

---

## 3. CONTAINER STYLING

### Background

- **Normal State**: rgba(0, 0, 0, 0) - Fully transparent
- **No fill color in default state**

### Border Properties

- **Border Style**: Solid
- **Border Width**: 1px on all sides
- **Border Color**:
  - Normal: #E8EAED1F (rgba(232, 234, 237, 0.122))
  - Very subtle, almost invisible border
- **Border Radius**: 8px (all corners)

### Shadows/Elevation

- **Box Shadow**: None
- **Elevation**: 0 (flat on surface)

### Internal Padding

- **Top**: 5px
- **Right**: 8px
- **Bottom**: 5px
- **Left**: 8px
- **Total clickable area**: Entire container

---

## 4. TEXT CONTENT STYLING

### Project Name Typography

- **Color**: #E8EAED (rgb(232, 234, 237))
- **Font Family**: "Google Sans Text", Roboto, Arial, sans-serif
- **Font Size**: 14px
- **Font Weight**: 400 (Regular)
- **Line Height**: 20px
- **Letter Spacing**: 0.2px
- **Text Transform**: None
- **Text Decoration**: None

### Text Behavior

- **Alignment**: Left-aligned within container
- **Overflow**: Hidden
- **Text Overflow**: Ellipsis
- **White Space**: No-wrap
- **Max Display Width**: Calculated based on container width minus icon spacing

---

## 5. INTERACTIVE STATES

### Hover State

- **Background Color**: rgba(232, 234, 237, 0.078) - Subtle white overlay
- **Border Color**: rgba(232, 234, 237, 0.122) - Slightly more visible
- **Text Color**: No change (#E8EAED)
- **Cursor**: Pointer
- **Shadow**: None

### Active/Pressed State

- **Background Color**: rgba(232, 234, 237, 0.122) - Darker overlay
- **Border Color**: rgba(232, 234, 237, 0.161)
- **Duration**: Applied while mouse button is held down

### Focus State (Keyboard Navigation)

- **Outline**: 2px solid #8AB4F8
- **Outline Offset**: 2px
- **Border Color**: Transparent (outline replaces border visual)
- **Background**: Same as hover state

---

## 6. SPACING

### Internal Content Layout

- **Icon to Text Gap**: 8px
- **Text to Container Edge**:
  - Left: 8px padding + icon width + 8px gap
  - Right: Variable (text grows to fill available space)

### Container Margins

- **Top Margin**: 0
- **Right Margin**: 0
- **Bottom Margin**: 0
- **Left Margin**: 16px from logo

---

## 7. TRANSITIONS

### Animation Properties

- **Duration**: 150ms for all transitions
- **Easing Function**: cubic-bezier(0.4, 0, 0.2, 1) - Google Material standard easing
- **Properties That Transition**:
  - background-color
  - border-color
  - box-shadow (for focus)

### Transition Triggers

- Mouse enter/leave (hover states)
- Focus/blur (keyboard navigation)
- Mouse down/up (active states)

---

## ADDITIONAL SPECIFICATIONS

### Accessibility

- **Role**: Button
- **ARIA Label**: "Select a project"
- **Keyboard Accessible**: Yes
- **Tab Index**: 0

### Responsive Behavior

- Container maintains fixed height across all viewports
- Width adjusts based on content and available space
- Text truncates with ellipsis on smaller screens

### Dark Theme Values (Currently Active)

All specifications above are for the dark theme implementation currently visible in the Google Cloud Console.

---

## EXCLUDED FROM THIS SPECIFICATION

- Dropdown arrow/chevron icon
- Dropdown menu that appears on click
- Project icon/badge on the left
- Any animation of the dropdown arrow
- Menu positioning or behavior

This document focuses EXCLUSIVELY on the container rectangle that houses the project name.

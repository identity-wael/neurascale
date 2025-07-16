# Google Cloud Platform Menu Bar Specification Document

## Overview

This document provides a comprehensive specification for implementing Google Cloud Platform (GCP) console menu bar styling in the NeuraScale Console application. All measurements and specifications are based on analysis of the actual GCP console interface.

⚠️ **CRITICAL REQUIREMENT**: The NEURASCALE logo/brand text must remain EXACTLY as currently implemented. This specification covers all other menu bar elements.

---

## 1. DIMENSIONS & LAYOUT

### Header Container

- **Height**: 48px
- **Background Color**: #303134 (dark theme)
- **Border Bottom**: 1px solid rgba(255, 255, 255, 0.08)
- **Display**: Flex
- **Align Items**: Center
- **Padding**: 0 8px

### Container Structure

- **Max Width**: Full width (100%)
- **Layout**: Three sections (left, center, right)
  - Left: Navigation button + Logo/Brand + Project selector
  - Center: Search bar
  - Right: Action buttons + User avatar

---

## 2. NAVIGATION MENU BUTTON

### Dimensions & Positioning

- **Size**: 40px × 40px
- **Margin from left edge**: 4px
- **Icon size**: 20px × 20px (centered)
- **Icon stroke width**: 2px
- **Icon color**: #E8EAED

### Interactive States

- **Default**: Background transparent
- **Hover**:
  - Background: rgba(255, 255, 255, 0.08)
  - Border-radius: 4px
  - Transition: background-color 200ms
- **Active/Pressed**:
  - Background: rgba(255, 255, 255, 0.12)
- **Focus**:
  - Outline: 2px solid #8AB4F8
  - Outline-offset: -2px

---

## 3. LOGO & BRAND AREA

### ⚠️ NEURASCALE Logo (DO NOT CHANGE)

- **Current Implementation**: Keep EXACTLY as is
- **Text**: "NEURASCALE" (split as "NEURA" and "SCALE")
- **Colors**: Keep existing colors unchanged
- **Font**: Keep existing font unchanged
- **Size**: Keep existing size unchanged

### Spacing Around Logo

- **Left margin**: 8px (from navigation button)
- **Right margin**: 16px (before project selector)

---

## 4. PROJECT SELECTOR

### Container

- **Height**: 36px
- **Min-width**: 200px
- **Max-width**: 280px
- **Background**: Transparent
- **Border**: 1px solid transparent
- **Border-radius**: 4px
- **Padding**: 0 12px
- **Display**: Flex
- **Align-items**: Center
- **Gap**: 8px

### Typography

- **Font-family**: "Google Sans", Roboto, Arial, sans-serif
- **Font-size**: 14px
- **Font-weight**: 400
- **Color**: #E8EAED
- **Line-height**: 20px

### Icons

- **Folder icon (left)**:
  - Size: 16px × 16px
  - Color: #8AB4F8
- **Dropdown arrow (right)**:
  - Size: 20px × 20px
  - Color: #9AA0A6

### Interactive States

- **Hover**:
  - Background: rgba(255, 255, 255, 0.08)
  - Border: 1px solid rgba(255, 255, 255, 0.08)
- **Focus**:
  - Border: 1px solid #8AB4F8
  - Outline: none
- **Active**:
  - Background: rgba(255, 255, 255, 0.12)

---

## 5. SEARCH BAR

### Container

- **Max-width**: 720px
- **Height**: 40px
- **Background**: #202124
- **Border**: 1px solid #5F6368
- **Border-radius**: 4px
- **Display**: Flex
- **Align-items**: Center
- **Margin**: 0 16px
- **Flex**: 1 1 auto

### Search Icon

- **Size**: 20px × 20px
- **Color**: #9AA0A6
- **Position**: Left side
- **Margin**: 0 12px

### Input Field

- **Font-family**: Roboto, Arial, sans-serif
- **Font-size**: 14px
- **Color**: #E8EAED
- **Line-height**: 20px
- **Background**: Transparent
- **Border**: None
- **Outline**: None
- **Flex**: 1
- **Placeholder color**: #9AA0A6

### Search Button

- **Position**: Right side within search bar
- **Height**: 32px
- **Padding**: 0 24px
- **Margin-right**: 4px
- **Background**: #1A73E8
- **Border**: None
- **Border-radius**: 4px
- **Font-family**: "Google Sans", Roboto, Arial, sans-serif
- **Font-size**: 14px
- **Font-weight**: 500
- **Color**: #FFFFFF
- **Letter-spacing**: 0.25px

### Focus State

- **Border-color**: #8AB4F8
- **Box-shadow**: 0 0 0 1px #8AB4F8

### Search Button Hover

- **Background**: #1765CC
- **Box-shadow**: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)

---

## 6. RIGHT-SIDE ACTION BUTTONS

### Container

- **Display**: Flex
- **Gap**: 4px
- **Align-items**: Center

### Individual Buttons

- **Size**: 40px × 40px
- **Border-radius**: 50%
- **Background**: Transparent
- **Icon size**: 20px × 20px
- **Icon color**: #E8EAED

### Button Order (left to right)

1. Gemini AI Assistant
2. Cloud Shell
3. Notifications (with badge if applicable)
4. Help
5. Settings
6. User Avatar

### Interactive States (for all buttons)

- **Hover**:
  - Background: rgba(255, 255, 255, 0.08)
- **Active**:
  - Background: rgba(255, 255, 255, 0.12)
- **Focus**:
  - Outline: 2px solid #8AB4F8
  - Outline-offset: -2px

### Notification Badge

- **Size**: 16px minimum width
- **Height**: 16px
- **Background**: #EA4335
- **Color**: #FFFFFF
- **Font-size**: 11px
- **Font-weight**: 500
- **Border-radius**: 8px
- **Position**: Absolute, top-right of button
- **Padding**: 0 4px

### User Avatar

- **Size**: 32px × 32px
- **Border-radius**: 50%
- **Margin-left**: 8px

---

## 7. COLOR PALETTE

### Primary Colors

- **Background (Dark)**: #303134
- **Surface (Dark)**: #202124
- **Text Primary**: #E8EAED
- **Text Secondary**: #9AA0A6
- **Border Default**: #5F6368
- **Border Subtle**: rgba(255, 255, 255, 0.08)

### Interactive Colors

- **Primary Blue**: #1A73E8
- **Primary Blue Hover**: #1765CC
- **Focus Blue**: #8AB4F8
- **Icon Blue**: #8AB4F8
- **Error Red**: #EA4335

### State Colors

- **Hover Background**: rgba(255, 255, 255, 0.08)
- **Active Background**: rgba(255, 255, 255, 0.12)
- **Disabled**: rgba(255, 255, 255, 0.38)

---

## 8. SPACING RHYTHM

### Consistent Spacing Units

- **Base unit**: 4px
- **Common spacings**:
  - 4px: Minimum spacing between elements
  - 8px: Standard spacing between related elements
  - 12px: Padding within components
  - 16px: Spacing between sections
  - 24px: Large spacing between major sections

### Specific Spacings

- Navigation button to logo: 8px
- Logo to project selector: 16px
- Project selector to search bar: 16px
- Search bar to right buttons: 16px
- Between action buttons: 4px
- Action buttons to user avatar: 8px

---

## Typography System

### Font Stack

```css
font-family: "Google Sans", Roboto, Arial, sans-serif;
```

### Font Weights

- Regular: 400
- Medium: 500

### Font Sizes

- Primary text: 14px
- Small text: 12px
- Badge text: 11px

### Line Heights

- Default: 20px
- Compact: 16px

---

## Implementation Notes

1. **Flexbox Layout**: The entire header uses flexbox for alignment and responsive behavior
2. **Focus Management**: All interactive elements must have proper focus states for accessibility
3. **Transitions**: Use 200ms transitions for hover states
4. **Touch Targets**: Maintain minimum 40px × 40px touch targets for mobile compatibility
5. **Dark Theme**: All specifications are for dark theme; light theme would need color inversions

---

## Responsive Behavior

### Mobile (< 768px)

- Hide project selector text, show icon only
- Reduce search bar max-width to 240px
- Stack some action buttons in overflow menu

### Tablet (768px - 1024px)

- Reduce search bar max-width to 480px
- Maintain all other elements

### Desktop (> 1024px)

- Full specifications as documented above

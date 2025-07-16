# GCP Main Dashboard Specifications

## 1. LAYOUT & SPACING

### Content Area

- **Background Color**: #F8F9FA (light gray)
- **Padding**: 24px (all sides)
- **Maximum Content Width**: 1440px (constrained with auto margins)
- **Margin from Header**: 0px (content area starts immediately after header)
- **Margin from Sidebar**: 0px when open (sidebar overlays content)

### Tab Navigation

- **Background**: White (#FFFFFF)
- **Border Bottom**: 1px solid #DADCE0
- **Height**: 48px
- **Tab Spacing**: 0px between tabs
- **Tab Padding**: 0 24px
- **Active Tab Indicator**: 3px solid #1A73E8 (bottom border)

## 2. PAGE TITLE/HEADER SECTION

### Tab Labels

- **Font Family**: Google Sans, Roboto, Arial, sans-serif
- **Font Size**: 14px
- **Font Weight**: 500 (medium)
- **Color (Active)**: #1A73E8 (Google Blue)
- **Color (Inactive)**: #5F6368 (dark gray)
- **Letter Spacing**: 0.25px
- **Text Transform**: Uppercase

### Page Actions (Customize Button)

- **Position**: Top right of content area
- **Font Size**: 14px
- **Color**: #1A73E8
- **Icon Size**: 18px
- **Padding**: 8px 16px

## 3. CARD/PANEL COMPONENTS

### Card Container

- **Background Color**: #FFFFFF (white)
- **Border**: 1px solid #DADCE0
- **Border Radius**: 8px
- **Box Shadow**: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)
- **Padding**: 24px
- **Margin Between Cards**: 16px

### Card Header

- **Display**: Flex (icon + title + actions)
- **Margin Bottom**: 16px
- **Icon Size**: 24px
- **Icon Color**: #5F6368
- **Title Font Size**: 16px
- **Title Font Weight**: 500
- **Title Color**: #202124
- **Actions Button**: 24px × 24px (three dots menu)

## 4. GRID SYSTEM

### Layout Grid

- **Type**: CSS Grid
- **Columns**:
  - Desktop: 3 columns
  - Tablet: 2 columns
  - Mobile: 1 column
- **Gap**: 16px
- **Card Spanning**: Variable (1-3 columns based on content)

### Responsive Breakpoints

- **Mobile**: < 600px
- **Tablet**: 600px - 1024px
- **Desktop**: > 1024px

## 5. TYPOGRAPHY HIERARCHY

### H1 (Page Title)

- **Font Size**: 24px
- **Font Weight**: 400
- **Line Height**: 32px
- **Color**: #202124
- **Margin**: 0 0 24px 0

### H2 (Card Titles)

- **Font Size**: 16px
- **Font Weight**: 500
- **Line Height**: 24px
- **Color**: #202124
- **Letter Spacing**: 0.1px

### Body Text

- **Font Size**: 14px
- **Line Height**: 20px
- **Color**: #3C4043
- **Font Family**: Roboto, Arial, sans-serif

### Small/Helper Text

- **Font Size**: 12px
- **Line Height**: 16px
- **Color**: #5F6368
- **Letter Spacing**: 0.3px

### Links

- **Color**: #1A73E8
- **Text Decoration**: None
- **Hover**: Underline
- **Font Weight**: Inherits from parent

## 6. DATA DISPLAY ELEMENTS

### Lists in Cards

- **Item Padding**: 12px 0
- **Border Between Items**: 1px solid #E8EAED
- **Icon Size**: 20px
- **Icon Margin Right**: 16px
- **Title/Value Display**: Flex with space-between

### Key-Value Pairs

- **Label Color**: #5F6368
- **Value Color**: #202124
- **Label Font Size**: 14px
- **Value Font Size**: 14px

### Resource Links

- **Container Padding**: 8px
- **Hover Background**: rgba(26,115,232,0.08)
- **Border Radius**: 4px
- **Transition**: background-color 150ms cubic-bezier(0.4,0,0.2,1)

## 7. ACTION ELEMENTS

### Primary Buttons

- **Background**: #1A73E8
- **Color**: #FFFFFF
- **Padding**: 8px 24px
- **Border Radius**: 4px
- **Font Size**: 14px
- **Font Weight**: 500
- **Height**: 36px
- **Hover**: Box shadow elevation
- **Active**: Darker shade (#1765CC)

### Text Buttons (Links styled as buttons)

- **Color**: #1A73E8
- **Background**: Transparent
- **Padding**: 8px
- **Font Size**: 14px
- **Font Weight**: 500
- **Hover**: Background rgba(26,115,232,0.08)

### Icon Buttons

- **Size**: 40px × 40px
- **Icon Size**: 24px
- **Color**: #5F6368
- **Hover Background**: rgba(60,64,67,0.08)
- **Border Radius**: 50%

## 8. STATUS INDICATORS

### Colors

- **Success**: #188038 (Green)
- **Warning**: #F9AB00 (Yellow)
- **Error**: #D93025 (Red)
- **Info**: #1A73E8 (Blue)
- **Neutral**: #5F6368 (Gray)

### Status Text

- **Font Size**: 14px
- **Font Weight**: 500
- **Display**: Inline with appropriate color

## 9. EMPTY STATES

### Container

- **Text Align**: Center
- **Padding**: 48px 24px

### Message

- **Font Size**: 14px
- **Color**: #5F6368
- **Line Height**: 20px
- **Max Width**: 400px
- **Margin**: 0 auto

### Action Link

- **Margin Top**: 16px
- **Style**: Primary text button

## 10. LOADING STATES

### Skeleton Screens

- **Background**: Linear gradient animation
- **Base Color**: #F1F3F4
- **Highlight Color**: #E8EAED
- **Animation Duration**: 1.5s
- **Border Radius**: Matches content shape

### Progress Indicators

- **Type**: Material Design circular progress
- **Size**: 24px
- **Color**: #1A73E8
- **Track Color**: rgba(26,115,232,0.2)

## 11. RESPONSIVE BEHAVIOR

### Content Reflow

- **Sidebar Open**: Content maintains same padding
- **Mobile**:
  - Cards stack vertically
  - Padding reduced to 16px
  - Font sizes remain constant

### Grid Adjustments

- **Mobile**: Single column
- **Tablet**: 2 columns where appropriate
- **Desktop**: Up to 3 columns

### Card Content

- **Maintains internal padding at all sizes**
- **Text truncation with ellipsis for long content**
- **Icons scale proportionally**

## ADDITIONAL SPECIFICATIONS

### Graphs/Charts

- **Height**: 200px minimum
- **Colors**: Google Material palette
- **Grid Lines**: #E8EAED
- **Axis Text**: 12px, #5F6368
- **Interactive Hover**: Tooltip with exact values

### Navigation Patterns

- **Breadcrumbs**: Not used in main dashboard
- **Tab Navigation**: Persistent across dashboard views
- **Deep Links**: Cards link to specific service pages

### Accessibility

- **Focus Indicators**: 2px solid #1A73E8 outline
- **Focus Offset**: 2px
- **Minimum Touch Target**: 48px × 48px
- **Color Contrast**: WCAG AA compliant

### Animation & Transitions

- **Duration**: 150-200ms
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1) (Material standard easing)
- **Properties**: Transform, opacity, box-shadow
- **Hover States**: Immediate feedback with subtle transitions

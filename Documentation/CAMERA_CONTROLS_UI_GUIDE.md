# Camera Control UI - Visual Reference

## Updated Camera Control Panel

```
┌─────────────────────────────────────────────────────┐
│  Camera Control                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ ☑ Auto-Exposure      [Auto Once]             │ │
│  │ Let camera automatically adjust exposure...  │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Exposure                          100.0 ms        │
│  ━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│  0.001 ms                             10000.0 ms   │
│                                                     │
│  Gain                                1.00x         │
│  ━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│  1.0x                                   16.0x      │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Live Camera Preview    [Stop Feed]           │ │
│  ├───────────────────────────────────────────────┤ │
│  │                                               │ │
│  │                                               │ │
│  │           [LIVE CAMERA FEED]                 │ │
│  │                                               │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│  Live feed • Exposure: 100.0ms • Gain: 1.00x      │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │         📸 Capture Image                      │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Auto-Exposure Section (Gray Box)

```
┌────────────────────────────────────────┐
│ ☑ Auto-Exposure      [Auto Once]      │  ← Checkbox + Button
│ Let camera automatically adjust...    │  ← Helper text
└────────────────────────────────────────┘
```

- **Checkbox**: Toggle continuous auto-exposure
- **Auto Once Button**: Perform one-time adjustment
- **Gray background**: Visually groups related controls

### 2. Exposure Slider

```
Exposure                          100.0 ms  ← Label + Value badge
━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━   ← Slider with thumb
0.001 ms                       10000.0 ms  ← Min/max labels
```

- **Blue slider track**: 2px height, gray background
- **Blue thumb**: 20px circle, grows on hover
- **Value badge**: Gray background, monospace font
- **Disabled state**: Grayed out when auto-exposure is on

### 3. Gain Slider

```
Gain                                1.00x  ← Label + Value badge
━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ← Slider with thumb
1.0x                              16.0x   ← Min/max labels
```

- **Same styling** as exposure slider
- **Always enabled**: Works even with auto-exposure

### 4. Live Feed Preview

```
┌──────────────────────────────────────┐
│ Live Camera Preview   [Stop Feed]   │  ← Header + Control
├──────────────────────────────────────┤
│                                      │
│       [STREAMING VIDEO FEED]         │  ← WebSocket feed
│                                      │
└──────────────────────────────────────┘
Live feed • Exposure: 100ms • Gain: 1x  ← Info bar
```

- **Aspect ratio**: 4:3
- **Dark background**: Better for viewing
- **Info bar**: Shows current settings below feed

## Slider States

### Normal State

```
Exposure                          100.0 ms
━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ↑
  Blue thumb (20px)
```

### Hover State

```
Exposure                          100.0 ms
━━━━━━━━━━━━◉━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ↑
  Darker blue + 10% larger
```

### Disabled State (Auto-Exposure On)

```
Exposure (Auto)                   142.3 ms
━━━━━━━━━━━━○━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ↑
  Gray thumb, no hover effect
```

## Auto-Exposure States

### Auto-Exposure OFF (Manual)

```
┌────────────────────────────────────────┐
│ ☐ Auto-Exposure      [Auto Once]      │
└────────────────────────────────────────┘

Exposure                          100.0 ms  ← Active
━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━   ← Blue
```

### Auto-Exposure ON (Continuous)

```
┌────────────────────────────────────────┐
│ ☑ Auto-Exposure      [Auto Once]      │  ← Checked
└────────────────────────────────────────┘

Exposure (Auto)                   142.3 ms  ← "(Auto)" badge
━━━━━━━━━━━━○━━━━━━━━━━━━━━━━━━━━━━━━━━━   ← Gray/disabled
```

## Interaction Flow

### Adjusting Exposure

```
1. User drags slider
   ↓
   ━━━━━━━━●━━━━━ → ━━━━━━━━━━━●━━━━
   100ms           150ms

2. Value updates in badge
   100.0 ms → 150.0 ms

3. Debounce timer (150ms)
   [Wait for user to stop moving]

4. API call sent
   PUT /settings {"exposure": 150}

5. Live feed updates
   [Feed brightness changes]
```

### Using Auto-Exposure

```
1. Click "Auto Once" button
   [Auto Once] → [Auto Once] (loading)

2. Camera adjusts exposure
   [Camera analyzing scene...]

3. New value appears
   100ms → 142.3ms

4. Slider position updates
   ━━●━━━━━━ → ━━━━●━━━━━
```

## Color Scheme

```
Blue (#3b82f6)      ■  Slider thumb, active controls
Dark Blue (#2563eb) ■  Hover states
Gray (#9ca3af)      ■  Disabled controls, labels
Light Gray (#f3f4f6)■  Background boxes
Dark Gray (#1f2937) ■  Live feed background
Red (#ef4444)       ■  Stop button
```

## Responsive Behavior

### Desktop (> 1024px)

```
Full width sliders, large preview
```

### Tablet (768px - 1024px)

```
Slightly smaller preview
Sliders still full width
```

### Mobile (< 768px)

```
Stacked layout
Smaller preview (maintains 4:3)
Touch-friendly sliders (larger thumbs)
```

## Accessibility

### Keyboard Navigation

- `Tab`: Move between controls
- `Arrow keys`: Adjust slider value
- `Space`: Toggle checkbox
- `Enter`: Activate buttons

### Screen Reader Support

- Sliders announce: "Exposure, 100 milliseconds"
- Checkbox announces: "Auto-exposure, unchecked"
- Buttons announce: "Auto Once button"

## Animation & Transitions

### Slider Thumb

```css
transition: all 0.15s ease-in-out;
```

- Smooth growth on hover (0% → 10%)
- Color change on hover
- Scale animation

### Value Badge

```css
No animation (instant update)
```

- Updates immediately as slider moves
- Fixed width to prevent layout shift

### Feed Updates

```css
No animation (live stream)
```

- Continuous feed, no transitions
- Brightness changes gradually as camera adjusts

## Technical Notes

### Debounce Timing

```
Slider Input Event
    ↓
  +0ms  - Event fired
  +50ms - User still dragging
 +100ms - User still dragging
 +150ms - ✓ Update sent (if stopped)
```

### Update Frequency

```
Without debounce: ~200 updates/second
With debounce:    ~6-7 updates/second (user dependent)
API savings:      ~97% fewer calls
```

### WebSocket Performance

```
Frame rate:     ~30 FPS (camera dependent)
Frame size:     ~50-100 KB (JPEG)
Bandwidth:      ~1.5-3 MB/s
Latency:        ~50-100ms
```

## Mobile Considerations

### Touch Targets

- Minimum 44x44px (Apple HIG)
- Slider thumb: 20px → 28px on touch devices
- Buttons: 48px minimum height

### Viewport Optimization

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

### Gesture Support

- Swipe on slider = adjust value
- Pinch on feed = zoom (future)
- Double-tap = reset to default (future)

## Browser Compatibility

### Slider Styling

```
Chrome/Edge:  ✓ Full support
Firefox:      ✓ Full support (different pseudo-elements)
Safari:       ✓ Full support
Mobile:       ✓ Full support (touch-optimized)
```

### WebSocket

```
All modern browsers: ✓ Full support
IE11:                ✗ Not supported (deprecated)
```

## Performance Metrics

### Target Performance

- **First render**: < 100ms
- **Slider response**: < 16ms (60 FPS)
- **API update**: < 150ms (after debounce)
- **Feed latency**: < 100ms

### Memory Usage

- **Component**: ~2-5 MB
- **WebSocket buffer**: ~10-20 MB
- **Total**: ~15-30 MB (acceptable for modern devices)

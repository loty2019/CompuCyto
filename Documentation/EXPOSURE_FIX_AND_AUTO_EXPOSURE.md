# Exposure Fix & Auto-Exposure Implementation

## 🐛 Problem Identified

You were getting this error:

```
WARNING:pixelink_camera:Camera rejected exposure 400000.0µs (error -2147483645), keeping current: 400000µs
```

**Root Cause**: Unit mismatch between your code and PixeLink API

### What Was Wrong:

1. **Your code stored exposure as microseconds (µs)** - e.g., `400000` for 400ms
2. **PixeLink API expects SECONDS** - e.g., `0.4` for 400ms
3. **Error code -2147483645** = `ApiInvalidParameterError` (value out of range)
4. You were passing `400000.0` to the API expecting it was microseconds, but the API thought you wanted **400,000 SECONDS** (4.6 days!) - way beyond camera limits

## ✅ Solution Implemented

### 1. Fixed Exposure Units

**New Standard**: All exposure values are now in **milliseconds (ms)** throughout the system:

- **Database**: stores milliseconds
- **API endpoints**: accept/return milliseconds
- **Frontend UI**: displays milliseconds
- **Internal conversion**: code converts ms ↔ seconds when talking to PixeLink API

**Example conversions:**

- 100ms → 0.1 seconds (for PixeLink API)
- PixeLink returns 0.1s → store as 100ms

### 2. Added Exposure & Gain Limits

The camera now reads its actual hardware limits on initialization:

```python
# Example limits from a typical PixeLink camera:
self.exposure_min = 0.001   # 1 microsecond (0.001ms)
self.exposure_max = 10000.0 # 10 seconds (10,000ms)
self.gain_min = 1.0
self.gain_max = 16.0
```

These limits are:

- ✅ Read from camera at startup
- ✅ Returned by `/settings` endpoint
- ✅ Used to clamp values before setting
- ✅ Available for frontend sliders (min/max bounds)

### 3. Implemented Auto-Exposure

Three auto-exposure modes are now supported (matching PixeLink SDK):

#### Mode 1: **MANUAL** (default)

- You control exposure manually via API or sliders
- Camera doesn't adjust anything automatically

#### Mode 2: **AUTO** (continuous)

- Camera continuously adjusts exposure based on scene brightness
- Like auto-exposure on a smartphone camera
- Enabled via: `PUT /settings` with `{"autoExposure": true}`

#### Mode 3: **ONEPUSH** (one-time)

- Camera adjusts exposure once, then returns to manual
- Useful for initial setup or scene changes
- Triggered via: `POST /settings/auto-exposure/once`

## 📝 Changes Made

### `pixelink_camera.py`

1. **Changed exposure storage from microseconds to milliseconds**

   ```python
   # Old: self.exposure = 100000  # microseconds
   # New: self.exposure = 100.0   # milliseconds
   ```

2. **Added camera limits tracking**

   ```python
   self.exposure_min = 0.001  # Read from camera
   self.exposure_max = 10000.0
   self.gain_min = 1.0
   self.gain_max = 16.0
   self.auto_exposure_enabled = False
   ```

3. **Fixed `_load_current_settings()`**
   - Now uses `getCameraFeatures()` to read min/max limits
   - Properly converts seconds → milliseconds
   - Detects if auto-exposure is active

4. **Fixed `_set_exposure()`**
   - Converts milliseconds → seconds before sending to camera
   - Clamps values to valid range
   - Better error logging with actual ranges

5. **Added `_set_auto_exposure()`**
   - Enables/disables continuous auto-exposure
   - Properly handles transitions between modes

6. **Added `perform_one_time_auto_exposure()`**
   - Initiates ONEPUSH auto-exposure
   - Polls camera until operation completes (max 5 seconds)
   - Returns final exposure value

7. **Updated `get_settings()` response**
   ```json
   {
     "exposure": 100.0,
     "exposureMin": 0.001,
     "exposureMax": 10000.0,
     "gain": 1.0,
     "gainMin": 1.0,
     "gainMax": 16.0,
     "autoExposure": false,
     "resolution": { "width": 1280, "height": 1024 },
     "connected": true,
     "streaming": false
   }
   ```

### `main.py`

1. **Updated request models**

   ```python
   class SettingsUpdate(BaseModel):
       exposure: Optional[float] = Field(None, description="Exposure in milliseconds (ms)")
       gain: Optional[float] = Field(None, description="Gain value")
       autoExposure: Optional[bool] = Field(None, description="Enable/disable auto-exposure")
   ```

2. **Updated `/settings` PUT endpoint**
   - Now accepts `autoExposure` parameter
   - Passes to `camera.update_settings()`

3. **Added new endpoint: `POST /settings/auto-exposure/once`**
   - Performs one-time auto-exposure adjustment
   - Returns new exposure value

4. **Improved startup logging**
   - Shows exposure range on startup
   - Shows gain range on startup

### `config.py`

1. **Updated default exposure**
   ```python
   # Old: default_exposure: float = 100000.0  # microseconds
   # New: default_exposure: float = 100.0     # milliseconds
   ```

## 🎛️ API Reference

### Get Current Settings

```http
GET /settings
```

**Response:**

```json
{
  "exposure": 100.0, // Current exposure in ms
  "exposureMin": 0.001, // Min exposure in ms (hardware limit)
  "exposureMax": 10000.0, // Max exposure in ms (hardware limit)
  "gain": 1.0, // Current gain
  "gainMin": 1.0, // Min gain (hardware limit)
  "gainMax": 16.0, // Max gain (hardware limit)
  "autoExposure": false, // Is auto-exposure enabled?
  "resolution": {
    "width": 1280,
    "height": 1024
  },
  "connected": true,
  "streaming": false
}
```

### Update Settings Manually

```http
PUT /settings
Content-Type: application/json

{
  "exposure": 150.0,      // Optional: exposure in ms
  "gain": 2.0,            // Optional: gain value
  "autoExposure": false   // Optional: enable/disable auto
}
```

**Response:** Same as GET /settings

### Enable Continuous Auto-Exposure

```http
PUT /settings
Content-Type: application/json

{
  "autoExposure": true
}
```

Camera will continuously adjust exposure automatically.

### Disable Auto-Exposure (Return to Manual)

```http
PUT /settings
Content-Type: application/json

{
  "autoExposure": false
}
```

Camera will stop adjusting and lock to current exposure value.

### One-Time Auto-Exposure

```http
POST /settings/auto-exposure/once
```

Camera will adjust exposure once, then return to manual control.

**Response:**

```json
{
  "success": true,
  "message": "One-time auto-exposure completed",
  "exposure": 142.5, // New exposure value determined by camera
  "gain": 1.0
}
```

## 🎨 Frontend Implementation Recommendations

### Exposure Slider

```typescript
// Fetch camera limits first
const settings = await fetch('/settings').then(r => r.json());

// Create slider with actual camera limits
<input
  type="range"
  min={settings.exposureMin}     // e.g., 0.001 ms
  max={settings.exposureMax}     // e.g., 10000 ms
  value={settings.exposure}      // e.g., 100 ms
  step="0.1"                     // Fine control
  disabled={settings.autoExposure}  // Disable if auto is on
  onChange={handleExposureChange}
/>

// Display with units
<span>{settings.exposure.toFixed(1)} ms</span>
```

**Consider logarithmic scale** since range is huge (0.001 to 10,000):

```typescript
// Convert linear slider (0-100) to logarithmic exposure
const sliderToExposure = (slider: number) => {
  const min = Math.log10(settings.exposureMin);
  const max = Math.log10(settings.exposureMax);
  const value = min + ((max - min) * slider) / 100;
  return Math.pow(10, value);
};

// Convert exposure back to slider position
const exposureToSlider = (exposure: number) => {
  const min = Math.log10(settings.exposureMin);
  const max = Math.log10(settings.exposureMax);
  const value = Math.log10(exposure);
  return ((value - min) / (max - min)) * 100;
};
```

### Gain Slider

```typescript
<input
  type="range"
  min={settings.gainMin}       // e.g., 1.0
  max={settings.gainMax}       // e.g., 16.0
  value={settings.gain}        // e.g., 1.0
  step="0.1"
  onChange={handleGainChange}
/>

<span>{settings.gain.toFixed(1)}x</span>
```

### Auto-Exposure Controls

```vue
<template>
  <div class="camera-controls">
    <!-- Manual Controls (disabled when auto is on) -->
    <div>
      <label>Exposure</label>
      <input
        type="range"
        :min="settings.exposureMin"
        :max="settings.exposureMax"
        v-model="exposure"
        :disabled="settings.autoExposure"
        @change="updateExposure"
      />
      <span>{{ exposure.toFixed(1) }} ms</span>
    </div>

    <div>
      <label>Gain</label>
      <input
        type="range"
        :min="settings.gainMin"
        :max="settings.gainMax"
        v-model="gain"
        step="0.1"
        @change="updateGain"
      />
      <span>{{ gain.toFixed(1) }}x</span>
    </div>

    <!-- Auto-Exposure Toggle -->
    <div>
      <label>
        <input
          type="checkbox"
          v-model="autoExposure"
          @change="toggleAutoExposure"
        />
        Continuous Auto-Exposure
      </label>
    </div>

    <!-- One-Time Auto-Exposure Button -->
    <button @click="performAutoExposureOnce" :disabled="settings.autoExposure">
      Auto-Adjust Once
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const settings = ref({
  exposure: 100,
  exposureMin: 0.001,
  exposureMax: 10000,
  gain: 1.0,
  gainMin: 1.0,
  gainMax: 16.0,
  autoExposure: false,
});

const exposure = ref(100);
const gain = ref(1.0);
const autoExposure = ref(false);

onMounted(async () => {
  // Load current settings
  const response = await fetch("http://localhost:8001/settings");
  settings.value = await response.json();
  exposure.value = settings.value.exposure;
  gain.value = settings.value.gain;
  autoExposure.value = settings.value.autoExposure;
});

async function updateExposure() {
  await fetch("http://localhost:8001/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exposure: exposure.value }),
  });
}

async function updateGain() {
  await fetch("http://localhost:8001/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gain: gain.value }),
  });
}

async function toggleAutoExposure() {
  const response = await fetch("http://localhost:8001/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ autoExposure: autoExposure.value }),
  });
  settings.value = await response.json();
}

async function performAutoExposureOnce() {
  const response = await fetch(
    "http://localhost:8001/settings/auto-exposure/once",
    {
      method: "POST",
    }
  );
  const result = await response.json();

  if (result.success) {
    // Update UI with new exposure value
    exposure.value = result.exposure;
    settings.value.exposure = result.exposure;
  }
}
</script>
```

## 🧪 Testing

### Test Exposure Setting

```python
# Test with Python camera service running
import requests

# Get current settings and limits
settings = requests.get('http://localhost:8001/settings').json()
print(f"Current exposure: {settings['exposure']}ms")
print(f"Range: {settings['exposureMin']}ms - {settings['exposureMax']}ms")

# Set to 200ms
response = requests.put('http://localhost:8001/settings',
                       json={'exposure': 200.0})
print(response.json())

# Set to minimum
response = requests.put('http://localhost:8001/settings',
                       json={'exposure': settings['exposureMin']})
print(response.json())

# Set to maximum
response = requests.put('http://localhost:8001/settings',
                       json={'exposure': settings['exposureMax']})
print(response.json())
```

### Test Auto-Exposure

```python
# Enable continuous auto-exposure
response = requests.put('http://localhost:8001/settings',
                       json={'autoExposure': True})
print(response.json())

# Wait a few seconds and check exposure
import time
time.sleep(3)
settings = requests.get('http://localhost:8001/settings').json()
print(f"Auto-adjusted to: {settings['exposure']}ms")

# Disable auto-exposure
response = requests.put('http://localhost:8001/settings',
                       json={'autoExposure': False})
print(response.json())

# Perform one-time auto-exposure
response = requests.post('http://localhost:8001/settings/auto-exposure/once')
print(response.json())
```

## 📚 Key Learnings from Sample Code

### From `getCameraFeature.py`:

- Always use `getCameraFeatures()` to read hardware limits
- Features have `FeatureFlags.PRESENCE` to check if supported
- Min/max values are stored in `feature.Params[i].fMinValue/fMaxValue`

### From `setFeature.py`:

- Always check return codes: `PxLApi.apiSuccess(ret[0])`
- Camera may adjust values slightly (returns `ApiSuccessParametersChanged`)
- Always read back values after setting to confirm

### From `autoExposure.py`:

- Three modes: `MANUAL`, `AUTO` (continuous), `ONEPUSH` (one-time)
- ONEPUSH requires polling until `ONEPUSH` flag clears
- Read exposure value immediately when switching from AUTO to MANUAL

### From `getSnapshot.py`:

- Exposure is always in **SECONDS** in PixeLink API
- Example: `params[0]` returns `0.1` for 100ms exposure
- Always convert: `exposure_ms = params[0] * 1000`

## 🎯 Next Steps

1. **Test with real camera** to verify limits are read correctly
2. **Implement frontend sliders** with proper min/max bounds
3. **Consider logarithmic scale** for exposure slider (range is 0.001 to 10000)
4. **Add exposure presets** (Low Light, Normal, Bright, etc.)
5. **Consider adding auto-gain** (similar to auto-exposure)
6. **Add exposure lock indicator** when auto-exposure is active

## 🔍 Troubleshooting

### Issue: Exposure still rejected

**Check:**

- Is camera actually connected? (`settings.connected == true`)
- Is value within camera's specific limits? (shown at startup)
- Are you passing milliseconds, not microseconds?

### Issue: Auto-exposure not working

**Check:**

- Camera must be streaming for auto-exposure to work
- Some cameras may not support auto-exposure (check `getCameraFeatures`)
- One-time auto-exposure has 5 second timeout

### Issue: Slider range too large

**Solution:** Use logarithmic scale (see frontend examples above)

### Issue: Exposure changes during capture

**This is expected if auto-exposure is enabled!**

- Either disable auto-exposure before capture
- Or read back actual exposure used from capture metadata

## 📖 References

- PixeLink SDK Sample: `Sample_PixcelinkAPI_python/autoExposure.py`
- PixeLink SDK Sample: `Sample_PixcelinkAPI_python/getCameraFeature.py`
- PixeLink SDK Sample: `Sample_PixcelinkAPI_python/setFeature.py`
- PixeLink API Docs: Exposure is always in SECONDS

// Fixed categorical color per platform, reused in every chart/table across
// the app so "Amazon" (etc.) reads as the same color everywhere - identity
// should follow the entity, never the row order or which chart it's in.
// Palette: validated categorical slots 1-5 (blue/orange/aqua/yellow/magenta),
// deliberately skipping the green/red slots since those are already reserved
// for status (Healthy/Critical) elsewhere in the app.
export const PLATFORM_COLOR_BY_ID = {
  AMZ: '#2a78d6', // blue
  FLP: '#eb6834', // orange
  MTR: '#1baf7a', // aqua
  BLK: '#eda100', // yellow
  JMT: '#e87ba4', // magenta
};

const PLATFORM_COLOR_BY_NAME = {
  Amazon: PLATFORM_COLOR_BY_ID.AMZ,
  Flipkart: PLATFORM_COLOR_BY_ID.FLP,
  Myntra: PLATFORM_COLOR_BY_ID.MTR,
  Blinkit: PLATFORM_COLOR_BY_ID.BLK,
  JioMart: PLATFORM_COLOR_BY_ID.JMT,
};

const FALLBACK_COLOR = '#6b7280'; // gray-500, for any platform outside the fixed set

export const getPlatformColor = (nameOrId) =>
  PLATFORM_COLOR_BY_ID[nameOrId] || PLATFORM_COLOR_BY_NAME[nameOrId] || FALLBACK_COLOR;

*** Begin Patch
*** Update File: docs/app.js
@@
-const LAT_UI_OFFSET = 0.27;
-const uiLat = (lat) => Number.isFinite(lat) ? (lat - LAT_UI_OFFSET) : lat;
-const rawLatFromUi = (lat) => Number.isFinite(lat) ? (lat + LAT_UI_OFFSET) : lat;
-const fmtUiLat = (lat, d=4) => Number.isFinite(lat) ? uiLat(lat).toFixed(d) : "—";
+const DEFAULT_LAT_UI_OFFSET = 0.27;
+const LAT_UI_OFFSET_KEY = "SEYDYAAR_UI_LAT_OFFSET";
+const getLatOffset = () => {
+  const v = Number(localStorage.getItem(LAT_UI_OFFSET_KEY));
+  return Number.isFinite(v) ? v : DEFAULT_LAT_UI_OFFSET;
+};
+const uiLat = (lat) => Number.isFinite(lat) ? (lat - getLatOffset()) : lat;
+const rawLatFromUi = (lat) => Number.isFinite(lat) ? (lat + getLatOffset()) : lat;
+const fmtUiLat = (lat, d=4) => Number.isFinite(lat) ? uiLat(lat).toFixed(d) : "—";
+
+window.getLatOffset = getLatOffset;
+window.applyUiLatOffset = uiLat;
+window.unapplyUiLatOffset = rawLatFromUi;
+window.setLatOffset = (v) => {
+  const n = Number(v);
+  if (!Number.isFinite(n)) {
+    console.warn("Invalid lat offset:", v);
+    return getLatOffset();
+  }
+  localStorage.setItem(LAT_UI_OFFSET_KEY, String(n));
+  console.log("SEYDYAAR_UI_LAT_OFFSET =", n);
+  return n;
+};
+window.resetLatOffset = () => {
+  localStorage.removeItem(LAT_UI_OFFSET_KEY);
+  console.log("SEYDYAAR_UI_LAT_OFFSET reset to default", DEFAULT_LAT_UI_OFFSET);
+  return DEFAULT_LAT_UI_OFFSET;
+};
*** End Patch

"""
Siafu — Weed Detection Module
Color thresholding + basic ML approach using Pillow (no OpenCV required)

Detects weeds vs crops in farm images using:
1. Color thresholding (green vegetation segmentation)
2. Size/shape filtering (crops are larger, evenly spaced)
3. Position filtering (crops grow in rows, weeds between rows)
"""

import math
from PIL import Image
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


# ============================================================
# DATA TYPES
# ============================================================

@dataclass
class Plant:
    """A detected plant (crop or weed)"""
    x: float          # center x in normalized coords [0..1]
    y: float          # center y in normalized coords [0..1]
    area_px: int      # area in pixels
    width: int        # bounding box width
    height: int       # bounding box height
    green_intensity: float  # average greenness (0..1)
    is_crop: bool = False   # classified as crop?
    confidence: float = 0.0  # classification confidence

@dataclass
class WeedMap:
    """Weed density map for a field cell"""
    cell_x: int
    cell_y: int
    weed_count: int
    weed_density: float  # 0.0 to 1.0
    timestamp: float = 0.0

@dataclass
class DetectionResult:
    """Result of a weed detection pass"""
    weeds: List[Plant] = field(default_factory=list)
    crops: List[Plant] = field(default_factory=list)
    weed_count: int = 0
    crop_count: int = 0
    image_width: int = 0
    image_height: int = 0
    mean_greenness: float = 0.0
    coverage_pct: float = 0.0  # % of image covered by vegetation


# ============================================================
# COLOR THRESHOLDING ENGINE
# ============================================================

class ColorWeedDetector:
    """
    Detects weeds using color thresholding.
    
    Pipeline:
      1. Convert RGB to HSV-like greenness metric
      2. Threshold to create vegetation mask
      3. Find connected components (blobs)
      4. Classify each blob as crop or weed based on size/spacing
      5. Return sorted list of weeds nearest to robot
    """
    
    def __init__(self, 
                 green_threshold: float = 0.25,
                 min_weed_area: int = 15,
                 max_weed_area: int = 800,
                 crop_min_area: int = 120,
                 saturation_threshold: int = 30,
                 brightness_threshold: int = 40):
        """
        Args:
            green_threshold: Minimum greenness score (0-1) to count as vegetation
            min_weed_area: Minimum pixels for a weed blob
            max_weed_area: Maximum pixels for a weed blob (bigger = crop)
            crop_min_area: Minimum pixels for a crop (larger plants)
            saturation_threshold: Minimum saturation (0-255) to avoid dirt
            brightness_threshold: Minimum brightness (0-255) to avoid shadows
        """
        self.green_threshold = green_threshold
        self.min_weed_area = min_weed_area
        self.max_weed_area = max_weed_area
        self.crop_min_area = crop_min_area
        self.saturation_threshold = saturation_threshold
        self.brightness_threshold = brightness_threshold
        
    def _greenness(self, r: int, g: int, b: int) -> float:
        """
        Compute a greenness score for an RGB pixel.
        
        Uses the "Excess Green" index: 2g - r - b
        Normalized to [0, 1] range.
        
        A high value means "very green" = likely vegetation.
        A low value means "not green" = soil, rock, sky.
        """
        # Normalize to [0, 1]
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        # Excess Green index
        exg = 2 * g_norm - r_norm - b_norm
        
        # Clamp and scale to [0, 1]
        # exg ranges from -1 (blue/red) to 2 (pure green)
        # We rescale so 0 = not green, 1 = very green
        green_score = (exg + 1.0) / 3.0
        return max(0.0, min(1.0, green_score))
    
    def _hsv_green_score(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """
        Convert RGB to HSV and return (hue_deg, saturation, value).
        Used for filtering out non-plant green (moss, algae) and shadows.
        """
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        mx = max(r_norm, g_norm, b_norm)
        mn = min(r_norm, g_norm, b_norm)
        diff = mx - mn
        
        # Value (brightness)
        v = mx
        
        # Saturation
        if mx == 0:
            s = 0.0
        else:
            s = diff / mx
        
        # Hue
        if diff == 0:
            h = 0.0
        elif mx == r_norm:
            h = (60 * ((g_norm - b_norm) / diff) + 360) % 360
        elif mx == g_norm:
            h = (60 * ((b_norm - r_norm) / diff) + 120) % 360
        else:
            h = (60 * ((r_norm - g_norm) / diff) + 240) % 360
            
        return (h, s * 255, v * 255)
    
    def _is_vegetation_pixel(self, r: int, g: int, b: int) -> bool:
        """
        Determine if a pixel is likely vegetation.
        
        Combines greenness score with HSV filtering.
        """
        # Quick check: green must be the dominant channel
        if g <= r or g <= b:
            return False
        
        green_score = self._greenness(r, g, b)
        if green_score < self.green_threshold:
            return False
        
        # HSV filter to avoid dirt, shadows, and non-plant green
        h, s, v = self._hsv_green_score(r, g, b)
        if s < self.saturation_threshold:
            return False  # low saturation = grey/brown = dirt
        if v < self.brightness_threshold:
            return False  # too dark = shadow
        
        # Hue range for green plants: ~80° to ~160°
        if h < 70 or h > 170:
            # Only reject if not very green
            if green_score < 0.4:
                return False
        
        return True
    
    def detect(self, image: Image.Image) -> DetectionResult:
        """
        Main detection pipeline.
        
        Args:
            image: PIL Image (RGB)
            
        Returns:
            DetectionResult with detected weeds and crops
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        width, height = image.size
        pixels = image.load()
        
        # Step 1: Create vegetation binary mask
        # Using a 2D list for connected component analysis
        mask = [[False for _ in range(width)] for _ in range(height)]
        total_greenness = 0.0
        green_pixels = 0
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                if self._is_vegetation_pixel(r, g, b):
                    mask[y][x] = True
                    total_greenness += self._greenness(r, g, b)
                    green_pixels += 1
        
        mean_greenness = total_greenness / max(green_pixels, 1)
        coverage_pct = (green_pixels / (width * height)) * 100
        
        # Step 2: Connected component labeling (8-connected)
        # Using a simple two-pass algorithm
        components = self._label_components(mask, width, height)
        
        # Step 3: Classify components as crop or weed
        crops = []
        weeds = []
        
        for comp_id, pixels_list in components.items():
            area = len(pixels_list)
            if area < self.min_weed_area:
                continue  # too small, likely noise
            
            # Compute bounding box and centroid
            xs = [p[0] for p in pixels_list]
            ys = [p[1] for p in pixels_list]
            cx = sum(xs) / area
            cy = sum(ys) / area
            bbox_w = max(xs) - min(xs)
            bbox_h = max(ys) - min(ys)
            
            # Average greenness of this blob
            blob_green = 0.0
            for (px, py) in pixels_list:
                r, g, b = pixels[px, py]
                blob_green += self._greenness(r, g, b)
            avg_green = blob_green / area
            
            # Classification logic:
            # Crops: larger, more uniform green, rounder shape
            # Weeds: smaller, sporadic, irregular
            
            is_crop = False
            confidence = 0.0
            
            # Size heuristic: crops are planted and grow larger
            if area > self.crop_min_area:
                is_crop = True
                confidence = min(1.0, area / 500.0)
            elif area < self.max_weed_area:
                is_crop = False
                confidence = min(1.0, 1.0 - (area / self.max_weed_area))
            
            # Aspect ratio heuristic: crops are more compact
            if bbox_w > 0 and bbox_h > 0:
                aspect = max(bbox_w, bbox_h) / min(bbox_w, bbox_h)
                if aspect > 3.0:
                    # Very elongated = likely weed grass
                    is_crop = False
                    confidence = max(confidence, 0.6)
            
            plant = Plant(
                x=cx / width,
                y=cy / height,
                area_px=area,
                width=bbox_w,
                height=bbox_h,
                green_intensity=avg_green,
                is_crop=is_crop,
                confidence=confidence,
            )
            
            if is_crop:
                crops.append(plant)
            else:
                weeds.append(plant)
        
        # Step 4: Refine using row-position filtering (if crops detected)
        # Weeds found in the inter-row space are higher priority
        if len(crops) >= 2:
            weeds = self._refine_by_row_position(weeds, crops, width, height)
        
        return DetectionResult(
            weeds=sorted(weeds, key=lambda w: w.y, reverse=True),  # nearest first
            crops=crops,
            weed_count=len(weeds),
            crop_count=len(crops),
            image_width=width,
            image_height=height,
            mean_greenness=mean_greenness,
            coverage_pct=coverage_pct,
        )
    
    def _label_components(self, mask, width, height):
        """
        Two-pass connected component labeling.
        Labels groups of adjacent vegetation pixels.
        """
        labels = [[0 for _ in range(width)] for _ in range(height)]
        current_label = 0
        equivalences = {}
        
        # First pass: assign provisional labels
        for y in range(height):
            for x in range(width):
                if not mask[y][x]:
                    continue
                
                # Check neighbors (8-connected: left, up-left, up, up-right)
                neighbor_labels = set()
                
                # Left
                if x > 0 and labels[y][x-1] > 0:
                    neighbor_labels.add(labels[y][x-1])
                # Up-left
                if x > 0 and y > 0 and labels[y-1][x-1] > 0:
                    neighbor_labels.add(labels[y-1][x-1])
                # Up
                if y > 0 and labels[y-1][x] > 0:
                    neighbor_labels.add(labels[y-1][x])
                # Up-right
                if x < width - 1 and y > 0 and labels[y-1][x+1] > 0:
                    neighbor_labels.add(labels[y-1][x+1])
                
                if not neighbor_labels:
                    current_label += 1
                    labels[y][x] = current_label
                else:
                    min_label = min(neighbor_labels)
                    labels[y][x] = min_label
                    for lbl in neighbor_labels:
                        if lbl != min_label:
                            equivalences[lbl] = min_label
        
        # Resolve equivalences
        for y in range(height):
            for x in range(width):
                lbl = labels[y][x]
                if lbl > 0 and lbl in equivalences:
                    labels[y][x] = equivalences[lbl]
        
        # Collect pixels per component
        components = {}
        for y in range(height):
            for x in range(width):
                lbl = labels[y][x]
                if lbl > 0:
                    if lbl not in components:
                        components[lbl] = []
                    components[lbl].append((x, y))
        
        return components
    
    def _refine_by_row_position(self, weeds, crops, width, height):
        """
        Reclassify weeds based on crop row positions.
        
        In row-crop agriculture:
        - Crops grow in straight rows
        - Weeds between rows are "real" weeds
        - Plants very close to crop rows might be crop offshoots
        
        We compute the line of crop rows and filter accordingly.
        """
        if len(crops) < 2:
            return weeds
        
        # Get crop positions in pixel coords
        crop_xs = [c.x * width for c in crops]
        crop_ys = [c.y * height for c in crops]
        
        # Simple row detection: group crops by x-position
        # (assuming robot is driving between rows)
        mean_crop_x = sum(crop_xs) / len(crop_xs)
        
        refined = []
        for weed in weeds:
            wx = weed.x * width
            
            # If weed is very close to crop x-positions, lower priority
            # (it might be a crop leaf)
            dist_from_crop_line = abs(wx - mean_crop_x)
            
            if dist_from_crop_line < width * 0.05:  # within 5% of image
                weed.confidence *= 0.7  # reduce confidence
            
            refined.append(weed)
        
        return refined
    
    def detect_simple(self, image: Image.Image) -> DetectionResult:
        """
        Simplified detection without connected components.
        Faster but less accurate. Good for initial testing.
        
        Just counts green pixels and reports density.
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        width, height = image.size
        pixels = image.load()
        
        veg_pixels = 0
        total = 0
        
        # Sample evenly across the image for speed
        step = 4  # check every 4th pixel
        for y in range(0, height, step):
            for x in range(0, width, step):
                r, g, b = pixels[x, y]
                if self._is_vegetation_pixel(r, g, b):
                    veg_pixels += 1
                total += 1
        
        coverage = (veg_pixels / max(total, 1)) * 100
        
        # Estimate weed count from coverage
        # (assumes average weed is ~50 pixels at step=4 sampling)
        estimated_weeds = max(0, int((coverage - 5) / 3)) if coverage > 5 else 0
        
        return DetectionResult(
            weed_count=estimated_weeds,
            coverage_pct=coverage,
            image_width=width,
            image_height=height,
        )


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def make_test_image(width=320, height=240):
    """
    Create a synthetic farm image for testing.
    
    Layout:
    - Brown background (soil)
    - Three green crop plants in a row
    - Several small green weeds scattered between rows
    """
    img = Image.new('RGB', (width, height), color=(120, 90, 60))  # soil brown
    pixels = img.load()
    
    import random
    random.seed(42)
    
    # Crop plants (large, evenly spaced)
    crop_positions = [
        (width // 4, height // 3),
        (width // 2, height // 3),
        (3 * width // 4, height // 3),
    ]
    
    for cx, cy in crop_positions:
        # Draw a crop as an ellipse of green pixels
        crop_radius_x = 25
        crop_radius_y = 20
        for dx in range(-crop_radius_x, crop_radius_x + 1):
            for dy in range(-crop_radius_y, crop_radius_y + 1):
                if (dx / crop_radius_x)**2 + (dy / crop_radius_y)**2 <= 1:
                    px = cx + dx
                    py = cy + dy
                    if 0 <= px < width and 0 <= py < height:
                        # Varying shades of green for realism
                        shade = random.randint(90, 160)
                        pixels[px, py] = (20, shade, 30)
    
    # Weeds (small, scattered in inter-row areas)
    for _ in range(30):
        wx = random.randint(10, width - 10)
        wy = random.randint(10, height - 10)
        
        # Don't place on crops
        on_crop = False
        for cx, cy in crop_positions:
            if abs(wx - cx) < 30 and abs(wy - cy) < 25:
                on_crop = True
                break
        if on_crop:
            continue
        
        # Weed size (small)
        weed_r = random.randint(3, 8)
        for dx in range(-weed_r, weed_r + 1):
            for dy in range(-weed_r, weed_r + 1):
                if dx*dx + dy*dy <= weed_r*weed_r:
                    px = wx + dx
                    py = wy + dy
                    if 0 <= px < width and 0 <= py < height:
                        shade = random.randint(130, 200)
                        pixels[px, py] = (30, shade, 20)
    
    # Add some noise (small rocks, dirt spots)
    for _ in range(50):
        nx = random.randint(0, width - 1)
        ny = random.randint(0, height - 1)
        pixels[nx, ny] = (100, 85, 65)  # dark soil
    
    return img


def draw_detection_debug(image: Image.Image, result: DetectionResult) -> Image.Image:
    """Draw detection results on the image for visual debugging."""
    img = image.copy()
    pixels = img.load()
    w, h = img.size
    
    # Highlight weeds in red
    for weed in result.weeds:
        px = int(weed.x * w)
        py = int(weed.y * h)
        half = max(weed.width, weed.height) // 2 + 2
        for dx in range(-half, half + 1):
            for dy in range(-half, half + 1):
                if abs(dx) <= 2 or abs(dy) <= 2:  # draw a box outline
                    sx = px + dx
                    sy = py + dy
                    if 0 <= sx < w and 0 <= sy < h:
                        pixels[sx, sy] = (255, 0, 0)
    
    # Highlight crops in green
    for crop in result.crops:
        px = int(crop.x * w)
        py = int(crop.y * h)
        half = max(crop.width, crop.height) // 2 + 2
        for dx in range(-half, half + 1):
            for dy in range(-half, half + 1):
                if abs(dx) <= 2 or abs(dy) <= 2:
                    sx = px + dx
                    sy = py + dy
                    if 0 <= sx < w and 0 <= sy < h:
                        pixels[sx, sy] = (0, 255, 0)
    
    return img


if __name__ == '__main__':
    print("=" * 50)
    print("Siafu — Weed Detection Test")
    print("=" * 50)
    
    # Create test image
    img = make_test_image()
    print(f"\nTest image: {img.size[0]}x{img.size[1]}")
    img.save('/tmp/siafu_test_field.png')
    print("Saved: /tmp/siafu_test_field.png")
    
    # Initialize detector
    detector = ColorWeedDetector(
        green_threshold=0.20,
        min_weed_area=10,
        max_weed_area=400,
        crop_min_area=100,
    )
    
    # Run detection
    result = detector.detect(img)
    
    print(f"\n--- Detection Results ---")
    print(f"Vegetation coverage: {result.coverage_pct:.1f}%")
    print(f"Mean greenness:      {result.mean_greenness:.3f}")
    print(f"Crops detected:      {result.crop_count}")
    print(f"Weeds detected:      {result.weed_count}")
    
    if result.weeds:
        print(f"\nWeed positions (normalized):")
        for i, w in enumerate(result.weeds[:10]):
            print(f"  Weed {i+1}: ({w.x:.3f}, {w.y:.3f}) area={w.area_px}px conf={w.confidence:.2f}")
    
    if result.crops:
        print(f"\nCrop positions:")
        for i, c in enumerate(result.crops):
            print(f"  Crop {i+1}: ({c.x:.3f}, {c.y:.3f}) area={c.area_px}px")
    
    # Quick test
    print(f"\n--- Quick Test Results ---")
    simple = detector.detect_simple(img)
    print(f"Simple estimate: {simple.weed_count} weeds, {simple.coverage_pct:.1f}% coverage")
    
    if result.weed_count > 0 and result.crop_count > 0:
        print("\n✅ Detection working: both crops and weeds identified")
    elif result.weed_count > 0:
        print("\n⚠️  Weeds found but no crops — check crop parameters")
    else:
        print("\n❌ No vegetation detected — check thresholds")
    
    print("\nDone.")

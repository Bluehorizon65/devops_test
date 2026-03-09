import cv2
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys
import argparse
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys
import argparse
import os

INPUT_IMAGE_PATH = "testcases/image copy 3.png"
TOLERANCE_VALUES = [3, 2]

TOLERANCE_VALUES = [3, 2]  # Test these tolerance values (±3, ±2)



def detect_rooftops_targeted(image, target_colors, tolerance=12):
    print(f"TARGETED ROOFTOP DETECTION")
    print(f"Target colors: {target_colors}")
    print(f"Tolerance: ±{tolerance}")
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    combined_mask = np.zeros(image_rgb.shape[:2], dtype=np.uint8)
    
    for i, (r, g, b) in enumerate(target_colors):
        lower = np.array([max(0, r-tolerance), max(0, g-tolerance), max(0, b-tolerance)])
        upper = np.array([min(255, r+tolerance), min(255, g+tolerance), min(255, b+tolerance)])
        
        color_mask = cv2.inRange(image_rgb, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, color_mask)
        
        pixels_found = np.sum(color_mask == 255)
        print(f"Color {i+1} RGB({r},{g},{b}): {pixels_found} pixels")
    
    total_detected = np.sum(combined_mask == 255)
    print(f"Total pixels detected: {total_detected}")
    
    kernel = np.ones((4, 4), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    final_mask = np.zeros_like(combined_mask)
    valid_areas = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if 150 < area < 50000:
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if 0.1 <= aspect_ratio <= 10.0:
                
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = area / hull_area if hull_area > 0 else 0
                
                if solidity > 0.4:
                    cv2.fillPoly(final_mask, [contour], 255)
                    valid_areas += 1
    
    final_pixels = np.sum(final_mask == 255)
    print(f"After filtering: {valid_areas} areas, {final_pixels} pixels")
    
    return final_mask


def place_solar_panels_optimal(image, rooftop_mask):
    result_image = image.copy()
    rows, cols = rooftop_mask.shape
    
    panel_width = 14
    panel_height = 10
    gap = 1
    min_coverage = 0.70
    
    panel_count = 0
    
    print(f"PANEL PLACEMENT")
    print(f"Panel size: {panel_width}x{panel_height}")
    print(f"Gap: {gap}px")
    print(f"Coverage required: {min_coverage*100}%")
    
    for y in range(0, rows - panel_height, panel_height + gap):
        for x in range(0, cols - panel_width, panel_width + gap):
            
            panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
            
            if panel_roi.size > 0:
                rooftop_pixels = np.sum(panel_roi == 255)
                total_pixels = panel_roi.size
                coverage = rooftop_pixels / total_pixels
                
                if coverage >= min_coverage:
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (255, 0, 0), -1)
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 1)
                    panel_count += 1
    
    small_panel_width = 10
    small_panel_height = 8
    min_coverage_small = 0.60  # Even lower threshold for gap filling
    
    print(f"Gap filling with {small_panel_width}x{small_panel_height} panels, {min_coverage_small*100}% threshold")
    
    for y in range(0, rows - small_panel_height, small_panel_height + gap):
        for x in range(0, cols - small_panel_width, small_panel_width + gap):
            
            center_x, center_y = x + small_panel_width//2, y + small_panel_height//2
            current_pixel = result_image[center_y, center_x]
            
            if not (current_pixel[0] > 200 and current_pixel[1] < 50 and current_pixel[2] < 50):
                
                panel_roi = rooftop_mask[y:y+small_panel_height, x:x+small_panel_width]
                
                if panel_roi.size > 0:
                    rooftop_pixels = np.sum(panel_roi == 255)
                    total_pixels = panel_roi.size
                    coverage = rooftop_pixels / total_pixels
                    
                    if coverage >= min_coverage_small:
                        cv2.rectangle(result_image, (x, y), (x + small_panel_width, y + small_panel_height), (255, 0, 0), -1)
                        cv2.rectangle(result_image, (x, y), (x + small_panel_width, y + small_panel_height), (0, 0, 0), 1)
                        panel_count += 1
    
    print(f"Placed {panel_count} solar panels")
    return result_image, panel_count


def place_solar_panels_double_density(image, rooftop_mask):
    result_image = image.copy()
    rows, cols = rooftop_mask.shape
    
    panel_width = 8     # Much smaller panels
    panel_height = 6    # Much smaller height
    gap = 0            # NO gap between panels for maximum density
    min_coverage = 0.50  # Lower threshold for more placement
    
    panel_count = 0
    
    print(f"DOUBLE DENSITY PANEL PLACEMENT")
    print(f"Panel size: {panel_width}x{panel_height}")
    print(f"Gap: {gap}px (no gaps)")
    print(f"Coverage required: {min_coverage*100}%")
    
    for y in range(0, rows - panel_height, panel_height + gap + 1):
        for x in range(0, cols - panel_width, panel_width + gap + 1):
            
            panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
            
            if panel_roi.size > 0:
                rooftop_pixels = np.sum(panel_roi == 255)
                total_pixels = panel_roi.size
                coverage = rooftop_pixels / total_pixels
                
                if coverage >= min_coverage:
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 255), -1)
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 1)
                    panel_count += 1
    
    micro_panel_width = 6
    micro_panel_height = 4
    min_coverage_micro = 0.40  # Very low threshold for micro panels
    
    print(f"Micro-panel filling with {micro_panel_width}x{micro_panel_height} panels, {min_coverage_micro*100}% threshold")
    
    for y in range(0, rows - micro_panel_height, micro_panel_height + 1):
        for x in range(0, cols - micro_panel_width, micro_panel_width + 1):
            
            center_x, center_y = x + micro_panel_width//2, y + micro_panel_height//2
            current_pixel = result_image[center_y, center_x]
            
            if not (current_pixel[2] > 200 and current_pixel[0] < 50 and current_pixel[1] < 50):
                
                panel_roi = rooftop_mask[y:y+micro_panel_height, x:x+micro_panel_width]
                
                if panel_roi.size > 0:
                    rooftop_pixels = np.sum(panel_roi == 255)
                    total_pixels = panel_roi.size
                    coverage = rooftop_pixels / total_pixels
                    
                    if coverage >= min_coverage_micro:
                        cv2.rectangle(result_image, (x, y), (x + micro_panel_width, y + micro_panel_height), (0, 165, 255), -1)
                        cv2.rectangle(result_image, (x, y), (x + micro_panel_width, y + micro_panel_height), (0, 0, 0), 1)
                        panel_count += 1
    
    print(f"Placed {panel_count} solar panels (DOUBLE DENSITY)")
    return result_image, panel_count


def place_solar_panels_custom(image, rooftop_mask, target_count, panel_width=40, panel_height=25):
    print(f"CUSTOM PANEL PLACEMENT")
    print(f"Target panels: {target_count}")
    print(f"Starting with default panel size: {panel_width}x{panel_height}")
    print(f"Gap: 3px")
    print(f"Color: Blue")
    
    result_image = image.copy()
    
    contours, _ = cv2.findContours(rooftop_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Try default size first (40x25)
    possible_positions = []
    gap = 3
    
    for contour in contours:
        x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
        
        for y in range(y_cont, y_cont + h_cont - panel_height + 1, panel_height + gap):
            for x in range(x_cont, x_cont + w_cont - panel_width + 1, panel_width + gap):
                panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
                
                if panel_roi.size > 0:
                    rooftop_pixels = np.sum(panel_roi == 255)
                    total_pixels = panel_roi.size
                    coverage = rooftop_pixels / total_pixels
                    
                    if coverage >= 0.4:
                        possible_positions.append((x, y, coverage))
    
    # If not enough space, try medium size (30x20)
    if len(possible_positions) < target_count:
        print(f"Not enough space for {target_count} panels at 40x25, trying 30x20...")
        panel_width, panel_height = 30, 20
        gap = 2
        possible_positions = []
        
        for contour in contours:
            x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
            
            for y in range(y_cont, y_cont + h_cont - panel_height + 1, panel_height + gap):
                for x in range(x_cont, x_cont + w_cont - panel_width + 1, panel_width + gap):
                    panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
                    
                    if panel_roi.size > 0:
                        rooftop_pixels = np.sum(panel_roi == 255)
                        total_pixels = panel_roi.size
                        coverage = rooftop_pixels / total_pixels
                        
                        if coverage >= 0.3:
                            possible_positions.append((x, y, coverage))
    
    # If still not enough, try smaller size (20x15)
    if len(possible_positions) < target_count:
        print(f"Still not enough space, trying 20x15...")
        panel_width, panel_height = 20, 15
        gap = 2
        possible_positions = []
        
        for contour in contours:
            x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
            
            for y in range(y_cont, y_cont + h_cont - panel_height + 1, panel_height + gap):
                for x in range(x_cont, x_cont + w_cont - panel_width + 1, panel_width + gap):
                    panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
                    
                    if panel_roi.size > 0:
                        rooftop_pixels = np.sum(panel_roi == 255)
                        total_pixels = panel_roi.size
                        coverage = rooftop_pixels / total_pixels
                        
                        if coverage >= 0.25:
                            possible_positions.append((x, y, coverage))
    
    # If still not enough, try micro size (12x8)
    if len(possible_positions) < target_count:
        print(f"Still not enough space, trying micro panels 12x8...")
        panel_width, panel_height = 12, 8
        gap = 1
        possible_positions = []
        
        for contour in contours:
            x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
            
            for y in range(y_cont, y_cont + h_cont - panel_height + 1, panel_height + gap):
                for x in range(x_cont, x_cont + w_cont - panel_width + 1, panel_width + gap):
                    panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
                    
                    if panel_roi.size > 0:
                        rooftop_pixels = np.sum(panel_roi == 255)
                        total_pixels = panel_roi.size
                        coverage = rooftop_pixels / total_pixels
                        
                        if coverage >= 0.15:
                            possible_positions.append((x, y, coverage))
    
    possible_positions.sort(key=lambda pos: pos[2], reverse=True)
    
    panels_placed = 0
    used_positions = set()
    
    # Adjust text size based on panel size
    if panel_width >= 30:
        font_scale = 0.7
        font_thickness = 2
        text_offset = 8
    elif panel_width >= 20:
        font_scale = 0.5
        font_thickness = 1
        text_offset = 6
    else:
        font_scale = 0.3
        font_thickness = 1
        text_offset = 4
    
    for x, y, coverage in possible_positions:
        if panels_placed >= target_count:
            break
            
        overlap = False
        for used_x, used_y in used_positions:
            if (abs(x - used_x) < panel_width + gap and 
                abs(y - used_y) < panel_height + gap):
                overlap = True
                break
        
        if not overlap:
            cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (255, 0, 0), -1)
            cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 1)
            
            panel_num = panels_placed + 1
            text_x = x + panel_width // 2 - text_offset
            text_y = y + panel_height // 2 + 3
            
            # Add text background for better visibility on larger panels
            if panel_width >= 20:
                cv2.rectangle(result_image, (text_x-text_offset, text_y-10), 
                            (text_x+text_offset*2, text_y+2), (0, 0, 0), -1)
            
            cv2.putText(result_image, str(panel_num), (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
            
            used_positions.add((x, y))
            panels_placed += 1
    
    print(f"Successfully placed {panels_placed} out of {target_count} requested panels")
    print(f"Final panel size used: {panel_width}x{panel_height}")
    return result_image, panels_placed


def main(args=None):
    target_colors = [
        (60, 49, 55), (55, 40, 45), (72, 53, 55), (81, 59, 64),
        (86, 63, 69), (79, 60, 66), (92, 70, 76), (74, 52, 58),
        (85, 64, 70), (78, 57, 63), (68, 50, 55), (89, 66, 72),
        (82, 61, 66), (58, 45, 51), (96, 73, 79), (70, 52, 57),
        (120, 100, 90), (110, 95, 85), (130, 110, 100), (100, 85, 75),
        (140, 120, 110), (125, 105, 95), (115, 100, 90), (135, 115, 105),
        (150, 120, 100), (160, 130, 110), (140, 110, 90), (155, 125, 105),
        (90, 85, 80), (105, 100, 95), (95, 90, 85), (110, 105, 100)
    ]
    
    if args and args.image:
        image_path = args.image
        if not os.path.exists(image_path):
            print(f"❌ Error: Image '{image_path}' not found!")
            return
    else:
        image_path = INPUT_IMAGE_PATH
        if not os.path.exists(image_path):
            print(f"❌ Error: Predefined image '{image_path}' not found!")
            print("💡 Please update the INPUT_IMAGE_PATH variable at the top of the script")
            return
    
    if args and args.panels:
        num_panels = args.panels
    else:
        while True:
            try:
                print(f"🔋 SOLAR PANEL PLACEMENT")
                print(f"📸 Input Image: {image_path}")
                print("-" * 50)
                num_panels = int(input("🎯 How many solar panels would you like to place? "))
                if num_panels > 0:
                    break
                else:
                    print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return
    
    print(f"\n🚀 Processing with {num_panels} solar panels...")
    
    images = [image_path]
    
    for fname in images:
        print(f"\n{'='*60}")
        print(f"Processing: {fname}")
        print(f"{'='*60}")
        
        image = cv2.imread(fname)
        if image is None:
            print(f"Could not load {fname}")
            continue
        
        h, w = image.shape[:2]
        print(f"Image size: {w}x{h}")
        
        tolerances = TOLERANCE_VALUES
        print(f"Testing tolerance values: ±{tolerances}")
        results = []
        
        for tolerance in tolerances:
            print(f"\n--- Testing Tolerance ±{tolerance} ---")
            
            rooftop_mask = detect_rooftops_targeted(image, target_colors, tolerance)
            
            total_pixels = h * w
            rooftop_pixels = np.sum(rooftop_mask == 255)
            coverage_pct = (rooftop_pixels / total_pixels) * 100
            
            print(f"Coverage: {coverage_pct:.1f}%")
            
            # Simple rooftop measurements
            contours, _ = cv2.findContours(rooftop_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # Get ALL contours to find the full polygon dimensions
                all_points = []
                for contour in contours:
                    for point in contour:
                        all_points.append(point[0])
                
                if all_points:
                    all_points = np.array(all_points)
                    # Get the full bounding rectangle of ALL rooftop areas
                    x_min = np.min(all_points[:, 0])
                    x_max = np.max(all_points[:, 0])
                    y_min = np.min(all_points[:, 1])
                    y_max = np.max(all_points[:, 1])
                    
                    # Full polygon dimensions
                    full_width = x_max - x_min
                    full_height = y_max - y_min
                    length = max(full_width, full_height)
                    breadth = min(full_width, full_height)
                    
                    # Get largest contour for area calculation
                    largest_contour = max(contours, key=cv2.contourArea)
                    pixel_count = cv2.countNonZero(rooftop_mask)
                    area_pixels = cv2.contourArea(largest_contour)
                    
                    # Convert to meters (0.15m per pixel for zoom level 20)
                    meters_per_pixel = 0.15
                    length_m = length * meters_per_pixel
                    breadth_m = breadth * meters_per_pixel
                    area_m2 = area_pixels * (meters_per_pixel ** 2)
                    total_roof_area_m2 = length_m * breadth_m  # Full rectangular roof area
                    
                    print(f"🏠 ROOFTOP: {pixel_count:,} pixels | Area: {area_pixels:,.0f}px² | Length: {length}px | Breadth: {breadth}px")
                    print(f"📐 METERS: Length: {length_m:.1f}m | Breadth: {breadth_m:.1f}m | Detected Area: {area_m2:.1f}m²")
                    print(f"🏗️  TOTAL ROOF: {length_m:.1f}m × {breadth_m:.1f}m = {total_roof_area_m2:.1f}m² (full polygon)")
                    
                    # Store measurements for averaging
                    measurements = {
                        'length_m': length_m,
                        'breadth_m': breadth_m,
                        'area_m2': area_m2,
                        'total_roof_area_m2': total_roof_area_m2
                    }
                else:
                    measurements = None
            
            result_image_custom, panel_count_custom = place_solar_panels_custom(
                image, rooftop_mask, num_panels)
            
            results.append({
                'tolerance': tolerance,
                'coverage': coverage_pct,
                'mask': rooftop_mask,
                'result_custom': result_image_custom,
                'panels_custom': panel_count_custom,
                'measurements': measurements,
                'mode': 'custom'
            })
        
        best_result = None
        best_score = 0
        
        for result in results:
            coverage_score = 100 if 5 <= result['coverage'] <= 20 else max(0, 50 - abs(result['coverage'] - 12.5))
            
            achieved_panels = result['panels_custom']
            panel_score = max(0, 100 - abs(num_panels - achieved_panels) * 2)
            print(f"Tolerance ±{result['tolerance']}: {result['coverage']:.1f}% coverage, {achieved_panels}/{num_panels} custom panels, Score: {coverage_score + panel_score:.1f}")
            
            total_score = coverage_score + panel_score
            
            if total_score > best_score:
                best_score = total_score
                best_result = result
        
        if best_result:
            # Calculate average measurements from all tolerances
            valid_measurements = [r['measurements'] for r in results if r['measurements'] is not None]
            if valid_measurements:
                avg_length = sum(m['length_m'] for m in valid_measurements) / len(valid_measurements)
                avg_breadth = sum(m['breadth_m'] for m in valid_measurements) / len(valid_measurements)
                avg_area = sum(m['area_m2'] for m in valid_measurements) / len(valid_measurements)
                avg_total_roof = sum(m['total_roof_area_m2'] for m in valid_measurements) / len(valid_measurements)
                
                print(f"\n🎯 AVERAGE ROOF MEASUREMENTS:")
                print(f"   📏 Length: {avg_length:.1f}m")
                print(f"   📐 Breadth: {avg_breadth:.1f}m") 
                print(f"   📊 Detected Area: {avg_area:.1f}m²")
                print(f"   🏗️  Total Roof: {avg_length:.1f}m × {avg_breadth:.1f}m = {avg_total_roof:.1f}m²")
            
            print(f"\n🎉 BEST RESULT:")
            print(f"   📊 Tolerance: ±{best_result['tolerance']}")
            print(f"   📈 Coverage: {best_result['coverage']:.1f}%")
            print(f"   🔋 Custom Panels: {best_result['panels_custom']}/{num_panels} (achieved/target)")
            
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            fig.suptitle(f'Custom Solar Panels - {best_result["panels_custom"]}/{num_panels} panels placed', fontsize=16, fontweight='bold')
            
            axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            axes[0].set_title('Original Image', fontsize=14, fontweight='bold')
            axes[0].axis('off')
            
            axes[1].imshow(best_result['mask'], cmap='gray')
            axes[1].set_title(f'Detected Rooftops\\n±{best_result["tolerance"]} tolerance', fontsize=14, fontweight='bold')
            axes[1].axis('off')
            
            axes[2].imshow(cv2.cvtColor(best_result['result_custom'], cv2.COLOR_BGR2RGB))
            axes[2].set_title(f'Custom Panels\\n{best_result["panels_custom"]} placed', fontsize=14, fontweight='bold')
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.show()
            
            output_name = os.path.basename(fname).split('.')[0]
            
            cv2.imwrite(f'final_rooftops_{output_name}.jpg', best_result['mask'])
            cv2.imwrite(f'final_solar_custom_{output_name}.jpg', best_result['result_custom'])
            
            print(f"\n💾 SAVED FILES:")
            print(f"   📁 Rooftops: final_rooftops_{output_name}.jpg")
            print(f"   🔋 Custom Panels: final_solar_custom_{output_name}.jpg")
            
        else:
            print("\n❌ No suitable results found")


if __name__ == "__main__":
    print("🔋 GK HACKS - ROOFTOP DETECTION & SOLAR PANEL PLACEMENT 🏠")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='🔋 GK HACKS - Rooftop Detection and Solar Panel Placement 🏠')
        parser.add_argument('--mode', choices=['normal', 'double', 'both', 'custom'], default='custom',
                           help='Solar panel placement mode (default: custom)')
        parser.add_argument('--image', type=str, help='Specific image file to process (optional)')
        parser.add_argument('--panels', type=int, help='Number of solar panels to place')
        
        args = parser.parse_args()
        
        if args.mode == 'custom' and args.panels is None:
            print("Error: --panels argument is required for custom mode")
            print("Example: python rooftop_detection_gk.py --mode custom --panels 10")
            sys.exit(1)
        if args.panels and args.panels <= 0:
            print("Error: Number of panels must be positive")
            sys.exit(1)
        
        main(args)
    else:
        print(f"📁 Using predefined image: {INPUT_IMAGE_PATH}")
        print("💡 To change the image, edit the INPUT_IMAGE_PATH variable at the top of the script")
        print()
        main()
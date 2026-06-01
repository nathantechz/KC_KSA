import subprocess
import sys
import os

os.chdir('/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA')

try:
    result = subprocess.run(
        ['/opt/homebrew/bin/python3', 'generate_table1_fig1.py'],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    # Print key output lines
    for line in result.stdout.split('\n'):
        if any(keyword in line for keyword in ['saved', 'Peak', 'improvements', 'COMPLETE', 'Figure']):
            print(line)
    
    if result.returncode == 0:
        print("\n✅ Script completed successfully!")
        print("Check for: fig1_annual_trend_v3.png")
    else:
        print(f"\n❌ Script failed with return code {result.returncode}")
        if result.stderr:
            print("STDERR:", result.stderr[-500:])
            
except subprocess.TimeoutExpired:
    print("Process timed out")
except Exception as e:
    print(f"Error: {e}")

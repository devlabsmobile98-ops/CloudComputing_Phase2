import argparse
from preprocessing_service.app import run_preprocessing
from detection_service.app import run_detection
from window_service.app import run_windowing
from validation_service.app import run_validation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--max-per-type", type=int, default=100)
    parser.add_argument("--window-size", type=int, default=50)
    args = parser.parse_args()

    pre = run_preprocessing(input_path=args.input)
    print(f"Cleaned data saved to: {pre['output_path']}")
    print(f"Rows: {pre['rows']}")

    det = run_detection()
    print(f"Enriched data saved to: {det['enriched_path']}")
    print(f"Detected events saved to: {det['events_path']}")
    print(f"Total events: {det['total_events']}")

    win = run_windowing(max_per_type=args.max_per_type, window_size=args.window_size)
    print(f"Output windows saved to: {win['output_dir']}")
    print(f"Windows created: {win['windows_created']}")
    print(f"Windows rejected: {win['windows_rejected']}")

    val = run_validation()
    print(f"Validation details saved to: {val['details_path']}")
    print(f"Windows checked: {val['window_files_checked']}")
    print(f"Windows passed: {val['windows_passed']}")
    print(f"Windows failed: {val['windows_failed']}")
    print("Phase 2 optimized pipeline completed successfully.")


if __name__ == "__main__":
    main()

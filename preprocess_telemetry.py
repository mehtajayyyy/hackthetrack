"""
Telemetry Data Preprocessing Script
====================================
Pre-processes large telemetry CSV files into aggregated Parquet format.

This script reads the raw telemetry CSV files (1.5GB each) and aggregates them
by vehicle_id, lap, and telemetry_name, then saves as compressed Parquet files.
This reduces file size by ~95% while maintaining all functionality.

Usage:
    python preprocess_telemetry.py

Output:
    - R1_barber_telemetry_aggregated.parquet
    - R2_barber_telemetry_aggregated.parquet
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Import from config (handle case where aggregated paths might not exist yet)
try:
    from config import (
        TELEMETRY_R1_PATH, 
        TELEMETRY_R2_PATH, 
        ID_COL, 
        LAP_COL
    )
    # Try to import aggregated paths, if not defined, use defaults
    try:
        from config import (
            TELEMETRY_R1_AGGREGATED_PATH,
            TELEMETRY_R2_AGGREGATED_PATH
        )
    except ImportError:
        TELEMETRY_R1_AGGREGATED_PATH = "R1_barber_telemetry_aggregated.parquet"
        TELEMETRY_R2_AGGREGATED_PATH = "R2_barber_telemetry_aggregated.parquet"
except ImportError:
    # Fallback if config doesn't exist
    TELEMETRY_R1_PATH = "R1_barber_telemetry_data.csv"
    TELEMETRY_R2_PATH = "R2_barber_telemetry_data.csv"
    TELEMETRY_R1_AGGREGATED_PATH = "R1_barber_telemetry_aggregated.parquet"
    TELEMETRY_R2_AGGREGATED_PATH = "R2_barber_telemetry_aggregated.parquet"
    ID_COL = "vehicle_id"
    LAP_COL = "lap"

# Chunk size for reading large CSV files
CHUNK_SIZE = 100000  # Read 100k rows at a time


def aggregate_telemetry_file(input_path: str, output_path: str) -> None:
    """
    Aggregate telemetry CSV file into Parquet format.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to output Parquet file
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return
    
    print(f"Processing {input_path}...")
    print(f"Output will be saved to: {output_path}")
    
    # Read CSV in chunks and aggregate
    aggregated_chunks = []
    total_rows = 0
    
    try:
        # Read file in chunks
        chunk_iter = pd.read_csv(
            input_path, 
            low_memory=False,
            chunksize=CHUNK_SIZE,
            iterator=True
        )
        
        for chunk_num, chunk in enumerate(chunk_iter):
            total_rows += len(chunk)
            
            # Convert timestamp to datetime
            if 'timestamp' in chunk.columns:
                chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], errors='coerce')
            
            # Convert telemetry_value to numeric
            if 'telemetry_value' in chunk.columns:
                chunk['telemetry_value'] = pd.to_numeric(
                    chunk['telemetry_value'], 
                    errors='coerce'
                )
            
            # Group by vehicle_id, lap, and telemetry_name, calculate mean
            # This matches the logic in process_telemetry()
            aggregated = chunk.groupby([ID_COL, LAP_COL, 'telemetry_name']).agg({
                'telemetry_value': 'mean',
                'timestamp': 'first'  # Keep first timestamp for reference
            }).reset_index()
            
            aggregated_chunks.append(aggregated)
            
            if (chunk_num + 1) % 10 == 0:
                print(f"  Processed {chunk_num + 1} chunks ({total_rows:,} rows)...")
        
        print(f"  Total rows processed: {total_rows:,}")
        print("  Combining chunks...")
        
        # Combine all chunks
        combined_df = pd.concat(aggregated_chunks, ignore_index=True)
        
        # Final aggregation in case of overlaps
        print("  Performing final aggregation...")
        final_df = combined_df.groupby([ID_COL, LAP_COL, 'telemetry_name']).agg({
            'telemetry_value': 'mean',
            'timestamp': 'first'
        }).reset_index()
        
        # Pivot to match the structure used in process_telemetry()
        # This creates columns for each telemetry_name
        print("  Creating pivot table...")
        pivot_df = final_df.pivot_table(
            index=[ID_COL, LAP_COL],
            columns='telemetry_name',
            values='telemetry_value',
            aggfunc='mean'
        ).reset_index()
        
        # Save as Parquet with compression
        print(f"  Saving to {output_path}...")
        pivot_df.to_parquet(
            output_path,
            compression='snappy',  # Fast compression
            index=False
        )
        
        # Get file sizes
        input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        reduction = (1 - output_size / input_size) * 100
        
        print(f"\n✓ Successfully processed {input_path}")
        print(f"  Input size:  {input_size:.2f} MB")
        print(f"  Output size: {output_size:.2f} MB")
        print(f"  Reduction:   {reduction:.1f}%")
        print(f"  Rows:        {len(pivot_df):,}")
        print(f"  Columns:     {len(pivot_df.columns)}")
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main function to process both telemetry files."""
    print("=" * 60)
    print("Telemetry Data Preprocessing")
    print("=" * 60)
    print()
    
    # Check if input files exist
    if not os.path.exists(TELEMETRY_R1_PATH):
        print(f"Warning: {TELEMETRY_R1_PATH} not found. Skipping Race 1.")
    else:
        aggregate_telemetry_file(TELEMETRY_R1_PATH, TELEMETRY_R1_AGGREGATED_PATH)
        print()
    
    if not os.path.exists(TELEMETRY_R2_PATH):
        print(f"Warning: {TELEMETRY_R2_PATH} not found. Skipping Race 2.")
    else:
        aggregate_telemetry_file(TELEMETRY_R2_PATH, TELEMETRY_R2_AGGREGATED_PATH)
        print()
    
    print("=" * 60)
    print("Preprocessing complete!")
    print("=" * 60)
    print("\nYou can now use the aggregated Parquet files in the application.")
    print("The app will automatically detect and use them if available.")


if __name__ == "__main__":
    main()


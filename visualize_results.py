import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# Set style for publication-quality graphs
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['figure.dpi'] = 150

def parse_args():
    parser = argparse.ArgumentParser(description="Generate visualizations for experiment results")
    parser.add_argument("--model", type=str, required=True, 
                       help="Model name (e.g., 'llama_3.1_8b', 'llama_3.3_70b', 'llama_3.2_3b')")
    parser.add_argument("--sample-size", type=int, default=5, 
                       help="Sample size used in the experiment")
    parser.add_argument("--output-dir", type=str, default="visualizations",
                       help="Base output directory for images")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Create model-specific output directory
    output_dir = Path(args.output_dir) / args.model
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"📊 Generating visualizations for: {args.model}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📈 Sample size: {args.sample_size}")
    print(f"{'='*60}\n")
    
    # ============================================================
    # DATA FROM YOUR SUCCESSFUL RUN (Llama 3.1 8B, sample-size 5)
    # UPDATE THESE VALUES FOR EACH MODEL
    # ============================================================
    
    strategies = ['Baseline', 'CoT', 'Repetition']
    positions = ['Top', 'Middle', 'End']
    
    # ⚠️ UPDATE THESE VALUES FOR EACH MODEL ⚠️
    recall_data = {
        'Baseline': [1.0, 1.0, 1.0],    # [Top, Middle, End]
        'CoT': [1.0, 1.0, 1.0],
        'Repetition': [1.0, 1.0, 1.0]
    }
    
    output_words_data = {
        'Baseline': [100.4, 102.4, 105.0],
        'CoT': [90.4, 92.6, 86.6],
        'Repetition': [118.4, 132.8, 128.8]
    }
    
    latency_data = {
        'Baseline': [5.60, 15.11, 15.56],
        'CoT': [15.73, 15.34, 15.36],
        'Repetition': [15.46, 16.16, 15.79]
    }
    
    # Position sensitivity (calculated)
    position_sensitivity = {
        'Baseline': max(recall_data['Baseline']) - min(recall_data['Baseline']),
        'CoT': max(recall_data['CoT']) - min(recall_data['CoT']),
        'Repetition': max(recall_data['Repetition']) - min(recall_data['Repetition'])
    }
    
    # ============================================================
    # SAVE RAW DATA AS CSV
    # ============================================================
    raw_data = []
    for strategy in strategies:
        for i, pos in enumerate(positions):
            raw_data.append({
                'model': args.model,
                'strategy': strategy,
                'position': pos,
                'recall': recall_data[strategy][i],
                'output_words': output_words_data[strategy][i],
                'latency_s': latency_data[strategy][i],
                'sample_size': args.sample_size,
                'timestamp': datetime.now().isoformat()
            })
    
    df = pd.DataFrame(raw_data)
    csv_path = output_dir / f"{args.model}_raw_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved raw data: {csv_path}")
    
    x = np.arange(len(positions))
    width = 0.25
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    # ============================================================
    # GRAPH 1: Recall by Position (Bar Chart)
    # ============================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = []
    for i, (strategy, color) in enumerate(zip(strategies, colors)):
        bars.append(ax.bar(x + i*width, recall_data[strategy], width, 
                           label=strategy, color=color, alpha=0.8))
    
    ax.set_ylabel('Recall (Minority Opinion Detection)', fontsize=12)
    ax.set_xlabel('Position of Negative Review', fontsize=12)
    ax.set_title(f'{args.model}: Recall by Position and Strategy\n(sample-size={args.sample_size})', fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(positions)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    
    for bar_group in bars:
        for bar in bar_group:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'recall_by_position.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved: recall_by_position.png")
    
    # ============================================================
    # GRAPH 2: Output Words by Position
    # ============================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (strategy, color) in enumerate(zip(strategies, colors)):
        ax.bar(x + i*width, output_words_data[strategy], width, 
               label=strategy, color=color, alpha=0.8)
    
    ax.set_ylabel('Output Length (Words)', fontsize=12)
    ax.set_xlabel('Position of Negative Review', fontsize=12)
    ax.set_title(f'{args.model}: Output Length by Position and Strategy\n(sample-size={args.sample_size})', fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(positions)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    for i, strategy in enumerate(strategies):
        for j, pos in enumerate(positions):
            val = output_words_data[strategy][j]
            ax.annotate(f'{val:.0f}', xy=(x[j] + i*width, val),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'output_words_by_position.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved: output_words_by_position.png")
    
    # ============================================================
    # GRAPH 3: Latency by Position
    # ============================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (strategy, color) in enumerate(zip(strategies, colors)):
        ax.bar(x + i*width, latency_data[strategy], width, 
               label=strategy, color=color, alpha=0.8)
    
    ax.set_ylabel('Latency (seconds)', fontsize=12)
    ax.set_xlabel('Position of Negative Review', fontsize=12)
    ax.set_title(f'{args.model}: Latency by Position and Strategy\n(sample-size={args.sample_size})', fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(positions)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    for i, strategy in enumerate(strategies):
        for j, pos in enumerate(positions):
            val = latency_data[strategy][j]
            ax.annotate(f'{val:.1f}s', xy=(x[j] + i*width, val),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'latency_by_position.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved: latency_by_position.png")
    
    # ============================================================
    # GRAPH 4: Recall Line Chart
    # ============================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    for strategy, color in zip(strategies, colors):
        ax.plot(positions, recall_data[strategy], 'o-', 
                label=strategy, color=color, linewidth=2, markersize=8)
    
    ax.set_ylabel('Recall', fontsize=12)
    ax.set_xlabel('Position of Negative Review', fontsize=12)
    ax.set_title(f'{args.model}: Recall Across Positions\n(sample-size={args.sample_size})', fontsize=14)
    ax.set_ylim(0.5, 1.05)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=1.0, color='green', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'recall_line_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved: recall_line_comparison.png")
    
    # ============================================================
    # GRAPH 5: Summary Table
    # ============================================================
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    
    avg_output = {s: sum(output_words_data[s])/3 for s in strategies}
    avg_latency = {s: sum(latency_data[s])/3 for s in strategies}
    
    table_data = [
        ['Strategy', 'Top Recall', 'Middle Recall', 'End Recall', 'Avg Output Words', 'Avg Latency (s)', 'Position Sensitivity'],
        ['Baseline', f'{recall_data["Baseline"][0]:.2f}', f'{recall_data["Baseline"][1]:.2f}', 
         f'{recall_data["Baseline"][2]:.2f}', f'{avg_output["Baseline"]:.1f}', f'{avg_latency["Baseline"]:.1f}', f'{position_sensitivity["Baseline"]:.2f}'],
        ['CoT', f'{recall_data["CoT"][0]:.2f}', f'{recall_data["CoT"][1]:.2f}', 
         f'{recall_data["CoT"][2]:.2f}', f'{avg_output["CoT"]:.1f}', f'{avg_latency["CoT"]:.1f}', f'{position_sensitivity["CoT"]:.2f}'],
        ['Repetition', f'{recall_data["Repetition"][0]:.2f}', f'{recall_data["Repetition"][1]:.2f}', 
         f'{recall_data["Repetition"][2]:.2f}', f'{avg_output["Repetition"]:.1f}', f'{avg_latency["Repetition"]:.1f}', f'{position_sensitivity["Repetition"]:.2f}'],
    ]
    
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Color coding for perfect recall
    for i in range(1, 4):
        for j in range(1, 4):
            if float(table_data[i][j]) == 1.0:
                table[(i, j)].set_facecolor('#90EE90')
    
    ax.set_title(f'{args.model}: Results Summary (sample-size={args.sample_size})', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'results_summary_table.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved: results_summary_table.png")
    
    # ============================================================
    # SUMMARY
    # ============================================================
    print(f"\n{'='*60}")
    print(f"✅ All visualizations saved to: {output_dir}/")
    print(f"{'='*60}")
    print("\n📁 Generated files:")
    for f in sorted(output_dir.iterdir()):
        size = f.stat().st_size / 1024
        print(f"   - {f.name} ({size:.1f} KB)")
    
    # Save a summary file
    summary_path = output_dir / f"{args.model}_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(f"Model: {args.model}\n")
        f.write(f"Sample Size: {args.sample_size}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Position Sensitivity:\n")
        for s in strategies:
            f.write(f"  {s}: {position_sensitivity[s]:.4f}\n")
    print(f"\n✓ Saved summary: {summary_path}")

if __name__ == "__main__":
    main()
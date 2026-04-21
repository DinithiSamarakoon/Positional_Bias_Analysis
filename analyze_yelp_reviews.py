import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev
import sys

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def validate_file(path: Path):
    """Check if file exists and is not empty."""
    if not path.exists():
        print(f"❌ File not found: {path}")
        return False
    if path.stat().st_size == 0:
        print(f"❌ File is empty: {path}")
        return False
    print(f"✓ File exists and has size: {path.stat().st_size / (1024*1024):.2f} MB")
    return True


def load_business_metadata(path: Path):
    """Load business metadata with error handling."""
    metadata = {}
    duplicates = set()
    malformed = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                business_id = record.get("business_id")
                
                if business_id in metadata:
                    duplicates.add(business_id)
                
                metadata[business_id] = {
                    "name": record.get("name", ""),
                    "reported_review_count": record.get("review_count"),
                }
            except json.JSONDecodeError as e:
                malformed += 1
                if malformed <= 3:  # Show first 3 errors
                    print(f"  ⚠ Malformed JSON at line {line_num}: {str(e)[:60]}")
    
    if malformed > 3:
        print(f"  ⚠ Total malformed records: {malformed}")
    if duplicates:
        print(f"  ⚠ Found {len(duplicates)} duplicate business IDs")
    
    return metadata, malformed, duplicates


def classify_review(stars: float):
    if stars >= 4:
        return "positive"
    if stars <= 2:
        return "negative"
    return "neutral"


def analyze_reviews(path: Path):
<<<<<<< HEAD
    counts = defaultdict(lambda: {"total": 0, "five_star": 0, "positive": 0, "negative": 0, "neutral": 0})
=======
    """Analyze reviews with error handling and data quality checks."""
    counts = defaultdict(lambda: {"total": 0, "positive": 0, "negative": 0, "neutral": 0})
>>>>>>> 6e2b721 (Initial commit)
    total_reviews = 0
    malformed = 0
    duplicates = defaultdict(int)
    star_distribution = defaultdict(int)

    with path.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                business_id = record["business_id"]
                stars = float(record["stars"])
                
                # Track star distribution
                star_distribution[int(stars)] += 1
                
                # Detect duplicates (same business_id appearing multiple times)
                if counts[business_id]["total"] > 0:
                    duplicates[business_id] += 1
                
                label = classify_review(stars)

<<<<<<< HEAD
            counts[business_id]["total"] += 1
            if stars == 5:
                counts[business_id]["five_star"] += 1
            counts[business_id][label] += 1
            total_reviews += 1

    return counts, total_reviews
=======
                counts[business_id]["total"] += 1
                counts[business_id][label] += 1
                total_reviews += 1
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                malformed += 1
                if malformed <= 3:
                    print(f"  ⚠ Malformed review at line {line_num}: {str(e)[:60]}")
    
    if malformed > 3:
        print(f"  ⚠ Total malformed review records: {malformed}")
    if duplicates:
        print(f"  ⚠ Found {len(duplicates)} businesses with duplicate reviews")
    
    return counts, total_reviews, malformed, duplicates, star_distribution
>>>>>>> 6e2b721 (Initial commit)


def build_rows(business_metadata, review_counts):
    rows = []
    all_business_ids = set(business_metadata) | set(review_counts)

    for business_id in all_business_ids:
        meta = business_metadata.get(business_id, {})
        counts = review_counts.get(business_id, {"total": 0, "positive": 0, "negative": 0, "neutral": 0})
        total = counts["total"]
        five_star = counts.get("five_star", 0)
        positive = counts["positive"]
        negative = counts["negative"]
        neutral = counts["neutral"]
        meets_threshold = five_star >= 10 and negative >= 1

        rows.append(
            {
                "business_id": business_id,
                "name": meta.get("name", ""),
                "reported_review_count": meta.get("reported_review_count", ""),
                "review_count": total,
                "five_star_reviews": five_star,
                "positive_reviews": positive,
                "negative_reviews": negative,
                "neutral_reviews": neutral,
                "meets_10_five_star_1_negative": meets_threshold,
            }
        )

    rows.sort(key=lambda row: (row["review_count"], row["five_star_reviews"], row["negative_reviews"]), reverse=True)
    return rows


def write_csv(rows, output_path: Path):
    fieldnames = [
        "business_id",
        "name",
        "reported_review_count",
        "review_count",
        "five_star_reviews",
        "positive_reviews",
        "negative_reviews",
        "neutral_reviews",
        "meets_10_five_star_1_negative",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_visualizations(reviewed_business_rows, star_distribution, output_dir: Path):
    """Generate and save visualizations."""
    if plt is None:
        print("⚠ matplotlib not installed. Skipping visualizations.")
        print("  Install with: pip install matplotlib")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Figure 1: Review count distribution
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Subplot 1: Star distribution
        stars = sorted(star_distribution.keys())
        counts = [star_distribution[s] for s in stars]
        axes[0, 0].bar(stars, counts, color='steelblue', alpha=0.7)
        axes[0, 0].set_xlabel('Star Rating')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].set_title('Distribution of Star Ratings')
        axes[0, 0].set_xticks(stars)
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # Subplot 2: Sentiment distribution
        sentiment_counts = defaultdict(int)
        for row in reviewed_business_rows:
            sentiment_counts['Positive'] += row['positive_reviews']
            sentiment_counts['Negative'] += row['negative_reviews']
            sentiment_counts['Neutral'] += row['neutral_reviews']
        
        sentiments = list(sentiment_counts.keys())
        sentiment_vals = list(sentiment_counts.values())
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        axes[0, 1].pie(sentiment_vals, labels=sentiments, autopct='%1.1f%%', colors=colors)
        axes[0, 1].set_title('Overall Sentiment Distribution')
        
        # Subplot 3: Reviews per business (histogram)
        review_counts = [row['review_count'] for row in reviewed_business_rows]
        axes[1, 0].hist(review_counts, bins=50, color='coral', alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Reviews per Business')
        axes[1, 0].set_ylabel('Number of Businesses')
        axes[1, 0].set_title('Distribution of Reviews per Business')
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # Subplot 4: Positive vs Negative scatter
        positive = [row['positive_reviews'] for row in reviewed_business_rows]
        negative = [row['negative_reviews'] for row in reviewed_business_rows]
        axes[1, 1].scatter(positive, negative, alpha=0.5, s=30, color='purple')
        axes[1, 1].set_xlabel('Positive Reviews')
        axes[1, 1].set_ylabel('Negative Reviews')
        axes[1, 1].set_title('Positive vs Negative Reviews by Business')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        viz_path = output_dir / "analysis_visualizations.png"
        plt.savefig(viz_path, dpi=100, bbox_inches='tight')
        print(f"✓ Visualization saved to: {viz_path}")
        plt.close()
        
    except Exception as e:
        print(f"⚠ Error creating visualizations: {e}")


def main():
    parser = argparse.ArgumentParser(description="Analyze Yelp business and review datasets.")
    parser.add_argument("--business-file", default="business.json", help="Path to business.json")
    parser.add_argument("--review-file", default="review.json", help="Path to review.json")
    parser.add_argument("--output-csv", default="business_review_stats.csv", help="Path for the detailed CSV output")
    parser.add_argument("--visualize", action="store_true", help="Generate visualization plots")
    args = parser.parse_args()

    workspace = Path(__file__).resolve().parent
    business_path = (workspace / args.business_file).resolve()
    review_path = (workspace / args.review_file).resolve()
    output_path = (workspace / args.output_csv).resolve()

    print("\n" + "="*60)
    print("YELP DATASET ANALYSIS")
    print("="*60 + "\n")

    # Validate files
    print("📁 File Validation:")
    if not validate_file(business_path):
        sys.exit(1)
    if not validate_file(review_path):
        sys.exit(1)
    print()

    # Load and analyze data
    print("📊 Loading Business Metadata...")
    business_metadata, biz_malformed, biz_duplicates = load_business_metadata(business_path)
    print(f"✓ Loaded {len(business_metadata)} unique businesses\n")

    print("📊 Analyzing Reviews...")
    review_counts, total_reviews, rev_malformed, rev_duplicates, star_dist = analyze_reviews(review_path)
    print(f"✓ Analyzed {total_reviews} reviews\n")

    rows = build_rows(business_metadata, review_counts)

    reviewed_business_rows = [row for row in rows if row["review_count"] > 0]
    threshold_rows = [row for row in reviewed_business_rows if row["meets_10_five_star_1_negative"]]
    review_counts_only = [row["review_count"] for row in reviewed_business_rows]

    write_csv(rows, output_path)

    total_businesses = len(rows)
    reviewed_businesses = len(reviewed_business_rows)
    threshold_businesses = len(threshold_rows)

<<<<<<< HEAD
    print("Dataset summary")
    print(f"Businesses in business.json: {total_businesses}")
    print(f"Businesses with at least one review: {reviewed_businesses}")
    print(f"Total reviews in review.json: {total_reviews}")
    print(f"Five-star reviews: {sum(row['five_star_reviews'] for row in reviewed_business_rows)}")
    print(f"Positive reviews (4-5 stars): {sum(row['positive_reviews'] for row in reviewed_business_rows)}")
    print(f"Negative reviews (1-2 stars): {sum(row['negative_reviews'] for row in reviewed_business_rows)}")
    print(f"Neutral reviews (3 stars): {sum(row['neutral_reviews'] for row in reviewed_business_rows)}")
    print()
    print("Per-business review count stats")
    print(f"Minimum reviews: {min(review_counts_only) if review_counts_only else 0}")
    print(f"Median reviews: {median(review_counts_only) if review_counts_only else 0}")
    print(f"Average reviews: {mean(review_counts_only):.2f}" if review_counts_only else "Average reviews: 0")
    print(f"Maximum reviews: {max(review_counts_only) if review_counts_only else 0}")
    print()
    print("Threshold check")
    print(f"Businesses with at least 10 five-star reviews and at least 1 negative review: {threshold_businesses}")
    if reviewed_businesses:
        print(f"Share of reviewed businesses meeting threshold: {threshold_businesses / reviewed_businesses:.2%}")
    print()
    print(f"Detailed CSV written to: {output_path}")
    print()
    print("Top 10 businesses by review count")
    for row in reviewed_business_rows[:10]:
        print(
            f"- {row['name'] or row['business_id']}: total={row['review_count']}, "
            f"five_star={row['five_star_reviews']}, negative={row['negative_reviews']}, "
            f"meets_threshold={row['meets_10_five_star_1_negative']}"
        )
=======
    print("━" * 60)
    print("DATASET SUMMARY")
    print("━" * 60)
    print(f"Businesses in business.json: {total_businesses:,}")
    print(f"Businesses with at least one review: {reviewed_businesses:,}")
    print(f"Total reviews in review.json: {total_reviews:,}")
    
    positive_total = sum(row['positive_reviews'] for row in reviewed_business_rows)
    negative_total = sum(row['negative_reviews'] for row in reviewed_business_rows)
    neutral_total = sum(row['neutral_reviews'] for row in reviewed_business_rows)
    
    print(f"Positive reviews (4-5 stars): {positive_total:,} ({positive_total/total_reviews*100:.1f}%)")
    print(f"Negative reviews (1-2 stars): {negative_total:,} ({negative_total/total_reviews*100:.1f}%)")
    print(f"Neutral reviews (3 stars): {neutral_total:,} ({neutral_total/total_reviews*100:.1f}%)")

    print("\n" + "━" * 60)
    print("REVIEW COUNT STATISTICS (Per Business)")
    print("━" * 60)
    if review_counts_only:
        print(f"Minimum reviews: {min(review_counts_only):,}")
        print(f"Median reviews: {median(review_counts_only):,.0f}")
        print(f"Average reviews: {mean(review_counts_only):,.2f}")
        print(f"Max reviews: {max(review_counts_only):,}")
        if len(review_counts_only) > 1:
            print(f"Std Dev: {stdev(review_counts_only):,.2f}")

    print("\n" + "━" * 60)
    print("THRESHOLD CHECK (10+ positive, 1+ negative)")
    print("━" * 60)
    print(f"Businesses meeting threshold: {threshold_businesses:,}")
    if reviewed_businesses:
        print(f"Share of reviewed businesses: {threshold_businesses / reviewed_businesses:.2%}")

    print("\n" + "━" * 60)
    print("DATA QUALITY REPORT")
    print("━" * 60)
    print(f"Business records - Malformed: {biz_malformed} | Duplicates: {len(biz_duplicates)}")
    print(f"Review records - Malformed: {rev_malformed} | Duplicates: {len(rev_duplicates)}")
    print(f"Star rating range: {min(star_dist.keys())}-{max(star_dist.keys())} stars")

    print("\n" + "━" * 60)
    print("OUTPUT FILES")
    print("━" * 60)
    print(f"✓ CSV written to: {output_path}")

    # Generate visualizations if requested
    if args.visualize:
        print("\n📈 Generating Visualizations...")
        plot_visualizations(reviewed_business_rows, star_dist, workspace / "analysis_output")

    print("\n" + "━" * 60)
    print("TOP 10 BUSINESSES BY REVIEW COUNT")
    print("━" * 60)
    for i, row in enumerate(reviewed_business_rows[:10], 1):
        name = row['name'] or row['business_id']
        status = "✓ ELIGIBLE" if row['meets_10_positive_1_negative'] else "✗ ineligible"
        print(f"{i:2d}. {name[:40]:40s} | total={row['review_count']:5d} | "
              f"+{row['positive_reviews']:3d} -{row['negative_reviews']:2d} {status}")

    print("\n" + "="*60 + "\n")
>>>>>>> 6e2b721 (Initial commit)


if __name__ == "__main__":
    main()
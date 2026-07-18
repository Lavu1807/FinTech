"""
Strategy Pattern for deterministic Chart Generation.
Generates both JSON metadata and physical PNG exports.
"""
import os
import uuid
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
from abc import ABC, abstractmethod
from typing import List, Optional
from .schemas import ChartMetadata
from .utils import get_numeric_cols, get_categorical_cols, get_date_col, get_target_metric

# Configure Matplotlib/Seaborn for accessibility and high quality
sns.set_theme(style="whitegrid", font_scale=1.1, palette="colorblind")
plt.rcParams.update({
    'figure.autolayout': True,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10
})

def _get_filenames(charts_dir, title: str):
    clean = "".join(c if c.isalnum() else "_" for c in title).lower()
    return (
        os.path.abspath(os.path.join(charts_dir, f"{clean}.png")),
        os.path.abspath(os.path.join(charts_dir, f"{clean}.svg"))
    )

class ChartStrategy(ABC):
    def __init__(self, target_analyses: List[str]):
        self.target_analyses = target_analyses
        
    def should_run(self, analysis_plan: List[str]) -> bool:
        # If no specific plan is provided, default to running it
        if not analysis_plan:
            return True
        return any(analysis in analysis_plan for analysis in self.target_analyses)

    @abstractmethod
    def generate(self, df: pd.DataFrame, analysis_type: str, charts_dir: str) -> Optional[ChartMetadata]:
        pass

class LineChartStrategy(ChartStrategy):
    def __init__(self):
        super().__init__(["trend", "time", "histor"])
        
    def generate(self, df: pd.DataFrame, analysis_type: str, charts_dir: str) -> Optional[ChartMetadata]:
        date_col = get_date_col(df)
        target = get_target_metric(df)
        if date_col and target:
            title = f"{target} over Time"
            png_path, svg_path = _get_filenames(charts_dir, title)
            
            try:
                plt.figure(figsize=(10, 6))
                df_sorted = df.sort_values(date_col)
                sns.lineplot(data=df_sorted, x=date_col, y=target)
                plt.title(title, fontweight='bold')
                plt.xticks(rotation=45)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.savefig(png_path, dpi=300)
                plt.savefig(svg_path)
                plt.close()
            except Exception:
                png_path, svg_path = None, None

            return ChartMetadata(
                chart_id=str(uuid.uuid4()),
                chart_title=title,
                chart_type="Line Chart",
                x_axis=date_col,
                y_axis=target,
                aggregation="Sum",
                sorting="Ascending (Date)",
                filters="None",
                description=f"A line chart showing the trend of {target} over {date_col}.",
                business_purpose="Analyze temporal patterns and trends.",
                source_analysis=analysis_type,
                confidence=0.9,
                file_path=png_path,
                svg_file_path=svg_path
            )
        return None

class BarChartStrategy(ChartStrategy):
    def __init__(self):
        super().__init__(["segment", "compar", "categor", "region", "product"])
        
    def generate(self, df: pd.DataFrame, analysis_type: str, charts_dir: str) -> Optional[ChartMetadata]:
        cats = get_categorical_cols(df)
        target = get_target_metric(df)
        if cats and target:
            cat = cats[0]
            title = f"{target} by {cat}"
            png_path, svg_path = _get_filenames(charts_dir, title)
            
            try:
                plt.figure(figsize=(10, 6))
                agg_df = df.groupby(cat)[target].sum().sort_values(ascending=False).head(10).reset_index()
                sns.barplot(data=agg_df, x=cat, y=target)
                plt.title(title, fontweight='bold')
                plt.xticks(rotation=45)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.savefig(png_path, dpi=300)
                plt.savefig(svg_path)
                plt.close()
            except Exception:
                png_path, svg_path = None, None

            return ChartMetadata(
                chart_id=str(uuid.uuid4()),
                chart_title=title,
                chart_type="Bar Chart",
                x_axis=cat,
                y_axis=target,
                aggregation="Sum",
                sorting="Descending (Value)",
                filters="Top 10",
                description=f"A bar chart comparing {target} across different {cat} categories.",
                business_purpose="Identify top-performing segments.",
                source_analysis=analysis_type,
                confidence=0.9,
                file_path=png_path,
                svg_file_path=svg_path
            )
        return None

class ScatterPlotStrategy(ChartStrategy):
    def __init__(self):
        super().__init__(["correlat", "driver", "relationship"])
        
    def generate(self, df: pd.DataFrame, analysis_type: str, charts_dir: str) -> Optional[ChartMetadata]:
        numerics = get_numeric_cols(df)
        if len(numerics) >= 2:
            title = f"{numerics[0]} vs {numerics[1]}"
            png_path, svg_path = _get_filenames(charts_dir, title)
            
            try:
                plt.figure(figsize=(8, 8))
                sns.scatterplot(data=df, x=numerics[0], y=numerics[1], alpha=0.6, edgecolor=None)
                plt.title(title, fontweight='bold')
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.savefig(png_path, dpi=300)
                plt.savefig(svg_path)
                plt.close()
            except Exception:
                png_path, svg_path = None, None

            return ChartMetadata(
                chart_id=str(uuid.uuid4()),
                chart_title=title,
                chart_type="Scatter Plot",
                x_axis=numerics[0],
                y_axis=numerics[1],
                aggregation="None",
                sorting="None",
                filters="None",
                description=f"A scatter plot showing the relationship between {numerics[0]} and {numerics[1]}.",
                business_purpose="Observe correlations between key numerical metrics.",
                source_analysis=analysis_type,
                confidence=0.85,
                file_path=png_path,
                svg_file_path=svg_path
            )
        return None

class PieChartStrategy(ChartStrategy):
    def __init__(self):
        super().__init__(["distribut", "proportion", "share", "segment"])
        
    def generate(self, df: pd.DataFrame, analysis_type: str, charts_dir: str) -> Optional[ChartMetadata]:
        cats = get_categorical_cols(df, max_card=10)
        if cats:
            title = f"Distribution of {cats[0]}"
            png_path, svg_path = _get_filenames(charts_dir, title)
            
            try:
                plt.figure(figsize=(8, 8))
                counts = df[cats[0]].value_counts()
                plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, 
                        colors=sns.color_palette("colorblind"))
                plt.title(title, fontweight='bold')
                plt.savefig(png_path, dpi=300)
                plt.savefig(svg_path)
                plt.close()
            except Exception:
                png_path, svg_path = None, None

            return ChartMetadata(
                chart_id=str(uuid.uuid4()),
                chart_title=title,
                chart_type="Pie Chart",
                x_axis=cats[0],
                y_axis="Count",
                aggregation="Count",
                sorting="Descending (Count)",
                filters="None",
                description=f"A pie chart showing the proportion of each {cats[0]}.",
                business_purpose="Understand the composition of the categorical variable.",
                source_analysis=analysis_type,
                confidence=0.8,
                file_path=png_path,
                svg_file_path=svg_path
            )
        return None

class HistogramStrategy(ChartStrategy):
    def __init__(self):
        super().__init__(["distribut", "spread", "frequenc", "outlier", "statistic"])
        
    def generate(self, df: pd.DataFrame, analysis_type: str, charts_dir: str) -> Optional[ChartMetadata]:
        target = get_target_metric(df)
        if target:
            title = f"Distribution of {target}"
            png_path, svg_path = _get_filenames(charts_dir, title)
            
            try:
                plt.figure(figsize=(10, 6))
                sns.histplot(data=df, x=target, kde=True, bins=30)
                plt.title(title, fontweight='bold')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.savefig(png_path, dpi=300)
                plt.savefig(svg_path)
                plt.close()
            except Exception:
                png_path, svg_path = None, None

            return ChartMetadata(
                chart_id=str(uuid.uuid4()),
                chart_title=title,
                chart_type="Histogram",
                x_axis=target,
                y_axis="Frequency",
                aggregation="Count",
                sorting="None",
                filters="None",
                description=f"A histogram displaying the distribution of {target}.",
                business_purpose="Analyze the frequency and spread of the primary metric.",
                source_analysis=analysis_type,
                confidence=0.9,
                file_path=png_path,
                svg_file_path=svg_path
            )
        return None

class ChartRegistry:
    """Registry that dynamically executes registered chart strategies based on the analysis plan."""
    def __init__(self, workflow_id: str):
        from backend.services.artifact_manager import ArtifactManager
        self.artifact_mgr = ArtifactManager(workflow_id)
        self.charts_dir = str(self.artifact_mgr.get_charts_dir())
        
        self._strategies = [
            LineChartStrategy(),
            BarChartStrategy(),
            ScatterPlotStrategy(),
            PieChartStrategy(),
            HistogramStrategy()
        ]
        
    def generate_all(self, df: pd.DataFrame, analysis_plan: List[str]) -> tuple[List[ChartMetadata], int]:
        charts = []
        skipped_count = 0
        
        # If no plan is provided, fallback to generating everything possible
        plan_to_use = [a.lower() for a in analysis_plan] if analysis_plan else [
            "trend", "segment", "correlat", "distribut"
        ]
        
        for strategy in self._strategies:
            # Check if this strategy is requested by the plan
            strategy_targets = [t.lower() for t in strategy.target_analyses]
            matching_analyses = [a for a in plan_to_use if any(t in a or a in t for t in strategy_targets)]
            if matching_analyses:
                # Use the first matched analysis as the source_analysis reason
                analysis_type = matching_analyses[0]
                try:
                    res = strategy.generate(df, analysis_type, self.charts_dir)
                    if res:
                        charts.append(res)
                    else:
                        skipped_count += 1
                except Exception:
                    skipped_count += 1
            else:
                skipped_count += 1
                
        # Generate chart manifest
        try:
            self.artifact_mgr.save_json("charts", "chart_manifest.json", [c.model_dump() for c in charts])
        except Exception:
            pass
            
        return charts, skipped_count
